from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import FastAPI, HTTPException, status, Depends, Response, Cookie
from app.models import RegisterMerchants
from jose import jwt, JWTError
from app.schema import (
    RegisterMerchant,
    LoginMerchant,
    MerchantTokenResponse,
    RegisterMerchantResponse,
)
from app.database import ASYNC_ENGINE, Base, session_local
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import AsyncGenerator
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    ALGORITHM,
    SECRET_KEY,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with ASYNC_ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="swiftlogistics core engine", lifespan=lifespan, version="1.0.0")


async def db_conn() -> AsyncGenerator[AsyncSession, None]:
    async with session_local() as session:
        yield session


async def check_email(email: str, db: AsyncSession):

    statement = select(RegisterMerchants).where(RegisterMerchants.email == email)
    exist = await db.execute(statement=statement)
    return exist.scalars().first()


@app.get("/")
async def root():
    return {
        "message": "Welcome to SwiftLogistics API",
        "docs": "Visit /docs for the interactive API documentation",
        "status": "online",
    }


@app.post(
    "/api/v1/register-merchant",
    response_model=RegisterMerchantResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_merchant(
    payload: RegisterMerchant, db: AsyncSession = Depends(db_conn)
):

    email_exist = await check_email(payload.email, db)
    if email_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="merchant with this email exist already",
        )

    pass_to_hash = hash_password(payload.password)

    new_merchant = RegisterMerchants(
        business_name=payload.business_name,
        email=payload.email,
        phone_number=payload.phone_number,
        hashed_password=pass_to_hash,
    )

    db.add(new_merchant)
    await db.commit()
    await db.refresh(new_merchant)
    return new_merchant


@app.post(
    "/api/v1/login-merchant",
    response_model=MerchantTokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login_merchant(
    response: Response, payload: LoginMerchant, db: AsyncSession = Depends(db_conn)
):

    merchant = await check_email(payload.email, db)

    if not merchant or not verify_password(payload.password, merchant.hashed_password):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="email or password is incorrrect",
        )

    access_token = create_access_token({"sub": str(merchant.id)}, timedelta(minutes=5))
    refresh_token = create_refresh_token({"sub": str(merchant.id)}, timedelta(days=7))

    merchant.is_loggedin = True

    await db.commit()
    await db.refresh(merchant)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=604800,
    )
    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "merchant": merchant,
    }


@app.post("/api/v1/refresh")
async def verify_refresh_token(
    response: Response,
    refresh_token: str | None = Cookie(None),
    db: AsyncSession = Depends(db_conn),
):

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="refresh token missing"
        )

    try:

        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=ALGORITHM)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token type"
            )

        merchant_id = payload.get("sub")

    except JWTError as e:

        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    data = {"sub": str(merchant_id)}
    new_token = create_access_token(data, timedelta(minutes=30))

    return {"access_token": new_token, "token_type": "Bearer"}
