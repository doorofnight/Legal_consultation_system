import os
import json
import logging
import hashlib
import shutil
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from app.core.config import settings
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)

class KnowledgeService:
    """知识库服务，处理文档向量化和检索"""
    
    def __init__(self):
        self.knowledge_base_path = Path("knowledge_base")
        self.vector_store_path = self.knowledge_base_path / "vector_store"
        self.embeddings_path = self.vector_store_path / "embeddings"
        self.metadata_path = self.vector_store_path / "metadata"
        
        # 创建必要的目录
        self.embeddings_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化ChromaDB客户端 - 禁用telemetry以避免错误
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.vector_store_path),
            settings=Settings(
                anonymized_telemetry=False,
                chroma_telemetry_impl=""
            )
        )
        
        # 获取或创建集合
        self.collection_name = "legal_knowledge"
        try:
            self.collection = self.chroma_client.get_collection(self.collection_name)
            logger.info(f"已加载现有集合: {self.collection_name}")
        except:
            # 创建新集合
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "法律知识库向量存储"}
            )
            logger.info(f"创建新集合: {self.collection_name}")
    
    def scan_documents(self) -> List[Dict[str, Any]]:
        """扫描知识库目录，获取所有文档"""
        documents = []
        
        # 支持的文档扩展名
        supported_extensions = {'.md', '.txt', '.pdf', '.docx'}
        
        # 遍历知识库目录
        for root, dirs, files in os.walk(self.knowledge_base_path):
            # 跳过vector_store目录
            if "vector_store" in root:
                continue
                
            for file in files:
                file_path = Path(root) / file
                file_ext = file_path.suffix.lower()
                
                if file_ext in supported_extensions:
                    # 计算文件哈希作为ID
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    
                    # 读取文件内容
                    try:
                        if file_ext == '.md' or file_ext == '.txt':
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                        else:
                            # 对于PDF和DOCX，暂时只记录文件名
                            content = f"文档: {file_path.name}"
                            logger.warning(f"暂不支持 {file_ext} 格式的完整内容提取: {file_path}")
                        
                        # 获取相对路径
                        rel_path = str(file_path.relative_to(self.knowledge_base_path))
                        
                        documents.append({
                            "id": file_hash,
                            "path": str(file_path),
                            "rel_path": rel_path,
                            "filename": file,
                            "extension": file_ext,
                            "content": content,
                            "category": Path(root).relative_to(self.knowledge_base_path).parts[0] if Path(root) != self.knowledge_base_path else "root"
                        })
                        
                    except Exception as e:
                        logger.error(f"读取文件失败 {file_path}: {e}")
        
        logger.info(f"扫描到 {len(documents)} 个文档")
        return documents
    
    async def vectorize_documents(self, documents: List[Dict[str, Any]], model_provider: str = None) -> Dict[str, Any]:
        """向量化文档"""
        if not documents:
            return {"success": False, "message": "没有文档可向量化"}
        
        # 提取文本内容
        texts = [doc["content"] for doc in documents]
        ids = [doc["id"] for doc in documents]
        
        # 生成元数据
        metadatas = []
        for doc in documents:
            metadata = {
                "path": doc["rel_path"],
                "filename": doc["filename"],
                "extension": doc["extension"],
                "category": doc["category"],
                "content_preview": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"]
            }
            metadatas.append(metadata)
        
        try:
            # 生成嵌入向量
            logger.info(f"开始向量化 {len(texts)} 个文档，使用模型提供商: {model_provider or settings.EMBEDDING_MODEL_PROVIDER}")
            embeddings = await embedding_service.generate_embeddings(
                texts=texts,
                model_provider=model_provider
            )
            
            # 保存到ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            # 保存元数据到文件
            self._save_metadata(documents, embeddings)
            
            logger.info(f"成功向量化 {len(documents)} 个文档")
            return {
                "success": True,
                "message": f"成功向量化 {len(documents)} 个文档",
                "count": len(documents)
            }
            
        except Exception as e:
            logger.error(f"文档向量化失败: {e}")
            return {
                "success": False,
                "message": f"文档向量化失败: {str(e)}"
            }
    
    def _save_metadata(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]):
        """保存元数据和嵌入向量到文件"""
        # 保存元数据到文件
        metadata_file = self.metadata_path / "documents_metadata.json"
        
        metadata_list = []
        for i, doc in enumerate(documents):
            metadata = {
                "id": doc["id"],
                "path": doc["rel_path"],
                "filename": doc["filename"],
                "category": doc["category"],
                "embedding_dim": len(embeddings[i]) if i < len(embeddings) else 0,
                "content_length": len(doc["content"]),
                "embedding_file": f"{doc['id']}.json"
            }
            metadata_list.append(metadata)
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_list, f, ensure_ascii=False, indent=2)
        
        # 保存嵌入向量到文件
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            embedding_file = self.embeddings_path / f"{doc['id']}.json"
            embedding_data = {
                "id": doc["id"],
                "filename": doc["filename"],
                "path": doc["rel_path"],
                "embedding": embedding,
                "embedding_dim": len(embedding)
            }
            with open(embedding_file, 'w', encoding='utf-8') as f:
                json.dump(embedding_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已保存 {len(documents)} 个文档的元数据和嵌入向量")
    
    async def search_similar_documents(self, query: str, n_results: int = 5, model_provider: str = None) -> List[Dict[str, Any]]:
        """搜索相似文档"""
        try:
            # 生成查询的嵌入向量
            query_embeddings = await embedding_service.generate_embeddings(
                texts=[query],
                model_provider=model_provider
            )
            
            if not query_embeddings:
                return []
            
            # 在集合中搜索
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # 格式化结果
            similar_docs = []
            if results["ids"] and len(results["ids"]) > 0:
                for i in range(len(results["ids"][0])):
                    doc_id = results["ids"][0][i]
                    distance = results["distances"][0][i] if results["distances"] else None
                    document = results["documents"][0][i] if results["documents"] else ""
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    
                    similar_docs.append({
                        "id": doc_id,
                        "score": 1.0 - (distance if distance else 0),  # 转换为相似度分数
                        "content": document[:500] + "..." if len(document) > 500 else document,
                        "metadata": metadata
                    })
            
            return similar_docs
            
        except Exception as e:
            logger.error(f"文档搜索失败: {e}")
            return []
    
    def create_directory(self, name: str) -> Dict[str, Any]:
        """创建知识库目录
        
        Args:
            name: 目录名
            
        Returns:
            创建结果字典
        """
        try:
            # 验证目录名
            if not name or not name.strip():
                return {"success": False, "message": "目录名不能为空"}
            
            # 清理目录名，只允许字母、数字、下划线和连字符
            import re
            clean_name = re.sub(r'[^\w\-]', '_', name.strip())
            
            # 创建目录路径
            dir_path = self.knowledge_base_path / clean_name
            
            # 检查目录是否已存在
            if dir_path.exists():
                return {"success": False, "message": f"目录 '{clean_name}' 已存在"}
            
            # 创建目录
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建知识库目录: {clean_name}")
            
            return {
                "success": True,
                "message": f"目录创建成功",
                "data": {
                    "name": clean_name,
                    "path": str(dir_path.relative_to(self.knowledge_base_path))
                }
            }
            
        except Exception as e:
            logger.error(f"创建目录失败: {e}")
            return {"success": False, "message": f"创建目录失败: {str(e)}"}
    
    def upload_file(self, file_content: bytes, filename: str, category: str = "") -> Dict[str, Any]:
        """上传文件到知识库
        
        Args:
            file_content: 文件内容字节
            filename: 文件名
            category: 分类目录（可选）
            
        Returns:
            上传结果字典
        """
        try:
            # 验证文件名
            if not filename or not filename.strip():
                return {"success": False, "message": "文件名不能为空"}
            
            # 验证文件内容
            if not file_content or len(file_content) == 0:
                return {"success": False, "message": "文件内容不能为空"}
            
            # 检查文件大小（限制为10MB）
            if len(file_content) > 10 * 1024 * 1024:
                return {"success": False, "message": "文件大小不能超过10MB"}
            
            # 检查文件扩展名
            import os
            file_ext = os.path.splitext(filename)[1].lower()
            supported_extensions = {'.md', '.txt', '.pdf', '.docx'}
            if file_ext not in supported_extensions:
                return {"success": False, "message": f"不支持的文件格式，仅支持{', '.join(supported_extensions)}格式"}
            
            # 确定目标目录
            if category and category.strip():
                # 清理目录名
                import re
                clean_category = re.sub(r'[^\w\-]', '_', category.strip())
                target_dir = self.knowledge_base_path / clean_category
            else:
                target_dir = self.knowledge_base_path
            
            # 确保目标目录存在
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # 构建完整文件路径
            file_path = target_dir / filename
            
            # 检查文件是否已存在
            if file_path.exists():
                return {"success": False, "message": f"文件 '{filename}' 已存在"}
            
            # 写入文件
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            logger.info(f"文件上传成功: {filename} -> {file_path}")
            
            # 获取文件信息
            import hashlib
            file_hash = hashlib.md5(file_content).hexdigest()
            file_size = len(file_content)
            
            return {
                "success": True,
                "message": "文件上传成功",
                "data": {
                    "id": file_hash,
                    "filename": filename,
                    "path": str(file_path.relative_to(self.knowledge_base_path)),
                    "size": file_size,
                    "size_formatted": self._format_size(file_size),
                    "category": category if category else "root"
                }
            }
            
        except Exception as e:
            logger.error(f"文件上传失败: {e}")
            return {"success": False, "message": f"文件上传失败: {str(e)}"}
    
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """删除知识库文件
        
        Args:
            file_path: 文件相对路径
            
        Returns:
            删除结果字典
        """
        try:
            # 验证文件路径
            if not file_path or not file_path.strip():
                return {"success": False, "message": "文件路径不能为空"}
            
            # 构建完整文件路径
            full_path = self.knowledge_base_path / file_path
            
            # 检查文件是否存在
            if not full_path.exists():
                return {"success": False, "message": f"文件不存在: {file_path}"}
            
            # 检查是否为文件（不是目录）
            if not full_path.is_file():
                return {"success": False, "message": f"路径不是文件: {file_path}"}
            
            # 删除文件
            import os
            os.remove(full_path)
            
            logger.info(f"文件删除成功: {file_path}")
            
            # 尝试从向量存储中删除对应的文档（如果存在）
            try:
                # 计算文件哈希作为可能的文档ID
                import hashlib
                with open(full_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                
                # 尝试从集合中删除
                self.collection.delete(ids=[file_hash])
                logger.info(f"已从向量存储中删除文档: {file_hash}")
            except Exception as e:
                logger.warning(f"从向量存储中删除文档失败（可能不存在）: {e}")
            
            return {
                "success": True,
                "message": "文件删除成功",
                "data": {
                    "path": file_path
                }
            }
            
        except Exception as e:
            logger.error(f"文件删除失败: {e}")
            return {"success": False, "message": f"文件删除失败: {str(e)}"}
    
    def delete_directory(self, dir_path: str) -> Dict[str, Any]:
        """删除知识库目录
        
        Args:
            dir_path: 目录相对路径
            
        Returns:
            删除结果字典
        """
        try:
            # 验证目录路径
            if not dir_path or not dir_path.strip():
                return {"success": False, "message": "目录路径不能为空"}
            
            # 构建完整目录路径
            full_path = self.knowledge_base_path / dir_path
            
            # 检查目录是否存在
            if not full_path.exists():
                return {"success": False, "message": f"目录不存在: {dir_path}"}
            
            # 检查是否为目录（不是文件）
            if not full_path.is_dir():
                return {"success": False, "message": f"路径不是目录: {dir_path}"}
            
            # 检查目录是否为空（可选，根据需求决定是否允许删除非空目录）
            # 这里我们允许删除非空目录，但会给出警告
            import shutil
            dir_contents = list(full_path.iterdir())
            if dir_contents:
                # 统计目录中的文件数量
                file_count = len([item for item in dir_contents if item.is_file()])
                dir_count = len([item for item in dir_contents if item.is_dir()])
                logger.warning(f"删除非空目录: {dir_path} (包含 {file_count} 个文件, {dir_count} 个子目录)")
            
            # 删除目录及其所有内容
            shutil.rmtree(full_path)
            
            logger.info(f"目录删除成功: {dir_path}")
            
            return {
                "success": True,
                "message": "目录删除成功",
                "data": {
                    "path": dir_path,
                    "was_empty": len(dir_contents) == 0 if 'dir_contents' in locals() else True
                }
            }
            
        except Exception as e:
            logger.error(f"目录删除失败: {e}")
            return {"success": False, "message": f"目录删除失败: {str(e)}"}
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "vector_store_path": str(self.vector_store_path)
            }
        except Exception as e:
            logger.error(f"获取集合统计失败: {e}")
            return {"error": str(e)}
    
    def _cleanup_old_folders(self):
        """清理旧的UUID文件夹，只保留embeddings、metadata和chroma.sqlite3"""
        import shutil
        vector_store_dir = self.vector_store_path
        
        # 需要保留的目录和文件
        keep_items = {"embeddings", "metadata", "chroma.sqlite3"}
        
        for item in vector_store_dir.iterdir():
            if item.name not in keep_items:
                if item.is_dir():
                    try:
                        shutil.rmtree(item)
                        logger.info(f"已删除旧文件夹: {item.name}")
                    except Exception as e:
                        logger.warning(f"删除文件夹失败 {item.name}: {e}")
                else:
                    try:
                        item.unlink()
                        logger.info(f"已删除旧文件: {item.name}")
                    except Exception as e:
                        logger.warning(f"删除文件失败 {item.name}: {e}")
    
    async def rebuild_vector_store(self, model_provider: str = None) -> Dict[str, Any]:
        """重建向量存储"""
        try:
            # 清理旧文件夹
            self._cleanup_old_folders()
            
            # 清空现有集合
            self.chroma_client.delete_collection(self.collection_name)
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "法律知识库向量存储"}
            )
            
            # 扫描并向量化文档
            documents = self.scan_documents()
            result = await self.vectorize_documents(documents, model_provider)
            
            return {
                "success": result["success"],
                "message": result["message"],
                "stats": self.get_collection_stats()
            }
            
        except Exception as e:
            logger.error(f"重建向量存储失败: {e}")
            return {
                "success": False,
                "message": f"重建向量存储失败: {str(e)}"
            }

# 全局知识库服务实例
knowledge_service = KnowledgeService()