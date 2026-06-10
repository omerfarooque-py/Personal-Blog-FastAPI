from pydantic import BaseModel
from datetime import datetime
from typing import List

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

class ImageResponse(BaseModel):
    id : int
    image_url : str
    post_id : int

    model_config = {
        "from_attributes" : True
    }

class HeartResponse(BaseModel):
    id: int
    user_id: int
    post_id: int

    model_config = {
        "from_attributes" : True
    }

class PostCreate(BaseModel):
    title : str
    slug : str
    content : str

class PostResponse(BaseModel):
    id : int
    title : str
    slug : str
    content : str
    created_at : datetime
    owner_id : int
    images : List[ImageResponse] = []
    hearts : List[HeartResponse] = [] 
    
    model_config = {
        "from_attributes" : True
    }

class CommentCreate(BaseModel):
    content : str

class CommentResponse(BaseModel):
    id : int
    content : str
    created_at : datetime
    owner_id : int
    post_id : int

    model_config = {
        "from_attributes" : True
    }