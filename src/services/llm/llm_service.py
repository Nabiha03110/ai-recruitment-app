from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_openai_model(model):
    llm = ChatOpenAI(model=model, openai_api_key=OPENAI_API_KEY)
    return llm


def get_chain(prompt):
    llm = get_openai_model(model="gpt-4o-mini")
    chain = prompt | llm

    return chain
  

  