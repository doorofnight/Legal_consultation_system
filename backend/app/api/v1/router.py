from fastapi import APIRouter
from app.api.v1.endpoints import chat, knowledge, survey

api_router = APIRouter()

# 包含聊天路由
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

# 包含知识库路由
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])

# 包含调查表路由
api_router.include_router(survey.router, prefix="/survey", tags=["survey"])