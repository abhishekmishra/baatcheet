from fastapi import FastAPI, APIRouter
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from ollama import AsyncClient, ChatResponse
import json

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


@api_router.get("/")
async def root():
    return {"message": "Hello World"}


@api_router.get("/chat", response_model=ChatResponse)
async def chat():
    return StreamingResponse(
        ollama_chat(
            model="deepseek-r1:1.5b",
            content="Why is the sky blue? Respond in one line. And don't overthink it.",
        )
    )


# Include the API router under the /api path
api_app.include_router(api_router)

# Mount the API app to the /api path
app.mount("/api", api_app)

# Mount the static files directory to the root path
app.mount("/", StaticFiles(directory="static", html=True), name="static")
