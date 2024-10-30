import openai
import Layout
import re
import json
import os
import GPIO_Communication
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import asyncio
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk

#import GUI

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
    
# Define the prompts
prompt_template_destination = ChatPromptTemplate.from_messages([("system", system_template_destination), ("user", "{text}")])
prompt_template_directions = ChatPromptTemplate.from_messages([("system", system_template_directions_output), ("user", "{text}")])

#define the chains
chain_destination = prompt_template_destination | model | parser
chain_directions = prompt_template_directions | model | parser

#Setup queue
fifo_queue = deque()

#Setup global variables
global_quit = False

#define the data for directions
directions_data = {
    "start_room": start_room,
    "goal_room": goal_room,
    "graph": Layout.graph,
    "heuristic": Layout.h
    }

# Function to find the route
def process_command_route(command):
    response = chain_directions.invoke({"text": command})
    return response

# Function to find the destination
def process_command_destination(command):
    response = chain_destination.invoke({"text": command})
    print("Destinaion is: ", response)
    
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
    current_room = directions_data["start_room"]
    
    #Create lists to store directions and distances
    directions_list = []
    distance_list = []
    
    #Look through the room route list
    for item in room_route:
        
        #ignore start room
        if item == directions_data["start_room"]:
            continue
            f
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
async def motion_control(route, distances, rooms):
    
    counter = 0
    
    for item in route:
        print("Moving", item)
        if item == "forward":
            async def move_f():
                await asyncio.gather(GPIO_Communication.motor_forward(distances[counter]))
            await move_f()
            
        elif item == "back":
            async def move_b():
                await asyncio.gather(GPIO_Communication.motor_backward(distances[counter]))
            await move_b()
            
        elif item == "left":
            async def move_l():
                await asyncio.gather(GPIO_Communication.motor_left(distances[counter]))
            await move_l()
        
        elif item == "right":
            async def move_r():
                await asyncio.gather(GPIO_Communication.motor_right(distances[counter]))
            await move_r()
            
        elif item == "diagonally forward and left":
            async def move_fl():
                await asyncio.gather(GPIO_Communication.motor_forward(distances[counter]), GPIO_Communication.motor_left(distances[counter]))
            await move_fl()
        
        elif item == "diagonally forward and right":
            async def move_fr():
                await asyncio.gather(GPIO_Communication.motor_forward(distances[counter]), GPIO_Communication.motor_right(distances[counter]))
            await move_fr()
            
        elif item == "diagonally right and back":
            async def move_rb():
                await asyncio.gather(GPIO_Communication.motor_backward(distances[counter]), GPIO_Communication.motor_right(distances[counter]))
            await move_rb()
            
        elif item == "diagonally left and back":
            async def move_lb():
                await asyncio.gather(GPIO_Communication.motor_backward(distances[counter]), GPIO_Communication.motor_left(distances[counter]))
            await move_lb()
        
        else:
            print("Unknown command for motor control")
            
        #stop motors after move
        GPIO_Communication.motor_stop()
    
        counter = counter + 1    
        
        #update current position
        print("Successfully moved from ", directions_data["start_room"], "to ", rooms[counter])
        print("Setting current room to", rooms[counter])
        directions_data["start_room"] = rooms[counter]
        
async def ActionCommand(command):
        
    #update goal_room    
    if not process_command_destination(command.title()):
        #return if goal room invalid
        return
        
    #State where we start and where we end    
    print("Start room is: ", directions_data["start_room"])
    print("Goal room is: ", directions_data["goal_room"])   
    
    #Get the route we'll take
    directions = process_command_route(system_template_directions.format(**directions_data))
    if directions == "That room is unknown.":
        print("Room not found. Please try again.")
        return
    
    #Simulate motor response    
    route_list = route_list_create(directions)
    print("Route is: ", route_list)
    directions_list, distance_list = directions_list_create(route_list)
    await motion_control(directions_list, distance_list, route_list)
    
    #update start room
    directions_data["start_room"] = directions_data["goal_room"]
    
async def input_loop(queue, gui_app):
    global global_quit
    #loop = asyncio.get_running_loop()
    while global_quit == False:
        # Get user input without blocking the event loop
        user_input = await gui_app.get_input()
        await queue.put(user_input)
        if user_input.lower() == 'quit':
            global_quit = True
            break
        if user_input.lower() == 'stop':
            #Stop the motors
            GPIO_Communication.motor_stop()
                        
            #purge queue
            while not queue.empty():
                await queue.get()
                queue.task_done()
            #Mark the stop command as done
            queue.task_done()
            # Inform user
            print("\nStop command received. Current task aborted and all future tasks cancelled.")
            break;

async def process_commands(queue):
    global global_quit
    while global_quit == False:
        # Retrieve the next command from the queue
        command = await queue.get()
        if command.lower() == 'quit':
            print("Exiting command processor.")
            global_quit = True
            queue.task_done()
            continue
        
        print(f"Processing command: {command}")
        # Action a user command
        await ActionCommand(command)
        print(f"Finished processing command: {command}")
        print("\n")
        queue.task_done()

class GUIApp():
    def __init__(self, root):
        self.root = root
        self.root.geometry("600x60")
        self.root.title("Command input")
        self.entry = tk.Entry(self.root, width=40)
        self.entry.pack()
        self.entry.bind("<Return>", self.on_enter)
        self.button = tk.Button(self.root, text="Submit", command=self.submit_input)
        self.button.pack()
        self.input_future = None

    def submit_input(self):
        # When the button is clicked, set the result of the future to the user input
        if self.input_future:
            self.input_future.set_result(self.entry.get())
            # Clear the text from the field
            self.entry.delete(0, tk.END)
        

    async def get_input(self):
        # Create a new future and wait for input from the GUI
        self.input_future = asyncio.get_event_loop().create_future()
        return await self.input_future
    
    def on_enter(self, event):
        self.submit_input()

# Refresh the window periodically
async def update_tk(root):
    global global_quit
    while global_quit == False:
        #Try to update the window, if not possible (i.e. window closed), stop the motors and terminate the whole program
        try:
            root.update()
        except:
            GPIO_Communication.motor_stop()
            global_quit = True
        await asyncio.sleep(0.01)

async def main():
    
    # Set up the GUI
    root = tk.Tk()
    gui_app = GUIApp(root)
    
    queue = asyncio.Queue()
    
    # Run the asyncio event loop with the Tkinter main loop
    loop = asyncio.get_event_loop()
    
    while global_quit == False:
        producer = asyncio.create_task(input_loop(queue, gui_app))
        consumer = asyncio.create_task(process_commands(queue))
        gui_refresh = asyncio.create_task(update_tk(root))
        # Look out for producer to send stop command so we can cancel the consumer tasks
        # Or, if GUI is closed, kill everything
        done, pending = await asyncio.wait([producer, consumer, gui_refresh], return_when=asyncio.FIRST_COMPLETED)
        
        if producer in done:
            consumer.cancel()
       # if 

if __name__ == "__main__":
    asyncio.run(main())
        
        

    


asyncio.run(main())
