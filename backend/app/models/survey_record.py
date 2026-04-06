from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class SurveyRecord(Base):
    """调查表填写记录模型"""
    __tablename__ = "survey_records"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("survey_templates.id"), nullable=False, comment="模板ID")
    user_id = Column(String(100), comment="用户ID（可为空，表示匿名填写）")
    answers = Column(JSON, nullable=False, comment="填写答案（JSON格式）")
    version = Column(String(20), default="1.0", comment="记录版本")
    status = Column(String(20), default="submitted", comment="状态：draft, submitted, analyzed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    template = relationship("SurveyTemplate")
    suggestions = relationship("LegalSuggestion", back_populates="record", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SurveyRecord(id={self.id}, template_id={self.template_id}, status='{self.status}')>"