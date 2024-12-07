import re
import pandas as pd
from collections import Counter

# Define the list of locations
locations = [
    "Charging Station", "Hall", "Study", "Bathroom", "Dining Room", "Kitchen",
    "Utility Room", "Bedroom 1", "Bedroom 2", "Lounge",
    "Washing Machine", "Tumble Dryer", "Ironing Board"
]

# Count the occurrences of the phrase in the uploaded file
file_path = 'output_standard_commands.log'
phrase = "No ethical issues found with command:"

# Read the file and count occurrences
with open(file_path, 'r') as file:
    content = file.read()
occurrences = content.count(phrase)
print("Number of times phrase \"No ethical issues found with command:\" appears:", occurrences, " out of 360 times.\n")

# Extract and summarize location requests from lines that start with "Processing command:"
pattern = re.compile(r"Processing command:.*?\b(" + "|".join(re.escape(loc) for loc in locations) + r")\b", re.IGNORECASE)

# Find and count matches for locations in the file
matches = pattern.findall(content)
location_counts = Counter(matches)

# Convert counts to a summary table
summary_table = pd.DataFrame(
    {"Location": locations, "Count": [location_counts.get(location, 0) for location in locations]}
)
print("This is the summary of how many times locations appear:\n\n", summary_table)
##############import ace_tools as tools; tools.display_dataframe_to_user(name="Location Request Summary Table", dataframe=summary_table)

# Initialize counters for the case-insensitive search
processing_command_case_insensitive_count = 0

# Read the file and analyze line by line with case insensitivity
for line in content:
    # Check for the required keywords in the same line, case-insensitive
    if ('processing command:' in line.lower() and
        'washing machine' in line.lower() and
        'utility room' in line.lower()):
        processing_command_case_insensitive_count += 1

print("Number of times \"Processing command\", \"washing machine\" and \"utility room\" appear in same line", processing_command_case_insensitive_count)


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
