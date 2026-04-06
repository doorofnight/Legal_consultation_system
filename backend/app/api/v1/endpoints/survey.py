from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.survey import (
    SurveyTemplate, SurveyTemplateCreate, SurveyTemplateUpdate,
    SurveyRecord, SurveyRecordCreate, SurveySubmitRequest, SurveySubmitResponse,
    LegalSuggestion, SurveyHistoryResponse
)
from app.services.survey_service import SurveyService

router = APIRouter()

# 调查表模板相关接口
@router.get("/templates", response_model=List[SurveyTemplate])
async def get_templates(
    active_only: bool = Query(True, description="是否只返回启用的模板"),
    db: Session = Depends(get_db)
):
    """获取调查表模板列表"""
    if active_only:
        return SurveyService.get_active_templates(db)
    else:
        return db.query(SurveyTemplate).all()

@router.get("/templates/{template_id}", response_model=SurveyTemplate)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """获取特定调查表模板"""
    template = SurveyService.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return template

@router.post("/templates", response_model=SurveyTemplate)
async def create_template(
    template_data: SurveyTemplateCreate,
    db: Session = Depends(get_db)
):
    """创建调查表模板"""
    try:
        return SurveyService.create_template(db, template_data)
    except Exception as e:
        # 记录详细错误信息
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        print(f"创建模板失败: {error_detail}")
        print(f"Traceback: {traceback_str}")
        raise HTTPException(status_code=500, detail=f"创建模板失败: {error_detail}")

@router.put("/templates/{template_id}", response_model=SurveyTemplate)
async def update_template(
    template_id: int,
    template_data: SurveyTemplateUpdate,
    db: Session = Depends(get_db)
):
    """更新调查表模板"""
    try:
        # 将Pydantic模型转换为字典，过滤掉None值
        update_data = {k: v for k, v in template_data.model_dump().items() if v is not None}
        
        template = SurveyService.update_template(db, template_id, update_data)
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        return template
    except Exception as e:
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        print(f"更新模板失败: {error_detail}")
        print(f"Traceback: {traceback_str}")
        raise HTTPException(status_code=500, detail=f"更新模板失败: {error_detail}")

@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """删除调查表模板"""
    success = SurveyService.delete_template(db, template_id)
    if not success:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    return {"message": "模板删除成功"}

# 调查表记录相关接口
@router.post("/submit", response_model=SurveySubmitResponse)
async def submit_survey(
    request: SurveySubmitRequest,
    db: Session = Depends(get_db)
):
    """提交调查表并生成法律建议"""
    try:
        result = SurveyService.submit_survey(db, request)
        
        response_data = {
            "record_id": result["record"].id,
            "message": "调查表提交成功，已生成法律建议"
        }
        
        if result["suggestion"]:
            response_data["suggestion"] = result["suggestion"]
            response_data["message"] = "调查表提交成功，已生成详细法律建议"
        
        return SurveySubmitResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交失败: {str(e)}")

@router.get("/records", response_model=SurveyHistoryResponse)
async def get_user_records(
    limit: int = Query(100, ge=1, le=1000, description="每页记录数"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db)
):
    """获取调查记录历史"""
    result = SurveyService.get_user_records(db, limit, offset)
    return SurveyHistoryResponse(**result)

@router.get("/records/{record_id}", response_model=SurveyRecord)
async def get_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """获取特定调查记录"""
    record = SurveyService.get_record_with_suggestions(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    return record

@router.delete("/records/{record_id}")
async def delete_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """删除调查记录"""
    success = SurveyService.delete_record(db, record_id)
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    return {"message": "记录删除成功"}

# 法律建议相关接口
@router.get("/suggestions/{record_id}", response_model=List[LegalSuggestion])
async def get_suggestions(
    record_id: int,
    db: Session = Depends(get_db)
):
    """获取调查记录的法律建议"""
    record = SurveyService.get_record_with_suggestions(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    return record.suggestions

@router.get("/latest-suggestion/{user_id}", response_model=Optional[LegalSuggestion])
async def get_latest_suggestion(
    user_id: str,
    db: Session = Depends(get_db)
):
    """获取用户最新的法律建议"""
    records = SurveyService.get_user_records(db, user_id, limit=1)
    if not records["records"]:
        return None
    
    latest_record = records["records"][0]
    if not latest_record.suggestions:
        return None
    
    # 返回最新的建议
    return latest_record.suggestions[0]