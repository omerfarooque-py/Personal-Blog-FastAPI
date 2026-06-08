from sqlalchemy import Integer, String, Column, Boolean
from sqlalchemy.orm import relationship
from src.database import Base

import requests

print(requests.get("https://upload.imagekit.io").status_code)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True, index = True)
    username = Column(String, unique = True, nullable = False)
    hashed_password = Column(String, nullable = False)
    posts = relationship("Post", back_populates="owner")
   # is_admin  = Column(Boolean, default = False, nullable = False)


from sqlalchemy import DateTime, func, ForeignKey

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key = True, index = True)
    title = Column(String, nullable = False)
    slug = Column(String, nullable = False)
    content = Column(String, nullable = False)
    created_at = Column(DateTime, server_default=func.now())
   # image_url = Column(String, nullable=True) 
    owner_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    owner = relationship("User", back_populates="posts")
    images = relationship("Image", back_populates="post", cascade="all, delete-orphan")

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key= True, nullable=False)
    image_url = Column(String)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    post = relationship("Post", back_populates="images")
