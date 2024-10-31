from langchain_core.prompts import ChatPromptTemplate
import Config

# Prompt template
system_template_ethics = "Could there be anything ethically wrong with this instruction to a robot? You should respond in a concise manner and your reponse should take the format \"Yes: \" followed by an exlanation, or \"No: \" followed by an explanation"

# Define the prompt
prompt_template_ethics = ChatPromptTemplate.from_messages([("system", system_template_ethics), ("user", "{text}")])

# Define the chain
chain_ethics = prompt_template_ethics | Config.model | Config.parser

# Function to assess ethics of command
async def process_ethics(command):
    response = chain_ethics.invoke({"text": command})
    return response
    
async def check_ethics(command):
	
	# Check whether GPT model can spot any ethical issues
	print("Checking command for ethical concerns using LLM.")
	response = await process_ethics(command)
	
	if "Yes" in response:
		print("Was ethical issue found?", response, "\n")
		return True		
	elif "No" in response:
		print("No ethical issues found with command.\n")
		return False
	else:
		print("Error checking command for ethical concerns. Please try again. Response from LLM was: ", response, "\n")
		return True
	
	
