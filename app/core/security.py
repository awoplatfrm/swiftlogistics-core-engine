from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from jose import jwt, JWTError, ExpiredSignatureError
from app.core.config import settings
import uuid

pass_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
o2auth_schema = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login-merchant")


async def get_current_merchant(token: str = Depends(o2auth_schema)) -> int:
    exception_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials or token expired",
    )
    try:
        payload = jwt.decode(token, settings.TOKEN_KEY, settings.ALGORITHM)
        if payload.get("token_type") != "access":
            raise exception_error

        merchant_id: str = payload.get("sub")
        if merchant_id is None:
            raise exception_error
    except (JWTError, ExpiredSignatureError):

        raise exception_error

    return int(merchant_id)


def hash_password(password: str) -> str:

    print("password to hash is ", password)

    return pass_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:

    return pass_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expires = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
    )

    to_encode.update({"exp": expires})
    return jwt.encode(data, settings.TOKEN_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict, expire: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expires = datetime.now(timezone.utc) + (
        expire or timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE)
    )
    jti = str(uuid.uuid4())
    iat = datetime.now(timezone.utc)
    to_encode.update({"exp": expires, "iat": iat, "jti": jti})
    token = jwt.encode(to_encode, settings.TOKEN_KEY, algorithm=settings.ALGORITHM)
    return token
