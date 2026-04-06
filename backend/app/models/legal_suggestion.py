from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class LegalSuggestion(Base):
    """法律建议记录模型"""
    __tablename__ = "legal_suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("survey_records.id", ondelete="CASCADE"), nullable=False, comment="调查记录ID")
    trigger_changes = Column(JSON, comment="触发变更的字段（JSON格式）")
    suggestion = Column(Text, nullable=False, comment="法律建议内容")
    analysis_type = Column(String(50), default="general", comment="分析类型：general, labor, contract, ip, tax, compliance")
    confidence_score = Column(Integer, default=80, comment="置信度分数（0-100）")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    record = relationship("SurveyRecord", back_populates="suggestions")
    
    def __repr__(self):
        return f"<LegalSuggestion(id={self.id}, record_id={self.record_id}, analysis_type='{self.analysis_type}')>"