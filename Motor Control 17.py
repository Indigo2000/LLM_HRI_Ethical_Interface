#import httpx
#import base64
import json
import os
import openai
import Layout
import re
import GPIO_Communication
#from PIL import Image
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
#from io import BytesIO
#import concurrent.futures
import asyncio

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
    
def directions_list_create(room_route):
    #Set the current room to be the start_room
    print("Setting current room to: ", directions_data["start_room"])
    current_room = directions_data["start_room"]
    
    #Create lists to store directions and distances
    directions_list = []
    distance_list = []
    
    #Look through the room route list
    for item in room_route:
        
        #ignore start room
        if item == directions_data["start_room"]:
            print("ignoring start room:", item)
            continue
            
        #Look through the list of available rooms from the current room
        for room in Layout.graph[current_room]:
            if room[0] == item:
                directions_list.append(room[2])
                distance_list.append(room[1])
        current_room = item
        
    print("Directions: ", directions_list)
    print("Distance: ", distance_list)
    return directions_list, distance_list
    
# Function to control the motor
def motion_control(route, distances):
    
    counter = 0
    
    for item in route:
        print("Loop: ", counter, "item is: ", item)
        if item == "forward":
            async def move_f():
                await asyncio.gather(GPIO_Communication.motor_forward(distances[counter]))
            asyncio.run(move_f())
            
        elif item == "back":
            async def move_b():
                await asyncio.gather(GPIO_Communication.motor_backward(distances[counter]))
            asyncio.run(move_b())
            
        elif item == "left":
            async def move_l():
                await asyncio.gather(GPIO_Communication.motor_left(distances[counter]))
            asyncio.run(move_l())
        
        elif item == "right":
            async def move_r():
                await asyncio.gather(GPIO_Communication.motor_right(distances[counter]))
            asyncio.run(move_r())
            
        elif item == "diagonally forward and left":
            async def move_fl():
                await asyncio.gather(GPIO_Communication.motor_forward(distances[counter]), GPIO_Communication.motor_left(distances[counter]))
            asyncio.run(move_fl())
        
        elif item == "diagonally forward and right":
            async def move_fr():
                await asyncio.gather(GPIO_Communication.motor_forward(distances[counter]), GPIO_Communication.motor_right(distances[counter]))
            asyncio.run(move_fr())
            
        elif item == "diagonally right and back":
            async def move_rb():
                await asyncio.gather(GPIO_Communication.motor_backward(distances[counter]), GPIO_Communication.motor_right(distances[counter]))
            asyncio.run(move_rb())
            
        elif item == "diagonally left and back":
            async def move_lb():
                await asyncio.gather(GPIO_Communication.motor_backward(distances[counter]), GPIO_Communication.motor_left(distances[counter]))
            asyncio.run(move_lb())
        
        else:
            print("Unknown command for motor control")
        counter = counter + 1
        #stop motors at the end of this loop
        GPIO_Communication.motor_stop()
        

#Main loop    
quit = False
while quit == False:
    #Get user input
    user_input = input("Enter command: ")
    
    #If user wishes to quit
    if user_input == 'quit':
        break;
    
    #update goal_room if it's valid    
    if not process_command_destination(user_input.title()):
        #restart loop if gaol room invalid
        continue
        
    #State where we start and where we end    
    print("Start room is: ", directions_data["start_room"])
    print("Goal room is: ", directions_data["goal_room"])   
    
    #Get the route we'll take
    directions = process_command_route(system_template_directions.format(**directions_data))
    if directions == "That room is unknown.":
        print("Room not found. Please try again.")
        continue
    
    #Simulate motor response    
    route_list = route_list_create(directions)
    print(route_list)
    directions_list, distance_list = directions_list_create(route_list)
    motion_control(directions_list, distance_list)
    
    #update start room
    directions_data["start_room"] = directions_data["goal_room"]



