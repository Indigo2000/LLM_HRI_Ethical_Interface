#import necessary libraries
from langchain_core.prompts import ChatPromptTemplate

# Define templates
system_template = "You are a helpful assistant."
user_template = "{text}"

# Create ChatPromptTemplate

prompt_template = ChatPromptTemplate.from_messages(

    [("system", system_template), ("user", user_template)]
    
)

# Create a sample input

input_data = {"text": "How can I help you today?"}


# Generate the prompt value

prompt_value = prompt_template.invoke(input_data)

# Print the result

print(prompt_value)
