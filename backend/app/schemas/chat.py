from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

# 聊天消息基础模型
class ChatMessageBase(BaseModel):
    role: str = Field(..., description="消息角色: user, assistant, system")
    content: str = Field(..., description="消息内容")

class ChatMessageCreate(ChatMessageBase):
    session_id: int = Field(..., description="会话ID")

class ChatMessage(ChatMessageBase):
    id: int
    session_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# 聊天会话基础模型
class ChatSessionBase(BaseModel):
    title: str = Field("新对话", description="会话标题")
    model_provider: str = Field("siliconflow", description="模型提供商: siliconflow, ollama")
    
    model_config = ConfigDict(protected_namespaces=())

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionUpdate(BaseModel):
    title: Optional[str] = None
    model_provider: Optional[str] = None
    
    model_config = ConfigDict(protected_namespaces=())

class ChatSession(ChatSessionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    message_count: Optional[int] = Field(None, description="会话中的消息数量")
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

# 聊天会话详情（包含消息）
class ChatSessionDetail(ChatSession):
    messages: List[ChatMessage] = []

# 聊天请求模型
class ChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")
    session_id: Optional[int] = Field(None, description="会话ID，为空则创建新会话")
    model_provider: Optional[str] = Field("siliconflow", description="模型提供商")
    user_id: Optional[int] = Field(None, description="用户ID，用于获取企业调查信息")
    
    model_config = ConfigDict(protected_namespaces=())

# 聊天响应模型
class ChatResponse(BaseModel):
    session_id: int = Field(..., description="会话ID")
    message_id: int = Field(..., description="消息ID")
    content: str = Field(..., description="AI回复内容")
    created_at: datetime = Field(..., description="创建时间")
    
    model_config = ConfigDict(protected_namespaces=())