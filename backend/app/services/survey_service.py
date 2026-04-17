from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
import json

from app.models.survey_template import SurveyTemplate
from app.models.survey_record import SurveyRecord
from app.models.legal_suggestion import LegalSuggestion
from app.schemas.survey import (
    SurveyTemplateCreate, SurveyRecordCreate, LegalSuggestionCreate,
    SurveySubmitRequest, SurveyAnalysisRequest
)
from app.services.ai_service import analyze_survey_changes

class SurveyService:
    """调查表服务"""
    
    @staticmethod
    def create_template(db: Session, template_data: SurveyTemplateCreate) -> SurveyTemplate:
        """创建调查表模板"""
        db_template = SurveyTemplate(**template_data.model_dump())
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        return db_template
    
    @staticmethod
    def get_template(db: Session, template_id: int) -> Optional[SurveyTemplate]:
        """获取调查表模板"""
        return db.query(SurveyTemplate).filter(SurveyTemplate.id == template_id).first()
    
    @staticmethod
    def get_active_templates(db: Session) -> List[SurveyTemplate]:
        """获取所有启用的模板"""
        return db.query(SurveyTemplate).filter(SurveyTemplate.is_active == 1).all()
    
    @staticmethod
    def update_template(db: Session, template_id: int, template_data: dict) -> Optional[SurveyTemplate]:
        """更新调查表模板"""
        template = db.query(SurveyTemplate).filter(SurveyTemplate.id == template_id).first()
        if not template:
            return None
        
        # 更新字段
        for key, value in template_data.items():
            if value is not None and hasattr(template, key):
                setattr(template, key, value)
        
        db.commit()
        db.refresh(template)
        return template

    @staticmethod
    def delete_template(db: Session, template_id: int) -> bool:
        """删除调查表模板"""
        template = db.query(SurveyTemplate).filter(SurveyTemplate.id == template_id).first()
        if not template:
            return False
        
        # 先删除所有关联的调查记录（这会级联删除法律建议）
        from app.models.survey_record import SurveyRecord
        from app.models.legal_suggestion import LegalSuggestion
        
        # 查找所有关联的调查记录
        related_records = db.query(SurveyRecord).filter(
            SurveyRecord.template_id == template_id
        ).all()
        
        # 删除每个记录（由于LegalSuggestion设置了ondelete="CASCADE"，会自动删除关联的建议）
        for record in related_records:
            db.delete(record)
        
        # 删除模板
        db.delete(template)
        db.commit()
        return True
    
    @staticmethod
    def create_record(db: Session, record_data: SurveyRecordCreate) -> SurveyRecord:
        """创建调查记录"""
        db_record = SurveyRecord(**record_data.model_dump())
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    
    @staticmethod
    def submit_survey(db: Session, request: SurveySubmitRequest) -> Dict[str, Any]:
        """提交调查表并生成法律建议"""
        # 1. 创建调查记录
        record_data = SurveyRecordCreate(
            template_id=request.template_id,
            user_id=request.user_id,
            answers=request.answers,
            status="submitted"
        )
        record = SurveyService.create_record(db, record_data)
        
        # 2. 分析变更并生成法律建议
        suggestion = None
        try:
            # 获取之前的记录（如果有）
            previous_record = db.query(SurveyRecord).filter(
                SurveyRecord.user_id == request.user_id,
                SurveyRecord.template_id == request.template_id,
                SurveyRecord.id != record.id
            ).order_by(desc(SurveyRecord.created_at)).first()
            
            previous_answers = previous_record.answers if previous_record else {}
            
            # 调用AI服务分析变更
            analysis_result = analyze_survey_changes(
                current_answers=request.answers,
                previous_answers=previous_answers,
                template_id=request.template_id
            )
            
            # 创建法律建议记录
            if analysis_result:
                suggestion_data = LegalSuggestionCreate(
                    record_id=record.id,
                    trigger_changes=analysis_result.get("trigger_changes"),
                    suggestion=analysis_result.get("suggestion", ""),
                    analysis_type=analysis_result.get("analysis_type", "general"),
                    confidence_score=analysis_result.get("confidence_score", 80)
                )
                suggestion = SurveyService.create_suggestion(db, suggestion_data)
                
                # 更新记录状态
                record.status = "analyzed"
                db.commit()
                db.refresh(record)
        
        except Exception as e:
            # 如果AI分析失败，仍然保存记录
            print(f"AI分析失败: {e}")
        
        return {
            "record": record,
            "suggestion": suggestion
        }
    
    @staticmethod
    def create_suggestion(db: Session, suggestion_data: LegalSuggestionCreate) -> LegalSuggestion:
        """创建法律建议"""
        db_suggestion = LegalSuggestion(**suggestion_data.model_dump())
        db.add(db_suggestion)
        db.commit()
        db.refresh(db_suggestion)
        return db_suggestion
    
    @staticmethod
    def get_user_records(db: Session, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """获取调查记录"""
        from sqlalchemy.orm import joinedload
        
        query = db.query(SurveyRecord)
        
        total = query.count()
        
        # 使用joinedload加载关联的suggestions和template
        records = query.options(joinedload(SurveyRecord.suggestions), joinedload(SurveyRecord.template))\
                      .order_by(desc(SurveyRecord.created_at))\
                      .offset(offset)\
                      .limit(limit)\
                      .all()
        
        return {
            "records": records,
            "total": total
        }
    
    @staticmethod
    def get_record_with_suggestions(db: Session, record_id: int) -> Optional[SurveyRecord]:
        """获取调查记录及其法律建议"""
        return db.query(SurveyRecord).filter(SurveyRecord.id == record_id).first()
    
    @staticmethod
    def delete_record(db: Session, record_id: int) -> bool:
        """删除调查记录"""
        record = db.query(SurveyRecord).filter(SurveyRecord.id == record_id).first()
        if not record:
            return False
        
        db.delete(record)
        db.commit()
        return True