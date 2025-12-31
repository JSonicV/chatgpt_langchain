import os
from dotenv import load_dotenv
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma

load_dotenv()

embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_SECRET_KEY"))

text_splitter = CharacterTextSplitter(
	separator="\n",
	chunk_size=200,
	chunk_overlap=0,
)

loader = TextLoader("facts.txt")
docs = loader.load_and_split(text_splitter=text_splitter)

db = Chroma.from_documents(
	docs,
	persist_directory="emb",
	embedding=embeddings,
)

results = db.similarity_search_with_score("A strange english thing?")

for result in results:
	print("\n")
	print(result[1])
	print(result[0].page_content)