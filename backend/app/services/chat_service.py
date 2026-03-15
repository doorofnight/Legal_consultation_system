from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
import logging

from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.schemas.chat import ChatRequest, ChatResponse, ChatSessionCreate, ChatMessageCreate
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)

class ChatService:
    """聊天服务"""
    
    @staticmethod
    def create_session(db: Session, session_data: ChatSessionCreate) -> ChatSession:
        """创建聊天会话"""
        db_session = ChatSession(**session_data.dict())
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session
    
    @staticmethod
    def get_session(db: Session, session_id: int) -> Optional[ChatSession]:
        """获取聊天会话"""
        return db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    @staticmethod
    def get_sessions(db: Session, skip: int = 0, limit: int = 100) -> List[ChatSession]:
        """获取聊天会话列表"""
        return db.query(ChatSession).order_by(desc(ChatSession.updated_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_session(db: Session, session_id: int, update_data: Dict[str, Any]) -> Optional[ChatSession]:
        """更新聊天会话"""
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            return None
        
        for key, value in update_data.items():
            if value is not None:
                setattr(session, key, value)
        
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def delete_session(db: Session, session_id: int) -> bool:
        """删除聊天会话"""
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            return False
        
        db.delete(session)
        db.commit()
        return True
    
    @staticmethod
    def create_message(db: Session, message_data: ChatMessageCreate) -> ChatMessage:
        """创建聊天消息"""
        db_message = ChatMessage(**message_data.dict())
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    
    @staticmethod
    def get_messages(db: Session, session_id: int, skip: int = 0, limit: int = 100) -> List[ChatMessage]:
        """获取聊天消息"""
        return db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_session_messages(db: Session, session_id: int, limit: int = 50) -> List[Dict[str, str]]:
        """获取会话消息用于AI生成"""
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at).limit(limit).all()
        
        # 转换为AI需要的格式
        ai_messages = []
        for msg in messages:
            ai_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return ai_messages
    
    @staticmethod
    async def process_chat_request(db: Session, chat_request: ChatRequest) -> ChatResponse:
        """处理聊天请求"""
        # 获取或创建会话
        if chat_request.session_id:
            session = ChatService.get_session(db, chat_request.session_id)
            if not session:
                # 如果会话不存在，创建新会话
                session_data = ChatSessionCreate(
                    title="新对话",
                    model_provider=chat_request.model_provider or "siliconflow"
                )
                session = ChatService.create_session(db, session_data)
        else:
            # 创建新会话
            session_data = ChatSessionCreate(
                title=chat_request.message[:50] + "..." if len(chat_request.message) > 50 else chat_request.message,
                model_provider=chat_request.model_provider or "siliconflow"
            )
            session = ChatService.create_session(db, session_data)
        
        # 保存用户消息
        user_message = ChatMessageCreate(
            session_id=session.id,
            role="user",
            content=chat_request.message
        )
        user_msg = ChatService.create_message(db, user_message)
        
        # 获取历史消息
        history_messages = ChatService.get_session_messages(db, session.id)
        
        # 调用AI生成回复
        ai_response = await ai_service.generate_chat_completion(
            messages=history_messages,
            model_provider=session.model_provider
        )
        
        # 保存AI回复
        ai_message = ChatMessageCreate(
            session_id=session.id,
            role="assistant",
            content=ai_response
        )
        ai_msg = ChatService.create_message(db, ai_message)
        
        # 更新会话标题（如果是新会话且第一条消息）
        if len(history_messages) == 1:  # 只有用户消息
            title = chat_request.message[:50] + "..." if len(chat_request.message) > 50 else chat_request.message
            ChatService.update_session(db, session.id, {"title": title})
        
        return ChatResponse(
            session_id=session.id,
            message_id=ai_msg.id,
            content=ai_response,
            created_at=ai_msg.created_at
        )