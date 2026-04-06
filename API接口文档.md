# API 接口文档

## 概述

AI法律咨询系统提供完整的RESTful API接口，支持法务咨询、企业调查、知识库管理等功能。所有API均遵循OpenAPI 3.0规范，可通过Swagger UI访问。

**基础URL**: `http://localhost:8000/api/v1`

## 认证方式

当前版本API无需认证，所有接口公开访问。

## 聊天相关接口

### 1. 获取聊天会话列表
**GET** `/chat/sessions`

**参数**:
- `skip` (可选): 跳过记录数，默认0
- `limit` (可选): 返回记录数，默认100

**响应**:
```json
[
  {
    "id": 1,
    "title": "劳动合同咨询",
    "model_provider": "siliconflow",
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:30:00"
  }
]
```

### 2. 创建聊天会话
**POST** `/chat/sessions`

**请求体**:
```json
{
  "title": "新会话",
  "model_provider": "siliconflow"
}
```

**响应**: 创建的会话对象

### 3. 获取会话详情
**GET** `/chat/sessions/{session_id}`

**参数**:
- `session_id` (路径参数): 会话ID

**响应**: 包含消息列表的会话详情

### 4. 更新会话
**PUT** `/chat/sessions/{session_id}`

**请求体**:
```json
{
  "title": "更新后的标题"
}
```

**响应**: 更新后的会话对象

### 5. 删除会话
**DELETE** `/chat/sessions/{session_id}`

### 6. 获取会话消息
**GET** `/chat/sessions/{session_id}/messages`

**参数**:
- `session_id` (路径参数): 会话ID
- `skip` (可选): 跳过记录数，默认0
- `limit` (可选): 返回记录数，默认100

**响应**: 消息列表

### 7. 发送聊天消息
**POST** `/chat/chat`

**请求体**:
```json
{
  "session_id": 1,
  "content": "劳动合同纠纷如何处理？",
  "use_knowledge_base": true
}
```

**响应**:
```json
{
  "message_id": 123,
  "content": "根据《劳动合同法》规定...",
  "role": "assistant",
  "created_at": "2024-01-01T10:35:00"
}
```

### 8. 获取聊天配置
**GET** `/chat/config`

**响应**:
```json
{
  "model_provider": "siliconflow",
  "embedding_model_provider": "siliconflow",
  "available_providers": ["siliconflow", "ollama"]
}
```

### 9. 健康检查
**GET** `/chat/health`

**响应**:
```json
{
  "status": "healthy",
  "service": "chat_api"
}
```

## 调查表相关接口

### 1. 获取调查表模板列表
**GET** `/survey/templates`

**参数**:
- `active_only` (可选): 是否只返回启用的模板，默认true

**响应**: 模板列表

### 2. 获取特定模板
**GET** `/survey/templates/{template_id}`

### 3. 创建模板
**POST** `/survey/templates`

**请求体**:
```json
{
  "name": "企业基本信息调查表",
  "description": "收集企业基本信息",
  "content": {
    "fields": [
      {
        "name": "company_name",
        "label": "企业名称",
        "type": "text",
        "required": true
      }
    ]
  },
  "is_active": true
}
```

### 4. 更新模板
**PUT** `/survey/templates/{template_id}`

**请求体**:
```json
{
  "name": "更新后的模板名称",
  "description": "更新后的描述",
  "is_active": false
}
```

### 5. 删除模板
**DELETE** `/survey/templates/{template_id}`

### 6. 提交调查表
**POST** `/survey/submit`

**请求体**:
```json
{
  "template_id": 1,
  "answers": {
    "company_name": "示例公司",
    "industry": "科技",
    "employee_count": 50
  }
}
```

**响应**:
```json
{
  "record_id": 1,
  "legal_suggestion": {
    "id": 1,
    "content": "根据您提供的信息...",
    "risk_level": "low",
    "suggestions": ["建议1", "建议2"]
  }
}
```

### 7. 获取调查记录
**GET** `/survey/records`

**参数**:
- `template_id` (可选): 模板ID
- `skip` (可选): 跳过记录数，默认0
- `limit` (可选): 返回记录数，默认100

### 8. 获取调查历史
**GET** `/survey/history`

**响应**: 包含历史记录和法律建议的完整历史

### 9. 获取调查记录详情
**GET** `/survey/records/{record_id}`

**参数**:
- `record_id` (路径参数): 记录ID

**响应**: 包含答案和法律建议的完整记录详情

## 知识库相关接口

### 1. 获取知识库统计
**GET** `/knowledge/stats`

**响应**:
```json
{
  "success": true,
  "data": {
    "total_documents": 15,
    "total_chunks": 245,
    "collection_size": "15.2MB",
    "last_updated": "2024-01-01T09:00:00"
  }
}
```

### 2. 获取知识库目录结构
**GET** `/knowledge/directory`

**响应**: 知识库目录树形结构

### 3. 获取知识库文档列表
**GET** `/knowledge/documents`

**参数**:
- `category` (可选): 文档分类过滤（如"案例分析"、"法律文件"等）
- `include_content` (可选): 是否包含文档内容，默认false

**响应**:
```json
{
  "success": true,
  "count": 15,
  "data": [
    {
      "id": "文档唯一标识",
      "filename": "劳动合同纠纷案例.md",
      "path": "案例分析/劳动合同纠纷案例.md",
      "category": "案例分析",
      "extension": ".md",
      "size": "45.2KB",
      "modified": "2024-01-01 10:00:00"
    }
  ]
}
```

### 4. 获取文档内容
**GET** `/knowledge/document/{id}/content`

**参数**:
- `id` (路径参数): 文档ID

**响应**: 包含文档内容的详细信息

### 5. 扫描知识库文档
**POST** `/knowledge/scan`

**功能**: 扫描knowledge_base目录下的文档，更新文档索引

### 6. 向量化文档
**POST** `/knowledge/vectorize`

**参数**:
- `model_provider` (可选): 模型提供商，ollama或siliconflow
- `rebuild` (可选): 是否重建向量存储，默认false

### 7. 搜索知识库
**POST** `/knowledge/search`

**请求体**:
```json
{
  "query": "劳动合同纠纷",
  "top_k": 3,
  "use_simple_mode": true
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "document": "劳动合同纠纷案例.md",
        "content": "案例内容...",
        "score": 0.85
      }
    ]
  }
}
```

### 8. 上传文档
**POST** `/knowledge/upload`

**Content-Type**: `multipart/form-data`

**参数**:
- `file`: 文档文件（支持.md, .txt, .pdf, .docx格式）
- `category` (可选): 分类（如"案例分析"、"法律文件"等）
- `tags` (可选): 标签，逗号分隔

### 9. 创建知识库目录
**POST** `/knowledge/directory/create`

**请求体**:
```json
{
  "directory_name": "新目录名称",
  "parent_path": "可选父目录路径"
}
```

### 10. 删除文档
**DELETE** `/knowledge/document/{id}`

**参数**:
- `id` (路径参数): 文档ID

## 系统状态接口

### 1. 健康检查
**GET** `/chat/health`

**响应**:
```json
{
  "status": "healthy",
  "service": "chat_api"
}
```

### 2. 获取系统信息
**GET** `/chat/config`

**响应**:
```json
{
  "model_provider": "siliconflow",
  "embedding_model_provider": "siliconflow",
  "available_providers": ["siliconflow", "ollama"]
}
```

## 错误处理

所有API使用标准HTTP状态码：

- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

错误响应格式：
```json
{
  "detail": "错误描述信息"
}
```

## 使用示例

### 使用cURL发送聊天消息
```bash
curl -X POST "http://localhost:8000/api/v1/chat/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": 1,
    "content": "劳动合同纠纷如何处理？",
    "use_knowledge_base": true
  }'
```

### 使用cURL获取聊天会话列表
```bash
curl -X GET "http://localhost:8000/api/v1/chat/sessions?limit=10"
```

### 使用cURL提交调查表
```bash
curl -X POST "http://localhost:8000/api/v1/survey/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": 1,
    "answers": {
      "company_name": "测试公司",
      "industry": "科技"
    }
  }'
```

### 使用cURL上传知识库文档
```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/upload" \
  -F "file=@劳动合同纠纷案例.md" \
  -F "category=案例分析"
```

### 使用Python requests提交调查表
```python
import requests

url = "http://localhost:8000/api/v1/survey/submit"
data = {
    "template_id": 1,
    "answers": {
        "company_name": "测试公司",
        "industry": "科技"
    }
}

response = requests.post(url, json=data)
print(response.json())
```

## 注意事项

1. 所有时间戳使用ISO 8601格式
2. 文件上传支持格式：.md, .txt, .pdf, .docx
3. 知识库搜索支持语义检索和关键词检索
4. 聊天接口支持流式响应（SSE）
5. 调查表提交会自动触发法律建议生成
6. 知识库文档分类：案例分析、法律文件、法律指南、合同案例
7. 默认模型提供商：siliconflow，支持切换至ollama
8. 向量存储自动构建，首次使用需运行初始化脚本