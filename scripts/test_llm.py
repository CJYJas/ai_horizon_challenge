import os
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o", temperature=0)

prompt = "Hello"
try:
    result = llm.invoke(prompt)
    print("Success:", result.content)
except Exception as e:
    print("Error:", repr(e))
