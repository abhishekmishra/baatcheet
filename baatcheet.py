from fastapi import FastAPI
from ollama import chat as ollama_chat

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/chat")
async def chat():
    stream = ollama_chat(
        model="deepseek-r1",
        messages=[{"role": "user", "content": "Why is the sky blue?"}],
        stream=True,
    )
    response = ""
    for chunk in stream:
        response += chunk["message"]["content"]
    return {"message": response}
