from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.db.base import Base

class SurveyTemplate(Base):
    """调查表模板模型"""
    __tablename__ = "survey_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="模板名称")
    description = Column(Text, comment="模板描述")
    fields = Column(JSON, nullable=False, comment="字段定义（JSON格式）")
    version = Column(String(20), default="1.0", comment="模板版本")
    is_active = Column(Integer, default=1, comment="是否启用（1启用，0禁用）")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<SurveyTemplate(id={self.id}, name='{self.name}', version='{self.version}')>"