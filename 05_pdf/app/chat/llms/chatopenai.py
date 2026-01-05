import os
from langchain_openai import ChatOpenAI
from app.chat.models import ChatArgs

def build_llm(chat_args: ChatArgs, model_name: str):
	return ChatOpenAI(api_key=os.environ["OPENAI_API_KEY"], model_name=model_name, streaming=chat_args.streaming)