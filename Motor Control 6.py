import httpx
import base64
import json
import os
import openai
from PIL import Image
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from io import BytesIO

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

#Location of Map
image_path = "Plan-small4.jpg"

#Load the map image as text
with open(image_path, "rb") as image_file:
    image_data = base64.b64encode(image_file.read()).decode("utf-8")

#Prove the map has been loaded
prompt = "List the rooms shown on this plan."

response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
    {"role": "system", "content": prompt},
    {"role": "user", "content": f"<image>{image_data}</image>"}
    ]
)

#completion_id = response['id']
print(response.choices[0].message.content)

#reply = response.get('content')
#print(reply)
#print(type(response))

# Set model and parser
model = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()

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




