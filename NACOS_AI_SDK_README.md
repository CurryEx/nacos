# Nacos AI SDK - Python Implementation

[中文版](#中文文档) | [English](#english-documentation)

---

## English Documentation

### Overview

This is a comprehensive Python SDK for Nacos AI features, providing support for:
- **Skill Management**: Download and manage Claude Skills
- **MCP Server Management**: Query and interact with Model Context Protocol servers
- **Prompt Management**: Retrieve and render AI prompts with variable substitution

Based on the official [Nacos Java SDK v3.2.1](https://nacos.io/docs/latest/manual/user/java-sdk/usage/).

### Installation

Simply copy `nacos_ai_sdk.py` to your project directory:

```bash
cp nacos_ai_sdk.py /path/to/your/project/
```

No additional dependencies required (uses Python standard library).

### Quick Start

#### 1. Basic Initialization

```python
import asyncio
from nacos_ai_sdk import NacosAiService

async def main():
    # Initialize the service
    ai_service = NacosAiService(
        server_addresses="127.0.0.1:8848",
        namespace="public"
    )
    
    # Start the service
    await ai_service.start()
    
    try:
        # Your code here
        pass
    finally:
        await ai_service.shutdown()

asyncio.run(main())
```

#### 2. Skill Management

```python
# Download skill (latest version)
skill_zip = await ai_service.download_skill_zip("my-skill")
print(f"Downloaded: {len(skill_zip)} bytes")

# Download specific version
skill_v1 = await ai_service.download_skill_zip_by_version("my-skill", "1.0.0")

# Download by label
skill_latest = await ai_service.download_skill_zip_by_label("my-skill", "latest")

# Extract to directory
await ai_service.extract_skill_to_directory(
    "my-skill",
    "./skills/my-skill",
    label="latest"
)
```

#### 3. Prompt Management

```python
# Get prompt
prompt = await ai_service.get_prompt("greeting-prompt")
print(f"Template: {prompt.template}")

# Render prompt with variables
rendered = prompt.render({
    "name": "Alice",
    "place": "Nacos"
})
print(f"Result: {rendered}")

# Get specific version
prompt_v1 = await ai_service.get_prompt_by_version("greeting-prompt", "1.0.0")

# Get by label
prompt_stable = await ai_service.get_prompt_by_label("greeting-prompt", "stable")
```

#### 4. MCP Server Management

```python
# Get MCP server info
mcp_server = await ai_service.get_mcp_server("my-mcp-server")
print(f"Name: {mcp_server.name}")
print(f"Protocol: {mcp_server.protocol}")
print(f"Description: {mcp_server.description}")

# Get specific version
mcp_v1 = await ai_service.get_mcp_server("my-mcp-server", "1.0.0")
```

### API Reference

#### Skill Management APIs

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `download_skill_zip(skill_name)` | Download skill (latest) | skill_name: str | bytes |
| `download_skill_zip_by_version(skill_name, version)` | Download specific version | skill_name: str, version: str | bytes |
| `download_skill_zip_by_label(skill_name, label)` | Download by label | skill_name: str, label: str | bytes |
| `extract_skill_to_directory(skill_name, target_dir, version?, label?)` | Download and extract | skill_name: str, target_dir: str, version?: str, label?: str | None |

#### Prompt Management APIs

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `get_prompt(prompt_key)` | Get prompt (latest) | prompt_key: str | Prompt |
| `get_prompt_by_version(prompt_key, version)` | Get specific version | prompt_key: str, version: str | Prompt |
| `get_prompt_by_label(prompt_key, label)` | Get by label | prompt_key: str, label: str | Prompt |

#### MCP Server Management APIs

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `get_mcp_server(mcp_name, version?)` | Get MCP server info | mcp_name: str, version?: str | McpServerDetailInfo |

### Data Models

#### Prompt

```python
@dataclass
class Prompt:
    prompt_key: str
    version: str
    template: str
    md5: Optional[str] = None
    variables: Optional[List[PromptVariable]] = None
    
    def render(self, user_variables: Dict[str, str]) -> str:
        """Render template with variables"""
```

#### Skill

```python
@dataclass
class Skill:
    namespace_id: str
    name: str
    description: str
    skill_md: Optional[str] = None
    resources: Optional[Dict[str, SkillResource]] = None
```

#### McpServerDetailInfo

```python
@dataclass
class McpServerDetailInfo:
    name: str
    protocol: str
    description: Optional[str] = None
    namespace_id: Optional[str] = None
    version: Optional[str] = None
    backend_endpoints: Optional[List[McpEndpointInfo]] = None
    frontend_endpoints: Optional[List[McpEndpointInfo]] = None
    tool_spec: Optional[McpToolSpecification] = None
    resource_spec: Optional[McpResourceSpecification] = None
```

### Error Handling

```python
from nacos_ai_sdk import NacosException

try:
    skill = await ai_service.download_skill_zip("my-skill")
except NacosException as e:
    print(f"Error [{e.err_code}]: {e.message}")
```

Error Codes:
- `400`: `INVALID_PARAM` - Invalid parameters
- `404`: `NOT_FOUND` - Resource not found
- `500`: `SERVER_ERROR` - Server error
- `304`: `NOT_MODIFIED` - Resource not modified

### Examples

Run the included examples:

```bash
python nacos_ai_sdk.py
```

This will run all three example scenarios:
1. Skill Management
2. Prompt Management
3. MCP Server Management

### Notes

1. **HTTP vs gRPC**: This implementation uses HTTP for simplicity. The Java SDK uses gRPC for MCP operations.
2. **Authentication**: Basic authentication is included but not fully implemented. Extend `_authenticate()` method as needed.
3. **Async/Await**: All API calls are asynchronous. Use `await` when calling methods.
4. **Production Ready**: For production use, consider:
   - Using `aiohttp` or `httpx` for better async HTTP support
   - Implementing proper connection pooling
   - Adding retry logic
   - Implementing subscription/listener patterns for real-time updates

### License

Apache License 2.0

---

## 中文文档

### 概述

这是一个全面的 Nacos AI 功能 Python SDK，提供以下支持：
- **Skill 管理**：下载和管理 Claude Skills
- **MCP 服务器管理**：查询和交互模型上下文协议服务器
- **Prompt 管理**：检索和渲染带变量替换的 AI 提示词

基于官方 [Nacos Java SDK v3.2.1](https://nacos.io/docs/latest/manual/user/java-sdk/usage/)。

### 安装

只需将 `nacos_ai_sdk.py` 复制到您的项目目录：

```bash
cp nacos_ai_sdk.py /path/to/your/project/
```

无需额外依赖（仅使用 Python 标准库）。

### 快速开始

#### 1. 基本初始化

```python
import asyncio
from nacos_ai_sdk import NacosAiService

async def main():
    # 初始化服务
    ai_service = NacosAiService(
        server_addresses="127.0.0.1:8848",
        namespace="public"
    )
    
    # 启动服务
    await ai_service.start()
    
    try:
        # 你的代码
        pass
    finally:
        await ai_service.shutdown()

asyncio.run(main())
```

#### 2. Skill 管理

```python
# 下载 skill（最新版本）
skill_zip = await ai_service.download_skill_zip("my-skill")
print(f"已下载: {len(skill_zip)} 字节")

# 下载指定版本
skill_v1 = await ai_service.download_skill_zip_by_version("my-skill", "1.0.0")

# 按标签下载
skill_latest = await ai_service.download_skill_zip_by_label("my-skill", "latest")

# 解压到目录
await ai_service.extract_skill_to_directory(
    "my-skill",
    "./skills/my-skill",
    label="latest"
)
```

#### 3. Prompt 管理

```python
# 获取 prompt
prompt = await ai_service.get_prompt("greeting-prompt")
print(f"模板: {prompt.template}")

# 使用变量渲染 prompt
rendered = prompt.render({
    "name": "小明",
    "place": "Nacos"
})
print(f"结果: {rendered}")

# 获取指定版本
prompt_v1 = await ai_service.get_prompt_by_version("greeting-prompt", "1.0.0")

# 按标签获取
prompt_stable = await ai_service.get_prompt_by_label("greeting-prompt", "stable")
```

#### 4. MCP 服务器管理

```python
# 获取 MCP 服务器信息
mcp_server = await ai_service.get_mcp_server("my-mcp-server")
print(f"名称: {mcp_server.name}")
print(f"协议: {mcp_server.protocol}")
print(f"描述: {mcp_server.description}")

# 获取指定版本
mcp_v1 = await ai_service.get_mcp_server("my-mcp-server", "1.0.0")
```

### API 参考

#### Skill 管理 API

| 方法 | 描述 | 参数 | 返回值 |
|------|------|------|--------|
| `download_skill_zip(skill_name)` | 下载 skill（最新） | skill_name: str | bytes |
| `download_skill_zip_by_version(skill_name, version)` | 下载指定版本 | skill_name: str, version: str | bytes |
| `download_skill_zip_by_label(skill_name, label)` | 按标签下载 | skill_name: str, label: str | bytes |
| `extract_skill_to_directory(skill_name, target_dir, version?, label?)` | 下载并解压 | skill_name: str, target_dir: str, version?: str, label?: str | None |

#### Prompt 管理 API

| 方法 | 描述 | 参数 | 返回值 |
|------|------|------|--------|
| `get_prompt(prompt_key)` | 获取 prompt（最新） | prompt_key: str | Prompt |
| `get_prompt_by_version(prompt_key, version)` | 获取指定版本 | prompt_key: str, version: str | Prompt |
| `get_prompt_by_label(prompt_key, label)` | 按标签获取 | prompt_key: str, label: str | Prompt |

#### MCP 服务器管理 API

| 方法 | 描述 | 参数 | 返回值 |
|------|------|------|--------|
| `get_mcp_server(mcp_name, version?)` | 获取 MCP 服务器信息 | mcp_name: str, version?: str | McpServerDetailInfo |

### 数据模型

#### Prompt

```python
@dataclass
class Prompt:
    prompt_key: str
    version: str
    template: str
    md5: Optional[str] = None
    variables: Optional[List[PromptVariable]] = None
    
    def render(self, user_variables: Dict[str, str]) -> str:
        """使用变量渲染模板"""
```

#### Skill

```python
@dataclass
class Skill:
    namespace_id: str
    name: str
    description: str
    skill_md: Optional[str] = None
    resources: Optional[Dict[str, SkillResource]] = None
```

#### McpServerDetailInfo

```python
@dataclass
class McpServerDetailInfo:
    name: str
    protocol: str
    description: Optional[str] = None
    namespace_id: Optional[str] = None
    version: Optional[str] = None
    backend_endpoints: Optional[List[McpEndpointInfo]] = None
    frontend_endpoints: Optional[List[McpEndpointInfo]] = None
    tool_spec: Optional[McpToolSpecification] = None
    resource_spec: Optional[McpResourceSpecification] = None
```

### 错误处理

```python
from nacos_ai_sdk import NacosException

try:
    skill = await ai_service.download_skill_zip("my-skill")
except NacosException as e:
    print(f"错误 [{e.err_code}]: {e.message}")
```

错误代码：
- `400`: `INVALID_PARAM` - 无效参数
- `404`: `NOT_FOUND` - 资源未找到
- `500`: `SERVER_ERROR` - 服务器错误
- `304`: `NOT_MODIFIED` - 资源未修改

### 示例

运行包含的示例：

```bash
python nacos_ai_sdk.py
```

这将运行所有三个示例场景：
1. Skill 管理
2. Prompt 管理
3. MCP 服务器管理

### 注意事项

1. **HTTP vs gRPC**：此实现为简化使用 HTTP。Java SDK 对 MCP 操作使用 gRPC。
2. **认证**：包含基本认证但未完全实现。根据需要扩展 `_authenticate()` 方法。
3. **异步/等待**：所有 API 调用都是异步的。调用方法时使用 `await`。
4. **生产就绪**：对于生产使用，请考虑：
   - 使用 `aiohttp` 或 `httpx` 以获得更好的异步 HTTP 支持
   - 实现适当的连接池
   - 添加重试逻辑
   - 实现订阅/监听器模式以进行实时更新

### 许可证

Apache License 2.0
