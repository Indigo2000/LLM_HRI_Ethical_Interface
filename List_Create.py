import re

def extract_list_from_text(text):
    # Use regular expression to capture list after equals sign until the last closing bracket
    match = re.search(r'=\s*(\[[^\]]*\])', text)
    if match:
        extracted_list = match.group(1)
        try:
            # Safely evaluate the extracted list string into a Python list
            result = eval(extracted_list)
            if isinstance(result, list):
                return result
        except Exception as e:
            print(f"Error evaluating list: {e}")
    return None

# Example usage
text = "some_variable = [1, 2, 3, 4, 'a', 'b'] something else"
extracted_list = extract_list_from_text(text)
print(extracted_list)
