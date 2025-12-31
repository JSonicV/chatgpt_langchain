# 04_agents - SQL Agent + Report Writer

## Purpose

Uses a LangChain OpenAI Functions agent to query a SQLite database and write
HTML reports. The agent is constrained by a system prompt and a set of tools.

## Entry Points and Files

- `04_agents/main.py` - agent setup and example queries
- `04_agents/tools/sql.py` - SQL tools (list, describe, run queries)
- `04_agents/tools/report.py` - report writer tool
- `04_agents/handlers/chat_model_start_handler.py` - callback logger
- `04_agents/db.sqlite` - SQLite database
- `04_agents/*.html` - example reports
- `04_agents/requirements.txt` - Python deps

## Environment

- `OPENAI_SECRET_KEY` - OpenAI API key for the chat model

## Runtime Flow (High Level)

1. Load env vars with `dotenv`.
2. Initialize `ChatOpenAI` with a callback handler for logging.
3. Build a system prompt that lists tables and tells the agent to use tools.
4. Define tools for SQL access and report writing.
5. Create `OpenAIFunctionsAgent` + `AgentExecutor` with memory.
6. Run a natural language request.

## Key Snippets and What They Do

### 1) System prompt and agent wiring
```py
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
```
This forces the agent to inspect schema instead of guessing columns.

### 2) SQL tools
```py
run_query_tool = Tool(
    name="run_sqlite_query",
    description="Run a SQLite query on the connected database and return the results.",
    func=run_sqlite_query,
    args_schema=RunQueryArgsSchema
)

describe_tables_tool = Tool(
    name="describe_tables",
    description="Given a list of table names, return the schema of those tables.",
    func=describe_tables,
    args_schema=DescribeTablesArgsSchema
)
```
These tools let the agent read schema and execute queries against `db.sqlite`.

### 3) HTML report tool
```py
def write_report(filename, html):
    with open(filename, "w") as f:
        f.write(html)

write_report_tool = StructuredTool.from_function(
    func=write_report,
    name="write_report",
    description="Write the provided HTML content to a file with the given filename. Use this tool whenever someone asks for a report.",
    args_schema=WriteReportArgsSchema
)
```
This tool is meant to be called when the user asks for a report.

### 4) Logging handler for model calls
```py
class ChatModelStartHandler(BaseCallbackHandler):
    printed_messages = []

    def on_chat_model_start(self, serialized, messages, **kwargs) -> None:
        for message in messages[0]:
            if message in self.printed_messages:
                continue
            self.printed_messages.append(message)
            ...
```
Avoids printing duplicate messages and formats each role with a colored box.

## Example Usage
```py
agent_executor("How many orders are there? Write the result to an html report")
```
The agent should run SQL queries and then write an HTML file using the report tool.

## How-To Recipes

### Add a new tool
1. Implement a function in `04_agents/tools`.
2. Wrap it with `Tool` or `StructuredTool`.
3. Add it to the `tools` list in `main.py`.

### Change the system prompt constraints
Edit the `SystemMessage` content in `main.py` to add rules or a different
schema discovery flow.

### Use a different database
Update the SQLite connection in `04_agents/tools/sql.py`:
```py
conn = sqlite3.connect('db.sqlite')
```
