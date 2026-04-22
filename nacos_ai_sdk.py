#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nacos AI SDK - Python Implementation
=====================================

This is a Python SDK implementation for Nacos AI features including:
- Skill Management
- MCP (Model Context Protocol) Server Management
- Prompt Management

Based on the official Nacos Java SDK v3.2.1
Documentation: https://nacos.io/docs/latest/manual/user/java-sdk/usage/

Author: Nacos Community
License: Apache License 2.0
"""

import asyncio
import hashlib
import json
import zipfile
import io
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# Exception Classes
# ============================================================================

class NacosException(Exception):
    """Base exception for Nacos operations."""
    
    INVALID_PARAM = 400
    NOT_FOUND = 404
    SERVER_ERROR = 500
    NOT_MODIFIED = 304
    
    def __init__(self, err_code: int = SERVER_ERROR, message: str = ""):
        self.err_code = err_code
        self.message = message
        super().__init__(f"[{err_code}] {message}")


# ============================================================================
# Data Models - Prompt
# ============================================================================

@dataclass
class PromptVariable:
    """Prompt variable definition with optional default value."""
    name: str
    default_value: Optional[str] = None
    description: Optional[str] = None


@dataclass
class Prompt:
    """
    Prompt entity for AI Prompt management.
    
    Prompt is stored as a Nacos configuration with fixed group "nacos-ai-prompt"
    and dataId "{promptKey}.json". The content is stored as JSON format.
    """
    prompt_key: str
    version: str
    template: str
    md5: Optional[str] = None
    variables: Optional[List[PromptVariable]] = None
    
    def render(self, user_variables: Optional[Dict[str, str]] = None) -> str:
        """
        Render the prompt template by replacing variables with provided values.
        
        Variables in the template are specified using {{variableName}} syntax.
        This method first applies default values from variable definitions,
        then overrides with user-provided values.
        
        Example:
            prompt = Prompt("greeting", "1.0.0", "Hello {{name}}, welcome to {{place}}!")
            result = prompt.render({"name": "Alice", "place": "Nacos"})
            # Result: "Hello Alice, welcome to Nacos!"
        
        Args:
            user_variables: Map of variable names to their values
            
        Returns:
            Rendered prompt content with variables replaced
        """
        if not self.template:
            return None
        
        merged = {}
        
        # Apply default values from variable definitions
        if self.variables:
            for var in self.variables:
                if var.default_value:
                    merged[var.name] = var.default_value
        
        # Override with user-provided values
        if user_variables:
            merged.update(user_variables)
        
        if not merged:
            return self.template
        
        result = self.template
        for key, value in merged.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, value if value else "")
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "promptKey": self.prompt_key,
            "version": self.version,
            "template": self.template,
            "md5": self.md5,
            "variables": [{"name": v.name, "defaultValue": v.default_value, "description": v.description} 
                         for v in self.variables] if self.variables else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Prompt':
        """Create from dictionary."""
        variables = None
        if data.get("variables"):
            variables = [
                PromptVariable(
                    name=v["name"],
                    default_value=v.get("defaultValue"),
                    description=v.get("description")
                )
                for v in data["variables"]
            ]
        
        return cls(
            prompt_key=data["promptKey"],
            version=data["version"],
            template=data["template"],
            md5=data.get("md5"),
            variables=variables
        )


# ============================================================================
# Data Models - Skill
# ============================================================================

@dataclass
class SkillResource:
    """Claude Skill Resource structure."""
    name: str
    type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    
    def get_resource_identifier(self) -> str:
        """
        Get resource unique identifier.
        Format: "type::name" if type is not blank, otherwise "name".
        """
        if self.type and self.type.strip():
            return f"{self.type}::{self.name}"
        return self.name


@dataclass
class Skill:
    """
    Claude Skill entity for independent Skills management.
    Simplified structure with core fields only.
    """
    namespace_id: str
    name: str
    description: str
    skill_md: Optional[str] = None
    resources: Optional[Dict[str, SkillResource]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "skillMd": self.skill_md,
            "resource": {k: {"name": v.name, "type": v.type, "content": v.content, "metadata": v.metadata}
                        for k, v in self.resources.items()} if self.resources else None
        }


# ============================================================================
# Data Models - MCP Server
# ============================================================================

@dataclass
class McpEndpointInfo:
    """MCP Server endpoint information."""
    address: str
    port: int
    protocol: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class McpCapability:
    """MCP Server capability."""
    name: str
    enabled: bool = True


@dataclass
class McpToolSpecification:
    """MCP Server tool specification."""
    tools: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class McpResourceSpecification:
    """MCP Server resource specification."""
    resources: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class McpServerBasicInfo:
    """AI MCP server basic info in Nacos."""
    name: str
    protocol: str
    description: Optional[str] = None
    namespace_id: Optional[str] = None
    version: Optional[str] = None
    front_protocol: Optional[str] = None
    enabled: bool = True
    status: str = "active"
    capabilities: Optional[List[McpCapability]] = None
    remote_server_config: Optional[Dict[str, Any]] = None
    local_server_config: Optional[Dict[str, Any]] = None


@dataclass
class McpServerDetailInfo(McpServerBasicInfo):
    """AI MCP server detail info in Nacos."""
    backend_endpoints: Optional[List[McpEndpointInfo]] = None
    frontend_endpoints: Optional[List[McpEndpointInfo]] = None
    tool_spec: Optional[McpToolSpecification] = None
    resource_spec: Optional[McpResourceSpecification] = None
    all_versions: Optional[List[Dict[str, Any]]] = None


@dataclass
class McpEndpointSpec:
    """MCP Server endpoint specification."""
    address: str
    port: int
    version: Optional[str] = None


# ============================================================================
# HTTP Client
# ============================================================================

class HttpAgent:
    """HTTP agent for making requests to Nacos server."""
    
    def __init__(self, server_addresses: str, namespace_id: str = "public"):
        """
        Initialize HTTP agent.
        
        Args:
            server_addresses: Nacos server address(es), e.g., "127.0.0.1:8848"
            namespace_id: Namespace identifier
        """
        self.server_addresses = server_addresses.split(",") if isinstance(server_addresses, str) else server_addresses
        self.namespace_id = namespace_id
        self.access_token = None
        self.current_server_index = 0
    
    async def get(self, path: str, params: Optional[Dict[str, Any]] = None, 
                  response_type: str = "json") -> Any:
        """
        Make GET request to Nacos server.
        
        Args:
            path: API path
            params: Query parameters
            response_type: Response type - "json" or "bytes"
            
        Returns:
            Response data
        """
        # This is a simplified implementation
        # In production, use aiohttp or httpx for async HTTP requests
        import urllib.request
        import urllib.parse
        
        server = self.server_addresses[self.current_server_index]
        if not server.startswith("http"):
            server = f"http://{server}"
        
        # Build URL with parameters
        if params:
            query_string = urllib.parse.urlencode(params)
            url = f"{server}{path}?{query_string}"
        else:
            url = f"{server}{path}"
        
        try:
            req = urllib.request.Request(url)
            
            # Add authentication headers if available
            if self.access_token:
                req.add_header("accessToken", self.access_token)
            
            with urllib.request.urlopen(req) as response:
                if response_type == "bytes":
                    return response.read()
                else:
                    data = response.read().decode('utf-8')
                    return json.loads(data)
        
        except Exception as e:
            raise NacosException(NacosException.SERVER_ERROR, f"HTTP request failed: {str(e)}")


# ============================================================================
# Skill Client
# ============================================================================

class SkillClient:
    """
    Client for Nacos Skill management operations.
    Handles downloading and managing Claude Skills from Nacos server.
    """
    
    def __init__(self, http_agent: HttpAgent):
        """
        Initialize the skill client.
        
        Args:
            http_agent: HTTP agent for making requests
        """
        self.http_agent = http_agent
        self.skill_download_path = "/v3/client/ai/skills"
    
    async def download_skill_zip(
        self, 
        skill_name: str, 
        version: Optional[str] = None, 
        label: Optional[str] = None
    ) -> bytes:
        """
        Download skill as ZIP byte array via HTTP REST API.
        
        Args:
            skill_name: Skill name (unique identifier)
            version: Explicit version (optional)
            label: Route label, e.g. 'latest'/'stable' (optional)
            
        Returns:
            ZIP file as byte array
            
        Raises:
            NacosException: If skill not found or request fails
        """
        if not skill_name:
            raise NacosException(NacosException.INVALID_PARAM, 
                               "Required parameter `skill_name` not present")
        
        params = {
            "namespaceId": self.http_agent.namespace_id,
            "name": skill_name
        }
        
        if version:
            params["version"] = version
        if label:
            params["label"] = label
        
        try:
            # Make HTTP GET request for skill ZIP
            zip_bytes = await self.http_agent.get(
                self.skill_download_path, 
                params=params,
                response_type="bytes"
            )
            
            # Validate ZIP bytes
            self._validate_zip_bytes(zip_bytes)
            
            # Validate ZIP entry paths for security
            self._validate_zip_entry_paths(zip_bytes)
            
            return zip_bytes
            
        except Exception as e:
            if isinstance(e, NacosException):
                raise
            raise NacosException(NacosException.SERVER_ERROR, 
                               f"Failed to download skill {skill_name}: {str(e)}")
    
    def _validate_zip_bytes(self, zip_bytes: bytes) -> None:
        """
        Validate that the bytes represent a valid ZIP file.
        
        Args:
            zip_bytes: Bytes to validate
            
        Raises:
            NacosException: If bytes are not a valid ZIP
        """
        if not zip_bytes:
            raise NacosException(NacosException.INVALID_PARAM, 
                               "Skill ZIP bytes are null or empty")
        
        try:
            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
                # Test ZIP integrity
                bad_file = zf.testzip()
                if bad_file:
                    raise NacosException(NacosException.SERVER_ERROR,
                                       f"ZIP file is corrupted: {bad_file}")
        except zipfile.BadZipFile:
            raise NacosException(NacosException.SERVER_ERROR, 
                               "Downloaded data is not a valid ZIP file")
    
    def _validate_zip_entry_paths(self, zip_bytes: bytes) -> None:
        """
        Validate ZIP entry paths to prevent path traversal attacks.
        
        Args:
            zip_bytes: ZIP file bytes
            
        Raises:
            NacosException: If ZIP contains unsafe paths
        """
        try:
            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
                for entry in zf.namelist():
                    # Check for path traversal attempts
                    if ".." in entry or entry.startswith("/"):
                        raise NacosException(
                            NacosException.SERVER_ERROR,
                            f"Unsafe ZIP entry path detected: {entry}"
                        )
        except zipfile.BadZipFile as e:
            raise NacosException(NacosException.SERVER_ERROR, 
                               f"Invalid ZIP file: {str(e)}")
    
    def extract_skill(self, zip_bytes: bytes, target_dir: str) -> None:
        """
        Extract skill ZIP to a directory.
        
        Args:
            zip_bytes: ZIP file bytes
            target_dir: Target directory for extraction
        """
        import os
        
        os.makedirs(target_dir, exist_ok=True)
        
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            zf.extractall(target_dir)


# ============================================================================
# Prompt Client
# ============================================================================

class PromptClient:
    """
    Client for Nacos Prompt management operations.
    """
    
    def __init__(self, http_agent: HttpAgent):
        """
        Initialize the prompt client.
        
        Args:
            http_agent: HTTP agent for making requests
        """
        self.http_agent = http_agent
        self.prompt_path = "/v3/client/ai/prompt"
    
    async def get_prompt(
        self,
        prompt_key: str,
        version: Optional[str] = None,
        label: Optional[str] = None,
        md5: Optional[str] = None
    ) -> Prompt:
        """
        Get prompt by prompt key.
        
        Args:
            prompt_key: Prompt key (unique identifier)
            version: Target prompt version (optional)
            label: Target prompt label (optional)
            md5: MD5 hash for CAS operations (optional)
            
        Returns:
            Prompt object
            
        Raises:
            NacosException: If prompt not found or query error
        """
        if not prompt_key:
            raise NacosException(NacosException.INVALID_PARAM,
                               "Parameter `prompt_key` can't be empty or null")
        
        params = {
            "namespaceId": self.http_agent.namespace_id,
            "promptKey": prompt_key
        }
        
        if version:
            params["version"] = version
        if label:
            params["label"] = label
        if md5:
            params["md5"] = md5
        
        try:
            response = await self.http_agent.get(self.prompt_path, params=params)
            
            # Response format: {"code": 0, "message": "success", "data": {...}}
            if response.get("code") != 0:
                raise NacosException(NacosException.SERVER_ERROR, 
                                   response.get("message", "Unknown error"))
            
            data = response.get("data")
            if not data:
                raise NacosException(NacosException.NOT_FOUND, 
                                   f"Prompt {prompt_key} not found")
            
            return Prompt.from_dict(data)
            
        except Exception as e:
            if isinstance(e, NacosException):
                raise
            raise NacosException(NacosException.SERVER_ERROR, 
                               f"Failed to get prompt {prompt_key}: {str(e)}")


# ============================================================================
# MCP Client
# ============================================================================

class McpClient:
    """
    Client for Nacos MCP server management operations.
    """
    
    def __init__(self, http_agent: HttpAgent):
        """
        Initialize the MCP client.
        
        Args:
            http_agent: HTTP agent for making requests
        """
        self.http_agent = http_agent
        # Note: MCP uses gRPC in the Java implementation
        # This HTTP implementation is simplified for demonstration
        self.mcp_path = "/v3/client/ai/mcp"
    
    async def get_mcp_server(
        self,
        mcp_name: str,
        version: Optional[str] = None
    ) -> McpServerDetailInfo:
        """
        Get MCP server detail info.
        
        Args:
            mcp_name: Name of MCP server
            version: Version of MCP (optional, defaults to latest)
            
        Returns:
            Detail information of MCP server
            
        Raises:
            NacosException: If MCP server not found or query error
        """
        if not mcp_name:
            raise NacosException(NacosException.INVALID_PARAM,
                               "Parameter `mcp_name` can't be empty or null")
        
        params = {
            "namespaceId": self.http_agent.namespace_id,
            "name": mcp_name
        }
        
        if version:
            params["version"] = version
        
        try:
            # This would use gRPC in production
            # For now, using HTTP as a simplified example
            response = await self.http_agent.get(self.mcp_path, params=params)
            
            if response.get("code") != 0:
                raise NacosException(NacosException.SERVER_ERROR,
                                   response.get("message", "Unknown error"))
            
            data = response.get("data")
            if not data:
                raise NacosException(NacosException.NOT_FOUND,
                                   f"MCP server {mcp_name} not found")
            
            # Convert to McpServerDetailInfo
            # Simplified implementation
            return McpServerDetailInfo(
                name=data.get("name"),
                protocol=data.get("protocol"),
                description=data.get("description"),
                namespace_id=data.get("namespaceId"),
                version=data.get("version")
            )
            
        except Exception as e:
            if isinstance(e, NacosException):
                raise
            raise NacosException(NacosException.SERVER_ERROR,
                               f"Failed to get MCP server {mcp_name}: {str(e)}")


# ============================================================================
# Main Nacos AI Service
# ============================================================================

class NacosAiService:
    """
    Main Nacos AI service with Skill, MCP, and Prompt management support.
    
    This is the primary entry point for using Nacos AI features in Python.
    """
    
    def __init__(
        self, 
        server_addresses: str,
        namespace: str = "public",
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Nacos AI Service.
        
        Args:
            server_addresses: Nacos server address(es), e.g., "127.0.0.1:8848"
            namespace: Namespace ID (default: "public")
            username: Username for authentication (optional)
            password: Password for authentication (optional)
            **kwargs: Additional configuration options
        """
        self.namespace_id = namespace
        self.server_addresses = server_addresses
        self.username = username
        self.password = password
        
        # Initialize HTTP agent
        self.http_agent = HttpAgent(server_addresses, namespace)
        
        # Initialize clients
        self.skill_client = SkillClient(self.http_agent)
        self.prompt_client = PromptClient(self.http_agent)
        self.mcp_client = McpClient(self.http_agent)
        
        self._started = False
    
    async def start(self):
        """Start the AI service."""
        if self._started:
            return
        
        # Perform authentication if credentials provided
        if self.username and self.password:
            await self._authenticate()
        
        self._started = True
    
    async def _authenticate(self):
        """Authenticate with Nacos server."""
        # Simplified authentication
        # In production, implement proper Nacos authentication
        pass
    
    # ==================== Skill Management APIs ====================
    
    async def download_skill_zip(self, skill_name: str) -> bytes:
        """
        Download skill as ZIP byte array by skill name (latest version).
        
        Args:
            skill_name: Skill name (unique identifier)
            
        Returns:
            ZIP file as byte array
            
        Raises:
            NacosException: If skill not found or query error
        """
        if not self._started:
            raise NacosException(NacosException.SERVER_ERROR,
                               "Service not started. Call start() first.")
        
        return await self.skill_client.download_skill_zip(skill_name)
    
    async def download_skill_zip_by_version(
        self, 
        skill_name: str, 
        version: str
    ) -> bytes:
        """
        Download skill as ZIP byte array by skill name and version.
        
        Args:
            skill_name: Skill name (unique identifier)
            version: Target skill version
            
        Returns:
            ZIP file as byte array
            
        Raises:
            NacosException: If skill not found or query error
        """
        if not self._started:
            raise NacosException(NacosException.SERVER_ERROR,
                               "Service not started. Call start() first.")
        
        return await self.skill_client.download_skill_zip(skill_name, version=version)
    
    async def download_skill_zip_by_label(
        self, 
        skill_name: str, 
        label: str
    ) -> bytes:
        """
        Download skill as ZIP byte array by skill name and label.
        
        Args:
            skill_name: Skill name (unique identifier)
            label: Target skill label (e.g., "latest", "stable")
            
        Returns:
            ZIP file as byte array
            
        Raises:
            NacosException: If skill not found or query error
        """
        if not self._started:
            raise NacosException(NacosException.SERVER_ERROR,
                               "Service not started. Call start() first.")
        
        return await self.skill_client.download_skill_zip(skill_name, label=label)
    
    async def extract_skill_to_directory(
        self, 
        skill_name: str, 
        target_dir: str,
        version: Optional[str] = None,
        label: Optional[str] = None
    ) -> None:
        """
        Download and extract skill to a directory.
        
        Args:
            skill_name: Skill name
            target_dir: Target directory for extraction
            version: Optional version
            label: Optional label
        """
        zip_bytes = await self.skill_client.download_skill_zip(
            skill_name, version=version, label=label
        )
        
        self.skill_client.extract_skill(zip_bytes, target_dir)
    
    # ==================== Prompt Management APIs ====================
    
    async def get_prompt(self, prompt_key: str) -> Prompt:
        """
        Get prompt by prompt key (latest version).
        
        Args:
            prompt_key: Prompt key (unique identifier)
            
        Returns:
            Prompt object
            
        Raises:
            NacosException: If prompt not found or query error
        """
        if not self._started:
            raise NacosException(NacosException.SERVER_ERROR,
                               "Service not started. Call start() first.")
        
        return await self.prompt_client.get_prompt(prompt_key)
    
    async def get_prompt_by_version(
        self, 
        prompt_key: str, 
        version: str
    ) -> Prompt:
        """
        Get prompt by prompt key and version.
        
        Args:
            prompt_key: Prompt key (unique identifier)
            version: Target prompt version
            
        Returns:
            Prompt object
            
        Raises:
            NacosException: If prompt not found or query error
        """
        if not self._started:
            raise NacosException(NacosException.SERVER_ERROR,
                               "Service not started. Call start() first.")
        
        return await self.prompt_client.get_prompt(prompt_key, version=version)
    
    async def get_prompt_by_label(
        self, 
        prompt_key: str, 
        label: str
    ) -> Prompt:
        """
        Get prompt by prompt key and label.
        
        Args:
            prompt_key: Prompt key (unique identifier)
            label: Target prompt label
            
        Returns:
            Prompt object
            
        Raises:
            NacosException: If prompt not found or query error
        """
        if not self._started:
            raise NacosException(NacosException.SERVER_ERROR,
                               "Service not started. Call start() first.")
        
        return await self.prompt_client.get_prompt(prompt_key, label=label)
    
    # ==================== MCP Server Management APIs ====================
    
    async def get_mcp_server(
        self,
        mcp_name: str,
        version: Optional[str] = None
    ) -> McpServerDetailInfo:
        """
        Get MCP server detail info.
        
        Args:
            mcp_name: Name of MCP server
            version: Version of MCP (optional, defaults to latest)
            
        Returns:
            Detail information of MCP server
            
        Raises:
            NacosException: If MCP server not found or query error
        """
        if not self._started:
            raise NacosException(NacosException.SERVER_ERROR,
                               "Service not started. Call start() first.")
        
        return await self.mcp_client.get_mcp_server(mcp_name, version)
    
    # ==================== Shutdown ====================
    
    async def shutdown(self):
        """Shutdown the AI service and close resources."""
        self._started = False


# ============================================================================
# Usage Examples
# ============================================================================

async def example_skill_management():
    """Example: Skill management usage."""
    print("=" * 60)
    print("Example 1: Skill Management")
    print("=" * 60)
    
    # Initialize Nacos AI Service
    ai_service = NacosAiService(
        server_addresses="127.0.0.1:8848",
        namespace="public"
    )
    
    # Start the service
    await ai_service.start()
    
    try:
        # Download skill by name (latest version)
        skill_zip = await ai_service.download_skill_zip("my-skill")
        print(f"Downloaded skill ZIP: {len(skill_zip)} bytes")
        
        # Download specific version
        skill_zip_v1 = await ai_service.download_skill_zip_by_version(
            "my-skill", 
            "1.0.0"
        )
        print(f"Downloaded skill v1.0.0 ZIP: {len(skill_zip_v1)} bytes")
        
        # Download by label
        skill_zip_latest = await ai_service.download_skill_zip_by_label(
            "my-skill", 
            "latest"
        )
        print(f"Downloaded skill (latest) ZIP: {len(skill_zip_latest)} bytes")
        
        # Extract to directory
        await ai_service.extract_skill_to_directory(
            "my-skill",
            "./skills/my-skill",
            label="latest"
        )
        print("Skill extracted to ./skills/my-skill")
        
    finally:
        await ai_service.shutdown()


async def example_prompt_management():
    """Example: Prompt management usage."""
    print("=" * 60)
    print("Example 2: Prompt Management")
    print("=" * 60)
    
    # Initialize Nacos AI Service
    ai_service = NacosAiService(
        server_addresses="127.0.0.1:8848",
        namespace="public"
    )
    
    await ai_service.start()
    
    try:
        # Get prompt by key
        prompt = await ai_service.get_prompt("greeting-prompt")
        print(f"Prompt: {prompt.prompt_key} v{prompt.version}")
        print(f"Template: {prompt.template}")
        
        # Render prompt with variables
        rendered = prompt.render({
            "name": "Alice",
            "place": "Nacos"
        })
        print(f"Rendered: {rendered}")
        
        # Get specific version
        prompt_v1 = await ai_service.get_prompt_by_version(
            "greeting-prompt",
            "1.0.0"
        )
        print(f"Prompt v1.0.0: {prompt_v1.template}")
        
        # Get by label
        prompt_stable = await ai_service.get_prompt_by_label(
            "greeting-prompt",
            "stable"
        )
        print(f"Stable prompt: {prompt_stable.template}")
        
    finally:
        await ai_service.shutdown()


async def example_mcp_management():
    """Example: MCP server management usage."""
    print("=" * 60)
    print("Example 3: MCP Server Management")
    print("=" * 60)
    
    # Initialize Nacos AI Service
    ai_service = NacosAiService(
        server_addresses="127.0.0.1:8848",
        namespace="public"
    )
    
    await ai_service.start()
    
    try:
        # Get MCP server info
        mcp_server = await ai_service.get_mcp_server("my-mcp-server")
        print(f"MCP Server: {mcp_server.name}")
        print(f"Protocol: {mcp_server.protocol}")
        print(f"Description: {mcp_server.description}")
        
        # Get specific version
        mcp_v1 = await ai_service.get_mcp_server("my-mcp-server", "1.0.0")
        print(f"MCP v1.0.0: {mcp_v1.name}")
        
    finally:
        await ai_service.shutdown()


async def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Nacos AI SDK - Python Examples" + " " * 17 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    try:
        # Run examples
        await example_skill_management()
        print("\n")
        
        await example_prompt_management()
        print("\n")
        
        await example_mcp_management()
        print("\n")
        
    except NacosException as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Run the examples
    print(__doc__)
    asyncio.run(main())
