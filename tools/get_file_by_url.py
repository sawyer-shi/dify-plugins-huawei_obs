import os
from typing import Any, Union
from urllib.parse import urlparse
from obs import ObsClient, ObsException
from dify_plugin import Tool
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class GetFileByUrlTool(Tool):
    """
    华为云OBS工具类 - 通过URL获取文件
    """
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Tool.ToolInvokeMessage:
        """
        调用工具获取文件
        
        Args:
            tool_parameters: 工具参数字典，包含文件URL
            
        Returns:
            ToolInvokeMessage: 包含文件数据的工具调用消息
        """
        # 获取文件URL
        file_url = tool_parameters.get("file_url")
        if not file_url:
            raise ToolProviderCredentialValidationError("文件URL不能为空")
        
        # 验证凭证
        self._validate_credentials()
        
        # 解析URL获取bucket和object key
        bucket_name, object_key = self._parse_url(file_url)
        
        # 创建OBS客户端
        client = None
        try:
            client = ObsClient(
                access_key_id=self.runtime.credentials.get("access_key_id"),
                secret_access_key=self.runtime.credentials.get("secret_access_key"),
                server=self.runtime.credentials.get("endpoint")
            )
            
            # 获取文件
            resp = client.getObject(bucket_name, object_key)
            
            if resp.status < 300:
                # 获取文件内容
                file_content = resp.body.response.read()
                
                # 获取文件元数据
                metadata = resp.body.metadata
                
                # 创建blob消息
                return self.create_blob_message(
                    blob=file_content,
                    meta={
                        "mime_type": metadata.get("contenttype", "application/octet-stream"),
                        "file_name": os.path.basename(object_key)
                    }
                )
            else:
                raise ToolProviderCredentialValidationError(f"获取文件失败: {resp.errorMessage}")
                
        except ObsException as e:
            raise ToolProviderCredentialValidationError(f"OBS操作失败: {e.message}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"获取文件失败: {str(e)}")
        finally:
            if client:
                client.close()
    
    def _validate_credentials(self) -> None:
        """
        验证凭证
        
        Raises:
            ToolProviderCredentialValidationError: 凭证验证失败时抛出
        """
        # 检查必需字段
        required_fields = ["access_key_id", "secret_access_key", "endpoint", "bucket"]
        for field in required_fields:
            if not self.runtime.credentials.get(field):
                raise ToolProviderCredentialValidationError(f"缺少必需字段: {field}")
        
        # 验证目录格式
        directory = self.runtime.credentials.get("directory", "")
        if directory and not directory.endswith("/"):
            raise ToolProviderCredentialValidationError("目录必须以/结尾")
        
        # 验证文件名格式
        filename = self.runtime.credentials.get("filename", "")
        if filename and (" " in filename or "/" in filename):
            raise ToolProviderCredentialValidationError("文件名不能包含空格或斜杠")
    
    def _parse_url(self, url: str) -> tuple[str, str]:
        """
        解析OBS URL获取bucket名称和对象key
        
        Args:
            url: OBS文件URL
            
        Returns:
            tuple: (bucket名称, 对象key)
            
        Raises:
            ToolProviderCredentialValidationError: URL解析失败时抛出
        """
        try:
            # 解析URL
            parsed = urlparse(url)
            
            # 获取endpoint
            endpoint = self.runtime.credentials.get("endpoint")
            if not endpoint:
                raise ToolProviderCredentialValidationError("缺少endpoint配置")
            
            # 确保endpoint格式正确
            if not endpoint.startswith("http://") and not endpoint.startswith("https://"):
                endpoint = f"https://{endpoint}"
            
            # 解析endpoint
            endpoint_parsed = urlparse(endpoint)
            endpoint_host = endpoint_parsed.netloc or endpoint_parsed.path
            
            # 验证URL是否匹配endpoint
            if parsed.netloc != endpoint_host:
                raise ToolProviderCredentialValidationError(f"URL与endpoint不匹配: {parsed.netloc} != {endpoint_host}")
            
            # 获取路径部分
            path = parsed.path.lstrip("/")
            
            # 获取bucket名称（路径的第一部分）
            path_parts = path.split("/", 1)
            if len(path_parts) < 1:
                raise ToolProviderCredentialValidationError("无法从URL中解析bucket名称")
            
            bucket_name = path_parts[0]
            
            # 获取对象key（路径的其余部分）
            object_key = path_parts[1] if len(path_parts) > 1 else ""
            
            if not object_key:
                raise ToolProviderCredentialValidationError("无法从URL中解析对象key")
            
            return bucket_name, object_key
            
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"URL解析失败: {str(e)}")