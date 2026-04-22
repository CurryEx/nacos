# Nacos AI Python SDK - 文件索引

## 📁 文件列表 / File List

### 主要文件 / Main Files

1. **nacos_ai_sdk.py** - Python SDK 主实现文件
   - 大小: 32KB (1037行)
   - 功能: 完整的 Skill、MCP、Prompt 管理实现
   - 可运行: ✅ (包含示例代码)

### 文档文件 / Documentation Files

2. **NACOS_AI_SDK_README.md** - 完整文档
   - 大小: 12KB (443行)
   - 语言: 中文 + English
   - 内容: 完整 API 参考、使用指南、数据模型

3. **QUICK_REFERENCE.md** - 快速参考
   - 大小: 6.7KB (274行)  
   - 语言: 中文 + English
   - 内容: 代码示例速查、常用 API

4. **PYTHON_SDK_SUMMARY.md** - 实现总结
   - 大小: 4.6KB (201行)
   - 语言: 中文
   - 内容: 架构设计、功能特性、统计信息

5. **本文件 (INDEX.md)** - 文件索引
   - 大小: ~2KB
   - 语言: 中文 + English
   - 内容: 文件导航和使用建议

---

## 🚀 快速开始 / Quick Start

### 1. 查看示例 / View Examples
```bash
# 运行内置示例
python3 nacos_ai_sdk.py
```

### 2. 阅读文档 / Read Documentation
- 新手: 先看 [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
- 详细: 再看 [NACOS_AI_SDK_README.md](./NACOS_AI_SDK_README.md)
- 总结: 最后看 [PYTHON_SDK_SUMMARY.md](./PYTHON_SDK_SUMMARY.md)

### 3. 集成到项目 / Integrate to Project
```bash
# 复制 SDK 文件到你的项目
cp nacos_ai_sdk.py /path/to/your/project/
```

---

## 📖 文档阅读顺序 / Reading Order

### 初学者路径 / Beginner Path
1. **QUICK_REFERENCE.md** - 快速上手 (10分钟)
2. **nacos_ai_sdk.py** - 运行示例代码 (5分钟)
3. **NACOS_AI_SDK_README.md** - 深入学习 (30分钟)

### 开发者路径 / Developer Path
1. **PYTHON_SDK_SUMMARY.md** - 了解架构 (10分钟)
2. **nacos_ai_sdk.py** - 阅读源码 (30分钟)
3. **NACOS_AI_SDK_README.md** - API 参考 (需要时查阅)

### 贡献者路径 / Contributor Path
1. **PYTHON_SDK_SUMMARY.md** - 架构和设计
2. **nacos_ai_sdk.py** - 源码实现
3. **所有文档** - 确保文档完整性

---

## 🎯 使用场景 / Use Cases

### Skill 管理
```python
# 下载 Claude Skill
skill_zip = await ai_service.download_skill_zip("my-skill")

# 解压到目录
await ai_service.extract_skill_to_directory(
    "my-skill", "./skills/my-skill"
)
```

### Prompt 管理
```python
# 获取并渲染 Prompt
prompt = await ai_service.get_prompt("greeting")
text = prompt.render({"name": "用户"})
```

### MCP 服务器管理
```python
# 获取 MCP 服务器信息
mcp = await ai_service.get_mcp_server("my-mcp")
print(mcp.protocol, mcp.backend_endpoints)
```

---

## 🔍 功能查找 / Feature Finder

### 我想...

#### 下载 Skill
→ 查看: `QUICK_REFERENCE.md` → Skill 管理部分  
→ API: `download_skill_zip()`, `download_skill_zip_by_version()`, `download_skill_zip_by_label()`

#### 使用 Prompt
→ 查看: `QUICK_REFERENCE.md` → Prompt 管理部分  
→ API: `get_prompt()`, `prompt.render()`

#### 查询 MCP 服务器
→ 查看: `QUICK_REFERENCE.md` → MCP 服务器管理部分  
→ API: `get_mcp_server()`

#### 了解完整 API
→ 查看: `NACOS_AI_SDK_README.md` → API Reference 部分

#### 了解架构设计
→ 查看: `PYTHON_SDK_SUMMARY.md` → 架构设计部分

#### 查看示例代码
→ 运行: `python3 nacos_ai_sdk.py`  
→ 或查看: `nacos_ai_sdk.py` 文件底部的示例

---

## 📊 文件大小统计 / File Statistics

| 文件 | 大小 | 行数 | 用途 |
|------|------|------|------|
| nacos_ai_sdk.py | 32KB | 1037 | 主实现 |
| NACOS_AI_SDK_README.md | 12KB | 443 | 完整文档 |
| QUICK_REFERENCE.md | 6.7KB | 274 | 快速参考 |
| PYTHON_SDK_SUMMARY.md | 4.6KB | 201 | 实现总结 |
| INDEX.md (本文件) | ~2KB | ~150 | 文件索引 |
| **总计** | **~57KB** | **~2105** | - |

---

## 💡 最佳实践 / Best Practices

### 1. 开发环境
```python
# 开发时使用详细的错误处理
from nacos_ai_sdk import NacosException

try:
    result = await ai_service.download_skill_zip("skill")
except NacosException as e:
    print(f"Error [{e.err_code}]: {e.message}")
```

### 2. 生产环境
```python
# 生产环境添加日志和重试
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    result = await ai_service.download_skill_zip("skill")
    logger.info(f"Downloaded {len(result)} bytes")
except NacosException as e:
    logger.error(f"Failed to download: {e}")
    # 实现重试逻辑
```

### 3. 资源管理
```python
# 总是使用 try-finally 确保资源释放
ai_service = NacosAiService(...)
await ai_service.start()

try:
    # 你的代码
    pass
finally:
    await ai_service.shutdown()
```

---

## 🔗 相关链接 / Related Links

### 内部文档
- [完整 README](./NACOS_AI_SDK_README.md)
- [快速参考](./QUICK_REFERENCE.md)
- [实现总结](./PYTHON_SDK_SUMMARY.md)
- [源代码](./nacos_ai_sdk.py)

### 外部资源
- [Nacos 官方网站](https://nacos.io)
- [Nacos 官方文档](https://nacos.io/docs/latest/)
- [Java SDK 文档](https://nacos.io/docs/latest/manual/user/java-sdk/usage/)
- [GitHub 仓库](https://github.com/alibaba/nacos)

---

## ❓ 常见问题 / FAQ

### Q: 如何安装？
A: 无需安装，直接复制 `nacos_ai_sdk.py` 到项目即可。

### Q: 有依赖吗？
A: 没有，仅使用 Python 标准库。

### Q: 支持哪些 Python 版本？
A: Python 3.7+

### Q: 如何运行示例？
A: 执行 `python3 nacos_ai_sdk.py`

### Q: 如何获取帮助？
A: 查看文档或提交 Issue

---

## 📝 更新日志 / Changelog

### v1.0.0 (2026-04-22)
- ✅ 初始版本发布
- ✅ 实现 Skill、MCP、Prompt 管理
- ✅ 完整的文档和示例
- ✅ 通过基本测试验证

---

## 📄 许可证 / License

Apache License 2.0

---

**最后更新**: 2026-04-22  
**Python 版本**: 3.7+  
**基于**: Nacos Java SDK v3.2.1
