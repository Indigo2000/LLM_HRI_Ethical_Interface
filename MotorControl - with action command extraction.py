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
import logging

# If this is running using ipykernel, import nest_asyncio and apply it
if 'ipykernel' in sys.modules:
    import nest_asyncio
    nest_asyncio.apply()
    
# To print stdout to file, remove the '#' on the next two lines and also from the last two lines of the file
#log_file = open("output.log", "w")
#sys.stdout = log_file
    
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Create a logger
logger = logging.getLogger()

# Add a handler to log to a file
file_handler = logging.FileHandler("output.log")
logger.addHandler(file_handler)

# Add a handler to log to the terminal (stdout)
console_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(console_handler)

# Redirect print to use logger
print = logger.info


# Set the initial start, end and action positions
start_location = 'Charging Station'
goal_location = 'Charging Station'
action_command = 'None'

# Prompt template
system_template_destination = "You are presented with an instruction destined for a robot. You need to return a destination location/utility, an action, or both. The format of your response should be given as \"Destination: ..., Action:...\" where \"...\" is replaced by the desired destination and action. If no destination or action is found in the command, replace \"...\" with \"None\". Your responses are limited to the locations and actioins in the lists provided."
    
# Define the prompt
prompt_template_destination = ChatPromptTemplate.from_messages([("system", system_template_destination), ("user", "{text}")])

# Define the chain
chain_destination = prompt_template_destination | Config.model | Config.parser

# Define the data for directions
directions_data = {
    "start_location": start_location,
    "goal_location": goal_location,
    "graph": Layout.graph,
    "heuristic": Layout.h,
    "action": action_command
    }

# Function to find the route
async def process_command_route():
    response = await Layout.a_star_search(Layout.graph, directions_data["start_location"], directions_data["goal_location"], Layout.h)
    print("Route found to be: %s", response)
    return response

# Function to find the destination and action
def process_loc_act(command):
    # Add the list of possible locations and actions to the command
    updated_command = command + " The list containing available locations/utilities is: " + str(Layout.h) + " The list containing available actions is: " + str(Layout.actions)
    
    # Invoke the LLM to generate the response
    response = chain_destination.invoke({"text": updated_command})
    
    # Extract the location from the response
    destination_start = response.find(":") + 2
    destination_end = response.find(",")    
    destination = response[destination_start:destination_end].strip()
    
    # Extract the action from the command
    action_start = response.find(":", destination_end + 1) + 2
    action = response[action_start:]
    
    print("Action was recorded as: %s", action)
    
    # Check if we have a valid location
    try:
        location = Layout.h[destination]
        directions_data["goal_location"] = destination
        directions_data["action"] = action
        return True
    except:
        print("Location not identified!\n")
        # If location does not exist, set the goal location to be the start location
        directions_data["goal_location"] =  directions_data["start_location"]
        return False

# Function to create lists of directions and distances
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
        
    print("Directions: %s", directions_list)
    print("Distance: %s", distance_list)
    return directions_list, distance_list
    
# Function to control the motor towards its destination
async def motion_control(route, distances, locations):
    
    # Counter for moving through the route
    counter = 0
    
    # 
    for item in route:
        print("Moving %s", item)
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
            
        elif item == "diagonally back and right":
            await asyncio.gather(GPIO_Communication.motor_backward(distances[counter]), GPIO_Communication.motor_right(distances[counter]))
            
        elif item == "diagonally back and left":
            await asyncio.gather(GPIO_Communication.motor_backward(distances[counter]), GPIO_Communication.motor_left(distances[counter]))
        
        else:
            print("Unknown command for motor control")
            
        # Stop motors after move
        GPIO_Communication.motor_stop()
        
        # Quit this loop if the stop command has been given. Do not do the next move.
        if Config.global_stop == True:
            break           
        
        # Update current position
        print("Successfully moved from %s", directions_data["start_location"], "to %s", locations[counter])
        print("Setting current location to %s", locations[counter])
        directions_data["start_location"] = locations[counter]
        counter = counter + 1 

# Function to action the command received from the user        
async def ActionCommand(command):
        
    # Update goal_location and action    
    if not process_loc_act(command.title()):
        # Return if goal location invalid
        return
    
    # If already at goal location, no need to move    
    if directions_data["start_location"] == directions_data["goal_location"]:
        print("Already at location %s", directions_data["goal_location"])
        return
        
    # State where we start and where we end    
    print("Start location is: %s", directions_data["start_location"])
    print("Goal location is: %s", directions_data["goal_location"])   
    
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

 
# Function to get input from the user
async def input_loop(queue, gui_app):
    
    while Config.global_quit == False:
        # Get user input without blocking the event loop
        user_input = await gui_app.get_input()
        
        # Check user is authorised to give command
        await SecurityCheck.check_security()
        
        # If user has typed quit, stop the motors and quit the program
        if user_input.lower() == 'quit':
            GPIO_Communication.motor_stop()
            Config.global_quit = True
            break
        
        # If user has typed stop, stop the motors and clear queue    
        if user_input.lower() == 'stop':            
            GPIO_Communication.motor_stop()
                        
            # Purge queue
            await EthicalControl.purge_queue(queue)
            break;
            
        # Check command for ethical issues. If issue found, restart loop. Otherwise, add the command to the loop
        if await EthicalControl.check_ethics(user_input):
            continue
        else:
            await queue.put(user_input)

# Function to process the commands in the queue
async def process_commands(queue):
    
    # Notification of queue being empty set to true initially because we do not need to notify on program launch
    empty_notified = True
    
    # Robot waiting time set to value above 60 initially to indicate it is already at charging station
    start_time = 61
    # Amount of time robot will wait for before returning to charge (in seconds)
    waiting = 60
    while Config.global_quit == False and Config.global_stop == False:
        
        # Checks to see if the queue is empty and if a notification has been given. Move the robot back to charge if queue is empty and it's not on charge already.
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
        print("Processing command: %s", command)
        # Action a user command
        await ActionCommand(command)
        print("Finished processing command: %s", command)
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
        
    # non async function to trigger emergency stop from button push    
    def run_emergency_stop(self):
        asyncio.create_task(self.emergency_stop())
    
    # Function to perform Emergency stop and clear the queue
    async def emergency_stop(self):
        GPIO_Communication.motor_stop()
        print("Emergency stop!")
        await EthicalControl.purge_queue(self.queue)
        Config.global_stop = True
    
    #Function to send the input from the user
    def submit_input(self):
        # When the button is clicked (or enter key hit), set the result of the future to the user input
        if self.input_future:
            self.input_future.set_result(self.entry.get())
            # Clear the text from the field
            self.entry.delete(0, tk.END)

    #Function to get the input from the user
    async def get_input(self):
        # Create a new future and wait for input from the GUI
        self.input_future = asyncio.get_event_loop().create_future()
        text = await self.input_future
        print("\nCommand received: %s", text)
        print("\n")
        return text
    
    # Function to submit user input when 'enter' is pressed.
    def on_enter(self, event):
        self.submit_input()

# Function to refresh the window periodically
async def update_tk(root):
    
    while Config.global_quit == False and Config.global_stop == False:
        # Try to update the window, if not possible (i.e. window closed), stop the motors and terminate the whole program
        try:
            root.update()
        except:
            GPIO_Communication.motor_stop()
            Config.global_quit = True
        await asyncio.sleep(0.01)

# Main function
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
        # Set up main concurrent tasks
        producer = asyncio.create_task(input_loop(queue, gui_app))
        consumer = asyncio.create_task(process_commands(queue))
        gui_refresh = asyncio.create_task(update_tk(root))
        ongoing_ethics = asyncio.create_task(EthicalControl.ethical_triggers(queue))
        
        # Look out for producer, gui_refresh or ongoing_ethics to complete so we can cancel the other tasks
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

#sys.stdout=sys.__stdout__
#log_file.close()
