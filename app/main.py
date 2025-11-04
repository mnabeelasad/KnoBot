import uuid
import os
import shutil
import base64
from typing import Dict, List

from fastapi import FastAPI, Depends, HTTPException, Response, UploadFile, File
from fastapi.responses import StreamingResponse

from fastapi.middleware.cors import CORSMiddleware


from . import auth, users, characters, rag_service, models
from .database import engine
from .schemas import Conversation, MessageInbound, User, SyncMessageResponse
from .agent import run_agent_sync, run_agent_text_stream, available_agents
from .audio_service import text_to_audio_sync, text_to_audio_stream

# This command ensures all database tables are created on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WattOS AI - Full Stack",
    description="A complete FastAPI backend with all required endpoints.",
    version="3.2.1",
)

# NEW: Add CORS Middleware to allow the frontend to connect
origins = [
    "http://localhost",
    "http://localhost:8501",  # The address of your Streamlit frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers
)

# --- Router Integration ---
app.include_router(users.router, prefix="/v1/users", tags=["Users & Account Settings"])
app.include_router(characters.router, prefix="/v1/characters", tags=["Characters"])



# --- In-memory Storage ---
conversation_threads: Dict[str, List[dict]] = {}


# --- API Endpoints ---
@app.get("/v1/agents", response_model=List[str], tags=["Agent Models"])
async def list_available_agents(current_user: User = Depends(auth.get_current_user)):
    return list(available_agents.keys())

@app.get("/v1/agents/{agent_name}/visualize", tags=["Agent Models"])
async def get_agent_visualization(agent_name: str, current_user: User = Depends(auth.get_current_user)):
    agent = available_agents.get(agent_name)
    if not agent: raise HTTPException(status_code=404, detail="Agent not found.")
    mermaid_text = agent.get_graph().draw_mermaid()
    return {"mermaid_text": mermaid_text}

@app.post("/v1/conversations", response_model=Conversation, tags=["Conversations"])
async def create_conversation(current_user: User = Depends(auth.get_current_user)):
    thread_id = f"thread_{uuid.uuid4()}"
    conversation_threads[thread_id] = []
    return Conversation(thread_id=thread_id)
# --- Conversation Endpoints (Simplified) ---
@app.post("/v1/conversations/message", response_model=SyncMessageResponse, tags=["Conversations"])
async def send_sync_message(message_in: MessageInbound, current_user: User = Depends(auth.get_current_user)):
    history = conversation_threads[message_in.thread_id]
    history.append({"role": "user", "content": message_in.message})
    
    # Directly call the sync agent with the selected LLM
    text_response = await run_agent_sync(message_in.message, history, message_in.llm_model)
    
    return SyncMessageResponse(thread_id=message_in.thread_id, response=text_response)

@app.post("/v1/conversations/message/stream", tags=["Conversations"])
async def stream_new_message(message_in: MessageInbound, current_user: User = Depends(auth.get_current_user)):
    history = conversation_threads[message_in.thread_id]
    history.append({"role": "user", "content": message_in.message})
    
    # Directly call the streaming agent with the selected LLM
    return StreamingResponse(
        run_agent_text_stream(message_in.message, history, message_in.llm_model),
        media_type="text/event-stream"
    )
# This is the endpoint that is currently missing from your running server
@app.post("/v1/conversations/message/audio", tags=["Conversations"])
async def download_audio_message(
    message_in: MessageInbound,
    current_user: User = Depends(auth.get_current_user)
):
    """Generates and returns a downloadable MP3 audio file for a given text message."""
    audio_bytes = await text_to_audio_sync(message_in.message)
    return Response(content=audio_bytes, media_type="audio/mpeg")

@app.post("/v1/artifacts/upload", tags=["Artifacts"])
async def upload_document(file: UploadFile = File(...), current_user: User = Depends(auth.get_current_user)):
    temp_dir = "temp_uploads"; os.makedirs(temp_dir, exist_ok=True); file_path = os.path.join(temp_dir, file.filename)
    try:
        with open(file_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
        success = rag_service.add_document_to_vector_store(file_path, file.filename)
        if success: return {"filename": file.filename, "status": "Successfully uploaded and processed."}
        else: raise HTTPException(status_code=500, detail="Failed to process document.")
    finally:
        if os.path.exists(file_path): os.remove(file_path)

@app.get("/v1/artifacts", response_model=List[str], tags=["Artifacts"])
async def list_uploaded_documents(current_user: User = Depends(auth.get_current_user)):
    return rag_service.get_uploaded_files()