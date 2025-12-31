# 02_tchat - CLI Chat with Memory (LangChain)

## Purpose

Runs an interactive terminal chat using `ChatOpenAI` and a memory module that
summarizes prior messages. The script loops forever, reads user input, and
prints the assistant response.

## Entry Points and Files

- `02_tchat/main.py` - CLI entry point
- `02_tchat/requirements.txt` - Python deps

## Environment

- `OPENAI_SECRET_KEY` - OpenAI API key for the chat model

## Runtime Flow (High Level)

1. Load env vars with `dotenv`.
2. Instantiate `ChatOpenAI`.
3. Attach a memory module (`ConversationSummaryMemory`).
4. Build a chat prompt that includes memory + new user content.
5. Create an `LLMChain` and loop on user input.

## Key Snippets and What They Do

### 1) Create the chat model and memory
```py
chat = ChatOpenAI(openai_api_key=os.getenv("OPENAI_SECRET_KEY"))

memory = ConversationSummaryMemory(
    memory_key="messages",
    return_messages=True,
    llm=chat
)
```
The summary memory compresses past conversation into a shorter summary using
`chat` as the summarizer. It stores messages under the `messages` key.

### 2) Prompt that injects memory + new user input
```py
prompt = ChatPromptTemplate(
    input_variables=["content", "messages"],
    messages=[
        MessagesPlaceholder(variable_name="messages"),
        HumanMessagePromptTemplate.from_template("{content}")
    ]
)
```
The `MessagesPlaceholder` inserts the memory messages before the new user
message.

### 3) LLMChain and main loop
```py
chain = LLMChain(
    llm=chat,
    prompt=prompt,
    memory=memory,
    verbose=True
)

while True:
    content = input(">> ")
    result = chain({"content": content})
    print(result["text"])
```
Each loop iteration sends the user message + memory to the model, then prints
`result["text"]`.

## Example Usage
```bash
python 02_tchat/main.py
```

## How-To Recipes

### Use file-backed chat history (uncomment in `main.py`)
```py
# from langchain.memory import ConversationBufferMemory, FileChatMessageHistory
# memory = ConversationBufferMemory(
#     chat_memory=FileChatMessageHistory(filename="messages.json"),
#     return_messages=True,
# )
```
This stores the raw message history in `messages.json` instead of summarizing.

### Switch memory to a pure buffer (no summarization)
Replace `ConversationSummaryMemory` with `ConversationBufferMemory`:
```py
memory = ConversationBufferMemory(
    memory_key="messages",
    return_messages=True
)
```

### Add a system instruction at the start of every chat
Insert a `SystemMessagePromptTemplate` into `ChatPromptTemplate.messages` before
the `MessagesPlaceholder`.
