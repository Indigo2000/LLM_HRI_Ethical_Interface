import EthicalControl
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
import tkinter as tk
import Config

# Set the initial start and end positions
start_room = 'Hall'
goal_room = 'Lounge'

# Prompt templates
system_template_destination = "Find the destination room/utility from this instruction and return its name. Your options are limited to the names contained in the list provided. If you cannot find the correct room in the list, say only: 'That location is unknown'."
system_template_directions = "Start room = {start_room} Goal room = {goal_room} Graph = {graph} and heuristics = {heuristic}"
system_template_directions_output = "Return the route from Start room to Goal room. Use A* search on the graph and heuristics provided. Only return the names of the rooms you pass through as a python list. If you receive a goal room that is not in the list, do not perform the search and say only: 'That room is unknown'." 
    
# Define the prompts
prompt_template_destination = ChatPromptTemplate.from_messages([("system", system_template_destination), ("user", "{text}")])
prompt_template_directions = ChatPromptTemplate.from_messages([("system", system_template_directions_output), ("user", "{text}")])

# Define the chains
chain_destination = prompt_template_destination | Config.model | Config.parser
chain_directions = prompt_template_directions | Config.model | Config.parser

# Setup global quit variable
global_quit = False

# Define the data for directions
directions_data = {
    "start_room": start_room,
    "goal_room": goal_room,
    "graph": Layout.graph,
    "heuristic": Layout.h
    }

# Function to find the route
async def process_command_route():
    response = await Layout.a_star_search(Layout.graph, directions_data["start_room"], directions_data["goal_room"], Layout.h)
    print("Route found to be: ", response)
    return response

# Function to find the destination
def process_command_destination(command):
    # Add the list of possible rooms to the command
    updated_command = command + " The list containing available rooms/utilities is: " + str(Layout.h)
    response = chain_destination.invoke({"text": updated_command})
    
    # Check if we have a valid room
    try:
        room = Layout.h[response]
        directions_data["goal_room"] = response
        return True
    except:
        print("No such room!\n")
        # If room does not exist, set the goal room to be the start room
        directions_data["goal_room"] =  directions_data["start_room"]
        return False

def directions_list_create(room_route):
    # Set the current room to be the start_room
    current_room = directions_data["start_room"]
    
    # Create lists to store directions and distances
    directions_list = []
    distance_list = []
    
    # Look through the room route list
    for item in room_route:
        # Ignore start room
        if item == directions_data["start_room"]:
            continue
            
        # Look through the list of available rooms from the current room
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
    
    # Counter for moving through the route
    counter = 0
    
    # 
    for item in route:
        print("Moving", item)
        if item == "forward":
            await asyncio.gather(GPIO_Communication.motor_forward(distances[counter]))

        elif item == "back":
            await asyncio.gather(GPIO_Communication.motor_backward(distances[counter]))
            
        elif item == "left":
            await asyncio.gather(GPIO_Communication.motor_left(distances[counter]))
        
        elif item == "right":
            await asyncio.gather(GPIO_Communication.motor_right(distances[counter]))
            
        elif item == "diagonally forward and left":
            await asyncio.gather(GPIO_Communication.motor_forward(distances[counter]), GPIO_Communication.motor_left(distances[counter]))
        
        elif item == "diagonally forward and right":
            await asyncio.gather(GPIO_Communication.motor_forward(distances[counter]), GPIO_Communication.motor_right(distances[counter]))
            
        elif item == "diagonally right and back":
            await asyncio.gather(GPIO_Communication.motor_backward(distances[counter]), GPIO_Communication.motor_right(distances[counter]))
            
        elif item == "diagonally left and back":
            await asyncio.gather(GPIO_Communication.motor_backward(distances[counter]), GPIO_Communication.motor_left(distances[counter]))
        
        else:
            print("Unknown command for motor control")
            
        # Stop motors after move
        GPIO_Communication.motor_stop()
    
           
        
        # Update current position
        print("Successfully moved from ", directions_data["start_room"], "to ", rooms[counter])
        print("Setting current room to", rooms[counter])
        directions_data["start_room"] = rooms[counter]
        counter = counter + 1 

# Function to action the command received from the user - command variable is the destination room        
async def ActionCommand(command):
        
    # Update goal_room    
    if not process_command_destination(command.title()):
        # Return if goal room invalid
        return
        
    # State where we start and where we end    
    print("Start room is: ", directions_data["start_room"])
    print("Goal room is: ", directions_data["goal_room"])   
    
    # Get the route we'll take
    directions = await process_command_route()
    if directions == "That room is unknown.":
        print("Room not found. Please try again.")
        return
    
    # Simulate motor response    
    directions_list, distance_list = directions_list_create(directions)
    await motion_control(directions_list, distance_list, directions)
    
    # Update start room
    directions_data["start_room"] = directions_data["goal_room"]
    
async def input_loop(queue, gui_app):
    global global_quit
    
    while global_quit == False:
        # Get user input without blocking the event loop
        user_input = await gui_app.get_input()
        
        if user_input.lower() == 'quit':
            # If user has typed quit, stop the motors and quit the program
            GPIO_Communication.motor_stop()
            global_quit = True
            break
        if user_input.lower() == 'stop':
            # Stop the motors
            GPIO_Communication.motor_stop()
                        
            # Purge queue
            while not queue.empty():
                await queue.get()
                queue.task_done()
            # Inform user
            print("\nStop command received. Current task aborted and all future tasks cancelled.")
            break;
            
        # Check command for ethical issues. If issue found, restart loop. Otherwise, add the command to the loop
        if await EthicalControl.check_ethics(user_input):
            continue
        else:
            await queue.put(user_input)

async def process_commands(queue):
    global global_quit
    # Notification of queue being empty set to true initially because we do not need to notify on program launch
    empty_notified = True
    while global_quit == False:
        # Retrieve the next command from the queue
        if queue.empty() and not empty_notified:
            empty_notified = True
            print("Awaiting further instructions...\n")
            await asyncio.sleep(30)
            print("Returning to charge and awaiting further instructions.\n")
            await ActionCommand("Hall")
            print("\nAwaiting further instructions.\n")
            
        command = await queue.get()
        empty_notified = False
        if command.lower() == 'quit':
            print("Exiting command processor.")
            global_quit = True
            queue.task_done()
            continue
        
        print("Processing command: ", command)
        # Action a user command
        await ActionCommand(command)
        print("Finished processing command: ", command)
        print("\n")
        queue.task_done()

class GUIApp():
    def __init__(self, root):
        # Create the command input window
        self.root = root
        self.root.geometry("600x60")
        self.root.title("Command input")
        self.entry = tk.Entry(self.root, width=40)
        self.entry.pack()
        
        # Allow user to hit enter or press submit button
        self.entry.bind("<Return>", self.on_enter)
        self.button = tk.Button(self.root, text="Submit", command=self.submit_input)
        self.button.pack()
        self.input_future = None

    def submit_input(self):
        # When the button is clicked (or enter key hit), set the result of the future to the user input
        if self.input_future:
            self.input_future.set_result(self.entry.get())
            # Clear the text from the field
            self.entry.delete(0, tk.END)
        

    async def get_input(self):
        # Create a new future and wait for input from the GUI
        self.input_future = asyncio.get_event_loop().create_future()
        text = await self.input_future
        print("\nCommand received: ", text, "\n")
        return text
    
    def on_enter(self, event):
        self.submit_input()

# Refresh the window periodically
async def update_tk(root):
    global global_quit
    while global_quit == False:
        # Try to update the window, if not possible (i.e. window closed), stop the motors and terminate the whole program
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
    
    # Set up the command queue
    queue = asyncio.Queue()
    
    # Run the asyncio event loop with the Tkinter main loop
    loop = asyncio.get_event_loop()
    
    while global_quit == False:
        producer = asyncio.create_task(input_loop(queue, gui_app))
        consumer = asyncio.create_task(process_commands(queue))
        gui_refresh = asyncio.create_task(update_tk(root))
        # Look out for producer to send stop command so we can cancel the consumer tasks
        done, pending = await asyncio.wait([producer, consumer, gui_refresh], return_when=asyncio.FIRST_COMPLETED)        
        if producer in done:
            consumer.cancel()

if __name__ == "__main__":
    asyncio.run(main())
        
        

    


asyncio.run(main())
