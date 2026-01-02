#!/usr/bin/env python3
"""
SQLAlchemy models for the LangSense Bot - SECURE FINANCIAL VERSION
Defines database schema for users, languages, countries, announcements, messaging, and financial transactions
"""

from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Optional
from decimal import Decimal

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text, 
    UniqueConstraint, Index, BigInteger, JSON, Numeric, LargeBinary, CheckConstraint, func
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column

Base = declarative_base(cls=AsyncAttrs)

class OutboxType(PyEnum):
    """Types of outbox messages"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal" 
    COMPLAINT = "complaint"
    SUPPORT = "support"
    BROADCAST = "broadcast"
    ANNOUNCEMENT = "announcement"

class OutboxStatus(PyEnum):
    """Status of outbox messages"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DeliveryStatus(PyEnum):
    """Status of message delivery"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BLOCKED = "blocked"

class User(Base):
    """User model for storing Telegram user information"""
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # ✅ Encrypted phone number (stored as bytes, decrypted on read)
    phone_encrypted: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    
    customer_code: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True, index=True)
    
    # Preferences
    language_code: Mapped[str] = mapped_column(String(5), nullable=False, default='ar')
    country_code: Mapped[str] = mapped_column(String(5), nullable=False, default='SA')
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # ✅ Financial fields - with Decimal precision and constraints
    balance: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2),
        CheckConstraint('balance >= 0', name='balance_non_negative'),
        nullable=False,
        default=Decimal('0.00'),
        server_default='0.00'
    )
    
    total_deposited: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2),
        nullable=False,
        default=Decimal('0.00'),
        server_default='0.00'
    )
    
    total_withdrawn: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2),
        nullable=False,
        default=Decimal('0.00'),
        server_default='0.00'
    )
    
    daily_withdraw_limit: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2),
        nullable=False,
        default=Decimal('10000.00'),
        server_default='10000.00'
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # ✅ Audit fields
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    last_modified_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), server_default=func.now())
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    outbox_messages = relationship("Outbox", back_populates="user", cascade="all, delete-orphan")
    announcement_deliveries = relationship("AnnouncementDelivery", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, customer_code={self.customer_code})>"

class Language(Base):
    """Language model for multi-language support"""
    __tablename__ = 'languages'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(5), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    native_name: Mapped[str] = mapped_column(String(100), nullable=False)
    rtl: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<Language(code={self.code}, name={self.name})>"

class Country(Base):
    """Country model for regional settings"""
    __tablename__ = 'countries'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(5), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    native_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_prefix: Mapped[str] = mapped_column(String(10), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<Country(code={self.code}, name={self.name})>"

class Announcement(Base):
    """Announcement model for system announcements"""
    __tablename__ = 'announcements'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title_ar: Mapped[str] = mapped_column(String(255), nullable=False)
    title_en: Mapped[str] = mapped_column(String(255), nullable=False)
    content_ar: Mapped[str] = mapped_column(Text, nullable=False)
    content_en: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Display settings
    display_duration: Mapped[int] = mapped_column(Integer, default=0)  # 0 = permanent
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    
    # Filtering
    target_language: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    target_country: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    deliveries = relationship("AnnouncementDelivery", back_populates="announcement", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Announcement(id={self.id}, title_ar={self.title_ar[:50]})>"

class AnnouncementDelivery(Base):
    """Track announcement delivery to users"""
    __tablename__ = 'announcement_deliveries'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    announcement_id: Mapped[int] = mapped_column(Integer, ForeignKey('announcements.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    
    status: Mapped[DeliveryStatus] = mapped_column(Enum(DeliveryStatus), default=DeliveryStatus.PENDING)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    announcement = relationship("Announcement", back_populates="deliveries")
    user = relationship("User", back_populates="announcement_deliveries")
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('announcement_id', 'user_id', name='uq_announcement_user'),)
    
    def __repr__(self):
        return f"<AnnouncementDelivery(announcement_id={self.announcement_id}, user_id={self.user_id}, status={self.status})>"

class Outbox(Base):
    """Outbox for user requests and system messages"""
    __tablename__ = 'outbox'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    type: Mapped[OutboxType] = mapped_column(Enum(OutboxType), nullable=False)
    status: Mapped[OutboxStatus] = mapped_column(Enum(OutboxStatus), default=OutboxStatus.PENDING)
    
    # Content
    subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    attachment_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Processing
    processed_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)  # Admin telegram_id
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    admin_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="outbox_messages")
    recipients = relationship("OutboxRecipient", back_populates="outbox", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_outbox_type_status', 'type', 'status'),
        Index('idx_outbox_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Outbox(id={self.id}, type={self.type}, status={self.status})>"

class OutboxRecipient(Base):
    """Track individual message recipients for broadcasts"""
    __tablename__ = 'outbox_recipients'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    outbox_id: Mapped[int] = mapped_column(Integer, ForeignKey('outbox.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    
    status: Mapped[DeliveryStatus] = mapped_column(Enum(DeliveryStatus), default=DeliveryStatus.PENDING)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_attempt: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    outbox = relationship("Outbox", back_populates="recipients")
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('outbox_id', 'user_id', name='uq_outbox_user'),)
    
    def __repr__(self):
        return f"<OutboxRecipient(outbox_id={self.outbox_id}, user_id={self.user_id}, status={self.status})>"


class Transaction(Base):
    """✅ Immutable financial transaction ledger with integrity verification"""
    __tablename__ = 'transactions'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # ✅ Idempotency key - prevents duplicate transactions
    idempotency_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Transaction type
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # CREDIT, DEBIT
    
    # ✅ Decimal amount with constraint
    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2),
        CheckConstraint('amount > 0', name='transaction_amount_positive'),
        nullable=False
    )
    
    # ✅ Balance snapshots for audit trail
    balance_before: Mapped[Decimal] = mapped_column(Numeric(precision=15, scale=2), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(precision=15, scale=2), nullable=False)
    
    # ✅ HMAC signature for integrity verification
    signature: Mapped[str] = mapped_column(String(256), nullable=False)
    
    # ✅ Immutable audit trail
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True
    )
    created_by: Mapped[int] = mapped_column(BigInteger, nullable=False)  # Admin telegram_id
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    
    # Reference to the request
    outbox_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('outbox.id'), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    
    __table_args__ = (
        Index('idx_transaction_user_created', 'user_id', 'created_at'),
        Index('idx_transaction_type', 'type'),
        CheckConstraint(
            "(type = 'CREDIT' AND balance_after > balance_before) OR (type = 'DEBIT' AND balance_after < balance_before)",
            name='check_transaction_balance_consistency'
        ),
    )
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, user={self.user_id}, type={self.type}, amount={self.amount})>"


class AuditLog(Base):
    """✅ Immutable audit log for all admin actions and sensitive operations"""
    __tablename__ = 'audit_logs'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Who performed the action
    admin_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    
    # What action was performed
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # What was the target (transaction, user, etc.)
    target_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    target_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Details in JSON format
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # ✅ Immutable timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True
    )
    
    # IP address for security tracking
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    
    # User agent for extra tracking
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    __table_args__ = (
        Index('idx_audit_log_admin_created', 'admin_id', 'created_at'),
        Index('idx_audit_log_action_created', 'action', 'created_at'),
        Index('idx_audit_log_target', 'target_type', 'target_id'),
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, admin={self.admin_id}, target={self.target_type}:{self.target_id})>"


class Commission(Base):
    """Agent commission tracking"""
    __tablename__ = 'commissions'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    agent_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    transaction_id: Mapped[int] = mapped_column(Integer, ForeignKey('transactions.id'), nullable=False)
    
    # Commission amount
    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2),
        CheckConstraint('amount > 0', name='commission_amount_positive'),
        nullable=False
    )
    
    # Commission rate (e.g., 0.025 for 2.5%)
    rate: Mapped[Decimal] = mapped_column(Numeric(precision=5, scale=4), nullable=False)
    
    # Payment status
    status: Mapped[str] = mapped_column(String(20), default='PENDING')  # PENDING, PAID, CANCELLED
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=func.now())
    
    __table_args__ = (
        Index('idx_commission_agent', 'agent_id'),
        Index('idx_commission_status', 'status'),
    )
    
    def __repr__(self):
        return f"<Commission(id={self.id}, agent={self.agent_id}, amount={self.amount})>"
