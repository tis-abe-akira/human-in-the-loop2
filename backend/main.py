# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4
from typing import List, Dict, Any
from agent import HumanInTheLoopAgent
import logging
from datetime import datetime

# python_dotenvを使って環境変数を読み込む
from dotenv import load_dotenv
load_dotenv(override=True)

# ログの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

app = FastAPI()

# CORSミドルウェアの追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # どこからでも許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# グローバル変数としてエージェントを保持
agent = HumanInTheLoopAgent()

# セッション管理のための簡易的なインメモリストア
sessions: Dict[str, Any] = {}

class Message(BaseModel):
    content: str
    type: str

class ConversationState(BaseModel):
    messages: List[Message]
    is_waiting_for_approval: bool

class HumanMessageRequest(BaseModel):
    message: str

@app.post("/start_conversation")
async def start_conversation():
    logging.info(f"Method called: start_conversation")
    thread_id = uuid4().hex
    sessions[thread_id] = {
        "messages": [],
        "is_waiting_for_approval": False
    }
    return {"thread_id": thread_id}

@app.post("/send_message/{thread_id}")
async def send_message(thread_id: str, request: HumanMessageRequest):
    logging.info(f"Method called: send_message with thread_id: {thread_id}")
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    agent.handle_human_message(request.message, thread_id)
    
    messages = agent.get_messages(thread_id)
    is_waiting_for_approval = agent.is_next_human_review_node(thread_id)
    
    sessions[thread_id] = {
        "messages": [Message(content=str(msg.content), type=msg.type) for msg in messages],
        "is_waiting_for_approval": is_waiting_for_approval
    }
    
    return ConversationState(**sessions[thread_id])

@app.post("/approve/{thread_id}")
async def approve(thread_id: str):
    logging.info(f"Method called: approve with thread_id: {thread_id}")
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if not sessions[thread_id]["is_waiting_for_approval"]:
        raise HTTPException(status_code=400, detail="No approval pending")
    
    agent.handle_approve(thread_id)
    
    messages = agent.get_messages(thread_id)
    is_waiting_for_approval = agent.is_next_human_review_node(thread_id)
    
    sessions[thread_id] = {
        "messages": [Message(content=str(msg.content), type=msg.type) for msg in messages],
        "is_waiting_for_approval": is_waiting_for_approval
    }
    
    return ConversationState(**sessions[thread_id])

@app.get("/conversation_state/{thread_id}")
async def get_conversation_state(thread_id: str):
    logging.info(f"Method called: get_conversation_state with thread_id: {thread_id}")
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return ConversationState(**sessions[thread_id])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
