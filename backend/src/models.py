from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from .database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    type = Column(String, nullable=False, index=True)
    severity = Column(Integer, nullable=False, index=True)
    source = Column(String, nullable=False)
    metadata = Column(JSON, default={})

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "type": self.type,
            "severity": self.severity,
            "source": self.source,
            "metadata": self.metadata
        }
