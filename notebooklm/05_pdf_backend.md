# 05_pdf Backend - Flask API, Celery, LangChain

## Purpose

Backend for a PDF chat app. It handles user auth, PDF upload, conversation
messages, scoring, and background embedding work. The API is served by Flask
and some work is delegated to Celery.

## Entry Points and Runtime Processes

- `05_pdf/app/web/__init__.py` - `create_app()` builds the Flask app
- `05_pdf/tasks.py` - Invoke tasks to run dev server and worker
- `05_pdf/app/celery/worker.py` - Celery worker entry point

## Environment Variables

- `SECRET_KEY` - Flask session secret
- `SQLALCHEMY_DATABASE_URI` - DB connection string
- `UPLOAD_URL` - base URL of the file upload service
- `REDIS_URI` - Celery broker URL
- `OPENAI_API_KEY` - embeddings (chat module)
- `PINECONE_API_KEY`, `PINECONE_ENV_NAME`, `PINECONE_INDEX_NAME` - vector store

## Config Object

`05_pdf/app/web/config/__init__.py` loads environment variables into Flask config.

```py
class Config:
    SESSION_PERMANENT = True
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]
    UPLOAD_URL = os.environ["UPLOAD_URL"]
    CELERY = {
        "broker_url": os.environ.get("REDIS_URI", False),
        "task_ignore_result": True,
        "broker_connection_retry_on_startup": False,
    }
```

## Data Model (SQLAlchemy)

Defined in `05_pdf/app/web/db/models`:

- `User` - email + password
- `Pdf` - uploaded documents owned by a user
- `Conversation` - chat sessions scoped to a PDF
- `Message` - per-conversation messages with role and content

### BaseModel helpers
```py
class BaseModel(db.Model):
    @classmethod
    def create(cls, commit=True, **kwargs):
        instance = cls(**kwargs)
        return instance.save(commit)

    @classmethod
    def find_by(cls, **kwargs):
        return db.session.execute(db.select(cls).filter_by(**kwargs)).scalar_one()
```
Provides shared CRUD helpers for all models.

### Example: Message conversion to LangChain objects
```py
def as_lc_message(self) -> HumanMessage | AIMessage | SystemMessage:
    if self.role == "human":
        return HumanMessage(content=self.content)
    elif self.role == "ai":
        return AIMessage(content=self.content)
    elif self.role == "system":
        return SystemMessage(content=self.content)
    else:
        raise Exception(f"Unknown message role: {self.role}")
```
This keeps DB records compatible with LangChain message types.

## DB Init Command

`05_pdf/app/web/db/__init__.py` defines `init-db` for local dev resets.

```py
@click.command("init-db")
def init_db_command():
    with current_app.app_context():
        try:
            os.makedirs(current_app.instance_path)
        except OSError:
            pass
        db.drop_all()
        db.create_all()
```
Running `flask --app app.web init-db` drops and recreates all tables.

## Core Flask App Setup

### App factory
```py
def create_app():
    app = Flask(__name__, static_folder="../../client/build")
    app.url_map.strict_slashes = False
    app.config.from_object(Config)

    register_extensions(app)
    register_hooks(app)
    register_blueprints(app)
    if Config.CELERY["broker_url"]:
        celery_init_app(app)

    return app
```
The app wires DB, hooks, and blueprints and optionally configures Celery.

### Celery init
```py
def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    if os.name == "posix":
        celery_app = Celery(app.name, task_cls=FlaskTask)
        celery_app.config_from_object(app.config["CELERY"])
        celery_app.set_default()
    else:
        celery_app = Celery(app.name)
        celery_app.config_from_object(app.config["CELERY"])
        celery_app.set_default()
        celery_app.Task = FlaskTask

    app.extensions["celery"] = celery_app
    return celery_app
```
This ensures tasks run with a Flask application context and handles Windows.

### Hooks and error handling
```py
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return {"message": "Unauthorized"}, 401
        return view(**kwargs)
    return wrapped_view
```
`login_required` protects endpoints and `handle_error` maps exceptions to HTTP
status codes.

## API Endpoints (Blueprints)

### Auth (`/api/auth`)
- `GET /user` - current user
- `POST /signup` - create user
- `POST /signin` - login
- `POST /signout` - logout

### PDFs (`/api/pdfs`)
- `GET /` - list PDFs for current user
- `POST /` - upload a PDF and start embedding process
- `GET /<pdf_id>` - get a PDF + download URL

### Conversations (`/api/conversations`)
- `GET /?pdf_id=...` - list conversations for a PDF
- `POST /?pdf_id=...` - create a conversation
- `POST /<conversation_id>/messages` - run chat (sync or stream)

### Scores (`/api/scores`)
- `POST /?conversation_id=...` - score a conversation
- `GET /` - list scores

## API Helpers (Non-HTTP)

`05_pdf/app/web/api.py` contains helper functions used by the chat layer.

```py
def get_messages_by_conversation_id(conversation_id: str):
    messages = (
        db.session.query(Message)
        .filter_by(conversation_id=conversation_id)
        .order_by(Message.created_on.desc())
    )
    return [message.as_lc_message() for message in messages]
```
This bridges stored DB messages into LangChain message objects.

## File Upload and Download

`05_pdf/app/web/files.py` uses an external upload service.

```py
upload_url = f"{Config.UPLOAD_URL}/upload"

def upload(local_file_path: str) -> Tuple[Dict[str, str], int]:
    with open(local_file_path, "rb") as f:
        response = requests.post(upload_url, files={"file": f})
        return json.loads(response.text), response.status_code
```
`download()` returns a context manager that fetches a file to a temp folder.

## Background Embeddings

### Celery task
```py
@shared_task()
def process_document(pdf_id: int):
    pdf = Pdf.find_by(id=pdf_id)
    with download(pdf.id) as pdf_path:
        create_embeddings_for_pdf(pdf.id, pdf_path)
```
Currently this is called directly in `pdf_views.upload_file`. A TODO comment
suggests moving it to the worker in the future.

### Embedding pipeline
```py
loader = PyPDFLoader(pdf_path)
docs = loader.load_and_split(text_splitter)
vector_store.add_documents(docs)
```
The vector store is defined in `app/chat/vector_stores/pinecone.py`.

## Chat and Scoring (Stubs)

- `app/chat/chat.py` -> `build_chat()` is a placeholder (`pass`).
- `app/chat/score.py` -> `score_conversation()` and `get_scores()` are stubs.

These are intended to integrate LangChain chat and Langfuse scoring but are
not implemented yet.

## How-To Recipes

### Add a new API endpoint
1. Create a new blueprint in `05_pdf/app/web/views/`.
2. Register it in `app/web/__init__.py` inside `register_blueprints()`.

### Move embedding to the Celery worker
Replace the direct call in `pdf_views.upload_file` with `.delay()`:
```py
process_document.delay(pdf.id)
```

### Serve the Svelte build
The Flask app serves static files from `client/build` via `client_views`.
Build the client and ensure the files exist in that folder.
