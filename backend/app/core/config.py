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
    AI_SIMPLE_MODE: bool = True  # AI简化模式：True=简化模式，False=完整模式
    
    # AI服务配置
    AI_USE_KNOWLEDGE_BASE: bool = True  # 是否使用知识库增强
    AI_DEFAULT_TEMPERATURE: float = 0.7  # 默认温度参数
    AI_DEFAULT_MAX_TOKENS: int = 2000  # 默认最大token数
    AI_LEGAL_SUGGESTION_TEMPERATURE: float = 0.3  # 法律建议生成的温度
    
    # 知识库检索配置
    KB_SIMPLE_RESULTS: int = 2  # 简化模式检索结果数
    KB_FULL_RESULTS: int = 3  # 完整模式检索结果数
    KB_LEGAL_SUGGESTION_RESULTS: int = 3  # 法律建议生成检索结果数
    KB_SIMPLE_TIMEOUT: float = 5.0  # 简化模式检索超时（秒）
    KB_LEGAL_SUGGESTION_TIMEOUT: float = 10.0  # 法律建议生成检索超时（秒）
    
    # HTTP客户端配置
    HTTP_CLIENT_TIMEOUT: float = 60.0  # HTTP客户端超时（秒）
    HTTP_MAX_KEEPALIVE_CONNECTIONS: int = 5  # 最大保持连接数
    HTTP_MAX_CONNECTIONS: int = 10  # 最大连接数
    
    # 模型请求超时配置
    SILICONFLOW_REQUEST_TIMEOUT: float = 30.0  # SiliconFlow请求超时（秒）
    SILICONFLOW_RETRY_TIMEOUT: float = 45.0  # SiliconFlow重试超时（秒）
    OLLAMA_REQUEST_TIMEOUT: float = 20.0  # Ollama请求超时（秒）
    
    # 对话历史配置
    AI_MAX_HISTORY_MESSAGES: int = 5  # 默认最大历史消息数
    AI_SIMPLE_MAX_HISTORY: int = 3  # 简化模式最大对话轮数
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()