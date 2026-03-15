import httpx
import logging
import asyncio
from typing import Optional, List, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    """AI服务，支持SiliconFlow和Ollama"""
    
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
                timeout=60.0,  # 增加超时时间到60秒
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
        return self.siliconflow_client
    
    async def get_ollama_client(self):
        """获取Ollama客户端"""
        if self.ollama_client is None:
            self.ollama_client = httpx.AsyncClient(
                base_url=settings.OLLAMA_BASE_URL,
                timeout=60.0,  # 增加超时时间到60秒
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
        return self.ollama_client
    
    async def generate_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model_provider: str = "siliconflow",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """生成聊天完成"""
        try:
            if model_provider == "siliconflow":
                return await self._generate_siliconflow(messages, temperature, max_tokens)
            elif model_provider == "ollama":
                return await self._generate_ollama(messages, temperature, max_tokens)
            else:
                raise ValueError(f"不支持的模型提供商: {model_provider}")
        except Exception as e:
            logger.error(f"AI生成失败: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"详细错误追踪: {traceback.format_exc()}")
            return f"抱歉，AI服务暂时不可用。错误: {type(e).__name__}: {str(e)}"
    
    async def _generate_siliconflow(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> str:
        """使用SiliconFlow生成"""
        client = await self.get_siliconflow_client()
        
        # 构建法律咨询专用提示词
        system_prompt = """你是一个专业的法律AI助手，专门为中国企业提供法律咨询服务。
        请根据用户的问题提供准确、专业的法律建议。
        回答时请：
        1. 引用相关法律条文（如《民法典》、《劳动合同法》等）
        2. 提供实际案例分析
        3. 给出具体的操作建议
        4. 提醒潜在的法律风险
        5. 使用清晰的结构（如分点说明）
        
        如果问题涉及具体案件，请说明需要更多信息才能给出准确建议。
        所有回答仅供参考，不构成正式法律意见。"""
        
        # 添加系统提示
        formatted_messages = [{"role": "system", "content": system_prompt}] + messages
        
        payload = {
            "model": settings.SILICONFLOW_MODEL,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        # 重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await client.post("/chat/completions", json=payload)
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
            except (httpx.ReadTimeout, httpx.ConnectTimeout) as e:
                logger.warning(f"SiliconFlow请求超时 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # 指数退避
                else:
                    raise
            except httpx.HTTPStatusError as e:
                logger.error(f"SiliconFlow HTTP错误: {e.response.status_code} - {e.response.text}")
                raise
    
    async def _generate_ollama(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float,
        max_tokens: int
    ) -> str:
        """使用Ollama生成"""
        client = await self.get_ollama_client()
        
        # 构建提示词
        system_prompt = """你是一个专业的法律AI助手，专门为中国企业提供法律咨询服务。
        请根据用户的问题提供准确、专业的法律建议。"""
        
        # 合并消息
        prompt = system_prompt + "\n\n"
        for msg in messages:
            prompt += f"{msg['role']}: {msg['content']}\n"
        prompt += "assistant: "
        
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        response = await client.post("/api/generate", json=payload)
        response.raise_for_status()
        result = response.json()
        
        return result["response"]
    
    async def close(self):
        """关闭客户端连接"""
        if self.siliconflow_client:
            await self.siliconflow_client.aclose()
        if self.ollama_client:
            await self.ollama_client.aclose()

# 全局AI服务实例
ai_service = AIService()