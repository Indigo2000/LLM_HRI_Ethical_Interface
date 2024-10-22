import httpx
import base64
import json
import os
import openai
import Layout
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





# Set model and parser
model = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()

#prompt templates:

system_template = "Find the destination room from this instruction and return the name of that room only:"

# Define the prompt
prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)


chain = prompt_template | model | parser

# Function to process commands
def process_command(command):
    response = chain.invoke({"text": command})
    print("Response is: ")
    print(response)
    return response

start_room = 'Hall'
quit = False

while quit == False:
    user_input = input("Enter command: ")
    goal_room=process_command(user_input)
    if goal_room == 'quit':
        break;
    path, total_cost = Layout.a_star_search(Layout.graph, start_room, goal_room, Layout.h)
    if path:
        print(f"Path from {start_room} to {goal_room}:")
        for room, direction in path:
            print(f" - Move {direction} to {room}")
        print(f"Total cost: {total_cost}")
        start_room = goal_room
    else:
        print(f"No path found from {start_room} to {goal_room}.")



