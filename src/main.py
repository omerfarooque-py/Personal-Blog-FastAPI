from fastapi import FastAPI, Depends, HTTPException, Form
from src.security import hash_pass
from sqlalchemy.orm import Session
from src.schemas import UserCreate, UserResponse
from src.database import get_db, engine
from src import models
import os
from imagekitio import ImageKit
from dotenv import load_dotenv
import os
import certifi




# Force Python's SSL context to trust the certifi bundle globally
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

load_dotenv()

imagekit = ImageKit(
    public_key   = os.getenv("IMAGEKIT_PUBLIC_KEY"),
    private_key  = os.getenv("IMAGEKIT_PRIVATE_KEY"),
    url_endpoint = os.getenv("IMAGEKIT_URL_ENDPOINT")

)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Blog", redirect_slashes=True)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 💡 Allows your Streamlit cloud instance to connect safely
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/register/", response_model= UserResponse)
def user_create(
    user : UserCreate,
    db : Session = Depends(get_db)
):
    user_exists = db.query(models.User).filter(models.User.username == user.username).first()

    if user_exists:
        raise HTTPException(status_code=400, detail="username already exists")
    
    elif len(user.password) < 8:
        raise HTTPException(status_code=400, detail="password should be atleast 8 charachters long")
    else:
        hashed_password = hash_pass(user.password)

        db_user = models.User(
            username = user.username,
            hashed_password = hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    return db_user

"""
In src/main.py, create a POST /login endpoint that accepts FastAPI's built-in
 OAuth2PasswordRequestForm = Depends() (imported from fastapi.security).

Find the user in the database by form_data.username.

If the user doesn't exist or verify_password returns False,
 raise an HTTPException(status_code=401, detail="Invalid credentials").

If successful, create a token with the username as the subject ("sub") and return it.

"""
#login endpoint

from fastapi.security import OAuth2PasswordRequestForm
from src.security import create_access_token, verify_pass

@app.post("/login/")
def user_login(
    db : Session = Depends(get_db),
    user_credentials : OAuth2PasswordRequestForm = Depends()
):    
    user_exists =  db.query(models.User).filter(models.User.username == user_credentials.username).first()

    if user_exists:
        password_varification = verify_pass(user_credentials.password, user_exists.hashed_password)
        if password_varification:
            token_payload = {'sub' : user_exists.username}
            jwt_token = create_access_token(token_payload)
            return {
                "message" : "success",
                "is_admin" : user_exists.is_admin,
                "access_token" : jwt_token
            }
        else:
            raise HTTPException(status_code=401, detail="invalid credentials")
    else:
        raise HTTPException(status_code=401, detail="invalid credentials")
    
"""
Task 3: The get_current_user Dependency
In src/main.py, create a dependency function that can be injected into any future route to make it private:

Use OAuth2PasswordBearer(tokenUrl="login") to automatically extract the token from the request's Authorization header.

Decode the token using jwt.decode(). If it's expired or invalid, raise a 401 Unauthorized exception.

Extract the username from the "sub" claim, fetch that user from the database, and return the User object.
"""
from fastapi.security import OAuth2PasswordBearer
from src.security import ALGORITHM, SECRET_KEY
from jose import jwt, JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(
        token : str = Depends(oauth2_scheme),
        db : Session = Depends(get_db)
):
    credentials_exception = HTTPException(
    status_code=401,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')

        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user =  db.query(models.User).filter(models.User.username == username).first()

    if not user: 
        raise credentials_exception
    return user

"""
Task 3: Public & Private Endpoints
In src/main.py, implement these endpoints:

POST /posts/ (Private): Should accept a PostCreate schema, require current_user = Depends(get_current_user),
 save the post to the database, and return a PostResponse.

GET /posts/ (Public): Anyone can hit this. Returns a list of all posts from the database.
"""
from src.schemas import PostCreate, PostResponse

@app.post("/posts/", response_model=PostResponse)
def create_post(
    post : PostCreate,
    current_user = Depends(get_current_user),
    db : Session = Depends(get_db)
):

    
    db_post = models.Post(
        title = post.title,
        slug = post.slug,
        content = post.content,
        owner_id = current_user.id
    )
    
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post

from src import schemas
@app.get("/posts/", response_model=list[schemas.PostResponse])
def get_all_posts(
    db : Session = Depends(get_db),
    limit: int = 10,
    offset: int = 0
):
    posts = db.query(models.Post).offset(offset).limit(limit).all()

    if not posts:
        raise HTTPException(status_code=404, detail="No posts found")

    return posts

import base64
from fastapi import UploadFile, File, HTTPException, Depends

@app.post("/upload/")
async def upload_file(
    title : str = Form(...),
    content : str = Form(...),
    current_user: models.User = Depends(get_current_user),
    file: UploadFile = File(...),
    db : Session = Depends(get_db)
):
    generated_slug = title.lower().strip().replace(" ","-")

    new_post = models.Post(
        title = title,
        content = content,
        slug = generated_slug,
        owner_id = current_user.id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are allowed")
        
    # 1. Read file bytes asynchronously
    file_bytes = await file.read()
    
    # 2. Encode to base64 string format
    base64_encoded = base64.b64encode(file_bytes).decode("utf-8")

    try:
        # 3. Stream the formatted string string directly to ImageKit
        upload_response = imagekit.upload_file(
            file=base64_encoded, # Passing standard string payload
            file_name=file.filename
       
        )
        
        # 4. Safely pull back the response web target
        try:
            image_url = upload_response.url
        except AttributeError:
            image_url =  upload_response.response_metadata.raw.get("url")

        db_image = models.Image(
            image_url = image_url,
            post_id = new_post.id
        )
        
        db.add(db_image)
        db.commit()

    except Exception as e:
        # Catch network or configuration errors explicitly for debugging
        raise HTTPException(status_code=500, detail=f"ImageKit Error: {str(e)}")
    
    return {"message": "🎉 Entry and media successfully saved!"}
    

@app.get("/posts/search/", response_model=list[schemas.PostResponse])
def search_post(
    q: str = "",
    db : Session = Depends(get_db)
):
    result = db.query(models.Post).filter((models.Post.title.ilike(f"%{q}%")) | (models.Post.content.ilike(f"%{q}%"))).all()
    return result

@app.delete("/posts/{post_id}/")
def delete_post(
    post_id : int,
    current_user : models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not db_post:
        raise HTTPException(status_code=404, detail="post not found")
    
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="unauthorised action")
    
    db.delete(db_post)
    db.commit()
    return {"message" : f"Successfully deleted post {post_id}"}


@app.get("/posts/{owner_id}/users/", response_model=schemas.UserResponse)
def get_user(
    owner_id : int,
    db : Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == owner_id).first()

    return user

from src.schemas import CommentCreate
@app.post("/posts/{id}/comments/")
def create_comment(
    id : int,
    content : CommentCreate,
    current_user : models.User = Depends(get_current_user),
    db : Session = Depends(get_db)
):
    post = db.query(models.Post).filter(models.Post.id == id).first() 
    if not post:
        raise HTTPException(status_code=404, detail="post does not exist")

    comment_db = models.Comment(
        content = content.content,
        post_id = id,
        owner_id = current_user.id
    )

    db.add(comment_db)
    db.commit()
    db.refresh(comment_db)


@app.get("/posts/{post_id}/comments/", response_model=list[schemas.CommentResponse])
def get_comments(
    post_id: int,
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0

):
    comments = (
        db.query(models.Comment)
        .filter(models.Comment.post_id == post_id)
        .order_by(models.Comment.created_at.desc()) # Newest first
        .offset(skip)
        .limit(limit)
        .all()
    )

    return comments
    

@app.post("/posts/{post_id}/heart/")
def toggle_heart(
    post_id: int,  # FastAPI now reads this directly from the URL path!
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    # Verify post exists
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check if the user already hearted this post
    existing_heart = db.query(models.Hearts).filter(
        models.Hearts.post_id == post_id, 
        models.Hearts.user_id == current_user.id
    ).first()

    if existing_heart:
        # User already liked it -> UNLIKE it
        db.delete(existing_heart)
        db.commit()
        liked = False
    else:
        # User hasn't liked it -> LIKE it
        new_heart = models.Hearts(user_id=current_user.id, post_id=post_id)
        db.add(new_heart)
        db.commit()
        liked = True

    # Get total count remaining
    total_hearts = db.query(models.Hearts).filter(models.Hearts.post_id == post_id).count()
    
    return {"liked": liked, "total_hearts": total_hearts}

@app.patch("/{user_id}/make-admin/")
def make_user_admin(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_admin = True
    db.commit()
    return {"message": f"User {user.username} has been granted admin privileges."}

