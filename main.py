import asyncio

async def input_loop(queue):
    loop = asyncio.get_running_loop()
    while True:
        # Get user input without blocking the event loop
        user_input = await loop.run_in_executor(None, input, "Enter command (or 'quit' to exit): ")
        await queue.put(user_input)
        if user_input.lower() == 'quit':
            break

async def process_commands(queue):
    while True:
        # Retrieve the next command from the queue
        command = await queue.get()
        if command.lower() == 'quit':
            print("Exiting command processor.")
            queue.task_done()
            break
        print(f"Processing command: {command}")
        # Simulate a time-consuming asynchronous operation
        await asyncio.sleep(2)  # Replace with your actual async processing
        print(f"Finished processing command: {command}")
        queue.task_done()

async def main():
    queue = asyncio.Queue()
    producer = asyncio.create_task(input_loop(queue))
    consumer = asyncio.create_task(process_commands(queue))

    # Wait for both the producer and consumer to finish
    await asyncio.gather(producer, consumer)

if __name__ == "__main__":
    asyncio.run(main())
