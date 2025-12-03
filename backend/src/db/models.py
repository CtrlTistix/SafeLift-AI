"""
SQLAlchemy database models for SafeLift-AI.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class UserRoleEnum(str, enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class EventSeverity(int,  enum.Enum):
    """Event severity levels."""
    LOW = 1
    MINOR = 2
    MODERATE = 3
    HIGH = 4
    CRITICAL = 5


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(SQLEnum(UserRoleEnum), default=UserRoleEnum.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user")


class Forklift(Base):
    """Forklift model representing individual vehicles."""
    __tablename__ = "forklifts"
    
    id = Column(Integer, primary_key=True, index=True)
    forklift_id = Column(String(50), unique=True, index=True, nullable=False)
    model = Column(String(100))
    manufacturer = Column(String(100))
    year = Column(Integer)
    max_load_kg = Column(Float)
    is_active = Column(Boolean, default=True)
    last_maintenance = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    telemetry = relationship("Telemetry", back_populates="forklift")
    events = relationship("Event", back_populates="forklift")


class Event(Base):
    """Safety event model."""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    type = Column(String(100), index=True, nullable=False)
    severity = Column(Integer, index=True, nullable=False)
    source = Column(String(100), index=True, nullable=False)
    forklift_id = Column(Integer, ForeignKey("forklifts.id"), nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    forklift = relationship("Forklift", back_populates="events")
    alert = relationship("Alert", back_populates="event", uselist=False)


class Telemetry(Base):
    """Telemetry data from forklifts."""
    __tablename__ = "telemetry"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    forklift_id = Column(Integer, ForeignKey("forklifts.id"), nullable=False)
    
    # GPS coordinates
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Motion data
    speed_kmh = Column(Float, nullable=True)
    acceleration_x = Column(Float, nullable=True)
    acceleration_y = Column(Float, nullable=True)
    acceleration_z = Column(Float, nullable=True)
    
    # Forklift-specific data
    mast_tilt_deg = Column(Float, nullable=True)
    load_weight_kg = Column(Float, nullable=True)
    mast_height_m = Column(Float, nullable=True)
    
    # Operator
    operator_id = Column(String(50), nullable=True)
    
    # Additional data
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    forklift = relationship("Forklift", back_populates="telemetry")


class Alert(Base):
    """Safety alert generated from rule violations."""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    rule_type = Column(String(100), index=True, nullable=False)
    severity = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=False)
    recommendation = Column(String(500), nullable=True)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    event = relationship("Event", back_populates="alert")


class AuditLog(Base):
    """Audit log for tracking user actions."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), index=True, nullable=False)
    resource = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
