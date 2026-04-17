# 📋 AI 法律咨询系统

基于FastAPI + Vue3 + PostgreSQL构建的AI法律咨询系统。

## 🎯 项目概述

**AI 法律咨询系统**是一个面向企业的智能法律服务平台，通过 AI 大模型技术结合专业法律知识库，为企业提供实时法律咨询、个性化调查、合同风险诊断一站式法律服务。系统采用前后端分离架构，支持云端与本地 AI 模型，确保数据安全与响应效率。

### 核心特性

- **智能法律咨询**：基于RAG技术的法律问答，结合知识库提供精准回答
- **企业调查分析**：动态表单收集企业信息，实时生成法律建议
- **合同风险诊断**：上传合同文件，自动识别风险条款并提供修改建议
- **知识库管理**：离线法律知识库，支持文档上传、分类管理和语义检索
- **多模型支持**：云端SiliconFlow和本地Ollama双模型支持
- **流式响应**：聊天接口支持Server-Sent Events流式输出

### 技术栈

- **后端**: FastAPI + SQLAlchemy + PostgreSQL + ChromaDB
- **前端**: Vue3 + TypeScript + Element Plus + Pinia + Vue Router + Vite
- **AI模型**: SiliconFlow（云端）、Ollama（本地）
- **向量数据库**: ChromaDB（知识库向量存储）
- **数据库**: PostgreSQL
- **部署**: 支持Docker容器化部署

## 🏗️ 系统架构

### 技术架构图

系统采用分层架构设计，前后端分离，支持云端与本地AI模型混合部署，采用RAG增强技术：

<div align="center">
  <img src="picture/技术框架图.png" alt="AI法律咨询系统技术架构图" width="800">
  <br>
  <em>图：AI法律咨询系统详细技术架构</em>
</div>

## 🏗️ 功能模块

### 1. 法务咨询聊天功能（已完成）
- 支持多轮对话，可切换LLM提供商（SiliconFlow/Ollama）
- 支持ai流式回答
- 支持清空对话、重新生成回答
- RAG增强：LLM自动结合最新调查表内容+历史聊天记录+知识库语义向量+用户问题综合回答，实现个性化法律咨询

<div align="center">
  <img src="picture/home.png" alt="法务咨询聊天界面" width="700">
  <br>
  <em>图：法务咨询聊天界面</em>
</div>

### 2. 企业调查表功能（已完成）
- 用户设置选项的调查表单（单选/多选/填空混合）
- 用户填写/修改企业信息后保存
- **关键逻辑**：任何字段修改 → 触发LLM分析变更 → 生成针对性法律建议
- 支持查看历史修改记录和建议

<div align="center">
  <img src="picture/survey.png" alt="企业调查表界面" width="700">
  <br>
  <em>图：企业调查表界面</em>
</div>

### 3. 知识库管理功能（已完成）
- 基于 `backend/knowledge_base/` 目录的离线知识库系统
- 向量化存储支持语义检索
- 支持文档上传、分类管理
- 与聊天功能深度集成，提供精准法律知识检索

<div align="center">
  <img src="picture/knowledge.png" alt="知识库管理界面" width="700">
  <br>
  <em>图：知识库管理界面</em>
</div>

### 4. 合同智能诊断功能（已完成）
- 支持拖拽上传Word文件（.docx, .doc, .txt格式）
- 后端解析合同文本（python-docx）
- 基于本地知识库进行离线风险识别
- 标注风险条款并给出修改建议
- 支持风险等级分类（高、中、低）
- 提供法条引用和具体修改建议
- 知识库完全离线运行，不依赖外部API（可使用本地Ollama模型）

<div align="center">
  <img src="picture/contract.png" alt="合同智能诊断界面" width="700">
  <br>
  <em>图：合同智能诊断界面</em>
</div>

### 5. 咨询历史管理（已完成）
- 完整记录企业调查表的历史修改记录
- 保存每次LLM生成的法律建议和分析报告
- 提供数据分析和ai报告功能

<div align="center">
  <img src="picture/history.png" alt="咨询历史管理界面" width="700">
  <br>
  <em>图：咨询历史管理界面</em>
</div>

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Git

### 1. 克隆项目
```bash
git clone <https://github.com/doorofnight/Legal_consultation_system.git>
cd Legal_consultation_system
```

### 2. 环境变量配置
将 `backend/.env.example` 文件修改为`backend/.env`，配置以下内容：

**数据库配置**：
```env
POSTGRES_HOST="localhost"
POSTGRES_PORT=5432
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="123456"
POSTGRES_DATABASE="legal_consultation"
```

**AI模型配置**：
```env
# 默认模型提供商
DEFAULT_MODEL_PROVIDER="siliconflow"  # siliconflow, ollama

# 嵌入模型提供商
EMBEDDING_MODEL_PROVIDER="siliconflow"  # siliconflow, ollama

# SiliconFlow配置（云端模型）
SILICONFLOW_API_KEY="your_api_key_here"
SILICONFLOW_BASE_URL="https://api.siliconflow.cn/v1"
SILICONFLOW_MODEL="deepseek-ai/DeepSeek-V3"
SILICONFLOW_EMBEDDING_MODEL="Qwen/Qwen3-Embedding-8B"

# Ollama配置（本地模型）
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL="deepseek-r1:1.5b"
OLLAMA_EMBEDDING_MODEL="qwen3-embedding:0.6b"
```

### 3. 后端部署

#### 方式1：使用脚本启动 (Windows，推荐)
```bash
cd backend
start.bat
```

#### 方式2：手动启动
```bash
cd backend

# 1. 检查Python环境（可选）
python --version

# 2. 创建虚拟环境（如果不存在）
python -m venv venv

# 3. 激活虚拟环境
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 4. 升级pip并安装依赖
pip install --upgrade pip
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 5. 初始化数据库表（需要PostgreSQL服务已启动）
python -c "from app.db.session import engine; from app.db.base import Base; Base.metadata.create_all(bind=engine); print('数据库表创建完成')"

# 6. 初始化知识库向量存储（首次运行需要）
python -c "from app.services.knowledge_service import knowledge_service; knowledge_service.initialize_vector_store(); print('知识库向量存储初始化完成')"

# 7. 启动后端服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 前端部署
```bash
cd frontend
npm install
npm run dev
```

### 5. 访问系统
1. 打开浏览器访问：`http://localhost:5173`
2. 后端API文档：`http://localhost:8000/docs` (Swagger UI)
3. 后端API文档（ReDoc）：`http://localhost:8000/redoc`

### 6. 测试合同诊断功能
1. 进入合同诊断页面
2. 上传合同文件（支持 .docx, .doc, .txt 格式）
3. 系统自动分析合同风险
4. 查看风险条款和建议

## 📈 开发进度

### 已完成功能
- [x] 项目基础目录结构
- [x] 后端环境配置(.env)
- [x] 数据库模型设计(SQLAlchemy)
- [x] FastAPI应用基础框架
- [x] Vue3前端基础框架
- [x] 基础路由和页面布局
- [x] 聊天功能API实现
- [x] AI服务集成（SiliconFlow/Ollama）
- [x] 前端聊天界面
- [x] 会话管理功能
- [x] 企业调查表功能
- [x] 知识库管理系统
- [x] 咨询历史管理
- [x] 合同智能诊断功能
- [x] 文件上传服务
- [x] 文档解析服务
- [x] 风险条款识别算法
- [x] 前端合同上传组件
- [x] 风险分析结果展示
- [x] 流式聊天响应
- [x] RAG增强检索
- [x] 知识库向量化存储
- [x] 多模型支持（SiliconFlow/Ollama）

### 待完成功能
- [ ] 用户认证与权限管理
- [ ] 多语言支持
- [ ] 移动端适配优化
- [ ] 数据导出功能（PDF/Word）
- [ ] 高级统计分析报表
- [ ] 第三方API集成（如电子签名）

## 📚 项目文档

系统提供完整的文档支持，分为以下专门指南：

1. **`README.md`** - 项目主文档，包含项目概述、快速开始、功能说明等核心信息
2. **`API接口文档.md`** - 详细的API接口说明，包含所有端点、参数、请求示例和响应格式
3. **`文件目录文档.md`** - 完整的项目目录结构说明，详细解释每个文件和目录的作用
4. **`本地模型下载指南.md`** - 本地Ollama模型下载、安装和配置指南
5. **`知识库使用指南（必看）.md`** - 知识库向量化、文档添加和使用方法指南
6. **`技术框架图.drawio`** - 系统技术架构图源文件（可使用Draw.io编辑）
7. **`合同诊断样本.txt`** - 合同诊断功能测试样本文件

### 文档使用说明
- **快速开始**：请先阅读README.md了解项目概况和部署步骤
- **API开发**：参考API接口文档.md进行前后端接口对接
- **项目结构**：查看文件目录文档.md了解代码组织架构
- **本地部署**：如需离线运行，参考本地模型下载指南.md配置Ollama
- **知识库管理**：知识库使用指南（必看）.md详细说明如何添加和管理法律文档

## 📄 许可证

本项目采用 MIT 许可证。详情请见 [LICENSE](LICENSE) 文件。
