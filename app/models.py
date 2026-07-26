from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
    JSON,
)
from datetime import datetime, timezone
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.database import Base


class RegisterMerchants(Base):
    __tablename__ = "merchants"
    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False, unique=True, index=True)
    phone_number = Column(String(20), nullable=False)

    hashed_password = Column(String(255), nullable=True)
    is_loggedin = Column(Boolean, default=False)
    access_token = Column(String(255), nullable=True, default=None)
    refresh_token = Column(String(255), nullable=True, default=None)
    account_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    shipments: Mapped[list["RegisterShipments"]] = relationship(
        "RegisterShipments", back_populates="merchant", cascade="all, delete-orphan"
    )


class RegisterShipments(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False)
    description = Column(String(255), nullable=True)
    total_weight = Column(Float, nullable=False)
    dimensions = Column(JSON, nullable=True)
    parcels = Column(JSON, nullable=False, default=list)
    account_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    merchant: Mapped[list["RegisterMerchants"]] = relationship(
        "RegisterMerchants", back_populates="shipments"
    )
