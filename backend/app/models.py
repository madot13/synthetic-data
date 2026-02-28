from sqlalchemy import Column, String, DateTime, JSON, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class UserTask(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, ingesting, creating, curating, completed, failed
    progress = Column(Float, default=0.0)      # 0 to 100
    created_at = Column(DateTime, default=datetime.utcnow)
    
    result_path = Column(String, nullable=True)
    
    stats = Column(JSON, nullable=True)