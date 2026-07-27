from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import FastAPI, HTTPException, status, Depends, Response, Cookie, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from app.models import Merchants
from jose import jwt, JWTError
from app.schema import (
    MerchantIn,
    LoginMerchant,
    MerchantTokenOut,
    MerchantOut,
)
from app.database import ASYNC_ENGINE, Base, db_conn
from contextlib import asynccontextmanager
from datetime import timedelta
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


router = APIRouter(prefix="/auth")


async def check_email(email: str, db: AsyncSession):

    statement = select(Merchants).where(Merchants.email == email)
    exist = await db.execute(statement=statement)
    return exist.scalars().first()


@router.post(
    "/register-merchant",
    response_model=MerchantOut,
    status_code=status.HTTP_201_CREATED,
)
async def register_merchant(payload: MerchantIn, db: AsyncSession = Depends(db_conn)):

    email_exist = await check_email(payload.email, db)
    if email_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="merchant with this email exist already",
        )

    pass_to_hash = hash_password(payload.password)

    new_merchant = Merchants(
        business_name=payload.business_name,
        email=payload.email,
        phone_number=payload.phone_number,
        hashed_password=pass_to_hash,
    )

    db.add(new_merchant)
    await db.commit()
    await db.refresh(new_merchant)
    return new_merchant


@router.post(
    "/login-merchant",
    response_model=MerchantTokenOut,
    status_code=status.HTTP_200_OK,
)
async def login_merchant(
    response: Response,
    payload: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(db_conn),
):

    email = payload.username
    password = payload.password
    merchant = await check_email(email, db)

    if not merchant or not verify_password(password, merchant.hashed_password):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="email or password is incorrrect",
        )

    access_token = create_access_token(
        {"sub": str(merchant.id), "token_type": "access"}, timedelta(minutes=5)
    )
    refresh_token = create_refresh_token(
        {"sub": str(merchant.id), "token_type": "refresh"}, timedelta(days=7)
    )

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


@router.post("/refresh")
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
        if payload.get("token_type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token type"
            )

        merchant_id = payload.get("sub")

    except JWTError as e:

        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    data = {"sub": str(merchant_id), "token_type": "refresh"}
    new_token = create_access_token(data, timedelta(minutes=30))

    return {"access_token": new_token, "token_type": "Bearer"}
