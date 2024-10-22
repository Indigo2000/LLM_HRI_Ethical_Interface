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

# Set the initial start and end positions
start_room = 'Hall'
goal_room = 'Lounge'

#prompt templates:
system_template_destination = "Find the destination room from this instruction and return the name of that room only:"
system_template_directions = "Return the directions from {start_room} to {goal_room} using A* search with graph {graph} and heuristic {heuristic}"

#define the data for directions
directions_data = {
    "start_room": start_room,
    "goal_room": goal_room,
    "graph": Layout.graph,
    "heuristic": Layout.h
    }
    
# Define the prompt
prompt_template_destination = ChatPromptTemplate.from_messages([("system", system_template_destination), ("user", "{text}")])
prompt_template_directions = ChatPromptTemplate.from_messages([("system", system_template_directions), ("user", "{text}")])

#define the chains
chain_destination = prompt_template_destination | model | parser
chain_directions = prompt_template_directions | model | parser

# Function to process commands
def process_command_destination(command):
    response = chain_destination.invoke({"text": command})
    print("Destinaion response is: ")
    print(response)
    return response
    
#def process_command_directions(command):
#    response = chain_directions.invoke({"text": command})
#    print("Directions response is: ")
#    print(response)
#    return response
    
quit = False
print("Starting loop...")
while quit == False:
    user_input = input("Enter command: ")
    goal_room=process_command_destination(user_input)
    if goal_room == 'quit':
        break;
    get_directions = system_template_directions.format(**directions_data)
    print(get_directions)
    directions= chain_directions.invoke({"text": get_directions})
    print("\n")
    print(directions)
    start_room = goal_room



