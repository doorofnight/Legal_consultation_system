import httpx
import logging
import asyncio
import json
from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.services.knowledge_service import knowledge_service

logger = logging.getLogger(__name__)

class AIService:
    """AI服务，支持SiliconFlow和Ollama，集成知识库"""
    
    def __init__(self):
        self.siliconflow_client = None
        self.ollama_client = None
        self.use_knowledge_base = settings.AI_USE_KNOWLEDGE_BASE  # 是否使用知识库增强
        self.simple_mode = settings.AI_SIMPLE_MODE  # 模式设置
        
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
    
    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model_provider: str = "siliconflow",
        temperature: float = settings.AI_DEFAULT_TEMPERATURE,
        max_tokens: int = settings.AI_DEFAULT_MAX_TOKENS,
        use_knowledge_base: bool = True,
        additional_context: str = "",
        survey_record: Optional[Dict[str, Any]] = None,
        trigger_changes: Optional[Dict[str, Any]] = None,
        max_history_messages: int = settings.AI_MAX_HISTORY_MESSAGES
    ) -> str:
        """生成聊天完成，整合所有上下文：
        1. 语义向量（向量检索获取Top-K相关文本片段）
        2. 调查记录和修改字段（结构化提取用户画像）
        3. 历史文本（截断/摘要，最近几轮对话）
        4. 问题词（直接保留当前用户query）
        5. AI角色设置（系统级指令）
        
        使用配置中的AI_SIMPLE_MODE设置决定使用简化模式还是完整模式
        """
        try:
            # 1. 获取知识库上下文（语义向量）
            knowledge_context = ""
            if use_knowledge_base and self.use_knowledge_base:
                knowledge_context = await self._get_knowledge_context(messages)
            
            # 2. 构建调查记录上下文（调查记录和修改字段）
            survey_context = ""
            if survey_record:
                survey_context = self._build_survey_context(survey_record, trigger_changes)
            
            # 3. 处理历史对话（截断/摘要）
            processed_messages = self._process_history_messages(messages, max_history_messages)
            
            # 4. 保留当前用户query（问题词）
            current_query = self._extract_current_query(messages)
            
            # 5. 整合所有上下文
            combined_context = self._combine_all_contexts(
                knowledge_context=knowledge_context,
                survey_context=survey_context,
                additional_context=additional_context,
                current_query=current_query
            )
            
            if model_provider == "siliconflow":
                return await self._generate_siliconflow(processed_messages, temperature, max_tokens, combined_context)
            elif model_provider == "ollama":
                return await self._generate_ollama(processed_messages, temperature, max_tokens, combined_context)
            else:
                raise ValueError(f"不支持的模型提供商: {model_provider}")
        except Exception as e:
            logger.error(f"AI生成失败: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"详细错误追踪: {traceback.format_exc()}")
            return f"抱歉，AI服务暂时不可用。错误: {type(e).__name__}: {str(e)}"
    
    async def _get_knowledge_context(self, messages: List[Dict[str, str]]) -> str:
        """从知识库获取相关上下文
        
        根据self.simple_mode决定使用简化模式还是完整模式：
        - True: 只检索Top-2结果，5秒超时，简化格式
        - False: 检索Top-3结果，详细格式
        """
        if not messages:
            return ""
        
        # 获取最后一条用户消息
        last_user_message = None
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_user_message = msg["content"]
                break
        
        if not last_user_message:
            return ""
        
        try:
            if self.simple_mode:
                # 简化模式：使用配置的检索结果数和超时
                similar_docs = await asyncio.wait_for(
                    knowledge_service.search_similar_documents(
                        query=last_user_message,
                        n_results=settings.KB_SIMPLE_RESULTS
                    ),
                    timeout=settings.KB_SIMPLE_TIMEOUT
                )
                
                if not similar_docs:
                    return ""
                
                # 构建简化上下文
                context_parts = ["相关法律知识："]
                for i, doc in enumerate(similar_docs, 1):
                    content = doc.get("content", "")
                    if len(content) > 100:
                        content = content[:100] + "..."
                    context_parts.append(f"{i}. {content}")
                
                return "\n".join(context_parts)
            else:
                # 完整模式：使用配置的检索结果数
                similar_docs = await knowledge_service.search_similar_documents(
                    query=last_user_message,
                    n_results=settings.KB_FULL_RESULTS
                )
                
                if not similar_docs:
                    return ""
                
                # 构建详细上下文
                context_parts = ["以下是从法律知识库中检索到的相关信息，请参考这些信息回答问题："]
                for i, doc in enumerate(similar_docs, 1):
                    content_preview = doc["metadata"].get("content_preview", doc["content"])
                    filename = doc["metadata"].get("filename", "未知文件")
                    category = doc["metadata"].get("category", "未知分类")
                    
                    context_parts.append(f"\n{i}. 【{category} - {filename}】")
                    context_parts.append(f"   相关度: {doc['score']:.2%}")
                    context_parts.append(f"   内容: {content_preview}")
                
                return "\n".join(context_parts)
            
        except asyncio.TimeoutError:
            logger.warning("知识库检索超时")
            return ""
        except Exception as e:
            logger.error(f"知识库检索失败: {e}")
            return ""
    
    def _build_survey_context(self, survey_record: Dict[str, Any], trigger_changes: Optional[Dict[str, Any]] = None) -> str:
        """构建调查记录上下文
        
        根据self.simple_mode决定使用简化模式还是完整格式：
        - True: 提取关键信息，简化格式
        - False: 提取所有信息，完整格式
        
        注意：调查表是完全可自定义的，字段名不固定
        """
        if not survey_record:
            return ""
        
        answers = survey_record.get("answers", {})
        if not answers:
            return ""
        
        if self.simple_mode:
            # 简化模式：提取非空的关键字段
            context_parts = []
            
            # 提取前5个非空字段作为关键信息
            count = 0
            for field_name, field_value in answers.items():
                if field_value is None or field_value == '' or field_value == '未填写':
                    continue
                    
                if isinstance(field_value, list):
                    if field_value:
                        # 只取前2个元素
                        display_value = ', '.join(str(v) for v in field_value[:2])
                        context_parts.append(f"{field_name}：{display_value}")
                        count += 1
                elif isinstance(field_value, dict):
                    # 跳过复杂嵌套结构
                    continue
                else:
                    context_parts.append(f"{field_name}：{field_value}")
                    count += 1
                
                # 最多提取5个字段
                if count >= 5:
                    break
            
            # 如果有触发变更，简要说明
            if trigger_changes:
                changed_count = len(trigger_changes)
                if changed_count > 0:
                    context_parts.append(f"最近修改了{changed_count}个字段")
            
            if context_parts:
                return "调查信息：" + " | ".join(context_parts)
            return ""
        else:
            # 完整模式：显示所有字段
            context_parts = ["\n=== 调查记录信息 ==="]
            
            # 显示所有非空字段
            for field_name, field_value in answers.items():
                if field_value is None or field_value == '':
                    continue
                    
                if isinstance(field_value, list):
                    if field_value:
                        context_parts.append(f"{field_name}：{', '.join(str(v) for v in field_value)}")
                    else:
                        context_parts.append(f"{field_name}：空列表")
                elif isinstance(field_value, dict):
                    # 如果是嵌套字典，简化为JSON字符串
                    import json
                    try:
                        json_str = json.dumps(field_value, ensure_ascii=False)
                        if len(json_str) > 100:
                            context_parts.append(f"{field_name}：{json_str[:100]}...")
                        else:
                            context_parts.append(f"{field_name}：{json_str}")
                    except:
                        context_parts.append(f"{field_name}：复杂对象")
                else:
                    context_parts.append(f"{field_name}：{field_value}")
            
            # 如果有触发变更的字段，显示详细信息
            if trigger_changes:
                context_parts.append("\n=== 最近修改的字段 ===")
                for field_key, change_info in trigger_changes.items():
                    previous = change_info.get("previous", "无")
                    current = change_info.get("current", "无")
                    context_parts.append(f"- {field_key}: 从 '{previous}' 修改为 '{current}'")
            
            # 如果有法律建议，添加摘要
            suggestions = survey_record.get("suggestions", [])
            if suggestions and len(suggestions) > 0:
                latest_suggestion = suggestions[0]
                suggestion_text = latest_suggestion.get("suggestion", "")
                if suggestion_text:
                    # 截取前200个字符作为摘要
                    preview = suggestion_text[:200] + "..." if len(suggestion_text) > 200 else suggestion_text
                    context_parts.append(f"\n=== 最新法律建议摘要 ===")
                    context_parts.append(preview)
            
            return "\n".join(context_parts)
    
    def _process_history_messages(self, messages: List[Dict[str, str]], max_history_messages: int = settings.AI_MAX_HISTORY_MESSAGES) -> List[Dict[str, str]]:
        """处理历史对话（截断/摘要，最近几轮对话）
        
        根据self.simple_mode决定处理方式：
        - True: 更激进地截断，使用配置的简化模式最大对话轮数
        - False: 保留更多历史，使用配置的最大历史消息数
        """
        if not messages:
            return []
        
        # 根据模式调整最大历史消息数
        if self.simple_mode:
            # 简化模式：更少的对话轮数
            effective_max = min(max_history_messages, settings.AI_SIMPLE_MAX_HISTORY)
        else:
            effective_max = max_history_messages
        
        max_total = effective_max * 2  # 每条对话有user和assistant
        
        # 如果消息数量超过限制，只保留最近的几轮
        if len(messages) <= max_total:
            return messages
        
        # 只保留最近的消息
        recent_messages = messages[-max_total:]
        
        # 如果截断了历史且不是简化模式，添加摘要说明
        if len(messages) > max_total and not self.simple_mode:
            summary_note = {
                "role": "system",
                "content": f"注意：由于对话历史较长，这里只显示最近{effective_max}轮对话。"
            }
            return [summary_note] + recent_messages
        
        return recent_messages
    
    def _extract_current_query(self, messages: List[Dict[str, str]]) -> str:
        """提取当前用户query（问题词）"""
        if not messages:
            return ""
        
        # 查找最后一条用户消息
        for msg in reversed(messages):
            if msg.get("role") == "user":
                return msg.get("content", "")
        
        return ""
    
    def _combine_all_contexts(
        self,
        knowledge_context: str = "",
        survey_context: str = "",
        additional_context: str = "",
        current_query: str = ""
    ) -> str:
        """整合所有上下文
        
        根据self.simple_mode决定使用哪种格式：
        - True: 简洁格式，紧凑布局
        - False: 详细格式，清晰结构
        """
        if self.simple_mode:
            # 简化模式：紧凑格式
            context_parts = []
            
            # 1. 简化系统指令
            system_instruction = "你是专业的法律AI助手，为中国企业提供法律咨询。请提供准确、实用的法律建议。"
            context_parts.append(system_instruction)
            
            # 2. 知识库上下文
            if knowledge_context:
                context_parts.append(knowledge_context)
            
            # 3. 调查记录上下文
            if survey_context:
                context_parts.append(survey_context)
            
            # 4. 额外上下文
            if additional_context:
                context_parts.append(additional_context)
            
            # 5. 当前问题
            if current_query:
                context_parts.append(f"问题：{current_query}")
            
            # 使用紧凑格式
            return " | ".join([part for part in context_parts if part])
        else:
            # 完整模式：详细格式
            context_parts = []
            
            # 1. 系统级指令（AI角色设置）
            system_instruction = """你是一个专业的法律AI助手，专门为中国企业提供法律咨询服务。
            请根据用户的问题提供准确、专业的法律建议。
            回答时请：
            1. 引用相关法律条文
            2. 提供实际案例分析
            3. 给出具体的操作建议
            4. 提醒潜在的法律风险
            5. 使用清晰的结构
            """
            
            context_parts.append(system_instruction)
            
            # 2. 知识库上下文（语义向量）
            if knowledge_context:
                context_parts.append("\n" + knowledge_context)
            
            # 3. 调查记录上下文（调查记录和修改字段）
            if survey_context:
                context_parts.append("\n" + survey_context)
            
            # 4. 额外上下文
            if additional_context:
                context_parts.append("\n" + additional_context)
            
            # 5. 当前问题（问题词）
            if current_query:
                context_parts.append(f"\n当前用户问题：{current_query}")
            
            return "\n".join(context_parts)
    
    async def _generate_siliconflow(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        context: str = ""
    ) -> str:
        """使用SiliconFlow生成
        
        根据self.simple_mode决定处理方式：
        - True: 减少超时时间，无重试，快速失败
        - False: 完整重试机制，较长超时
        """
        client = await self.get_siliconflow_client()
        
        # 现在context已经包含了所有上下文（系统指令、知识库、调查记录等）
        # 直接使用context作为系统提示
        system_prompt = context if context else """你是一个专业的法律AI助手，专门为中国企业提供法律咨询服务。
        请根据用户的问题提供准确、专业的法律建议。"""
        
        # 添加系统提示
        formatted_messages = [{"role": "system", "content": system_prompt}] + messages
        
        payload = {
            "model": settings.SILICONFLOW_MODEL,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        if self.simple_mode:
            # 简化模式：增加超时时间，添加一次重试
            max_retries = 1
            last_exception = None
            
            for attempt in range(max_retries + 1):  # 0次重试意味着尝试1次
                try:
                    # 增加超时时间：调查表分析需要更长时间
                    timeout = httpx.Timeout(
                        settings.SILICONFLOW_REQUEST_TIMEOUT * 1.5,  # 增加50%的超时时间
                        connect=15.0,  # 增加连接超时
                        read=settings.SILICONFLOW_REQUEST_TIMEOUT * 1.2  # 增加读取超时
                    )
                    response = await client.post("/chat/completions", json=payload, timeout=timeout)
                    response.raise_for_status()
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                except (httpx.ReadTimeout, httpx.ConnectTimeout, asyncio.TimeoutError) as e:
                    logger.warning(f"SiliconFlow请求超时（简化模式，尝试 {attempt + 1}/{max_retries + 1}）: {e}")
                    last_exception = e
                    if attempt < max_retries:
                        await asyncio.sleep(3)  # 重试前等待3秒
                        continue
                    else:
                        return "抱歉，AI响应超时。请尝试简化您的问题或稍后重试。"
                except httpx.HTTPStatusError as e:
                    logger.error(f"SiliconFlow HTTP错误（简化模式）: {e.response.status_code} - {e.response.text}")
                    return f"AI服务暂时不可用。HTTP错误: {e.response.status_code}"
                except Exception as e:
                    logger.error(f"SiliconFlow错误（简化模式）: {e}")
                    return f"AI服务暂时不可用。错误: {type(e).__name__}"
            
            return "抱歉，AI响应超时。请尝试简化您的问题或稍后重试。"
        else:
            # 完整模式：更强大的重试机制
            max_retries = 3
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    # 增加超时时间：使用配置的重试超时设置
                    timeout = httpx.Timeout(
                        settings.SILICONFLOW_RETRY_TIMEOUT,
                        connect=15.0,
                        read=settings.SILICONFLOW_RETRY_TIMEOUT - 10.0
                    )
                    response = await client.post("/chat/completions", json=payload, timeout=timeout)
                    response.raise_for_status()
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                except (httpx.ReadTimeout, httpx.ConnectTimeout, asyncio.TimeoutError) as e:
                    logger.warning(f"SiliconFlow请求超时 (尝试 {attempt + 1}/{max_retries}): {e}")
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = 2 * (attempt + 1)  # 指数退避：2, 4, 6秒
                        await asyncio.sleep(wait_time)
                    else:
                        break
                except httpx.HTTPStatusError as e:
                    logger.error(f"SiliconFlow HTTP错误: {e.response.status_code} - {e.response.text}")
                    last_exception = e
                    break
                except Exception as e:
                    logger.error(f"SiliconFlow未知错误: {e}")
                    last_exception = e
                    break
            
            # 所有重试都失败
            if last_exception:
                if isinstance(last_exception, (httpx.ReadTimeout, httpx.ConnectTimeout, asyncio.TimeoutError)):
                    return "抱歉，AI响应超时。请尝试简化您的问题或稍后重试。"
                else:
                    raise last_exception
            else:
                return "抱歉，AI服务暂时不可用。"
    
    async def _generate_ollama(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        context: str = ""
    ) -> str:
        """使用Ollama生成
        
        根据self.simple_mode决定处理方式：
        - True: 简化提示，设置超时，快速失败
        - False: 完整提示，无超时限制
        """
        client = await self.get_ollama_client()
        
        if self.simple_mode:
            # 简化模式：构建简化提示
            prompt_parts = []
            for msg in messages:
                if msg["role"] == "system":
                    # 系统提示简化
                    system_content = msg["content"]
                    if len(system_content) > 200:
                        system_content = system_content[:200] + "..."
                    prompt_parts.append(f"系统: {system_content}")
                else:
                    prompt_parts.append(f"{msg['role']}: {msg['content']}")
            
            prompt = "\n".join(prompt_parts) + "\nassistant: "
        else:
            # 完整模式：使用context作为系统提示
            system_prompt = context if context else """你是一个专业的法律AI助手，专门为中国企业提供法律咨询服务。
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
        
        try:
            if self.simple_mode:
                # 简化模式：设置超时
                timeout = httpx.Timeout(settings.OLLAMA_REQUEST_TIMEOUT, connect=5.0)
                response = await client.post("/api/generate", json=payload, timeout=timeout)
            else:
                response = await client.post("/api/generate", json=payload)
            
            response.raise_for_status()
            result = response.json()
            return result["response"]
        except (httpx.ReadTimeout, httpx.ConnectTimeout, asyncio.TimeoutError) as e:
            logger.warning(f"Ollama请求超时: {e}")
            return "抱歉，本地AI响应超时。请尝试简化问题或使用云端AI。"
        except Exception as e:
            logger.error(f"Ollama错误: {e}")
            return f"本地AI服务暂时不可用。错误: {type(e).__name__}"
    
    async def close(self):
        """关闭客户端连接"""
        if self.siliconflow_client:
            await self.siliconflow_client.aclose()
        if self.ollama_client:
            await self.ollama_client.aclose()
    
    async def analyze_survey_changes(
        self,
        current_answers: Dict[str, Any],
        previous_answers: Dict[str, Any],
        template_id: int = 1
    ) -> Dict[str, Any]:
        """分析调查表变更并生成法律建议"""
        
        # 识别变更的字段
        changed_fields = {}
        for key, value in current_answers.items():
            if key not in previous_answers or previous_answers[key] != value:
                changed_fields[key] = {
                    "previous": previous_answers.get(key),
                    "current": value
                }
        
        # 如果没有变更，使用当前答案进行分析
        if not changed_fields:
            analysis_context = "分析企业基本情况，提供全面的法律建议。"
            answers_for_analysis = current_answers
        else:
            analysis_context = f"检测到以下字段变更：{list(changed_fields.keys())}，请针对这些变更提供法律建议。"
            answers_for_analysis = changed_fields
        
        # 构建分析提示
        prompt = f"""你是一个专业的法律AI助手，专门为中国企业提供法律咨询服务。

请分析以下企业调查表信息，并提供针对性的法律建议：

企业信息：
{json.dumps(answers_for_analysis, ensure_ascii=False, indent=2)}

{analysis_context}

请按照以下格式提供建议：
1. 风险识别：识别潜在的法律风险
2. 合规建议：提供具体的合规建议
3. 行动步骤：建议企业采取的具体行动
4. 相关法规：引用相关的法律法规

请用中文回答，保持专业、实用。"""
        
        try:
            # 使用知识库增强
            context = ""
            if self.use_knowledge_base:
                # 根据企业类型和行业获取相关知识
                industry = current_answers.get("industry", "")
                company_type = current_answers.get("companyType", "")
                
                query_parts = []
                if industry:
                    query_parts.append(f"{industry}行业")
                if company_type:
                    query_parts.append(f"{company_type}企业")
                if current_answers.get("legalNeeds"):
                    query_parts.append("法律需求")
                
                query = " ".join(query_parts) if query_parts else "企业法律合规"
                
                # 获取相关知识，减少结果数量以提升性能
                try:
                    knowledge_results = await asyncio.wait_for(
                        knowledge_service.search_similar_documents(query, n_results=settings.KB_LEGAL_SUGGESTION_RESULTS),
                        timeout=settings.KB_LEGAL_SUGGESTION_TIMEOUT
                    )
                    if knowledge_results:
                        context = "相关法律知识：\n"
                        for i, result in enumerate(knowledge_results[:settings.KB_LEGAL_SUGGESTION_RESULTS]):
                            # 限制内容长度
                            content_preview = result['content'][:150] + "..." if len(result['content']) > 150 else result['content']
                            context += f"{i+1}. {content_preview}\n"
                except asyncio.TimeoutError:
                    logger.warning("知识库检索超时，继续使用AI分析")
                except Exception as e:
                    logger.warning(f"知识库检索失败: {e}")
            
            # 生成法律建议
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            suggestion = await self.generate_chat_completion(
                messages=messages,
                model_provider="siliconflow",
                temperature=settings.AI_LEGAL_SUGGESTION_TEMPERATURE,
                max_tokens=1500,
                use_knowledge_base=False  # 我们已经手动添加了上下文
            )
            
            # 确定分析类型
            analysis_type = "general"
            legal_needs = current_answers.get("legalNeeds", [])
            if "劳动合同管理" in legal_needs:
                analysis_type = "labor"
            elif "知识产权保护" in legal_needs:
                analysis_type = "ip"
            elif "合同审查" in legal_needs:
                analysis_type = "contract"
            elif "税务合规" in legal_needs:
                analysis_type = "tax"
            
            # 确保suggestion不为空
            if not suggestion or suggestion.strip() == "":
                suggestion = "基于您提供的信息，建议您关注企业合规管理，建立健全的法律风险防控体系。具体建议包括：1) 完善劳动合同管理；2) 加强知识产权保护；3) 规范合同审查流程；4) 定期进行税务合规检查。"
            
            return {
                "trigger_changes": changed_fields,
                "suggestion": suggestion,
                "analysis_type": analysis_type,
                "confidence_score": 85
            }
            
        except Exception as e:
            logger.error(f"调查表分析失败: {e}")
            # 返回默认建议
            return {
                "trigger_changes": changed_fields,
                "suggestion": "基于您提供的信息，建议您关注企业合规管理，建立健全的法律风险防控体系。具体建议包括：1) 完善劳动合同管理；2) 加强知识产权保护；3) 规范合同审查流程；4) 定期进行税务合规检查。",
                "analysis_type": "general",
                "confidence_score": 70
            }

# 全局AI服务实例
ai_service = AIService()

# 同步包装函数（用于survey_service）
def analyze_survey_changes(current_answers: Dict[str, Any], previous_answers: Dict[str, Any], template_id: int = 1) -> Dict[str, Any]:
    """同步包装的调查表分析函数 - 简化版本，避免事件循环问题"""
    import asyncio
    import threading
    import queue
    
    # 使用队列在线程间传递结果
    result_queue = queue.Queue()
    exception_queue = queue.Queue()
    
    def run_analysis():
        """在线程中运行分析"""
        try:
            # 创建全新的事件循环
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            
            # 重要：重新创建AI服务实例，避免共享的客户端使用错误的事件循环
            from app.services.ai_service import AIService
            local_ai_service = AIService()
            
            # 运行分析
            result = new_loop.run_until_complete(
                local_ai_service.analyze_survey_changes(
                    current_answers=current_answers,
                    previous_answers=previous_answers,
                    template_id=template_id
                )
            )
            
            # 清理资源
            new_loop.run_until_complete(local_ai_service.close())
            new_loop.close()
            
            result_queue.put(result)
            
        except Exception as e:
            exception_queue.put(e)
    
    # 创建并启动线程
    thread = threading.Thread(target=run_analysis)
    thread.daemon = True  # 设置为守护线程
    thread.start()
    
    # 等待线程完成，设置超时
    thread.join(timeout=120)
    
    if thread.is_alive():
        logger.error("调查表分析超时（线程仍在运行）")
        # 返回默认建议
        return {
            "trigger_changes": {},
            "suggestion": "分析超时，建议稍后查看历史记录或重新提交。系统已保存您的调查记录。",
            "analysis_type": "general",
            "confidence_score": 50
        }
    
    # 检查是否有异常
    if not exception_queue.empty():
        exception = exception_queue.get()
        logger.error(f"调查表分析失败: {exception}")
        import traceback
        logger.error(f"详细错误追踪: {traceback.format_exc()}")
        
        # 返回错误建议
        return {
            "trigger_changes": {},
            "suggestion": f"分析失败: {type(exception).__name__}。请检查网络连接或联系管理员。",
            "analysis_type": "general",
            "confidence_score": 30
        }
    
    # 获取结果
    if not result_queue.empty():
        return result_queue.get()
    
    # 如果既没有结果也没有异常，返回默认建议
    logger.warning("调查表分析未返回结果")
    return {
        "trigger_changes": {},
        "suggestion": "分析未完成，请稍后重试。",
        "analysis_type": "general",
        "confidence_score": 40
    }