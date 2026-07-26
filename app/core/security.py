from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from typing import Optional
from jose import jwt
from dotenv import load_dotenv
import uuid
import os

load_dotenv()
pass_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get("TOKEN_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = 30
REFRESH_TOKEN_EXPIRE = 7200


def hash_password(password: str) -> str:

    print("password to hash is ", password)

    return pass_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:

    return pass_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expires = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    )

    to_encode.update({"exp": expires})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expire: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expires = datetime.now(timezone.utc) + (
        expire or timedelta(seconds=REFRESH_TOKEN_EXPIRE)
    )
    jti = str(uuid.uuid4())
    iat = datetime.now(timezone.utc)
    to_encode.update({"type": "refresh", "exp": expires, "iat": iat, "jti": jti})
    print("🔑 ENCODE SECRET_KEY:", repr(SECRET_KEY))
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token
