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
    user_input = entry.get()
    if user_input.lower() == 'exit':
        root.quit()  # Close GUI
    else:
        await loop.sock_sendall(client_socket, user_input.encode('utf-8'))

# Function to run tkinter's mainloop in the asyncio event loop
async def run_tk():
    while True:
        root.update()  # Update the Tkinter GUI
        await asyncio.sleep(0.01)  # Avoid blocking the event loop

# Set up client socket (for the sake of example)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 12345))

# Asyncio event loop setup
loop = asyncio.get_event_loop()

# Tkinter button to trigger sending input
button = tk.Button(root, text="Send", command=lambda: loop.create_task(send_input()))
button.pack()

# Run both the Tkinter main loop and asyncio loop
loop.run_until_complete(run_tk())
