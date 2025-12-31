import os
import argparse
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("--language", default="python")
parser.add_argument("--task", default="generate a random number")
args = parser.parse_args()

llm = OpenAI(openai_api_key=os.getenv("OPENAI_SECRET_KEY"))

code_prompt = PromptTemplate(
	template="Write a very short {language} function that will {task}.",
	input_variables=["language", "task"],
)
test_prompt = PromptTemplate(
	template="Write a test case for the following {language} function:\n\n{code}",
	input_variables=["language", "code"],
)

code_chain = LLMChain(
	llm=llm,
	prompt=code_prompt,
	output_key="code"
)
test_chain = LLMChain(
	llm=llm,
	prompt=test_prompt,
	output_key="test"
)

chain = SequentialChain(
	chains=[code_chain, test_chain],
	input_variables=["language", "task"],
	output_variables=["code", "test"],
)

result = chain.invoke({
	"language": args.language,
	"task": args.task
})

print(result)