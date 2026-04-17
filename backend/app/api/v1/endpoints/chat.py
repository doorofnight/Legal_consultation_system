from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.db.session import get_db
from app.schemas.chat import (
    ChatSession, ChatSessionCreate, ChatSessionUpdate, ChatSessionDetail,
    ChatMessage, ChatRequest, ChatResponse
)
from app.services.chat_service import ChatService
from app.services.ai_service import ai_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# 聊天会话相关接口
@router.get("/sessions", response_model=List[ChatSession])
async def get_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取聊天会话列表"""
    sessions = ChatService.get_sessions(db, skip=skip, limit=limit)
    return sessions

@router.post("/sessions", response_model=ChatSession, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: ChatSessionCreate,
    db: Session = Depends(get_db)
):
    """创建聊天会话"""
    session = ChatService.create_session(db, session_data)
    return session

@router.get("/sessions/{session_id}", response_model=ChatSessionDetail)
async def get_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """获取聊天会话详情"""
    session = ChatService.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    # 获取消息
    messages = ChatService.get_messages(db, session_id)
    
    session_detail = ChatSessionDetail(
        id=session.id,
        title=session.title,
        model_provider=session.model_provider,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=messages
    )
    
    return session_detail

@router.put("/sessions/{session_id}", response_model=ChatSession)
async def update_session(
    session_id: int,
    update_data: ChatSessionUpdate,
    db: Session = Depends(get_db)
):
    """更新聊天会话"""
    session = ChatService.update_session(db, session_id, update_data.dict(exclude_unset=True))
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    return session

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """删除聊天会话"""
    success = ChatService.delete_session(db, session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )

# 聊天消息相关接口
@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessage])
async def get_session_messages(
    session_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取会话消息"""
    # 检查会话是否存在
    session = ChatService.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    messages = ChatService.get_messages(db, session_id, skip=skip, limit=limit)
    return messages

# 聊天接口
@router.post("/", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    db: Session = Depends(get_db)
):
    """发送聊天消息（非流式）"""
    try:
        response = await ChatService.process_chat_request(db, chat_request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"聊天处理失败: {str(e)}"
        )

# 流式聊天接口
@router.post("/stream")
async def chat_stream(
    chat_request: ChatRequest,
    db: Session = Depends(get_db)
):
    """流式发送聊天消息
    
    返回Server-Sent Events (SSE)格式的流式响应
    """
    from fastapi.responses import StreamingResponse
    import json
    
    async def event_stream():
        try:
            # 获取或创建会话
            if chat_request.session_id:
                session = ChatService.get_session(db, chat_request.session_id)
                if not session:
                    # 如果会话不存在，创建新会话
                    from app.schemas.chat import ChatSessionCreate
                    session_data = ChatSessionCreate(
                        title="新对话",
                        model_provider=chat_request.model_provider or "siliconflow"
                    )
                    session = ChatService.create_session(db, session_data)
            else:
                # 创建新会话
                from app.schemas.chat import ChatSessionCreate
                session_data = ChatSessionCreate(
                    title=chat_request.message[:50] + "..." if len(chat_request.message) > 50 else chat_request.message,
                    model_provider=chat_request.model_provider or "siliconflow"
                )
                session = ChatService.create_session(db, session_data)
            
            # 保存用户消息
            from app.schemas.chat import ChatMessageCreate
            user_message = ChatMessageCreate(
                session_id=session.id,
                role="user",
                content=chat_request.message
            )
            user_msg = ChatService.create_message(db, user_message)
            
            # 获取历史消息
            history_messages = ChatService.get_session_messages(db, session.id)
            
            # 获取最新的调查记录和触发变更的字段
            survey_record = None
            trigger_changes = None
            
            try:
                from sqlalchemy import desc
                from app.models.survey_record import SurveyRecord
                from app.models.legal_suggestion import LegalSuggestion
                
                # 获取最新的调查记录（不依赖user_id）
                latest_record = db.query(SurveyRecord).order_by(
                    desc(SurveyRecord.created_at)
                ).first()
                
                if latest_record:
                    # 构建调查记录字典
                    survey_record = {
                        "id": latest_record.id,
                        "user_id": latest_record.user_id,
                        "template_id": latest_record.template_id,
                        "answers": latest_record.answers or {},
                        "status": latest_record.status,
                        "created_at": latest_record.created_at.isoformat() if latest_record.created_at else None,
                        "suggestions": []
                    }
                    
                    # 获取关联的法律建议
                    suggestions = db.query(LegalSuggestion).filter(
                        LegalSuggestion.record_id == latest_record.id
                    ).order_by(desc(LegalSuggestion.created_at)).all()
                    
                    for suggestion in suggestions:
                        survey_record["suggestions"].append({
                            "id": suggestion.id,
                            "record_id": suggestion.record_id,
                            "trigger_changes": suggestion.trigger_changes,
                            "suggestion": suggestion.suggestion,
                            "analysis_type": suggestion.analysis_type,
                            "confidence_score": suggestion.confidence_score,
                            "created_at": suggestion.created_at.isoformat() if suggestion.created_at else None
                        })
                    
                    # 获取最新的触发变更字段
                    if suggestions and len(suggestions) > 0:
                        latest_suggestion = suggestions[0]
                        trigger_changes = latest_suggestion.trigger_changes
                    
            except Exception as e:
                logger.error(f"获取调查记录失败: {e}")
            
            # 发送开始事件
            yield f"data: {json.dumps({'event': 'start', 'session_id': session.id, 'message_id': 'streaming'})}\n\n"
            
            full_response = ""
            async for chunk in ai_service.generate_chat_completion_stream(
                messages=history_messages,
                model_provider=session.model_provider,
                use_knowledge_base=True,
                survey_record=survey_record,
                trigger_changes=trigger_changes,
                max_history_messages=settings.AI_SIMPLE_MAX_HISTORY
            ):
                # 解析chunk中的内容
                if chunk.startswith("data: "):
                    chunk_data = chunk[6:]  # 移除"data: "前缀
                    try:
                        data = json.loads(chunk_data)
                        if "content" in data:
                            content = data["content"]
                            full_response += content
                            # 转发内容给客户端
                            yield f"data: {json.dumps({'content': content})}\n\n"
                        elif "error" in data:
                            yield f"data: {json.dumps({'error': data['error']})}\n\n"
                            break
                    except json.JSONDecodeError:
                        continue
            
            # 保存AI回复到数据库
            ai_message = ChatMessageCreate(
                session_id=session.id,
                role="assistant",
                content=full_response
            )
            ai_msg = ChatService.create_message(db, ai_message)
            
            # 更新会话标题（如果是新会话且第一条消息）
            if len(history_messages) == 1:  # 只有用户消息
                title = chat_request.message[:50] + "..." if len(chat_request.message) > 50 else chat_request.message
                ChatService.update_session(db, session.id, {"title": title})
            
            # 发送完成事件
            yield f"data: {json.dumps({'event': 'complete', 'message_id': ai_msg.id, 'full_response': full_response})}\n\n"
            
        except Exception as e:
            logger.error(f"流式聊天处理失败: {e}")
            yield f"data: {json.dumps({'error': f'流式聊天处理失败: {str(e)}'})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用Nginx缓冲
        }
    )

# 健康检查
@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "chat_api"}

# 配置接口
@router.get("/config")
async def get_config():
    """获取应用配置"""
    from app.core.config import settings
    return {
        "model_provider": settings.DEFAULT_MODEL_PROVIDER,
        "embedding_model_provider": settings.EMBEDDING_MODEL_PROVIDER,
        "available_providers": ["siliconflow", "ollama"]
    }