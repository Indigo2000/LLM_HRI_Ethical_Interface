import asyncio

#Gets a user instruction
async def GetCommand():
	quit = False
    while quit == False:
        #Get user input
        user_input = input("Enter command: ")
    
        #If user wishes to quit
        if user_input == 'quit':
            break;

#Actions a command            
def ActionCommand():
    #Get command out of queue (FIFO) and action it	
    
        #update goal_room    
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
