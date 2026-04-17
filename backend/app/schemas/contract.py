from pydantic import BaseModel, field_validator
from typing import Optional, List, Any, Union
from datetime import datetime

# 合同风险项
class ContractRiskBase(BaseModel):
    clause: str  # 风险条款内容
    risk_level: str  # 风险等级：high, medium, low
    risk_type: str  # 风险类型
    description: str  # 风险描述
    suggestion: str  # 修改建议
    line_number: Optional[int] = None  # 在合同中的行号
    paragraph_index: Optional[int] = None  # 段落索引

class ContractRiskCreate(ContractRiskBase):
    pass

class ContractRisk(ContractRiskBase):
    id: Optional[int] = None
    
    class Config:
        from_attributes = True

# 合同上传记录
class ContractUploadBase(BaseModel):
    filename: str
    file_type: str
    file_size: int

class ContractUploadCreate(ContractUploadBase):
    pass

class ContractUpload(ContractUploadBase):
    id: int
    file_path: str
    status: str
    contract_type: Optional[str] = None
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 合同诊断结果
class ContractDiagnosisBase(BaseModel):
    contract_type: Optional[str] = None
    summary: Optional[str] = None
    suggestions: Optional[str] = None
    analysis_time: Optional[int] = None
    model_used: Optional[str] = None
    perspective: Optional[str] = None
    focus_areas: Optional[List[str]] = None

class ContractDiagnosisCreate(ContractDiagnosisBase):
    upload_id: int
    risks: Optional[List[ContractRiskBase]] = None

class ContractDiagnosis(ContractDiagnosisBase):
    id: int
    upload_id: int
    risks: Optional[List[Union[ContractRisk, dict]]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_validator('risks', mode='before')
    @classmethod
    def validate_risks(cls, v):
        """验证并转换风险数据"""
        if v is None:
            return None
        
        # 如果已经是ContractRisk对象列表，直接返回
        if isinstance(v, list) and len(v) > 0 and isinstance(v[0], ContractRisk):
            return v
        
        # 如果是字典列表，转换为ContractRisk对象
        if isinstance(v, list):
            validated_risks = []
            for risk_item in v:
                if isinstance(risk_item, dict):
                    # 确保字典包含必需的字段，为缺失字段提供默认值
                    risk_dict = risk_item.copy()
                    
                    # 检查必需字段，如果缺失则提供默认值
                    if 'clause' not in risk_dict or not risk_dict['clause']:
                        risk_dict['clause'] = "未指定条款"
                    if 'risk_level' not in risk_dict:
                        risk_dict['risk_level'] = "medium"
                    if 'risk_type' not in risk_dict:
                        risk_dict['risk_type'] = "未分类风险"
                    if 'description' not in risk_dict:
                        risk_dict['description'] = "风险描述缺失"
                    if 'suggestion' not in risk_dict:
                        risk_dict['suggestion'] = "请人工审查"
                    
                    # 创建ContractRisk对象
                    validated_risks.append(ContractRisk(**risk_dict))
                else:
                    # 如果不是字典，保持原样（可能是ContractRisk对象）
                    validated_risks.append(risk_item)
            return validated_risks
        
        return v
    
    class Config:
        from_attributes = True

# API请求/响应模型
class ContractUploadRequest(BaseModel):
    file: Any  # 文件对象，实际使用中会是UploadFile

class ContractUploadResponse(BaseModel):
    upload: ContractUpload
    pre_analysis: Optional[dict] = None

class ContractDiagnosisRequest(BaseModel):
    upload_id: int
    contract_type: Optional[str] = None  # 合同类型（技术合同、服务合同等）
    perspective: Optional[str] = None  # 审查立场（甲方/乙方等）
    focus_areas: Optional[List[str]] = None
    model_provider: Optional[str] = "siliconflow"

class ContractDiagnosisResponse(BaseModel):
    diagnosis: ContractDiagnosis
    analysis_time: int
    model_used: str

class ContractDiagnosisStatus(BaseModel):
    upload_id: int
    status: str  # uploading, parsing, analyzing, completed, failed
    progress: int  # 0-100
    message: str

class ContractUploadWithDiagnosis(ContractUpload):
    """包含诊断记录的上传记录"""
    diagnoses: List[ContractDiagnosis] = []

class ContractHistoryResponse(BaseModel):
    uploads: List[ContractUploadWithDiagnosis]
    total: int