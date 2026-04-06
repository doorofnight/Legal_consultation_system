from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from fastapi import UploadFile
import asyncio
import os
from pathlib import Path

from app.db.session import get_db
from app.services.knowledge_service import knowledge_service
from app.core.config import settings

router = APIRouter()

@router.get("/stats")
async def get_knowledge_stats():
    """获取知识库统计信息"""
    try:
        stats = knowledge_service.get_collection_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识库统计失败: {str(e)}"
        )

def _build_directory_structure(path: Path, base_path: Path, exclude_dirs: set, exclude_files: set):
    """递归构建目录结构"""
    result = []
    
    for item in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
        if item.name in exclude_dirs:
            continue
            
        if item.is_dir():
            # 递归处理子目录
            children = _build_directory_structure(item, base_path, exclude_dirs, exclude_files)
            dir_info = {
                "type": "directory",
                "name": item.name,
                "path": str(item.relative_to(base_path)),
                "children": children
            }
            result.append(dir_info)
        elif item.is_file() and item.name not in exclude_files:
            # 文件
            try:
                stat = item.stat()
                file_info = {
                    "type": "file",
                    "name": item.name,
                    "path": str(item.relative_to(base_path)),
                    "size": _format_size(stat.st_size),
                    "modified": _format_time(stat.st_mtime),
                    "extension": item.suffix.lower()
                }
                result.append(file_info)
            except:
                continue
    
    return result

@router.get("/directory")
async def get_knowledge_directory():
    """获取知识库目录结构"""
    try:
        knowledge_base_path = Path("knowledge_base")
        
        # 排除的目录和文件
        exclude_dirs = {"vector_store", "__pycache__", ".git"}
        exclude_files = {"README.md"}
        
        # 递归构建目录结构
        directory_structure = _build_directory_structure(
            knowledge_base_path,
            knowledge_base_path,
            exclude_dirs,
            exclude_files
        )
        
        return {
            "success": True,
            "data": directory_structure
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取目录结构失败: {str(e)}"
        )

def _format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def _format_time(timestamp):
    """格式化时间戳"""
    from datetime import datetime
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

@router.get("/documents")
async def get_knowledge_documents(
    category: Optional[str] = Query(None, description="文档分类过滤"),
    include_content: bool = Query(False, description="是否包含文档内容")
):
    """获取知识库文档列表"""
    try:
        documents = knowledge_service.scan_documents()
        
        # 过滤vector_store目录
        filtered_docs = []
        for doc in documents:
            # 跳过vector_store目录下的文件
            if "vector_store" in doc["path"]:
                continue
                
            # 按分类过滤
            if category and doc.get("category") != category:
                continue
                
            # 如果不包含内容，则移除content字段以减少响应大小
            doc_copy = doc.copy()
            if not include_content:
                doc_copy.pop("content", None)
                
            # 添加文件大小和修改时间信息
            try:
                file_path = Path(doc["path"])
                if file_path.exists():
                    stat = file_path.stat()
                    doc_copy["size_bytes"] = stat.st_size
                    doc_copy["size"] = _format_size(stat.st_size)
                    doc_copy["modified"] = _format_time(stat.st_mtime)
                else:
                    doc_copy["size"] = "未知"
                    doc_copy["modified"] = "未知"
            except:
                doc_copy["size"] = "未知"
                doc_copy["modified"] = "未知"
                
            filtered_docs.append(doc_copy)
        
        return {
            "success": True,
            "count": len(filtered_docs),
            "data": filtered_docs
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文档列表失败: {str(e)}"
        )

@router.get("/document/{id}/content")
async def get_document_content(id: str):
    """获取文档内容"""
    try:
        documents = knowledge_service.scan_documents()
        
        # 查找匹配的文档
        for doc in documents:
            if doc["id"] == id:
                # 检查文件是否存在
                file_path = Path(doc["path"])
                if not file_path.exists():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="文档文件不存在"
                    )
                
                # 读取文件内容
                try:
                    if doc["extension"] in ['.md', '.txt']:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    else:
                        # 对于其他格式，返回不支持的消息
                        content = f"文档格式 {doc['extension']} 暂不支持在线预览"
                    
                    return {
                        "success": True,
                        "data": {
                            "id": doc["id"],
                            "filename": doc["filename"],
                            "path": doc["rel_path"],
                            "category": doc["category"],
                            "extension": doc["extension"],
                            "content": content
                        }
                    }
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"读取文档内容失败: {str(e)}"
                    )
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文档内容失败: {str(e)}"
        )

@router.post("/scan")
async def scan_knowledge_documents():
    """扫描知识库文档"""
    try:
        documents = knowledge_service.scan_documents()
        return {
            "success": True,
            "message": f"扫描到 {len(documents)} 个文档",
            "data": {
                "count": len(documents),
                "documents": [
                    {
                        "id": doc["id"],
                        "filename": doc["filename"],
                        "category": doc["category"],
                        "path": doc["rel_path"]
                    }
                    for doc in documents[:10]  # 只返回前10个文档的摘要
                ]
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"扫描知识库文档失败: {str(e)}"
        )

@router.post("/vectorize")
async def vectorize_knowledge_documents(
    model_provider: str = None,
    rebuild: bool = False
):
    """向量化知识库文档"""
    try:
        if rebuild:
            # 重建向量存储
            result = await knowledge_service.rebuild_vector_store(model_provider)
        else:
            # 扫描并向量化文档
            documents = knowledge_service.scan_documents()
            result = await knowledge_service.vectorize_documents(documents, model_provider)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "data": knowledge_service.get_collection_stats()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"向量化知识库文档失败: {str(e)}"
        )

@router.post("/search")
async def search_knowledge(
    query: str,
    n_results: int = 5,
    model_provider: str = None
):
    """搜索知识库"""
    try:
        if not query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="查询内容不能为空"
            )
        
        similar_docs = await knowledge_service.search_similar_documents(
            query=query,
            n_results=n_results,
            model_provider=model_provider
        )
        
        return {
            "success": True,
            "query": query,
            "count": len(similar_docs),
            "data": similar_docs
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索知识库失败: {str(e)}"
        )

@router.get("/config")
async def get_knowledge_config():
    """获取知识库配置"""
    return {
        "success": True,
        "data": {
            "embedding_model_provider": settings.EMBEDDING_MODEL_PROVIDER,
            "available_providers": ["siliconflow", "ollama"],
            "siliconflow_embedding_model": settings.SILICONFLOW_EMBEDDING_MODEL,
            "ollama_embedding_model": settings.OLLAMA_EMBEDDING_MODEL,
            "knowledge_base_path": str(knowledge_service.knowledge_base_path),
            "vector_store_path": str(knowledge_service.vector_store_path)
        }
    }

@router.post("/test-embedding")
async def test_embedding(
    text: str = "测试文本",
    model_provider: str = None
):
    """测试嵌入生成"""
    try:
        from app.services.embedding_service import embedding_service
        
        embeddings = await embedding_service.generate_embeddings(
            texts=[text],
            model_provider=model_provider
        )
        
        if embeddings and len(embeddings) > 0:
            return {
                "success": True,
                "message": "嵌入生成成功",
                "data": {
                    "text": text,
                    "embedding_dim": len(embeddings[0]),
                    "embedding_sample": embeddings[0][:5] if len(embeddings[0]) > 5 else embeddings[0],
                    "model_provider": model_provider or settings.EMBEDDING_MODEL_PROVIDER
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="嵌入生成失败"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"测试嵌入生成失败: {str(e)}"
        )

@router.post("/directory")
async def create_directory(
    folder_name: str
):
    """创建知识库目录"""
    try:
        result = knowledge_service.create_directory(folder_name)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "data": result.get("data", {})
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建目录失败: {str(e)}"
        )


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form("")
):
    """上传文档到知识库"""
    try:
        # 读取文件内容
        file_content = await file.read()
        
        # 调用知识库服务上传文件
        result = knowledge_service.upload_file(
            file_content=file_content,
            filename=file.filename,
            category=category
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "data": result.get("data", {})
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传文档失败: {str(e)}"
        )


@router.post("/upload-multiple")
async def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    category: str = Form("")
):
    """批量上传文档到知识库"""
    try:
        results = []
        success_count = 0
        fail_count = 0
        
        for file in files:
            try:
                # 读取文件内容
                file_content = await file.read()
                
                # 调用知识库服务上传文件
                result = knowledge_service.upload_file(
                    file_content=file_content,
                    filename=file.filename,
                    category=category
                )
                
                if result["success"]:
                    success_count += 1
                    results.append({
                        "filename": file.filename,
                        "success": True,
                        "message": result["message"]
                    })
                else:
                    fail_count += 1
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "message": result["message"]
                    })
            except Exception as e:
                fail_count += 1
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "message": f"上传失败: {str(e)}"
                })
        
        return {
            "success": True,
            "message": f"批量上传完成，成功 {success_count} 个，失败 {fail_count} 个",
            "data": {
                "total": len(files),
                "success": success_count,
                "failed": fail_count,
                "results": results
            }
        }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量上传文档失败: {str(e)}"
        )


@router.delete("/document/{file_path:path}")
async def delete_document(file_path: str):
    """删除知识库文档"""
    try:
        # 调用知识库服务删除文件
        result = knowledge_service.delete_file(file_path)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "data": result.get("data", {})
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文档失败: {str(e)}"
        )


@router.delete("/directory/{dir_path:path}")
async def delete_directory(dir_path: str):
    """删除知识库目录"""
    try:
        # 调用知识库服务删除目录
        result = knowledge_service.delete_directory(dir_path)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "data": result.get("data", {})
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除目录失败: {str(e)}"
        )


@router.get("/document/{file_path:path}/download")
async def download_document(file_path: str):
    """下载知识库文档"""
    try:
        # 解码URL路径
        decoded_path = file_path
        
        # 构建完整的文件路径
        knowledge_base_path = Path("knowledge_base")
        file_full_path = knowledge_base_path / decoded_path
        
        # 检查文件是否存在
        if not file_full_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document file not found"
            )
        
        # 检查是否为文件（不是目录）
        if not file_full_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Path is not a file"
            )
        
        # 使用FileResponse，它自动处理文件下载和编码
        from fastapi.responses import FileResponse
        
        return FileResponse(
            path=str(file_full_path),
            filename=file_full_path.name,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # 使用英文错误消息避免编码问题
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Download failed: {str(e)}"
        )