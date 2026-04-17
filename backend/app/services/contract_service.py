import os
import json
import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from app.services.ai_service import ai_service
from app.services.knowledge_service import knowledge_service
from app.core.config import settings

logger = logging.getLogger(__name__)

class ContractService:
    """合同分析服务"""
    
    def __init__(self):
        self.supported_extensions = {'.txt', '.docx', '.doc', '.pdf'}
        
    def _read_file_with_fallback(self, file_path: str, encoding: str = 'utf-8') -> str:
        """读取文件，如果失败则尝试二进制读取"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, 'rb') as f:
                content = f.read()
                return content.decode(encoding, errors='ignore')
        except Exception as e:
            logger.warning(f"文件读取失败: {e}")
            raise
    
    async def extract_text_from_file(self, file_path: str) -> str:
        """从文件中提取文本内容"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.txt':
                return self._read_file_with_fallback(file_path)
            
            elif file_ext == '.docx':
                # 使用python-docx库解析docx文件
                try:
                    import docx
                    doc = docx.Document(file_path)
                    full_text = []
                    for para in doc.paragraphs:
                        full_text.append(para.text)
                    return '\n'.join(full_text)
                except ImportError:
                    logger.warning("python-docx未安装，尝试使用文本模式读取")
                    return self._read_file_with_fallback(file_path, 'utf-8')
            
            elif file_ext == '.pdf':
                # 使用PyPDF2解析PDF文件
                try:
                    import PyPDF2
                    text = ""
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        for page in pdf_reader.pages:
                            text += page.extract_text() + "\n"
                    return text
                except ImportError:
                    logger.warning("PyPDF2未安装，无法解析PDF")
                    return "PDF文件需要安装PyPDF2库才能解析"
            
            else:
                # 其他格式尝试文本读取
                return self._read_file_with_fallback(file_path)
                        
        except Exception as e:
            logger.error(f"提取文件文本失败: {e}")
            return f"文件解析失败: {str(e)}"
    
    async def analyze_contract_content(
        self,
        contract_text: str,
        perspective: str = "neutral",
        focus_areas: Optional[List[str]] = None,
        model_provider: str = "siliconflow",
        contract_type: Optional[str] = None  
    ) -> Dict[str, Any]:
        """分析合同内容，使用AI生成诊断结果"""
        
        if focus_areas is None:
            focus_areas = ["权利义务", "违约责任", "争议解决", "保密条款", "知识产权"]
        
        # 从知识库获取相关法律知识
        knowledge_context = ""
        try:
            # 根据合同类型搜索相关法律知识
            query = "合同法律风险审查条款"
            if contract_type and contract_type != "未知合同类型":
                query = f"{contract_type}法律风险审查条款"
                
            similar_docs = await knowledge_service.search_similar_documents(
                query=query,
                n_results=3
            )
            
            if similar_docs:
                knowledge_context = "相关法律知识参考：\n"
                for i, doc in enumerate(similar_docs, 1):
                    content_preview = doc.get("content", "")[:200]
                    knowledge_context += f"{i}. {content_preview}\n"
        except Exception as e:
            logger.warning(f"知识库检索失败: {e}")
        
        # 构建分析提示
        contract_type_info = f"合同类型：{contract_type}" if contract_type else "合同类型：待识别"
        system_prompt = f"""你是一个专业的法律AI助手，专门从事合同审查和风险诊断。

{contract_type_info}
审查立场：{perspective}
重点关注领域：{', '.join(focus_areas)}

{knowledge_context}

请对以下合同文本进行全面的法律风险分析："""
        
        user_prompt = f"""请分析以下合同：

{contract_text[:3000]}

请按以下格式回复：
合同类型：[类型]
总体风险：[描述]

风险分析：
1. 风险等级：[高/中/低]
   风险类型：[类型]
   风险条款：[原文]
   风险描述：[描述]
   修改建议：[建议]

2. [继续...]

综合建议：[建议]
法律依据：[依据]"""
        
        try:
            # 使用AI服务生成分析
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            analysis_result = await ai_service.generate_chat_completion(
                messages=messages,
                model_provider=model_provider,
                temperature=0.3,
                max_tokens=2500,
                use_knowledge_base=False
            )
            
            # 解析AI返回的结果
            return self._parse_analysis_result(analysis_result, contract_text, contract_type)
            
        except Exception as e:
            logger.error(f"合同AI分析失败: {e}")
            # 返回默认分析结果
            return self._get_default_analysis(contract_text)
    
    def _parse_analysis_result(self, ai_response: str, contract_text: str, contract_type: Optional[str] = None) -> Dict[str, Any]:
        """解析AI返回的分析结果"""
        
        # 使用传入的合同类型，如果没有则使用默认值
        if not contract_type:
            contract_type = "未知合同类型"
        
        # 提取风险条款
        risks = self._parse_risks(ai_response)
        
        # 提取总体评价（总体风险）
        summary = self._extract_summary(ai_response)
        
        # 提取综合建议
        suggestions = self._extract_suggestions(ai_response)
        
        return {
            "contract_type": contract_type,
            "summary": summary,
            "risks": risks,
            "suggestions": suggestions,
            "full_analysis": ai_response,
            "analysis_time": datetime.now().timestamp()
        }
    
    def _parse_risks(self, ai_response: str) -> List[Dict[str, Any]]:
        """解析风险信息"""
        risks = []
        lines = ai_response.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if '风险等级：' in line or '风险等级:' in line:
                risk = {
                    "clause": "",
                    "risk_level": "中风险",
                    "risk_type": "",
                    "description": "",
                    "suggestion": ""
                }
                
                # 提取风险等级
                if '高风险' in line:
                    risk["risk_level"] = "高风险"
                elif '低风险' in line:
                    risk["risk_level"] = "低风险"
                
                # 尝试提取后续信息
                for j in range(i, min(i+5, len(lines))):
                    curr_line = lines[j].strip()
                    if '风险类型：' in curr_line or '风险类型:' in curr_line:
                        parts = curr_line.split('：') if '：' in curr_line else curr_line.split(':')
                        if len(parts) > 1:
                            risk["risk_type"] = parts[1].strip('[] ')
                    elif '风险条款：' in curr_line or '风险条款:' in curr_line:
                        parts = curr_line.split('：') if '：' in curr_line else curr_line.split(':')
                        if len(parts) > 1:
                            risk["clause"] = parts[1].strip('[] ')
                    elif '风险描述：' in curr_line or '风险描述:' in curr_line:
                        parts = curr_line.split('：') if '：' in curr_line else curr_line.split(':')
                        if len(parts) > 1:
                            risk["description"] = parts[1].strip('[] ')
                    elif '修改建议：' in curr_line or '修改建议:' in curr_line:
                        parts = curr_line.split('：') if '：' in curr_line else curr_line.split(':')
                        if len(parts) > 1:
                            risk["suggestion"] = parts[1].strip('[] ')
                
                risks.append(risk)
        
        # 如果没有找到，返回一个默认风险
        if not risks:
            risks.append({
                "clause": "请查看完整分析",
                "risk_level": "中风险",
                "risk_type": "需要详细审查",
                "description": "AI分析完成",
                "suggestion": "请查看完整分析报告"
            })
        
        return risks
    
    def _extract_summary(self, ai_response: str) -> str:
        """从AI响应中提取总体评价（总体风险）"""
        lines = ai_response.split('\n')
        
        # 查找"总体风险："或"总体评价："开头的行
        for line in lines:
            line = line.strip()
            if line.startswith('总体风险：') or line.startswith('总体评价：'):
                # 提取冒号后的内容
                parts = line.split('：', 1)
                if len(parts) > 1:
                    return parts[1].strip()
            elif '总体风险:' in line or '总体评价:' in line:
                # 处理英文冒号
                parts = line.split(':', 1)
                if len(parts) > 1:
                    return parts[1].strip()
        
        # 如果没有找到，使用默认逻辑
        if "高风险" in ai_response:
            return "合同存在高风险条款，建议重点审查。"
        elif "中风险" in ai_response:
            return "合同存在中等风险，建议修改相关条款。"
        elif "低风险" in ai_response:
            return "合同风险较低，基本符合规范。"
        else:
            return "合同AI分析完成。"
    
    def _extract_suggestions(self, ai_response: str) -> str:
        """从AI响应中提取综合建议"""
        lines = ai_response.split('\n')
        
        # 查找"综合建议："开头的行
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('综合建议：'):
                # 提取冒号后的内容
                parts = line.split('：', 1)
                if len(parts) > 1:
                    suggestion = parts[1].strip()
                    # 如果建议很短，可能后面还有更多内容
                    if len(suggestion) < 50 and i + 1 < len(lines):
                        # 收集后续行直到遇到空行或其他标题
                        additional_lines = []
                        for j in range(i + 1, len(lines)):
                            next_line = lines[j].strip()
                            if not next_line or next_line.startswith(('法律依据：', '---', '###', '**')):
                                break
                            additional_lines.append(next_line)
                        if additional_lines:
                            suggestion += '\n' + '\n'.join(additional_lines)
                    return suggestion
            elif '综合建议:' in line:
                # 处理英文冒号
                parts = line.split(':', 1)
                if len(parts) > 1:
                    return parts[1].strip()
        
        # 如果没有找到，返回AI响应的前1000个字符作为建议
        return ai_response[:1000]
    
    def _get_default_analysis(self, contract_text: str) -> Dict[str, Any]:
        """获取默认分析结果（当AI分析失败时使用）"""
        
        # 简单分析合同文本
        word_count = len(contract_text.split())
        line_count = len(contract_text.split('\n'))
        
        # 默认风险分析
        risks = [
            {
                "clause": "请查看完整合同文本",
                "risk_level": "中风险",
                "risk_type": "需要详细审查",
                "description": "系统分析完成，建议人工复核",
                "suggestion": "请专业律师进行最终审查"
            }
        ]
        
        return {
            "contract_type": "未知合同类型",
            "summary": f"合同文本分析完成，共{word_count}字，{line_count}行。建议进行人工法律审查。",
            "risks": risks,
            "suggestions": "1. 建议由专业律师审查合同条款\n2. 注意权利义务对等性\n3. 明确违约责任条款\n4. 完善争议解决机制",
            "full_analysis": "AI分析服务暂时不可用，返回默认分析结果。",
            "analysis_time": datetime.now().timestamp()
        }
    
    async def generate_contract_summary(self, contract_text: str) -> Dict[str, Any]:
        """生成合同摘要"""
        
        # 简单统计
        words = contract_text.split()
        lines = contract_text.split('\n')
        
        # 识别关键条款
        key_sections = []
        section_keywords = {
            "合同双方": ["甲方", "乙方", "双方", "当事人"],
            "合同标的": ["标的", "产品", "服务", "内容"],
            "价款支付": ["价款", "价格", "费用", "支付", "付款"],
            "履行期限": ["期限", "时间", "日期", "完成", "交付"],
            "违约责任": ["违约", "责任", "赔偿", "违约金"],
            "争议解决": ["争议", "仲裁", "诉讼", "管辖", "法院"],
            "保密条款": ["保密", "秘密", "机密", "不得泄露"],
            "知识产权": ["知识", "产权", "专利", "商标", "版权"]
        }
        
        for section, keywords in section_keywords.items():
            for kw in keywords:
                if kw in contract_text:
                    key_sections.append(section)
                    break
        
        return {
            "word_count": len(words),
            "line_count": len(lines),
            "key_sections": list(set(key_sections)),
            "has_signature_block": "签字" in contract_text or "盖章" in contract_text or "签署" in contract_text,
            "has_date": "年" in contract_text and "月" in contract_text and "日" in contract_text
        }

# 全局合同服务实例
contract_service = ContractService()

def _run_async_sync(async_func, *args, **kwargs):
    """通用的异步函数同步包装器"""
    import asyncio
    
    # 创建新的事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(async_func(*args, **kwargs))
        return result
    finally:
        loop.close()

# 同步包装函数（用于后台任务）
def extract_text_from_file_sync(file_path: str) -> str:
    """同步版本的文本提取函数"""
    return _run_async_sync(contract_service.extract_text_from_file, file_path)

def analyze_contract_content_sync(
    contract_text: str,
    perspective: str = "neutral",
    focus_areas = None,
    model_provider: str = "siliconflow",
    contract_type: Optional[str] = None
) -> Dict[str, Any]:
    """同步版本的合同分析函数"""
    if focus_areas is None:
        focus_areas = ["权利义务", "违约责任", "争议解决", "保密条款", "知识产权"]
    
    return _run_async_sync(
        contract_service.analyze_contract_content,
        contract_text=contract_text,
        perspective=perspective,
        focus_areas=focus_areas,
        model_provider=model_provider,
        contract_type=contract_type
    )

def generate_contract_summary_sync(contract_text: str) -> Dict[str, Any]:
    """同步版本的合同摘要生成函数"""
    return _run_async_sync(contract_service.generate_contract_summary, contract_text)