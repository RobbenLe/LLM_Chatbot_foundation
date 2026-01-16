import os #Read variable : (USE_MOCK_LLM, OPENAI_API_KEY)
import json
from fastapi import FastAPI, HTTPException #FastAPI create server, HTTPException handle errors
from pydantic import BaseModel #định nghĩa dữ liệu đầu vào (schema)
from dotenv import load_dotenv #Đọc file .env (chứa key, config).
from fastapi.middleware.cors import CORSMiddleware #Cho phép frontend (chạy trên domain khác) gọi API
from pathlib import Path
from dotenv import load_dotenv

load_dotenv() #read .env file

USE_MOCK_LLM = os.getenv("USE_MOCK_LLM", "false").lower() == "true" #take value òf USE_MOCK_LLM from .env

BASE_DIR = Path(__file__).resolve().parents[1] #“Load .env from project root, no matter where I run from.”
load_dotenv(BASE_DIR / ".env")

#Khởi Tạo server và client 
client = None
app = FastAPI()
app.add_middleware( # Enable CORS for frontend access
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Defind dữ liệu đầu vào (schema)
#Bạn đang nói với FastAPI + Pydantic: “Đây KHÔNG phải class thường, Đây là schema dữ liệu”
#Basemodel Tạo constructor tự động, validate dữ liệu, 
class ChatRequest(BaseModel):  #Say to fastAPi: “Khi ai gọi API /chat, họ phải gửi JSON có field message là string”
    message: str #BaseModel biến class thành “schema”

#FastAPI tự động parse JSON body thành object ChatRequest
    #rbody = json.loads(http_body)
    #req = ChatRequest(**body)

    #chat(req)
@app.post("/chat")
def chat(req: ChatRequest):
    try:
        if USE_MOCK_LLM:
            return {
                "answer": f"[MOCK] You asked: {req.message}",
                "confidence": 0.99
            }

        # Only require API key when using real LLM
        global client
        if client is None:
            client = OpenAI()  # will read OPENAI_API_KEY from env

        response = client.responses.create(
            model="gpt-5.2",
            input=req.message,
            instructions=(
                "Return ONLY valid JSON with keys: answer, confidence. "
                "confidence must be a number between 0 and 1."
            ),
        )

        text = response.output_text.strip()
        data = json.loads(text)

        if "answer" not in data or "confidence" not in data:
            raise ValueError("Missing required JSON keys: answer, confidence")

        return data

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Model did not return valid JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
