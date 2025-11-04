from pydantic import BaseModel, Field, ConfigDict # CHANGED: Import ConfigDict
from typing import Optional, List

# --- Character Schemas ---
class CharacterBase(BaseModel):
    role: str
    agent_model: str
    voice_id: str
    voice_model: str
    system_prompt: str

class CharacterCreate(CharacterBase):
    pass

# NEW: Schema for updating a character
class CharacterUpdate(CharacterBase):
    pass

class Character(CharacterBase):
    id: int
    # CHANGED: Use model_config with from_attributes
    model_config = ConfigDict(from_attributes=True)

# --- User Schemas ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=64)

class UserUpdate(BaseModel):
    password: Optional[str] = Field(None, min_length=8, max_length=64)

class User(UserBase):
    id: int
    # CHANGED: Use model_config with from_attributes
    model_config = ConfigDict(from_attributes=True)
    
# --- (The rest of the file is the same) ---
class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    username: Optional[str] = None
class MessageInbound(BaseModel):
    thread_id: Optional[str] = Field(None)
    message: str
    character: str = Field("Assistant")
    llm_model: str = Field("gpt-4o")
    agent_model: str = Field("chatbot_fast")
class Conversation(BaseModel):
    thread_id: str
    message: str = "Conversation started."
class SyncMessageResponse(BaseModel):
    thread_id: str
    response: str