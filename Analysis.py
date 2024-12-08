import re
import pandas as pd
from collections import Counter

# Define the list of locations
locations = [
    {"charging station": 0}, {"hall": 0}, {"study": 0}, {"bathroom": 0}, {"dining room": 0}, {"kitchen": 0},
    {"utility room": 0}, {"bedroom 1": 0}, {"bedroom 2": 0}, {"lounge": 0},
    {"washing machine": 0}, {"tumble Dryer": 0}, {"ironing board": 0}, {"location": 0}, {"laundry room": 0},
    {"location not identified": 0}
]

# Initialize counters for the case-insensitive search
pro_wash_ute = 0
no_ethical_issues = 0
ethical_issues = 0
location_in_command_count = 0

# Count the occurrences of the phrase in the uploaded file
file_path = 'output_standard_commands.log'
#phrase = "No ethical issues found with command:"

# Read the file and count occurrences
with open(file_path, 'r') as file:
    content = file.readlines()

    # Analyze line by line with case insensitivity
    for line in content:
        lower_line = line.lower()
        # Check for processing, w/machine and utility in same line,
        if (not 'finished' in lower_line and 'processing command:' in lower_line
        and 'washing machine' in lower_line and 'utility room' in
               lower_line):
            pro_wash_ute += 1
        # Check for no ethical issues found then retrieve locations
        if "no ethical issues found with command:" in lower_line:
            no_ethical_issues += 1

            # Count how many times a location appears as a goal
            for item in locations:
                # Update locations with tally of how many times a location appears in the command
                location_word = list(item.keys())[0]
                if location_word in lower_line:
                    item[location_word] += 1

                    # Update total number of locations found in a command
                    location_in_command_count += 1

        # Check for ethical issues found then retrieve locations
        if ("was ethical issue found with command:" in lower_line):
            ethical_issues += 1





# Extract and summarize goal locations from lines that start with "Goal location is:"
#pattern = re.compile(r"Goal location is:.*?\b(" + "|".join(re.escape(loc) for loc in locations) + r")\b", re.IGNORECASE)


#response.find(":") + 2

# Find and count matches for locations in the file
#matches = pattern.findall(content)
#location_counts = Counter(matches)

# Convert counts to a summary table
#goal_summary_table = pd.DataFrame(
#    {"Location": locations, "Count": [location_counts.get(location, 0) for location in locations]}
#)

# Get the total locations


# Extract and summarize goal locations from lines that start with "Goal location is:"
#pattern = re.compile(r"Already at location.*?\b(" + "|".join(re.escape(loc) for loc in locations) + r")\b", re.IGNORECASE)

# Find and count matches for locations in the file
#matches = pattern.findall(content)
#location_counts = Counter(matches)

# Convert counts to a summary table
#already_summary_table = pd.DataFrame(
#    {"Location": locations, "Count": [location_counts.get(location, 0) for location in locations]}
#)


print("\nNumber of times phrase \"No ethical issues found with command:\" appears:", no_ethical_issues, " out of 360 times.\n")
#print("\nThis is the summary of how many times locations appear as goal location:\n\n", goal_summary_table)
#print("\nThis is the summary of how many times locations appear as already at location:\n\n", already_summary_table)
print("\nNumber of times \"Processing command\", \"washing machine\" and \"utility room\" appear in same line", pro_wash_ute)
print("\n\n\n")
print(locations)
print("\n")
print("Total number of locations found in commands: ", location_in_command_count)

## Re-analyze including the duplicate phrase twice in the results
## Adjust to ensure duplicate is counted separately by treating it as two entries
#duplicated_phrases_counts = corrected_phrases.copy()  # Keep the duplicate as is

## Count occurrences for all including duplicates
#duplicated_all_phrases_counts = [
#    (phrase, sum(1 for line in cleaned_file_content if phrase in line))
#    for phrase in duplicated_phrases_counts
#]

## Convert to DataFrame for display
#duplicated_all_phrases_counts_df = pd.DataFrame(duplicated_all_phrases_counts, columns=["Phrase", "Count"])

## Display the adjusted results
#tools.display_dataframe_to_user(
#    name="Full Phrase Occurrence Summary (Including Duplicate)", dataframe=duplicated_all_phrases_counts_df
#)
