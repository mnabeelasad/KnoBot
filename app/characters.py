from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas
from .database import get_db
from .auth import get_current_user

# All endpoints in this file will require authentication.
router = APIRouter(dependencies=[Depends(get_current_user)])

@router.post("/", response_model=schemas.Character)
def create_character(character: schemas.CharacterCreate, db: Session = Depends(get_db)):
    """Creates a new character and saves it to the database."""
    db_character = models.Character(**character.dict())
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character

@router.get("/", response_model=List[schemas.Character])
def read_characters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieves a list of all characters from the database."""
    characters = db.query(models.Character).offset(skip).limit(limit).all()
    return characters

@router.put("/{character_id}", response_model=schemas.Character)
def update_character(character_id: int, character: schemas.CharacterUpdate, db: Session = Depends(get_db)):
    db_character = db.query(models.Character).filter(models.Character.id == character_id).first()
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    for var, value in vars(character).items():
        setattr(db_character, var, value) if value else None

    db.commit()
    db.refresh(db_character)
    return db_character

@router.delete("/{character_id}", response_model=schemas.Character)
def delete_character(character_id: int, db: Session = Depends(get_db)):
    db_character = db.query(models.Character).filter(models.Character.id == character_id).first()
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    db.delete(db_character)
    db.commit()
    return db_character


@router.delete("/{character_id}", response_model=schemas.Character)
def delete_character(character_id: int, db: Session = Depends(get_db)):
    """Deletes a character from the database by its ID."""
    db_character = db.query(models.Character).filter(models.Character.id == character_id).first()
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    db.delete(db_character)
    db.commit()
    return db_character