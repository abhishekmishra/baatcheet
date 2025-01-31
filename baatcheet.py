from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ollama import AsyncClient, ChatResponse
import json
import uuid
from pydantic import BaseModel

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
    session_id = body.get("session_id", str(uuid.uuid4()))
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
