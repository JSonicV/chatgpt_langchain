# 03_facts - Embeddings + Retrieval over a Fact List

## Purpose

Creates embeddings for a plain text file of facts, stores them in Chroma, and
retrieves relevant chunks. A second script wires a custom retriever into a
`RetrievalQA` chain.

## Entry Points and Files

- `03_facts/main.py` - build embeddings and run a similarity search
- `03_facts/prompt.py` - RetrievalQA using a custom retriever
- `03_facts/redundant_filter_retriever.py` - custom retriever using MMR
- `03_facts/facts.txt` - source text
- `03_facts/emb/` - persisted Chroma DB
- `03_facts/requirements.txt` - Python deps

## Environment

- `OPENAI_SECRET_KEY` - OpenAI API key for embeddings and chat

## Runtime Flow (main.py)

1. Load env vars with `dotenv`.
2. Split `facts.txt` into chunks.
3. Create embeddings with `OpenAIEmbeddings`.
4. Persist to Chroma (`emb/`).
5. Run `similarity_search_with_score` and print results.

## Key Snippets and What They Do

### 1) Split text into chunks and build the vector store
```py
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
```
This creates a Chroma store on disk under `emb/`.

### 2) Run a similarity search
```py
results = db.similarity_search_with_score("A strange english thing?")

for result in results:
    print(result[1])
    print(result[0].page_content)
```
Each result is a `(Document, score)` tuple.

## Runtime Flow (prompt.py)

1. Load the existing Chroma DB from `emb/`.
2. Wrap it with `RedundantFilterRetriever` (MMR search).
3. Use `RetrievalQA` to answer a natural language question.

### Custom retriever using MMR
```py
class RedundantFilterRetriever(BaseRetriever):
    embeddings: Embeddings
    chroma: Chroma

    def get_relevant_documents(self, query):
        emb = self.embeddings.embed_query(query)
        return self.chroma.max_marginal_relevance_search_by_vector(
            embedding=emb,
            lambda_mult=0.8
        )
```
MMR (Max Marginal Relevance) reduces redundancy by balancing relevance and
diversity in the retrieved chunks.

## Example Usage
```bash
python 03_facts/main.py
python 03_facts/prompt.py
```

## How-To Recipes

### Rebuild the Chroma index from scratch
Delete the `03_facts/emb/` directory and rerun `main.py`.

### Change chunk size or overlap
Edit `CharacterTextSplitter` args in `main.py`:
```py
CharacterTextSplitter(chunk_size=400, chunk_overlap=50)
```

### Use a different similarity strategy
Swap `similarity_search_with_score` for an MMR call:
```py
db.max_marginal_relevance_search("your query")
```
