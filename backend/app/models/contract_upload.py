from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class ContractUpload(Base):
    """合同上传记录模型"""
    __tablename__ = "contract_uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)  # 字节数
    status = Column(String(50), default='uploaded')  # uploaded, parsing, analyzing, completed, failed
    contract_type = Column(String(100), nullable=True)  # 合同类型
    user_id = Column(Integer, nullable=True)  # 用户ID，可为空
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    diagnoses = relationship("ContractDiagnosis", back_populates="upload", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ContractUpload(id={self.id}, filename='{self.filename}', status='{self.status}')>"


class ContractDiagnosis(Base):
    """合同诊断结果模型"""
    __tablename__ = "contract_diagnoses"
    
    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("contract_uploads.id", ondelete="CASCADE"), nullable=False)
    contract_type = Column(String(100), nullable=True)  # 合同类型
    summary = Column(Text, nullable=True)  # 总体评价
    risks = Column(JSON, nullable=True)  # 风险列表，JSON格式
    suggestions = Column(Text, nullable=True)  # 综合建议
    analysis_time = Column(Integer, nullable=True)  # 分析耗时（秒）
    model_used = Column(String(100), nullable=True)  # 使用的模型
    perspective = Column(String(100), nullable=True)  # 审查立场
    focus_areas = Column(JSON, nullable=True)  # 重点关注领域
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    upload = relationship("ContractUpload", back_populates="diagnoses")
    
    def __repr__(self):
        return f"<ContractDiagnosis(id={self.id}, upload_id={self.upload_id}, contract_type='{self.contract_type}')>"