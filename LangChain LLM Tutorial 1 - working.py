import getpass
import os

os.environ["OPENAI_API_KEY"] = getpass.getpass()
print("Done1!")

from langchain_openai import ChatOpenAI
print("Done2!")

model = ChatOpenAI(model="gpt-4o-mini")
print("Done3!")

from langchain_core.messages import HumanMessage, SystemMessage
print("Done4!")

messages = [
    SystemMessage("content = translate the following from English into Italian"),
    HumanMessage(content="hi!")
    ]
print("Done5!")
    
model.invoke(messages)

print("Done6!")
