import tkinter as tk
import asyncio

class GUIApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("300x100")
        self.entry = tk.Entry(self.root)
        self.entry.pack()
        self.button = tk.Button(self.root, text="Submit", command=self.submit_input)
        self.button.pack()
        self.input_future = None

    def submit_input(self):
        # When the button is clicked, set the result of the future to the user input
        if self.input_future:
            self.input_future.set_result(self.entry.get())

    async def get_input(self):
        # Create a new future and wait for input from the GUI
        self.input_future = asyncio.get_event_loop().create_future()
        return await self.input_future

async def input_loop(queue, gui_app):
    global quit
    while not quit:
        # Get input from the GUI
        user_input = await gui_app.get_input()
        await queue.put(user_input)
        if user_input.lower() == 'quit':
            quit = True
            break
        elif user_input.lower() == 'stop':
            # Stop motors or other tasks
            print("Stop command received.")
            # Clear the queue or any other actions
            while not queue.empty():
                await queue.get()
                queue.task_done()
            break

if __name__ == "__main__":
    quit = False
    root = tk.Tk()
    gui_app = GUIApp(root)
    
    queue = asyncio.Queue()
    
    # Run the asyncio event loop with the Tkinter main loop
    loop = asyncio.get_event_loop()
    
    async def main():
        await asyncio.gather(
            input_loop(queue, gui_app)
        )
    
    loop.create_task(main())
    
    # Tkinter main loop
    root.mainloop()
