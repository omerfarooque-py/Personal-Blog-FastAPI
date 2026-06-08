#security.py

import bcrypt
def hash_pass(password : str):
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode("utf-8")

import os 
from dotenv import load_dotenv
from jose import jwt 

load_dotenv()

SECRET_KEY = os.getenv("MY_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_pass(plain_password: str, hashed_password : str) -> bool:
   return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

from datetime import timedelta, timezone, datetime

def create_access_token(data : dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp" : expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt