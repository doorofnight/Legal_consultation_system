import httpx
import logging
import asyncio
from typing import List, Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """嵌入服务，支持SiliconFlow和Ollama"""
    
    def __init__(self):
        self.siliconflow_client = None
        self.ollama_client = None
        
    async def get_siliconflow_client(self):
        """获取SiliconFlow客户端"""
        if self.siliconflow_client is None:
            self.siliconflow_client = httpx.AsyncClient(
                base_url=settings.SILICONFLOW_BASE_URL,
                headers={
                    "Authorization": f"Bearer {settings.SILICONFLOW_API_KEY}",
                    "Content-Type": "application/json"
                },
                timeout=settings.HTTP_CLIENT_TIMEOUT,
                limits=httpx.Limits(
                    max_keepalive_connections=settings.HTTP_MAX_KEEPALIVE_CONNECTIONS,
                    max_connections=settings.HTTP_MAX_CONNECTIONS
                )
            )
        return self.siliconflow_client
    
    async def get_ollama_client(self):
        """获取Ollama客户端"""
        if self.ollama_client is None:
            self.ollama_client = httpx.AsyncClient(
                base_url=settings.OLLAMA_BASE_URL,
                timeout=settings.HTTP_CLIENT_TIMEOUT,
                limits=httpx.Limits(
                    max_keepalive_connections=settings.HTTP_MAX_KEEPALIVE_CONNECTIONS,
                    max_connections=settings.HTTP_MAX_CONNECTIONS
                )
            )
        return self.ollama_client
    
    async def generate_embeddings(
        self,
        texts: List[str],
        model_provider: str = None,
        batch_size: int = 10
    ) -> List[List[float]]:
        """生成文本嵌入向量"""
        if model_provider is None:
            model_provider = settings.EMBEDDING_MODEL_PROVIDER
            
        try:
            if model_provider == "siliconflow":
                return await self._generate_siliconflow_embeddings(texts, batch_size)
            elif model_provider == "ollama":
                return await self._generate_ollama_embeddings(texts, batch_size)
            else:
                raise ValueError(f"不支持的嵌入模型提供商: {model_provider}")
        except Exception as e:
            logger.error(f"嵌入生成失败: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"详细错误追踪: {traceback.format_exc()}")
            raise
    
    async def _generate_siliconflow_embeddings(
        self,
        texts: List[str],
        batch_size: int
    ) -> List[List[float]]:
        """使用SiliconFlow生成嵌入"""
        client = await self.get_siliconflow_client()
        
        all_embeddings = []
        
        # 分批处理以避免请求过大
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            payload = {
                "model": settings.SILICONFLOW_EMBEDDING_MODEL,
                "input": batch_texts,
                "encoding_format": "float"
            }
            
            # 重试机制
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = await client.post("/embeddings", json=payload)
                    response.raise_for_status()
                    result = response.json()
                    
                    # 提取嵌入向量
                    batch_embeddings = [item["embedding"] for item in result["data"]]
                    all_embeddings.extend(batch_embeddings)
                    break
                    
                except (httpx.ReadTimeout, httpx.ConnectTimeout) as e:
                    logger.warning(f"SiliconFlow嵌入请求超时 (尝试 {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # 指数退避
                    else:
                        raise
                except httpx.HTTPStatusError as e:
                    logger.error(f"SiliconFlow HTTP错误: {e.response.status_code} - {e.response.text}")
                    raise
        
        return all_embeddings
    
    async def _generate_ollama_embeddings(
        self,
        texts: List[str],
        batch_size: int
    ) -> List[List[float]]:
        """使用Ollama生成嵌入"""
        client = await self.get_ollama_client()
        
        all_embeddings = []
        
        # Ollama一次只能处理一个文本
        for text in texts:
            payload = {
                "model": settings.OLLAMA_EMBEDDING_MODEL,
                "prompt": text
            }
            
            try:
                response = await client.post("/api/embeddings", json=payload)
                response.raise_for_status()
                result = response.json()
                
                # 提取嵌入向量
                if "embedding" in result:
                    all_embeddings.append(result["embedding"])
                else:
                    logger.error(f"Ollama响应中没有嵌入向量: {result}")
                    raise ValueError("Ollama响应中没有嵌入向量")
                    
            except Exception as e:
                logger.error(f"Ollama嵌入生成失败: {e}")
                raise
        
        return all_embeddings
    
    async def close(self):
        """关闭客户端连接"""
        if self.siliconflow_client:
            await self.siliconflow_client.aclose()
        if self.ollama_client:
            await self.ollama_client.aclose()

# 全局嵌入服务实例
embedding_service = EmbeddingService()