import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
# from langchain.memory import ConversationBufferMemory, FileChatMessageHistory
from langchain.memory import ConversationSummaryMemory
from langchain.prompts import HumanMessagePromptTemplate, MessagesPlaceholder, ChatPromptTemplate

load_dotenv()

chat = ChatOpenAI(openai_api_key=os.getenv("OPENAI_SECRET_KEY"))

# memory = ConversationBufferMemory(
# 	chat_memory=FileChatMessageHistory(filename="messages.json"),
# 	return_messages=True,
# )

memory = ConversationSummaryMemory(
	memory_key="messages",
	return_messages=True,
	llm=chat
)

prompt = ChatPromptTemplate(
	input_variables=["content", "messages"],
	messages=[
		MessagesPlaceholder(variable_name="messages"),
		HumanMessagePromptTemplate.from_template("{content}")
	]
)

chain = LLMChain(
	llm=chat,
	prompt=prompt,
	memory=memory,
	verbose=True
)

while True:
	content = input(">> ")

	result = chain({"content": content})

	print(result['text'])
