from sqlalchemy import Column, Integer, String
from .database import Base
from sqlalchemy.orm import declarative_base


# NEW: Create the Base class here. All models will inherit from this.
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, unique=True, index=True)
    agent_model = Column(String)
    voice_id = Column(String)
    voice_model = Column(String)
    system_prompt = Column(String)