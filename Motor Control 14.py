import httpx
import base64
import json
import os
import openai
import Layout
import re
#import GPIO_Communication
from PIL import Image
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from io import BytesIO


import sys
print(sys.executable)

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
system_template_directions = "Start room = {start_room} Goal room = {goal_room} Graph = {graph} and heuristics = {heuristic}"
system_template_directions_output = "Return the route from Start room to Goal room. Use A* search on the graph and heuristics provided. Only return the names of the rooms you pass through as a python list. If you receive a goal room that is not in the list, do not perform the search and say only: 'That room is unknown'." 

#define the data for directions
directions_data = {
    "start_room": start_room,
    "goal_room": goal_room,
    "graph": Layout.graph,
    "heuristic": Layout.h
    }
    
# Define the prompts
prompt_template_destination = ChatPromptTemplate.from_messages([("system", system_template_destination), ("user", "{text}")])
prompt_template_directions = ChatPromptTemplate.from_messages([("system", system_template_directions_output), ("user", "{text}")])

#define the chains
chain_destination = prompt_template_destination | model | parser
chain_directions = prompt_template_directions | model | parser

# Function to find the destination
def process_command_destination(command):
    response = chain_destination.invoke({"text": command})
    print("Destinaion response is: ")
    print(response)
    
    #Check if we have a valid room
    try:
        room = Layout.h[response]
        directions_data["goal_room"] = response
        return True
    except:
        print("No such room!\n")
        #If room does not exist, set the goal room to be the start room
        directions_data["goal_room"] =  directions_data["start_room"]
        return False

# Function to find the route
def process_command_route(command):
    response = chain_directions.invoke({"text": command})
    return response
    
def route_list_create(room_list):
    #extract python list from text
        # Use regular expression to capture list after equals sign until the last closing bracket
    match = re.search(r'(\[[^\]]*\])', room_list)
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

    
# Function to control the motor
def motion_control(route):
    print("To do")
    
#      if "forward" in response:
#        #motor_forward()
#        print("Yeah, I'll go forwards")
#        return True
#    elif "backward" in response:
#        #motor_backward()
#        print("Yeah, I'll go backwards")
#        return True
#    elif "stop" in response:
#        print("Yeah, I'll stop")
#        #motor_stop()
#        return True
#    elif "quit" in response:
#        return False
#    else:
#        print("Unknown command")
#        return True  
  

#Main loop    
quit = False
while quit == False:
    #Get user input
    user_input = input("Enter command: ")
    
    #If user wishes to quit
    if user_input == 'quit':
        break;
    
    #update goal_room    
    if not process_command_destination(user_input.title()):
        #restart loop if gaol room invalid
        continue
        
    #State where we start and where we end    
    print("Start room is: ", directions_data["start_room"])
    print("Goal room is: ", directions_data["goal_room"])   
    
    #Get the route we'll take
    directions = process_command_route(system_template_directions.format(**directions_data))
    
    #Simulate motor response    
    route_list = route_list_create(directions)
    print(route_list)
    
    #update start room
    directions_data["start_room"] = directions_data["goal_room"]



