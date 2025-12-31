import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import OpenAIFunctionsAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
from langchain.prompts import (
	ChatPromptTemplate,
	HumanMessagePromptTemplate,
	MessagesPlaceholder
)
from tools.sql import list_tables, run_query_tool, describe_tables_tool
from tools.report import write_report_tool
from handlers.chat_model_start_handler import ChatModelStartHandler


load_dotenv()

handler = ChatModelStartHandler()
chat = ChatOpenAI(
	openai_api_key=os.getenv("OPENAI_SECRET_KEY"),
	callbacks=[handler],
)

tables = list_tables()
prompt = ChatPromptTemplate(
	messages=[
		SystemMessage(content=(
			"You are an AI that has access to a sqlite database.\n"
			f"The database has tables of:\n{tables}\n"
			"Do not make any assumptions about what table exist or what columns exist.\n"
			"Instead, use the 'describe_tables' function."
		)),
		MessagesPlaceholder(variable_name="chat_history"),
		HumanMessagePromptTemplate.from_template("{input}"),
		MessagesPlaceholder(variable_name="agent_scratchpad"),
	]
)

memory = ConversationBufferMemory(
	memory_key="chat_history",
	return_messages=True
)

tools = [run_query_tool, describe_tables_tool, write_report_tool]

agent = OpenAIFunctionsAgent(
	llm=chat,
	prompt=prompt,
	tools=tools,
)

agent_executor = AgentExecutor(
	agent=agent,
	tools=tools,
	# verbose=True,
	memory=memory
)


# agent_executor("How many users have provided the address?")
# agent_executor("Summarize the top 5 most popular products. Write the results to a report file.")
agent_executor("How many orders are there? Write the result to an html report")
agent_executor("Repeat the exact same process for users", "tables")