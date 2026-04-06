from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

# 调查表模板相关Schema
class SurveyTemplateBase(BaseModel):
    name: str = Field(..., description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    fields: Dict[str, Any] = Field(..., description="字段定义")
    version: str = Field("1.0", description="模板版本")
    is_active: int = Field(1, description="是否启用")

class SurveyTemplateCreate(SurveyTemplateBase):
    pass

class SurveyTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[Dict[str, Any]] = None
    version: Optional[str] = None
    is_active: Optional[int] = None

class SurveyTemplate(SurveyTemplateBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 法律建议相关Schema
class LegalSuggestionBase(BaseModel):
    record_id: int = Field(..., description="调查记录ID")
    trigger_changes: Optional[Dict[str, Any]] = Field(None, description="触发变更的字段")
    suggestion: str = Field(..., description="法律建议内容")
    analysis_type: str = Field("general", description="分析类型")
    confidence_score: int = Field(80, description="置信度分数")

class LegalSuggestionCreate(LegalSuggestionBase):
    pass

class LegalSuggestion(LegalSuggestionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 调查表记录相关Schema
class SurveyRecordBase(BaseModel):
    template_id: int = Field(..., description="模板ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    answers: Dict[str, Any] = Field(..., description="填写答案")
    version: str = Field("1.0", description="记录版本")
    status: str = Field("submitted", description="状态")

class SurveyRecordCreate(SurveyRecordBase):
    pass

class SurveyRecordUpdate(BaseModel):
    answers: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class SurveyRecord(SurveyRecordBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    suggestions: Optional[List[LegalSuggestion]] = Field(None, description="关联的法律建议")
    template: Optional[SurveyTemplate] = Field(None, description="关联的模板")
    
    class Config:
        from_attributes = True

# 法律建议相关Schema
class LegalSuggestionBase(BaseModel):
    record_id: int = Field(..., description="调查记录ID")
    trigger_changes: Optional[Dict[str, Any]] = Field(None, description="触发变更的字段")
    suggestion: str = Field(..., description="法律建议内容")
    analysis_type: str = Field("general", description="分析类型")
    confidence_score: int = Field(80, description="置信度分数")

class LegalSuggestionCreate(LegalSuggestionBase):
    pass

class LegalSuggestion(LegalSuggestionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 请求和响应Schema
class SurveySubmitRequest(BaseModel):
    template_id: int = Field(..., description="模板ID")
    answers: Dict[str, Any] = Field(..., description="填写答案")
    user_id: Optional[str] = Field(None, description="用户ID")

class SurveySubmitResponse(BaseModel):
    record_id: int = Field(..., description="调查记录ID")
    suggestion: Optional[LegalSuggestion] = Field(None, description="生成的法律建议")
    message: str = Field(..., description="响应消息")

class SurveyAnalysisRequest(BaseModel):
    record_id: int = Field(..., description="调查记录ID")
    previous_answers: Optional[Dict[str, Any]] = Field(None, description="之前的答案（用于比较变更）")

class SurveyHistoryResponse(BaseModel):
    records: List[SurveyRecord] = Field(..., description="调查记录列表")
    total: int = Field(..., description="总记录数")