# 离线法律知识库

本地模型参考使用的离线法律知识库，包含各类法律文档、合同模板、法律条文等。

## 目录结构

```
knowledge_base/
├── README.md                    # 本文件
├── legal_documents/             # 法律条文文档
│   ├── civil_code/             # 民法典相关
│   ├── labor_law/              # 劳动法相关
│   ├── contract_law/           # 合同法相关
│   └── company_law/            # 公司法相关
├── contract_templates/          # 合同模板
│   ├── labor_contract/         # 劳动合同模板
│   ├── service_contract/       # 服务合同模板
│   ├── lease_contract/         # 租赁合同模板
│   └── sales_contract/         # 销售合同模板
├── case_analysis/              # 案例分析
│   ├── labor_disputes/         # 劳动纠纷案例
│   ├── contract_disputes/      # 合同纠纷案例
│   └── intellectual_property/  # 知识产权案例
├── legal_guidelines/           # 法律指南
│   ├── compliance_guide/       # 合规指南
│   ├── risk_prevention/        # 风险防范指南
│   └── legal_procedures/       # 法律程序指南
└── vector_store/               # 向量存储（自动生成）
    ├── embeddings/             # 嵌入向量
    └── metadata/               # 元数据
```

## 使用说明

1. **文档格式**：支持 `.txt`, `.md`, `.pdf`, `.docx` 格式
2. **文档命名**：使用中文命名，清晰描述文档内容
3. **文档分类**：按照目录结构分类存放
4. **向量化**：系统会自动将文档转换为向量并存储到 `vector_store/`

## 系统集成

- **前端显示**：在法务咨询和合同诊断页面显示"离线法律知识库"
- **模型参考**：本地模型（Ollama）会参考知识库内容生成回答
- **检索功能**：基于向量相似度检索相关法律知识

## 维护指南

1. 定期更新法律条文和案例
2. 添加新的合同模板
3. 清理过时的文档
4. 重新生成向量索引（当文档更新时）