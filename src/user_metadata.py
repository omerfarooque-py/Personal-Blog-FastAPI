from src.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends
from src import models

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    

from fastapi import Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from src import models

def get_post_metadata(
    post_id: int,  # 💡 Explicitly name this post_id for clarity
    db: Session = Depends(get_db),
    query: Optional[List[str]] = None
):
    # 1. Fetch the post record using the post's primary key ID
    post_record = db.query(models.Post).filter(models.Post.id == post_id).first()
    
    # Safety guard: If the post doesn't exist, return empty or handle early
    if not post_record:
        return {"error": "Post not found"}
    
    # 2. Build the complete metadata map using SQLAlchemy relationships.
    # post_record.owner gives you the User object instantly without a second query!
    full_metadata = {
        "user_id": post_record.owner_id,
        "created_at": post_record.created_at,
        "author": post_record.owner.username if post_record.owner else None
    }
    
    # 3. 💡 FIXED COMPREHENSION: If specific keys are requested, filter the dictionary.
    # Otherwise, return the whole metadata payload.
    if query:
        return {key: full_metadata[key] for key in query if key in full_metadata}
        
    return full_metadata

