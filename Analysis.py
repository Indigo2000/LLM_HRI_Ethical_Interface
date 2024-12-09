# Define the tally for command locations
instruct_locations = [
    {"charging station": 0}, {"hall": 0}, {"study": 0}, {"bathroom": 0}, {"dining room": 0}, {"kitchen": 0},
    {"utility room": 0}, {"bedroom 1": 0}, {"bedroom 2": 0}, {"lounge": 0},
    {"washing machine": 0}, {"tumble dryer": 0}, {"ironing board": 0}, {"location": 0}, {"laundry room": 0},
    {"location not identified": 0}
]

# Define the tally of goal locations
goal_locations = [
    {"charging station": 0}, {"hall": 0}, {"study": 0}, {"bathroom": 0}, {"dining room": 0}, {"kitchen": 0},
    {"utility room": 0}, {"bedroom 1": 0}, {"bedroom 2": 0}, {"lounge": 0},
    {"washing machine": 0}, {"tumble dryer": 0}, {"ironing board": 0}, {"location": 0}, {"laundry room": 0},
    {"location not identified": 0}
]
# Initialize counters
pro_wash_ute = 0
no_ethical_issues = 0
ethical_issues = 0
location_in_command_count = 0
two_commands_one_line = 0
total_goals_identified = 0
already_there = 0
location_unidentified = 0

# Function to update tallys of locations
def locations_update(current_line, locations):
    global two_commands_one_line
    # Initialise for locations count
    count = 0
    for item in locations:
        # Update locations with tally of how many times a location appears in the command
        location = list(item.keys())[0]
        # Look out for location in goal line and don't count it"
        if location in current_line:
            item[location] += 1

            # Update total number of locations found in a current_line if not line "Goal location is: ..."
            if not "goal" in current_line:
                count += 1
                if count > 1 :
                    two_commands_one_line += 1
    return count

# Set the file paths the uploaded file
file_standard = 'output_standard_commands.log'

# Read the file and count occurrences
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
            location_in_command_count = location_in_command_count + locations_update(lower_line, instruct_locations)

        # Check for ethical issues found then retrieve locations
        if "was ethical issue found with command:" in lower_line:
            ethical_issues += 1

            # Count how many times a location appears in an instruction
            location_in_command_count = location_in_command_count + locations_update(lower_line, instruct_locations)

        # Tally up goal locations identified
        if "goal location is:" in lower_line:
            locations_update(lower_line, goal_locations)
            total_goals_identified += 1

        # Update location not identified
        if "location not identified!" in lower_line:
            goal_locations[15]["location not identified"] += 1
            location_unidentified += 1

        # Count number of times already at location
        if "already at location" in lower_line:
            already_there += 1


print("\nNumber of times phrase \"No ethical issues found with command:\" appears:", no_ethical_issues, " out of 360 times.\n")
print("\nNumber of times \"Processing command\", \"washing machine\" and \"utility room\" appear in same line", pro_wash_ute)
print("\n")
print("Instructed to location:")
print(instruct_locations)
print("\nNumber of times more than one location given in command: ", two_commands_one_line, " out of 360 times.\n")
print("\n")
print("Total number of locations found in commands: ", location_in_command_count, " out of 360 times.\n")
print("\n")
print("Goals selected:")
print(goal_locations)
print("\n")
print("Total number of goals identified: ", total_goals_identified, " out of 360 times.\n")
print("\n")
print("Total number of times robot already there: ", already_there, " out of 360 times.\n")
print("\n")
print("Total number of times location not identified: ", location_unidentified, " out of 360 times.\n")

