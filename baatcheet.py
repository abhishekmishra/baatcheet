from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from ollama import AsyncClient, ChatResponse
import json

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


async def ollama_chat(model, content, stream=True):
    message = {"role": "user", "content": content}
    async for part in await AsyncClient().chat(
        model=model, messages=[message], stream=stream
    ):
        # print(part)
        yield json.dumps(part.dict()).encode("utf-8")  # Convert part to dict and encode


@app.get("/chat", response_model=ChatResponse)
async def chat():
    return StreamingResponse(
        ollama_chat(
            model="deepseek-r1:1.5b",
            content="Why is the sky blue? Respond in one line. And don't overthink it.",
        )
    )
