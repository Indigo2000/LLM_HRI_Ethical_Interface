import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

def load_keys():
    try:
        file = open("../Keys/RPKeys.json")
        keys = json.load(file)
        print("Keys loaded.")
        file.close()
        return keys

    except FileNotFoundError:
        print("File not Found")
        
loaded_keys = load_keys()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = loaded_keys.get('LANGCHAIN_API_KEY')
os.environ["LANGCHAIN_PROJECT"] = "LangChain Tutorial 1"
os.environ["OPENAI_API_KEY"] = loaded_keys.get('OPENAI_API_KEY')


model = ChatOpenAI(model="gpt-4")
parser = StrOutputParser()

#prompt templates:

user_input = input("Please enter text for translating into Italian: ")

system_template = "Translate the following into {language}:"

prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)

# result = prompt_template.invoke({"language": "italian", "text": "hi"})

chain = prompt_template | model | parser

answer = chain.invoke({"language": "italian", "text": user_input})

print(answer)



