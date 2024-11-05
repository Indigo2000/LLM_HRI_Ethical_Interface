import Config
import asyncio
import EthicalControl
import SecurityCheck
import Layout
import GPIO_Communication
from langchain_core.prompts import ChatPromptTemplate
import tkinter as tk
import time
import math
import sys

if 'ipykernel' in sys.modules:
    import nest_asyncio
    nest_asyncio.apply()

# Set the initial start and end positions
start_location = 'Charging Station'
goal_location = 'Hall'

# Prompt templates
system_template_destination = "Find the destination room/utility from this instruction and return its name. Your options are limited to the names contained in the list provided. If you cannot find the correct room/utility in the list, say only: 'That location is unknown'."
system_template_directions = "Start location = {start_location} Goal location = {goal_location} Graph = {graph} and heuristics = {heuristic}"
system_template_directions_output = "Return the route from Start location to Goal location. Use A* search on the graph and heuristics provided. Only return the names of the locations you pass through as a python list. If you receive a goal location that is not in the list, do not perform the search and say only: 'That location is unknown'." 
    
# Define the prompts
prompt_template_destination = ChatPromptTemplate.from_messages([("system", system_template_destination), ("user", "{text}")])
prompt_template_directions = ChatPromptTemplate.from_messages([("system", system_template_directions_output), ("user", "{text}")])

# Define the chains
chain_destination = prompt_template_destination | Config.model | Config.parser
chain_directions = prompt_template_directions | Config.model | Config.parser

# Define the data for directions
directions_data = {
    "start_location": start_location,
    "goal_location": goal_location,
    "graph": Layout.graph,
    "heuristic": Layout.h
    }

# Function to find the route
async def process_command_route():
    response = await Layout.a_star_search(Layout.graph, directions_data["start_location"], directions_data["goal_location"], Layout.h)
    print("Route found to be: ", response)
    return response

# Function to find the destination
def process_command_destination(command):
    # Add the list of possible locations to the command
    updated_command = command + " The list containing available locations/utilities is: " + str(Layout.h)
    response = chain_destination.invoke({"text": updated_command})
    
    # Check if we have a valid location
    try:
        location = Layout.h[response]
        directions_data["goal_location"] = response
        return True
    except:
        print("No such location!\n")
        # If location does not exist, set the goal location to be the start location
        directions_data["goal_location"] =  directions_data["start_location"]
        return False

def directions_list_create(location_route):
    # Set the current location to be the start_location
    current_location = directions_data["start_location"]
    
    # Create lists to store directions and distances
    directions_list = []
    distance_list = []
    
    # Look through the location route list
    for item in location_route:
        # Ignore start location
        if item == directions_data["start_location"]:
            continue
            
        # Look through the list of available locations from the current location
        for location in Layout.graph[current_location]:
            if location[0] == item:
                directions_list.append(location[2])
                distance_list.append(location[1])
        current_location = item
        
    print("Directions: ", directions_list)
    print("Distance: ", distance_list)
    return directions_list, distance_list
    
# Function to control the motor
async def motion_control(route, distances, locations):
    
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
            print("sending command")
            await asyncio.gather(GPIO_Communication.motor_forward(distances[counter]), GPIO_Communication.motor_left(distances[counter]))
        
        elif item == "diagonally forward and right":
            await asyncio.gather(GPIO_Communication.motor_forward(distances[counter]), GPIO_Communication.motor_right(distances[counter]))
            
        elif item == "diagonally back and right":
            await asyncio.gather(GPIO_Communication.motor_backward(distances[counter]), GPIO_Communication.motor_right(distances[counter]))
            
        elif item == "diagonally back and left":
            await asyncio.gather(GPIO_Communication.motor_backward(distances[counter]), GPIO_Communication.motor_left(distances[counter]))
        
        else:
            print("Unknown command for motor control")
            
        # Stop motors after move
        GPIO_Communication.motor_stop()
        
        if Config.global_stop == True:
            break
    
           
        
        # Update current position
        print("Successfully moved from ", directions_data["start_location"], "to ", locations[counter])
        print("Setting current location to", locations[counter])
        directions_data["start_location"] = locations[counter]
        counter = counter + 1 

# Function to action the command received from the user - command variable is the destination location        
async def ActionCommand(command):
        
    # Update goal_location    
    if not process_command_destination(command.title()):
        # Return if goal location invalid
        return
        
    if directions_data["start_location"] == directions_data["goal_location"]:
        print("Already at location", directions_data["goal_location"])
        return
        
    # State where we start and where we end    
    print("Start location is: ", directions_data["start_location"])
    print("Goal location is: ", directions_data["goal_location"])   
    
    # Get the route we'll take
    directions = await process_command_route()
    if directions == "That location is unknown.":
        print("location not found. Please try again.")
        return
    
    # Simulate motor response    
    directions_list, distance_list = directions_list_create(directions)
    await motion_control(directions_list, distance_list, directions)
    
    # Update start location
    directions_data["start_location"] = directions_data["goal_location"]

    
async def input_loop(queue, gui_app):
    
    while Config.global_quit == False:
        # Get user input without blocking the event loop
        user_input = await gui_app.get_input()
        
        # Check user is authorised to give command
        await SecurityCheck.check_security()
        
        if user_input.lower() == 'quit':
            # If user has typed quit, stop the motors and quit the program
            GPIO_Communication.motor_stop()
            Config.global_quit = True
            break
        if user_input.lower() == 'stop':
            # Stop the motors
            GPIO_Communication.motor_stop()
                        
            # Purge queue
            await EthicalControl.purge_queue(queue)
            break;
            
        # Check command for ethical issues. If issue found, restart loop. Otherwise, add the command to the loop
        if await EthicalControl.check_ethics(user_input):
            continue
        else:
            await queue.put(user_input)

async def process_commands(queue):
    
    # Notification of queue being empty set to true initially because we do not need to notify on program launch
    empty_notified = True
    # Robot waiting time set to value above 60 initially to indicate it is already at charging station
    start_time = 61
    waiting = 60
    while Config.global_quit == False and Config.global_stop == False:
        # Check to see if the queue is empty and move the robot back to charge after 1 minute
        if queue.empty() and not empty_notified:
            empty_notified = True
            print("Awaiting further instructions...\n")
            start_time = math.trunc(time.time())
            await asyncio.sleep(0.01)
            continue
        if directions_data["start_location"] != "Charging Station":   
            if queue.empty() and empty_notified:
                if math.trunc(time.time()) - start_time < waiting:
                    await asyncio.sleep(0.01)
                    continue
                elif math.trunc(time.time()) - start_time == waiting:
                    print("Returning to charge and awaiting further instructions.\n")
                    await ActionCommand("Charging Station")
                    print("\nAwaiting further instructions.\n")
                    continue
                
        # Retrieve the next command from the queue
        command = await queue.get()
        empty_notified = False        
        print("Processing command: ", command)
        # Action a user command
        await ActionCommand(command)
        print("Finished processing command: ", command)
        print("\n")
        queue.task_done()

class GUIApp():
    def __init__(self, queue, root):
        
        self.queue = queue
        
        # Create the command input window
        self.root = root
        self.root.geometry("600x100")
        self.root.title("Command input")
        
        # Command input cell
        self.entry = tk.Entry(self.root, width=40)
        self.entry.pack()
        self.entry.focus_set()
        
        # Setup for user to be able to hit enter or press submit button
        self.entry.bind("<Return>", self.on_enter)
        self.submit_button = tk.Button(self.root, text="Submit", command=self.submit_input)
        self.submit_button.pack()
        
        # Setup for user to be able to hit emergency stop button
        self.stop_button = tk.Button(self.root, text="Emergency Stop!", command=self.run_emergency_stop)
        self.stop_button.pack()
        self.input_future = None
        
    def run_emergency_stop(self):
        asyncio.create_task(self.emergency_stop())
    
    async def emergency_stop(self):
        GPIO_Communication.motor_stop()
        print("Emergency stop!")
        await EthicalControl.purge_queue(self.queue)
        Config.global_stop = True

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
    
    while Config.global_quit == False and Config.global_stop == False:
        # Try to update the window, if not possible (i.e. window closed), stop the motors and terminate the whole program
        try:
            root.update()
        except:
            GPIO_Communication.motor_stop()
            Config.global_quit = True
        await asyncio.sleep(0.01)

async def main():
    # Set up the command queue
    queue = asyncio.Queue()    
    
    # Set up the GUI
    root = tk.Tk()
    root.attributes('-topmost', 1)
    gui_app = GUIApp(queue, root)
    
    # Run the asyncio event loop with the Tkinter main loop
    loop = asyncio.get_event_loop()
    
    while Config.global_quit == False:
        producer = asyncio.create_task(input_loop(queue, gui_app))
        consumer = asyncio.create_task(process_commands(queue))
        gui_refresh = asyncio.create_task(update_tk(root))
        ongoing_ethics = asyncio.create_task(EthicalControl.ethical_triggers(queue))
        # Look out for producer, gui_refresh or ongoing_ethics to send stop command so we can cancel the consumer tasks
        done, pending = await asyncio.wait([producer, consumer, gui_refresh, ongoing_ethics], return_when=asyncio.FIRST_COMPLETED)
        # Cancel other tasks if ine ends
        if producer in done:
            consumer.cancel()
            gui_refresh.cancel()
            ongoing_ethics.cancel()
        elif ongoing_ethics in done:
            producer.cancel()
            consumer.cancel()
            gui_refresh.cancel()
        elif gui_refresh in done:
            producer.cancel()
            consumer.cancel()
            ongoing_ethics.cancel()
        # Reset global_stop command
        Config.global_stop = False
            

if __name__ == "__main__":
    asyncio.run(main())

