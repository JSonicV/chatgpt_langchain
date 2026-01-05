from langchain.memory import ConversationBufferWindowMemory
from app.chat.models import ChatArgs
from .history.sql_history import SQLChatMessageHistory

def build_window_memory(chat_args: ChatArgs):
	return ConversationBufferWindowMemory(
		chat_memory=SQLChatMessageHistory(conversation_id=chat_args.conversation_id),
		return_messages=True,
		memory_key="chat_history",
		output_key="answer",
		k=2
	)