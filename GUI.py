import asyncio
import tkinter as tk
import socket

# Set up Tkinter window
root = tk.Tk()
root.title("Async Input GUI")

label = tk.Label(root, text="Enter Command:")
label.pack()

entry = tk.Entry(root)
entry.pack()

# Async function to handle user input
async def send_input():
    global gloal_quit
    
    user_input = entry.get()
    if user_input.lower() == 'quit':
        root.quit()  # Close GUI
        global_quit = True
    else:
        return user_input

# Function to run tkinter's mainloop in the asyncio event loop
async def run_tk():
    while True:
        root.update()  # Update the Tkinter GUI
        await asyncio.sleep(0.01)  # Avoid blocking the event loop

async def run_gui():
    # Asyncio event loop setup
    loop = asyncio.get_running_loop()

    # Tkinter button to trigger sending input
    button = tk.Button(root, text="Send", command=lambda: loop.create_task(send_input()))
    button.pack()

    # Run both the Tkinter main loop and asyncio loop
    loop.run_until_complete(run_tk())
