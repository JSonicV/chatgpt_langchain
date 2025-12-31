import os
from dotenv import load_dotenv
from langchain.vectorstores.chroma import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from redundant_filter_retriever import RedundantFilterRetriever

load_dotenv()

chat = ChatOpenAI(openai_api_key=os.getenv("OPENAI_SECRET_KEY"))
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_SECRET_KEY"))

db = Chroma(
	embedding_function=embeddings,
	persist_directory="emb",
)

retriever = RedundantFilterRetriever(
	embeddings=embeddings,
	chroma=db
)

chain = RetrievalQA.from_chain_type(
	llm=chat,
	retriever=retriever,
	chain_type="stuff",
)

result = chain.run("something about english?")
print(result)
