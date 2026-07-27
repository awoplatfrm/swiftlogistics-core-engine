from fastapi import FastAPI, HTTPException, Depends, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.security import get_current_merchant
from app.database import Base, ASYNC_ENGINE, db_conn
from app.models import Shipments, Sender, Recipient
from app.schema import (
    ShipmentIn,
    ShipmentOut,
    ShipmentsUpdateIn,
    ShipmentUpdateOut,
    PaginatedShipments,
)
from contextlib import asynccontextmanager
from typing import Optional


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with ASYNC_ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield


app = FastAPI(title="swiftlogistics core engine", version="1.1.0")
router = APIRouter(prefix="/shipments", tags=["shipments"])


@router.post("/get-shipment/{shipment_id}", status_code=status.HTTP_200_OK)
async def get_shipment(
    shipment_id: int,
    db: AsyncSession = Depends(db_conn),
    merchant_id: int = Depends(get_current_merchant),
):

    query = select(Shipments).where(Shipments.id == shipment_id)

    result = await db.execute(query)

    shipment = result.scalar_one_or_none()

    return shipment


@router.post(
    "/register-shipment",
    status_code=status.HTTP_201_CREATED,
    response_model=ShipmentOut,
)
async def create_shipment(
    payload: ShipmentIn,
    merchant_id: int = Depends(get_current_merchant),
    db: AsyncSession = Depends(db_conn),
):

    new_sender = Sender(**payload.sender.model_dump())
    new_recipient = Recipient(**payload.recipient.model_dump())

    db.add_all([new_sender, new_recipient])
    await db.flush()

    # instantiate shipments object
    shipment_data = payload.model_dump(exclude={"sender", "recipient"})

    new_shipment = Shipments(
        merchant_id=merchant_id,
        sender_id=new_sender.id,
        recipient_id=new_recipient.id,
        **shipment_data
    )

    db.add(new_shipment)
    await db.commit()

    await db.refresh(new_shipment, attribute_names=["sender", "recipient", "merchant"])

    return new_shipment


@router.put("/update-shipment/{shipment_id}", response_model=ShipmentUpdateOut)
async def update_shipment(
    shipment_id: int,
    payload: ShipmentsUpdateIn,
    db: AsyncSession = Depends(db_conn),
    merchant_id: int = Depends(get_current_merchant),
):

    db_query = await db.execute(select(Shipments).where(Shipments.id == shipment_id))
    database_shipment = db_query.scalar_one_or_none()

    if not database_shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=" shipment not found"
        )

    to_update = payload.model_dump(exclude_unset=True)
    sender = to_update.pop("sender", None)
    recipient = to_update.pop("recipient", None)

    for name, value in to_update.items():
        setattr(database_shipment, name, value)

    if sender and database_shipment.sender:
        for name, value in sender.items():
            setattr(database_shipment.sender, name, value)

    if recipient and database_shipment.recipient:
        for name, value in recipient.items():
            setattr(database_shipment.recipient, name, value)

    await db.commit()
    await db.refresh(database_shipment, attribute_names=["sender", "recipient"])

    return database_shipment


@router.delete("/delete-shipment/{shipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shipment(
    shipment_id: int,
    db: AsyncSession = Depends(db_conn),
    merchant_id: int = Depends(get_current_merchant),
):

    querry = await db.execute(select(Shipments).where(Shipments.id == shipment_id))
    shipment_data = querry.scalar_one_or_none()

    if not shipment_data:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT, detail="shipment not found"
        )

    await db.delete(shipment_data)
    await db.commit()

    return None
