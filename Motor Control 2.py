import httpx
import base64
import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Loads OpenAI and LangChain Keys
def load_keys():
    try:
        file = open("../Keys/RPKeys.json")
        keys = json.load(file)
        print("Keys loaded.")
        file.close()
        return keys

    except FileNotFoundError:
        print("File not Found")
        
#Load Keys and set environment variables
loaded_keys = load_keys()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = loaded_keys.get('LANGCHAIN_API_KEY')
os.environ["LANGCHAIN_PROJECT"] = "LangChain Tutorial 1"
os.environ["OPENAI_API_KEY"] = loaded_keys.get('OPENAI_API_KEY')

# Set model and parser
model = ChatOpenAI(model="gpt-4")
parser = StrOutputParser()

#Location of Map
image_url = "Plan.png"

#Load the image data is text
image_data = base64.b64encode(httpx.get(image_url).content).decode("utf-8")

#Prove the map has been loaded
message = HumanMessage(
    content=[
        {"type": "text", "text": "List the rooms shown on this plan."},
        {"type": "image_url", "image_url": {"url": f*data:image/png;base64,{image_data}"}},
    ]
)

response = model.invoke([message])
print(response.content)


#prompt templates:

system_template = "Interpret the following command for motor control in a concise manner:"

# Define the prompt
prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)


chain = prompt_template | model | parser

# Function to process commands
def process_command(command):
    response = chain.invoke({"text": command})
    print(response)
    if "forward" in response:
        #motor_forward()
        print("Yeah, I'll go forwards")
        return True
    elif "backward" in response:
        #motor_backward()
        print("Yeah, I'll go backwards")
        return True
    elif "stop" in response:
        print("Yeah, I'll stop")
        #motor_stop()
        return True
    elif "quit" in response:
        return False
    else:
        print("Unknown command")
        return True

# Example usage
test = True
while test==True:
    user_input = input("Enter command: ")
    test=process_command(user_input)




