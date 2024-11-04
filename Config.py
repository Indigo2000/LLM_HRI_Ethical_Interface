import sys
import os
# Make sure to look in the local path for the libraries
#sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'langchain_core'))
#sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'langchain_openai'))
#sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'openai'))

# Setup global quit variable
global_quit = False
global_stop = False

import json
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# Loads OpenAI and LangChain Keys
def load_keys():
    try:
        file = open("../Keys/RPKeys.json")
        keys = json.load(file)
        print("Keys loaded.")
        file.close()
        return keys

    except FileNotFoundError:
        print("File not Found")
        
# Load Keys and set environment variables
loaded_keys = load_keys()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = loaded_keys.get('LANGCHAIN_API_KEY')
os.environ["LANGCHAIN_PROJECT"] = "LangChain Tutorial 1"
os.environ["OPENAI_API_KEY"] = loaded_keys.get('OPENAI_API_KEY')

# Set model and parser
model = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()
