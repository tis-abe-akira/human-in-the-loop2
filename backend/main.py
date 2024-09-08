# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from typing import List, Dict, Any
from agent import HumanInTheLoopAgent

app = FastAPI()

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
    thread_id = uuid4().hex
    sessions[thread_id] = {
        "messages": [],
        "is_waiting_for_approval": False
    }
    return {"thread_id": thread_id}

@app.post("/send_message/{thread_id}")
async def send_message(thread_id: str, request: HumanMessageRequest):
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
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return ConversationState(**sessions[thread_id])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
