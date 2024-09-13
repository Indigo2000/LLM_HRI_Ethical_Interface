# from langchain import OpenAI, ConversationChain
from langchain_community import llms
from langchain.prompts import ChatPrompt

# Define the prompt
prompt = ChatPrompt(messages=[
    {"role": "system", "content": "You are a motor control assistant."},
    {"role": "user", "content": "You can control a motor using text commands."},
])

# Initialize the OpenAI language model
llm = OpenAI(temperature=0.7)

# Create a conversation chain with the prompt
conversation = ConversationChain(prompt=prompt, llm=llm)

# Function to process commands
def process_command(command):
    response = conversation.run(command)
    if "forward" in response:
        motor_forward()
    elif "backward" in response:
        motor_backward()
    elif "stop" in response:
        motor_stop()
    else:
        print("Unknown command")

# Example usage
while True:
    user_input = input("Enter command: ")
    process_command(user_input)
