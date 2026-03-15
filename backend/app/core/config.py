from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    PROJECT_NAME: str = "AI 法律咨询系统"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # API配置
    API_V1_STR: str = "/api/v1"
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]
    
    # 数据库配置
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "123456"
    POSTGRES_DATABASE: str = "legal_consultation"
    
    # AI模型配置
    DEFAULT_MODEL_PROVIDER: str = "siliconflow"  # siliconflow, ollama
    EMBEDDING_MODEL_PROVIDER: str = "siliconflow"  # siliconflow, ollama
    
    # SiliconFlow配置
    SILICONFLOW_API_KEY: str = ""
    SILICONFLOW_BASE_URL: str = "https://api.siliconflow.cn/v1"
    SILICONFLOW_MODEL: str = "deepseek-ai/DeepSeek-V3"
    SILICONFLOW_EMBEDDING_MODEL: str = "Qwen/Qwen3-Embedding-8B"
    
    # Ollama配置
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "deepseek-r1:1.5b"
    OLLAMA_EMBEDDING_MODEL: str = "qwen3-embedding:0.6b"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # 聊天配置
    MAX_CHAT_HISTORY: int = 50  # 最大聊天历史记录数
    CHAT_TIMEOUT: int = 30  # 聊天超时时间（秒）
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()