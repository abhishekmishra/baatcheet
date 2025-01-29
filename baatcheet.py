from fastapi import FastAPI, APIRouter
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from ollama import AsyncClient, ChatResponse
import json
from pydantic import BaseModel

app = FastAPI()

api_app = FastAPI()

# Create an API router
api_router = APIRouter()


async def ollama_chat(model, content, stream=True):
    message = {"role": "user", "content": content}
    async for part in await AsyncClient().chat(
        model=model, messages=[message], stream=stream
    ):
        # print(part)
        yield json.dumps(part.dict()).encode("utf-8")  # Convert part to dict and encode


class ChatRequest(BaseModel):
    model: str
    content: str


@api_router.get("/")
async def root():
    return {"message": "Hello World"}


@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    return StreamingResponse(
        ollama_chat(
            model=request.model,
            content=request.content,
        )
    )


# Include the API router under the /api path
api_app.include_router(api_router)

# Mount the API app to the /api path
app.mount("/api", api_app)

# Mount the static files directory to the root path
app.mount("/", StaticFiles(directory="static", html=True), name="static")
