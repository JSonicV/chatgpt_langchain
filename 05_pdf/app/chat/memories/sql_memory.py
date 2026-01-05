from langchain.memory import ConversationBufferMemory
from app.chat.models import ChatArgs
from .history.sql_history import SQLChatMessageHistory

def build_buffer_memory(chat_args: ChatArgs):
	return ConversationBufferMemory(
		chat_memory=SQLChatMessageHistory(conversation_id=chat_args.conversation_id),
		return_messages=True,
		memory_key="chat_history",
		output_key="answer",
	)