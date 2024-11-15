from langchain_core.prompts import ChatPromptTemplate
import config
import gpio_communication
import asyncio

# Prompt template
system_template_ethics = ("Could there be anything ethically wrong with this instruction to a robot? You should respond"
                         " in a concise manner and your response should take the format \"Yes: \" followed by an"
                          " explanation, or \"No: \" followed by an explanation")

# Define the prompt
prompt_template_ethics = ChatPromptTemplate.from_messages([("system", system_template_ethics), ("user", "{text}")])

# Define the chain
chain_ethics = prompt_template_ethics | config.model | config.parser


# Function to assess ethics of command
async def process_ethics(command):
    response = chain_ethics.invoke({"text": command})
    return response


# Function to check ethics of the given command    
async def check_ethics(command):

    # Check whether GPT model can spot any ethical issues
    print("Checking command for ethical concerns using LLM.")
    response = await process_ethics(command)

    if "Yes" in response:
        print("\nWas ethical issue found? ", response, "\n")
        return True
    elif "No" in response:
        print("No ethical issues found with command.\n")
        return False
    else:
        print("Error checking command for ethical concerns. Please try again. Response from LLM was: ", response, "\n")
        return True


# Function to purge the command queue    
async def purge_queue(queue):
    while not queue.empty():
        await queue.get()
        queue.task_done()
    # Inform user
    print("\nStop command received. Current task aborted and all future tasks cancelled.")
    

# Function to continually check for ethical triggers
async def ethical_triggers(queue):
    if gpio_communication.motors:
        await gpio_communication.emergency_stop(queue)
    else:
        while not config.global_quit:
            await asyncio.sleep(0.01)




