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


class WithdrawalAddress(Base):
    """نموذج العناوين المحفوظة للسحب"""
    __tablename__ = 'withdrawal_addresses'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.telegram_id'), nullable=False, index=True)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    label: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # "المنزل", "العمل", إلخ
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=func.now())
    
    # Relationships
    user: Mapped['User'] = relationship('User', foreign_keys=[user_id])
    
    __table_args__ = (
        Index('idx_withdrawal_address_user', 'user_id'),
        Index('idx_withdrawal_address_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<WithdrawalAddress(id={self.id}, user={self.user_id}, label={self.label})>"


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


# ==================== NEW MODELS - WALLET SYSTEM ====================

class CurrencyEnum(str, PyEnum):
    """العملات المدعومة"""
    SAR = "SAR"
    USD = "USD"
    EUR = "EUR"
    AED = "AED"
    EGP = "EGP"
    KWD = "KWD"
    QAR = "QAR"
    BHD = "BHD"
    OMR = "OMR"
    JOD = "JOD"
    TRY = "TRY"


class Wallet(Base):
    """محفظة المستخدم - كل مستخدم له محفظة لكل عملة"""
    __tablename__ = 'wallets'
    __table_args__ = (
        UniqueConstraint('user_id', 'currency', name='uq_user_currency'),
    )
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    currency = Column(Enum(CurrencyEnum), nullable=False, default=CurrencyEnum.SAR)
    balance = Column(Numeric(15, 2), default=0.0, nullable=False)
    frozen_amount = Column(Numeric(15, 2), default=0.0)
    total_deposited = Column(Numeric(15, 2), default=0.0)
    total_withdrawn = Column(Numeric(15, 2), default=0.0)
    total_commission = Column(Numeric(15, 2), default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="wallets")
    transactions = relationship("WalletTransaction", back_populates="wallet", cascade="all, delete-orphan")


class WalletTransaction(Base):
    """سجل معاملات المحفظة - غير قابل للتعديل"""
    __tablename__ = 'wallet_transactions'
    
    id = Column(Integer, primary_key=True)
    wallet_id = Column(Integer, ForeignKey('wallets.id'), nullable=False)
    type = Column(String(20), nullable=False)  # deposit, withdraw, commission, refund
    amount = Column(Numeric(15, 2), nullable=False)
    reference_id = Column(String(100))
    description = Column(Text)
    status = Column(String(20), default='completed')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")


# ==================== NEW MODELS - AFFILIATE SYSTEM ====================

class AffiliateStatus(str, PyEnum):
    """حالة الوكيل"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class CommissionType(str, PyEnum):
    """نوع العمولة"""
    PERCENTAGE = "percentage"
    FIXED = "fixed"


class Affiliate(Base):
    """الوكيل أو المسوق"""
    __tablename__ = 'affiliates'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    affiliate_code = Column(String(20), unique=True, nullable=False)
    affiliate_link = Column(String(255))
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    commission_type = Column(Enum(CommissionType), default=CommissionType.PERCENTAGE)
    commission_rate = Column(Numeric(10, 2), nullable=False)
    total_referrals = Column(Integer, default=0)
    active_referrals = Column(Integer, default=0)
    total_commission_earned = Column(Numeric(15, 2), default=0.0)
    total_commission_paid = Column(Numeric(15, 2), default=0.0)
    pending_commission = Column(Numeric(15, 2), default=0.0)
    status = Column(Enum(AffiliateStatus), default=AffiliateStatus.ACTIVE)
    is_verified = Column(Boolean, default=False)
    minimum_payout = Column(Numeric(10, 2), default=100.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="affiliate")
    referrals = relationship("AffiliateReferral", back_populates="affiliate")
    commissions = relationship("AffiliateCommission", back_populates="affiliate")
    payouts = relationship("AffiliatePayout", back_populates="affiliate")


class AffiliateReferral(Base):
    """الإحالات - العملاء الذين جاءوا من الوكيل"""
    __tablename__ = 'affiliate_referrals'
    
    id = Column(Integer, primary_key=True)
    affiliate_id = Column(Integer, ForeignKey('affiliates.id'), nullable=False)
    referred_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    referral_date = Column(DateTime, default=datetime.utcnow)
    total_spent = Column(Numeric(15, 2), default=0.0)
    commission_earned = Column(Numeric(15, 2), default=0.0)
    status = Column(String(20), default='active')
    
    # Relationships
    affiliate = relationship("Affiliate", back_populates="referrals")
    referred_user = relationship("User")


class AffiliateCommission(Base):
    """عمولات الوكيل"""
    __tablename__ = 'affiliate_commissions'
    
    id = Column(Integer, primary_key=True)
    affiliate_id = Column(Integer, ForeignKey('affiliates.id'), nullable=False)
    transaction_id = Column(Integer)
    transaction_amount = Column(Numeric(15, 2), nullable=False)
    commission_amount = Column(Numeric(15, 2), nullable=False)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    affiliate = relationship("Affiliate", back_populates="commissions")


class AffiliatePayout(Base):
    """دفعات الوكيل"""
    __tablename__ = 'affiliate_payouts'
    
    id = Column(Integer, primary_key=True)
    affiliate_id = Column(Integer, ForeignKey('affiliates.id'), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(10), default='SAR')
    payment_method = Column(String(50))
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # Relationships
    affiliate = relationship("Affiliate", back_populates="payouts")


# ==================== NEW MODELS - PAYMENT METHODS ====================

class PaymentMethodType(str, PyEnum):
    """أنواع طرق الدفع"""
    BANK_TRANSFER = "bank_transfer"
    IBAN = "iban"
    WALLET = "wallet"
    CRYPTO = "crypto"
    CARD = "card"


class PaymentMethodStatus(str, PyEnum):
    """حالة طريقة الدفع"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DISABLED = "disabled"


class PaymentMethod(Base):
    """طرق الدفع المتاحة"""
    __tablename__ = 'payment_methods'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(Enum(PaymentMethodType), nullable=False)
    display_name_ar = Column(String(150), nullable=False)
    display_name_en = Column(String(150))
    deposit_fee = Column(Numeric(5, 2), default=0.0)
    withdrawal_fee = Column(Numeric(5, 2), default=0.0)
    min_deposit = Column(Numeric(15, 2), default=0.0)
    max_deposit = Column(Numeric(15, 2), default=999999.99)
    min_withdrawal = Column(Numeric(15, 2), default=0.0)
    max_withdrawal = Column(Numeric(15, 2), default=999999.99)
    supported_currencies = Column(JSON, default=['SAR'])
    bank_details = Column(JSON)
    config = Column(JSON)
    status = Column(Enum(PaymentMethodStatus), default=PaymentMethodStatus.ACTIVE)
    is_active = Column(Boolean, default=True)
    is_deposit = Column(Boolean, default=True)
    is_withdrawal = Column(Boolean, default=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserPaymentMethod(Base):
    """طرق الدفع المحفوظة للمستخدم"""
    __tablename__ = 'user_payment_methods'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    payment_method_id = Column(Integer, ForeignKey('payment_methods.id'), nullable=False)
    account_holder_name = Column(String(150))
    account_number = Column(String(50))
    bank_code = Column(String(10))
    card_last_digits = Column(String(4))
    extra_data = Column(JSON)
    is_verified = Column(Boolean, default=False)
    is_primary = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Update User model to add relationships
User.wallets = relationship("Wallet", back_populates="user")
User.affiliate = relationship("Affiliate", back_populates="user", uselist=False)
