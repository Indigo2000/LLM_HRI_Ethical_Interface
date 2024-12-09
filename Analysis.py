import pandas as pd
import ethically_dubious_commands

pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)

# Define the tally for command locations
instruct_locations = {
    "locations" : [
    "charging station", "hall", "study", "bathroom", "dining room", "kitchen", "utility room", "bedroom 1", "bedroom 2",
    "lounge", "washing machine", "tumble dryer", "ironing board", "location", "laundry room", "location not identified"
    ],
    # Initialise all to zero
    "Count": [0] * 16
}

# Define the tally of goal locations
goal_locations = {
    "locations" : [
    "charging station", "hall", "study", "bathroom", "dining room", "kitchen", "utility room", "bedroom 1", "bedroom 2",
    "lounge", "washing machine", "tumble dryer", "ironing board", "location", "laundry room", "location not identified"
    ],
    # Initialise all to zero
    "Count": [0] * 16
}

# Initialise dataframes
df_command_locations = pd.DataFrame(instruct_locations)
df_goal_locations = pd.DataFrame(goal_locations)
df_unethical_tallies = pd.DataFrame(ethically_dubious_commands.commands_tally)

# Initialize counters
pro_wash_ute = 0
no_ethical_issues = 0
ethical_issues = 0
location_in_command_count = 0
two_commands_one_line = 0
total_goals_identified = 0
already_there = 0
location_unidentified = 0
correct_queue = 0
queue_counter = 0
# For checking which line phrase appears in file
start_line = 0
# Lists of dictionaries for commands and goals
queued_goals = []
inferred_goals = []
a_star_route_check = []
# For counting entries in the list
list_entry = 0
# For counting entries in A Star route
a_star_route_count = 0


# Function to update tallies in dataframes
def tally_update(current_line, to_tally):
    global two_commands_one_line

    # Initialise for locations count
    command_count = 0

    for index, row in to_tally.iterrows():
        if row[to_tally.columns[0]] in current_line:
            to_tally.at[index, 'Count'] += 1

            # Phrase "Shoot the gun" appears as part of another phrase so don't count it twice
            if "Shoot the gun at David" in current_line:
                if to_tally.loc[index, 'command'] == "Shoot the gun":
                    to_tally.loc[index, 'Count'] -= 1

            # Count number of times phrase found for command locations count
            if not "goal" in current_line and to_tally.columns[0] != "command":
                command_count += 1
                if command_count > 1:
                    two_commands_one_line += 1

        # Avoid counting location word from "goal location is". Location will never be a goal.
        if "goal location is" in current_line:
            if to_tally.loc[index, 'locations'] == "location":
                to_tally.loc[index, 'Count'] -= 1

    return command_count

# Set the file paths the uploaded file
file_standard = 'output_standard_commands.log'
file_inferred = 'output_standard_commands_location_inference.log'
file_unethical = 'output_unethical_commands_10_runs.log'

# Read the file for standard commands and count occurrences
with open(file_standard, 'r') as standard_file:
    content = standard_file.readlines()

    # Analyze line by line with case insensitivity
    for line in content:
        lower_line = line.lower()

        # Check for processing, w/machine and utility in same line,
        if (not 'finished' in lower_line and 'processing command:' in lower_line
        and 'washing machine' in lower_line and 'utility room' in lower_line):

            pro_wash_ute += 1

        # Check for no ethical issues found then retrieve locations
        if "no ethical issues found with command:" in lower_line:
            no_ethical_issues += 1

            # Count how many times a location appears in an instruction
            location_in_command_count = location_in_command_count + tally_update(lower_line, df_command_locations)

            # Add key for checking queue operation
            queued_goals.append({"Given Command": lower_line[39:-1], "Processed Command": ""})

        # Check for ethical issues found then retrieve locations
        if "was ethical issue found with command:" in lower_line:
            ethical_issues += 1

            # Count how many times a location appears in an instruction
            location_in_command_count = location_in_command_count + tally_update(lower_line, df_command_locations)

        if "start location is:" in lower_line:
            # Add start for checking A* operation
            a_star_route_check.append({"Start": lower_line[20:-1], "Goal": "", "Route": ""})

        # Tally up goal locations identified
        if "goal location is:" in lower_line:
            tally_update(lower_line, df_goal_locations)
            total_goals_identified += 1

            # Add in the goal for this command to A* route check
            a_star_route_check[a_star_route_count]["Goal"] = lower_line[19:-1]

        # Update location not identified
        if "location not identified!" in lower_line:
            #goal_locations[15]["location not identified"] += 1
            location_unidentified += 1

        # Count number of times already at location
        if "already at location" in lower_line:
            already_there += 1

        # Check the queue for correct operation - does processing match given?
        if "processing command" in lower_line and "finished" not in lower_line:
            # Find the next entry in the list and update its value
            queued_goals[list_entry]["Processed Command"] = lower_line[19:-1]
            list_entry += 1

        # Add route to A* route check
        if "route found to be:" in lower_line:
            a_star_route_check[a_star_route_count]["Route"] = lower_line[21:-2]
            a_star_route_count +=1

# Convert queued goals data to a data frame
df_queued_goals = pd.DataFrame(queued_goals)

# Convert A* route check to a data frame
df_a_star_route_check = pd.DataFrame(a_star_route_check)

# Check queue for correct operation
for item in queued_goals:
    if queued_goals[queue_counter]["Given Command"][:-1] == queued_goals[queue_counter]["Processed Command"][2:]:
        correct_queue += 1
    queue_counter += 1
###### Now check commands for inferring location

# Reset required counters
list_entry = 0

# Read the file for inferred commands and count occurrences
with open(file_inferred, 'r') as inferred_file:
    content = inferred_file.readlines()

    # Analyze line by line with case insensitivity
    for count, line in enumerate(content):
        lower_line = line.lower()

        if "processing command" in lower_line and not "finished" in lower_line:
            inferred_goals.append({"Command": lower_line[21:-1], "Goal": ""})
        if "goal location is:" in lower_line:
            # Find the next entry in the list and update it's value
            inferred_goals[list_entry]["Goal"] = lower_line[19:-1]
            list_entry += 1

# Convert to a dat frame
df_inferred_locations = pd.DataFrame(inferred_goals)


##### Now check ethically dubious commands
# Read the file for standard commands and count occurrences
with open(file_unethical, 'r') as unethical_file:
    content = unethical_file.readlines()

    # Analyze line by line with case insensitivity
    for line in content:
        lower_line = line.lower()
        if "was ethical issue found" in lower_line:# or "no ethical issues found" in lower_line:
            tally_update(line, df_unethical_tallies)


# Print out all the results
print("\nNumber of times phrase \"No ethical issues found with command:\" appears:", no_ethical_issues, " out of 360 times.\n")
print("\nNumber of times \"Processing command\", \"washing machine\" and \"utility room\" appear in same line", pro_wash_ute)
print("\n")
print("Instructed to location:")
print(df_command_locations.to_string(justify="left"))
print("\nNumber of times more than one location given in command: ", two_commands_one_line, " out of 360 times.\n")
print("\n")
print("Total number of locations found in commands: ", location_in_command_count, " out of 360 times.\n")
print("\n")
print("Goals selected:")
print(df_goal_locations.to_string(justify="left"))
print("\n")
print("Total number of goals identified: ", total_goals_identified, " out of 360 times.\n")
print("\n")
print("Total number of times robot already there: ", already_there, " out of 360 times.\n")
print("\n")
print("Total number of times location not identified: ", location_unidentified, " out of 360 times.\n")
print("\n\n")
print("Queue operation - command given then command processing:")
print(df_queued_goals.to_string(justify="left"))
print("\n", correct_queue, " out of 360 commands queued and processed correctly")
print("\n\n")
print("A* route check:")
print(df_a_star_route_check.to_string(justify="left"))
print("\n\n")
print("Inferred Commands:")
print(df_inferred_locations.to_string(justify="left"))
print("\n\n")
print("Ethically dubious commands tally:")
print(df_unethical_tallies.to_string(justify="left"))


