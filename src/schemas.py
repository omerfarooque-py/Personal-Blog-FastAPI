from pydantic import BaseModel

class UserCreate(BaseModel):
    username : str
    password : str

class UserResponse(BaseModel):
    id : int
    username : str

    model_config = {
        "from_attributes" : True
    }

class UserToken(BaseModel):
    access_token : str
    token_type : str

"""
Task 2: Post Schemas
Open src/schemas.py. Create validation structures for your post layer:

PostCreate: Needs title, slug, and content.

PostResponse: Needs id, title, slug, content, and created_at. Don't forget from_attributes = True
"""

class ImageResponse(BaseModel):
    id : int
    image_url : str
    post_id : int

    model_config = {
        "from_attributes" : True
    }

class PostCreate(BaseModel):
    title : str
    slug : str
    content : str

from datetime import datetime
from typing import List

class PostResponse(BaseModel):
    id : int
    title : str
    slug : str
    content : str
    created_at : datetime
    owner_id : int
    images : List[ImageResponse] = []
    model_config = {
        "from_attributes" : True
    }