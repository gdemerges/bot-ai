from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os

client = OpenAI()
app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        response = client.chat.completions.create(model="gpt-4o",
        messages=[{"role": "user", "content": request.message}],
        api_key=OPENAI_API_KEY)
        return {"response": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}