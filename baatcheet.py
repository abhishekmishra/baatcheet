from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ollama import AsyncClient, ChatResponse
import json
import uuid
from pydantic import BaseModel


class ChatSession:
    """
    A class to manage a single chat session.

    Each session has a unique session ID and a model name.

    Each session has a sequence of pairs of request and response messages.
    """

    def __init__(self, model: str, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.model = model
        self.messages = []

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def add_request(self, content: str):
        self.add_message("user", content)

    def add_response(self, content: str):
        self.add_message("bot", content)

    def __iter__(self):
        return self

    def __next__(self):
        if not self.messages:
            raise StopIteration
        return self.messages.pop(0)


class ChatSessionList:
    """
    A class to manage a list of chat sessions.

    Each session is identified by a unique session ID.
    """

    def __init__(self):
        self.sessions = {}

    def create_session(self, model: str):
        session = ChatSession(model)
        self.sessions[session.session_id] = session
        return session.session_id

    def get_session(self, session_id: str):
        return self.sessions.get(session_id)


app = FastAPI()

api_app = FastAPI()

# Create an API router
api_router = APIRouter()


async def ollama_chat(sessionId, model, content, stream=True):
    message = {"role": "user", "content": content}
    async for part in await AsyncClient().chat(
        model=model, messages=[message], stream=stream
    ):
        partDict = part.dict()
        partDict["session_id"] = sessionId
        yield json.dumps(partDict).encode("utf-8")


class ChatRequest(BaseModel):
    model: str
    content: str
    session_id: str = None


@api_router.get("/")
async def root():
    return {"message": "Hello World"}


@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: Request):
    body = await request.json()
    session_id = body.get("session_id", None) or str(uuid.uuid4())
    chat_request = ChatRequest(**body)
    return StreamingResponse(
        ollama_chat(
            sessionId=session_id,
            model=chat_request.model,
            content=chat_request.content,
        )
    )


# Include the API router under the /api path
api_app.include_router(api_router)

# Mount the API app to the /api path
app.mount("/api", api_app)

# Mount the static files directory to the root path
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/c/{session_id}", response_class=HTMLResponse)
async def chat_page(request: Request, session_id: str):
    return templates.TemplateResponse(
        request=request, name="chat.html", context={"session_id": session_id}
    )


@app.get("/", response_class=HTMLResponse)
async def chat_page_without_session_id(request: Request):
    return templates.TemplateResponse(request=request, name="chat.html", context={})
