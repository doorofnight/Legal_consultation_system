from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.chat import (
    ChatSession, ChatSessionCreate, ChatSessionUpdate, ChatSessionDetail,
    ChatMessage, ChatRequest, ChatResponse
)
from app.services.chat_service import ChatService

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
@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    db: Session = Depends(get_db)
):
    """发送聊天消息"""
    try:
        response = await ChatService.process_chat_request(db, chat_request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"聊天处理失败: {str(e)}"
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