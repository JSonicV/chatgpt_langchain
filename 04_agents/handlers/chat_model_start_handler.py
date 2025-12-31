from langchain.callbacks.base import BaseCallbackHandler
from pyboxen import boxen

def boxen_print(*args, **kwargs) -> None:
	print(boxen(*args, **kwargs))

class ChatModelStartHandler(BaseCallbackHandler):
	printed_messages = []

	def on_chat_model_start(self, serialized, messages, **kwargs) -> None:
		for message in messages[0]:
			if message in self.printed_messages:
				continue
			self.printed_messages.append(message)

			if message.type == "system":
				print("\n\n========= Sending messages to Chat Model =========\n\n")
				boxen_print(message.content, title=message.type.upper(), color="yellow")
			
			elif message.type == "human":
				boxen_print(message.content, title=message.type.upper(), color="green")
			
			elif message.type == "ai" and "function_call" in message.additional_kwargs:
				call = message.additional_kwargs["function_call"]
				boxen_print(f"Running tool {call['name']} with args {call['arguments']}", title=message.type.upper(), color="cyan")
			
			elif message.type == "ai":
				boxen_print(message.content, title=message.type.upper(), color="blue")

			elif message.type == "function":
				boxen_print(message.content, title=f"FUNCTION {message.name.upper()}", color="purple")

			else:
				boxen_print(message.content, title=message.type.upper(), color="grey")