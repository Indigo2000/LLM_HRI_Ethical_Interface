import asyncio
import CommandQueue



#Main function    
async def main():
        
    #Add other main async modules here when they are done: Action command, security check, ethical check
    #Need some kind of global variable to quit them all
    print("Starting asyncio")
    await asyncio.gather(CommandQueue.GetUserCommand(), CommandQueue.RetreiveCommand())
    


asyncio.run(main())
    
    
    
    
    
    
 



