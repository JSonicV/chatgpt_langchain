# 01_project - Code + Test Generator (LangChain CLI)

## Purpose

Generates a short function and a matching test using a two-step LangChain
SequentialChain. The CLI accepts a language and a task, builds prompts, and
prints a dict containing both the code and the test.

## Entry Points and Files

- `01_project/main.py` - CLI entry point and chain wiring
- `01_project/requirements.txt` - Python deps
- `01_project/chatgpt_langchain_integration.txt` - course transcript (no code)

## Environment

- `OPENAI_SECRET_KEY` - used to authenticate the OpenAI LLM

## Runtime Flow (High Level)

1. Load env vars with `dotenv`.
2. Parse `--language` and `--task` CLI args.
3. Build two prompt templates: one for code, one for tests.
4. Create two `LLMChain` instances and connect them with `SequentialChain`.
5. Invoke the chain and print the result.

## Key Snippets and What They Do

### 1) Prompt templates for code and tests
```py
code_prompt = PromptTemplate(
    template="Write a very short {language} function that will {task}.",
    input_variables=["language", "task"],
)

test_prompt = PromptTemplate(
    template="Write a test case for the following {language} function:\n\n{code}",
    input_variables=["language", "code"],
)
```
These templates produce the prompt strings that are fed into the LLM. The
second prompt expects the output of the first step (`code`).

### 2) Chains and the sequential pipeline
```py
code_chain = LLMChain(llm=llm, prompt=code_prompt, output_key="code")

test_chain = LLMChain(llm=llm, prompt=test_prompt, output_key="test")

chain = SequentialChain(
    chains=[code_chain, test_chain],
    input_variables=["language", "task"],
    output_variables=["code", "test"],
)
```
The `SequentialChain` maps outputs from `code_chain` into inputs for
`test_chain`. Output keys are renamed to `code` and `test` to keep the
result dict readable.

### 3) Invocation with CLI args
```py
result = chain.invoke({
    "language": args.language,
    "task": args.task
})

print(result)
```
The chain expects a dict with the variables declared in the prompt template.

## Example Usage
```bash
python 01_project/main.py --language python --task "return a list of numbers"
```

## How-To Recipes

### Change default language or task
Update the defaults in `argparse`:
```py
parser.add_argument("--language", default="python")
parser.add_argument("--task", default="generate a random number")
```

### Add a third step (example: explain the code)
Add a new prompt template and chain, then include it in `SequentialChain`:
```py
explain_prompt = PromptTemplate(
    template="Explain the following {language} code:\n\n{code}",
    input_variables=["language", "code"],
)

explain_chain = LLMChain(llm=llm, prompt=explain_prompt, output_key="explanation")

chain = SequentialChain(
    chains=[code_chain, test_chain, explain_chain],
    input_variables=["language", "task"],
    output_variables=["code", "test", "explanation"],
)
```

### Print only the code or test
```py
print(result["code"])
print(result["test"])
```
