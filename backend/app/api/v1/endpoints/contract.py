from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
import uuid
import logging
from datetime import datetime

from app.db.session import get_db
from app.models.contract_upload import ContractUpload, ContractDiagnosis
from app.schemas.contract import (
    ContractUploadResponse,
    ContractDiagnosisRequest,
    ContractDiagnosisResponse,
    ContractDiagnosisStatus,
    ContractHistoryResponse,
    ContractUpload as ContractUploadSchema,
    ContractDiagnosis as ContractDiagnosisSchema,
    ContractUploadWithDiagnosis
)
from app.services.contract_service import contract_service, extract_text_from_file_sync, analyze_contract_content_sync, generate_contract_summary_sync

logger = logging.getLogger(__name__)

router = APIRouter()

# 文件上传目录
UPLOAD_DIR = "uploads/contracts"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=ContractUploadResponse)
async def upload_contract(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    上传合同文件
    """
    # 检查文件类型
    allowed_extensions = ['.docx', '.doc', '.txt']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="只支持 .docx, .doc, .txt 格式的文件")
    
    # 检查文件大小 (10MB)
    file_size = 0
    file_content = await file.read()
    file_size = len(file_content)
    await file.seek(0)  # 重置文件指针
    
    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=400, detail="文件大小不能超过 10MB")
    
    # 生成唯一文件名
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 创建数据库记录
    db_upload = ContractUpload(
        filename=file.filename,
        file_path=file_path,
        file_type=file_ext[1:],  # 去掉点号
        file_size=file_size,
        status="uploaded"
    )
    
    db.add(db_upload)
    db.commit()
    db.refresh(db_upload)
    
    # 简单的预分析（这里可以扩展为真正的文档解析）
    pre_analysis = {
        "contract_type": "未知合同类型",
        "total_pages": 1,
        "total_paragraphs": 10,
        "potential_risks_count": 0
    }
    
    # 尝试从文件名推断合同类型
    filename_lower = file.filename.lower()
    if "劳动" in filename_lower:
        pre_analysis["contract_type"] = "劳动合同"
    elif "租赁" in filename_lower:
        pre_analysis["contract_type"] = "租赁合同"
    elif "买卖" in filename_lower or "销售" in filename_lower:
        pre_analysis["contract_type"] = "买卖合同"
    elif "服务" in filename_lower:
        pre_analysis["contract_type"] = "服务合同"
    elif "借款" in filename_lower:
        pre_analysis["contract_type"] = "借款合同"
    
    return ContractUploadResponse(
        upload=db_upload,
        pre_analysis=pre_analysis
    )

@router.post("/diagnose", response_model=ContractDiagnosisResponse)
async def diagnose_contract(
    request: ContractDiagnosisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    诊断合同
    """
    # 检查上传记录是否存在
    upload = db.query(ContractUpload).filter(ContractUpload.id == request.upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="合同上传记录不存在")
    
    # 更新上传状态
    upload.status = "analyzing"
    db.commit()
    
    # 创建诊断记录，使用前端传递的合同类型
    db_diagnosis = ContractDiagnosis(
        upload_id=request.upload_id,
        contract_type=request.contract_type,  # 使用前端传递的合同类型
        perspective=request.perspective,
        focus_areas=request.focus_areas,
        model_used=request.model_provider
    )
    
    db.add(db_diagnosis)
    db.commit()
    db.refresh(db_diagnosis)
    
    # 在后台启动分析任务
    background_tasks.add_task(
        analyze_contract_task,
        upload.id,
        db_diagnosis.id,
        request.model_provider,
        db
    )
    
    return ContractDiagnosisResponse(
        diagnosis=db_diagnosis,
        analysis_time=0,
        model_used=request.model_provider
    )

@router.get("/status/{upload_id}", response_model=ContractDiagnosisStatus)
async def get_diagnosis_status(
    upload_id: int,
    db: Session = Depends(get_db)
):
    """
    获取合同诊断状态
    """
    upload = db.query(ContractUpload).filter(ContractUpload.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="合同上传记录不存在")
    
    # 根据状态返回进度
    status_map = {
        "uploaded": 10,
        "parsing": 30,
        "analyzing": 70,
        "completed": 100,
        "failed": 0
    }
    
    progress = status_map.get(upload.status, 0)
    message = get_status_message(upload.status)
    
    return ContractDiagnosisStatus(
        upload_id=upload_id,
        status=upload.status,
        progress=progress,
        message=message
    )

@router.get("/history", response_model=ContractHistoryResponse)
async def get_contract_history(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    获取合同上传历史
    """
    uploads = db.query(ContractUpload).order_by(ContractUpload.created_at.desc()).offset(offset).limit(limit).all()
    total = db.query(ContractUpload).count()
    
    # 为每个上传记录获取对应的诊断结果
    uploads_with_diagnoses = []
    for upload in uploads:
        # 获取该上传记录的所有诊断结果
        diagnoses = db.query(ContractDiagnosis).filter(ContractDiagnosis.upload_id == upload.id).all()
        
        # 创建包含诊断记录的上传记录对象
        # 使用Pydantic的dict()方法获取模型字典
        upload_data = {
            'id': upload.id,
            'filename': upload.filename,
            'file_path': upload.file_path,
            'file_type': upload.file_type,
            'file_size': upload.file_size,
            'status': upload.status,
            'contract_type': upload.contract_type,
            'user_id': upload.user_id,
            'created_at': upload.created_at,
            'updated_at': upload.updated_at,
            'diagnoses': diagnoses
        }
        uploads_with_diagnoses.append(ContractUploadWithDiagnosis(**upload_data))
        
    return ContractHistoryResponse(
        uploads=uploads_with_diagnoses,
        total=total
    )

@router.get("/diagnosis/{diagnosis_id}", response_model=ContractDiagnosisSchema)
async def get_contract_diagnosis(
    diagnosis_id: int,
    db: Session = Depends(get_db)
):
    """
    获取特定合同诊断结果
    """
    diagnosis = db.query(ContractDiagnosis).filter(ContractDiagnosis.id == diagnosis_id).first()
    if not diagnosis:
        raise HTTPException(status_code=404, detail="诊断结果不存在")
    
    return diagnosis

@router.get("/upload/{upload_id}", response_model=ContractUploadSchema)
async def get_contract_upload(
    upload_id: int,
    db: Session = Depends(get_db)
):
    """
    获取特定合同上传记录
    """
    upload = db.query(ContractUpload).filter(ContractUpload.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="上传记录不存在")
    
    return upload

@router.delete("/upload/{upload_id}")
async def delete_contract_upload(
    upload_id: int,
    db: Session = Depends(get_db)
):
    """
    删除合同上传记录
    """
    upload = db.query(ContractUpload).filter(ContractUpload.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="上传记录不存在")
    
    # 删除文件
    if os.path.exists(upload.file_path):
        os.remove(upload.file_path)
    
    # 删除数据库记录（级联删除诊断记录）
    db.delete(upload)
    db.commit()
    
    return {"message": "删除成功"}

@router.get("/types")
async def get_supported_contract_types():
    """
    获取支持的合同类型
    """
    return [
        "买卖合同",
        "租赁合同",
        "劳动合同",
        "服务合同",
        "技术合同",
        "借款合同",
        "担保合同",
        "委托合同",
        "合伙协议",
        "其他合同"
    ]

@router.get("/risk-categories")
async def get_risk_categories():
    """
    获取风险类型分类
    """
    return {
        "categories": [
            "权利义务不对等",
            "违约责任过重",
            "争议解决条款不合理",
            "保密条款缺失",
            "知识产权归属不明确",
            "付款条款风险",
            "解除合同条件苛刻",
            "法律适用问题",
            "格式条款问题",
            "其他风险"
        ],
        "risk_levels": ["high", "medium", "low"]
    }

# 辅助函数
def get_status_message(status: str) -> str:
    messages = {
        "uploaded": "文件已上传，等待分析",
        "parsing": "正在解析合同文本",
        "analyzing": "正在分析合同风险",
        "completed": "分析完成",
        "failed": "分析失败"
    }
    return messages.get(status, "未知状态")

def analyze_contract_task(upload_id: int, diagnosis_id: int, model_provider: str, db: Session):
    """
    后台分析合同任务 - 使用真正的合同分析服务
    """
    try:
        # 获取上传记录
        upload = db.query(ContractUpload).filter(ContractUpload.id == upload_id).first()
        if not upload:
            logger.error(f"上传记录不存在: {upload_id}")
            return
        
        # 更新状态为解析中
        upload.status = "parsing"
        db.commit()
        
        # 提取合同文本（使用同步版本）
        contract_text = ""
        try:
            contract_text = extract_text_from_file_sync(upload.file_path)
            if not contract_text or len(contract_text.strip()) < 10:
                raise ValueError("合同文本提取失败或内容过短")
        except Exception as e:
            logger.error(f"合同文本提取失败: {e}")
            upload.status = "failed"
            db.commit()
            return
        
        # 更新状态为分析中
        upload.status = "analyzing"
        db.commit()
        
        # 获取诊断记录
        diagnosis = db.query(ContractDiagnosis).filter(ContractDiagnosis.id == diagnosis_id).first()
        if not diagnosis:
            logger.error(f"诊断记录不存在: {diagnosis_id}")
            upload.status = "failed"
            db.commit()
            return
        
        # 使用合同服务进行真正的AI分析（使用同步版本）
        import json
        from datetime import datetime
        
        try:
            # 分析合同内容，传递用户选择的合同类型
            analysis_result = analyze_contract_content_sync(
                contract_text=contract_text,
                perspective=diagnosis.perspective or "neutral",
                focus_areas=diagnosis.focus_areas or ["权利义务", "违约责任", "争议解决"],
                model_provider=model_provider,
                contract_type=diagnosis.contract_type  # 传递用户选择的合同类型
            )
            
            # 生成合同摘要
            summary_info = generate_contract_summary_sync(contract_text)
            
            # 更新诊断结果
            # 优先使用诊断记录中已有的合同类型（来自前端选择），如果为空则使用AI分析结果
            if not diagnosis.contract_type or diagnosis.contract_type == "未知合同类型":
                diagnosis.contract_type = analysis_result.get("contract_type", "未知合同类型")
            diagnosis.summary = analysis_result.get("summary", "合同分析完成")
            diagnosis.risks = analysis_result.get("risks", [])
            diagnosis.suggestions = analysis_result.get("suggestions", "请查看详细分析")
            
            # 计算分析时间
            start_time = diagnosis.created_at.timestamp() if diagnosis.created_at else datetime.now().timestamp()
            analysis_time = int(datetime.now().timestamp() - start_time)
            diagnosis.analysis_time = analysis_time
            diagnosis.model_used = model_provider
            
            # 更新上传状态和合同类型
            upload.status = "completed"
            upload.contract_type = diagnosis.contract_type
            
            db.commit()
            
            logger.info(f"合同分析完成: upload_id={upload_id}, diagnosis_id={diagnosis_id}, 耗时={analysis_time}秒")
            
        except Exception as e:
            logger.error(f"合同AI分析失败: {e}")
            # 使用默认分析结果
            from app.services.contract_service import contract_service
            analysis_result = contract_service._get_default_analysis(contract_text)
            
            diagnosis.contract_type = analysis_result.get("contract_type", "未知合同类型")
            diagnosis.summary = analysis_result.get("summary", "分析失败，使用默认结果")
            diagnosis.risks = analysis_result.get("risks", [])
            diagnosis.suggestions = analysis_result.get("suggestions", "请专业律师审查")
            diagnosis.analysis_time = 0
            diagnosis.model_used = model_provider
            
            upload.status = "completed"  # 即使失败也标记为完成，但有默认结果
            upload.contract_type = diagnosis.contract_type
            
            db.commit()
        
    except Exception as e:
        # 更新状态为失败
        logger.error(f"合同分析任务失败: {e}")
        upload = db.query(ContractUpload).filter(ContractUpload.id == upload_id).first()
        if upload:
            upload.status = "failed"
            db.commit()