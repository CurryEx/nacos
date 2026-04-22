# Nacos AI SDK - Quick Reference Guide

## 快速参考 / Quick Reference

### Python 版本要求 / Python Version
- Python 3.7+
- 仅使用标准库 / Standard library only

---

## 使用方法 / Usage

### 1. 导入 SDK / Import SDK

```python
from nacos_ai_sdk import (
    NacosAiService,
    NacosException,
    Prompt,
    Skill,
    McpServerDetailInfo
)
```

### 2. 初始化服务 / Initialize Service

```python
import asyncio

async def main():
    # 创建服务实例 / Create service instance
    ai_service = NacosAiService(
        server_addresses="127.0.0.1:8848",  # Nacos 服务器地址
        namespace="public",                  # 命名空间
        username="nacos",                    # 可选：用户名
        password="nacos"                     # 可选：密码
    )
    
    # 启动服务 / Start service
    await ai_service.start()
    
    try:
        # 你的代码 / Your code here
        pass
    finally:
        # 关闭服务 / Shutdown service
        await ai_service.shutdown()

# 运行 / Run
asyncio.run(main())
```

---

## API 速查表 / API Cheat Sheet

### Skill 管理 / Skill Management

```python
# 下载最新版本 / Download latest version
zip_bytes = await ai_service.download_skill_zip("skill-name")

# 下载指定版本 / Download specific version
zip_bytes = await ai_service.download_skill_zip_by_version("skill-name", "1.0.0")

# 按标签下载 / Download by label
zip_bytes = await ai_service.download_skill_zip_by_label("skill-name", "latest")

# 下载并解压 / Download and extract
await ai_service.extract_skill_to_directory(
    skill_name="skill-name",
    target_dir="./skills/skill-name",
    label="latest"  # 可选 / optional
)
```

### Prompt 管理 / Prompt Management

```python
# 获取最新版本 / Get latest version
prompt = await ai_service.get_prompt("prompt-key")

# 获取指定版本 / Get specific version
prompt = await ai_service.get_prompt_by_version("prompt-key", "1.0.0")

# 按标签获取 / Get by label
prompt = await ai_service.get_prompt_by_label("prompt-key", "stable")

# 渲染 Prompt / Render prompt
rendered_text = prompt.render({
    "variable1": "value1",
    "variable2": "value2"
})
```

### MCP 服务器管理 / MCP Server Management

```python
# 获取最新版本 / Get latest version
mcp_server = await ai_service.get_mcp_server("mcp-name")

# 获取指定版本 / Get specific version
mcp_server = await ai_service.get_mcp_server("mcp-name", "1.0.0")

# 访问属性 / Access properties
print(mcp_server.name)
print(mcp_server.protocol)
print(mcp_server.description)
print(mcp_server.backend_endpoints)
```

---

## 数据结构 / Data Structures

### Prompt 对象 / Prompt Object

```python
prompt = Prompt(
    prompt_key="greeting",
    version="1.0.0",
    template="Hello {{name}}!",
    variables=[
        PromptVariable(name="name", default_value="World")
    ]
)

# 渲染 / Render
result = prompt.render({"name": "Alice"})  # "Hello Alice!"
result = prompt.render({})                 # "Hello World!" (使用默认值)
```

### Skill 对象 / Skill Object

```python
skill = Skill(
    namespace_id="public",
    name="my-skill",
    description="My awesome skill",
    skill_md="# Skill documentation...",
    resources={
        "config.json": SkillResource(
            name="config.json",
            type="config",
            content="{...}"
        )
    }
)
```

### MCP 服务器对象 / MCP Server Object

```python
mcp_server = McpServerDetailInfo(
    name="my-mcp",
    protocol="http",
    description="My MCP server",
    version="1.0.0",
    backend_endpoints=[
        McpEndpointInfo(
            address="127.0.0.1",
            port=8080
        )
    ]
)
```

---

## 错误处理 / Error Handling

```python
from nacos_ai_sdk import NacosException

try:
    skill = await ai_service.download_skill_zip("non-existent-skill")
except NacosException as e:
    # 错误代码 / Error code
    print(f"Error Code: {e.err_code}")
    
    # 错误消息 / Error message
    print(f"Error Message: {e.message}")
    
    # 常见错误代码 / Common error codes:
    # 400 - INVALID_PARAM (无效参数 / Invalid parameter)
    # 404 - NOT_FOUND (未找到 / Not found)
    # 500 - SERVER_ERROR (服务器错误 / Server error)
    # 304 - NOT_MODIFIED (未修改 / Not modified)
```

---

## 完整示例 / Complete Example

```python
import asyncio
from nacos_ai_sdk import NacosAiService, NacosException

async def example():
    # 1. 初始化 / Initialize
    ai_service = NacosAiService(
        server_addresses="127.0.0.1:8848",
        namespace="public"
    )
    
    await ai_service.start()
    
    try:
        # 2. 下载 Skill / Download skill
        print("Downloading skill...")
        skill_zip = await ai_service.download_skill_zip("my-skill")
        print(f"✓ Downloaded {len(skill_zip)} bytes")
        
        # 3. 获取 Prompt / Get prompt
        print("\nGetting prompt...")
        prompt = await ai_service.get_prompt("greeting")
        print(f"✓ Prompt: {prompt.template}")
        
        # 4. 渲染 Prompt / Render prompt
        rendered = prompt.render({"name": "Developer"})
        print(f"✓ Rendered: {rendered}")
        
        # 5. 获取 MCP 服务器 / Get MCP server
        print("\nGetting MCP server...")
        mcp = await ai_service.get_mcp_server("my-mcp")
        print(f"✓ MCP: {mcp.name} ({mcp.protocol})")
        
    except NacosException as e:
        print(f"✗ Error: [{e.err_code}] {e.message}")
    
    finally:
        # 6. 关闭 / Shutdown
        await ai_service.shutdown()

# 运行 / Run
if __name__ == "__main__":
    asyncio.run(example())
```

---

## 提示 / Tips

1. **异步编程 / Async Programming**
   - 所有 API 调用都是异步的 / All API calls are async
   - 必须使用 `await` / Must use `await`
   - 在 `async` 函数中运行 / Run in `async` functions

2. **错误处理 / Error Handling**
   - 总是捕获 `NacosException` / Always catch `NacosException`
   - 检查错误代码以确定问题类型 / Check error code to determine issue type

3. **资源管理 / Resource Management**
   - 使用 `try-finally` 确保关闭 / Use `try-finally` to ensure shutdown
   - 调用 `shutdown()` 清理资源 / Call `shutdown()` to cleanup resources

4. **生产使用 / Production Use**
   - 考虑添加重试逻辑 / Consider adding retry logic
   - 实现连接池 / Implement connection pooling
   - 使用 `aiohttp` 替代标准库 / Use `aiohttp` instead of stdlib

---

## 相关文档 / Related Documentation

- 完整文档 / Full Documentation: `NACOS_AI_SDK_README.md`
- 源代码 / Source Code: `nacos_ai_sdk.py`
- 官方文档 / Official Docs: https://nacos.io/docs/latest/

---

## 许可证 / License

Apache License 2.0
