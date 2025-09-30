import os
import time
from datetime import datetime
from typing import Any, Union
from obs import ObsClient, ObsException
from dify_plugin import Tool
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from .utils import get_file_extension, get_file_type


class UploadFileTool(Tool):
    """
    华为云OBS工具类 - 上传文件
    """
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Tool.ToolInvokeMessage:
        """
        调用工具上传文件
        
        Args:
            tool_parameters: 工具参数字典，包含文件、目录等信息
            
        Returns:
            ToolInvokeMessage: 包含上传结果的工具调用消息
        """
        # 获取文件
        file = tool_parameters.get("file")
        if not file:
            raise ToolProviderCredentialValidationError("文件不能为空")
        
        # 获取目录
        directory = tool_parameters.get("directory", "")
        
        # 获取文件名
        filename = tool_parameters.get("filename", "")
        
        # 获取文件名模式
        filename_mode = tool_parameters.get("filename_mode", "filename")
        
        # 获取目录模式
        directory_mode = tool_parameters.get("directory_mode", "no_subdirectory")
        
        # 验证凭证
        self._validate_credentials()
        
        # 创建OBS客户端
        client = None
        try:
            client = ObsClient(
                access_key_id=self.runtime.credentials.get("access_key_id"),
                secret_access_key=self.runtime.credentials.get("secret_access_key"),
                server=self.runtime.credentials.get("endpoint")
            )
            
            # 生成文件名
            object_key = self._generate_object_key(file, filename, directory, filename_mode, directory_mode)
            
            # 获取bucket名称
            bucket_name = self.runtime.credentials.get("bucket")
            
            # 上传文件
            resp = client.putObject(bucket_name, object_key, file)
            
            if resp.status < 300:
                # 构建文件URL
                endpoint = self.runtime.credentials.get("endpoint")
                if not endpoint.startswith("http://") and not endpoint.startswith("https://"):
                    endpoint = f"https://{endpoint}"
                
                file_url = f"{endpoint}/{bucket_name}/{object_key}"
                
                # 获取文件大小
                file_size = len(file.getvalue()) if hasattr(file, 'getvalue') else 0
                
                # 获取文件类型
                file_type = get_file_type(file)
                
                # 创建文本消息
                return self.create_text_message(
                    f"文件上传成功\n"
                    f"文件名: {os.path.basename(object_key)}\n"
                    f"文件大小: {file_size} bytes\n"
                    f"文件类型: {file_type}\n"
                    f"文件URL: {file_url}"
                )
            else:
                raise ToolProviderCredentialValidationError(f"文件上传失败: {resp.errorMessage}")
                
        except ObsException as e:
            raise ToolProviderCredentialValidationError(f"OBS操作失败: {e.message}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"文件上传失败: {str(e)}")
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
    
    def _generate_object_key(self, file: Any, filename: str, directory: str, 
                           filename_mode: str, directory_mode: str) -> str:
        """
        生成对象key
        
        Args:
            file: 文件对象
            filename: 指定的文件名
            directory: 指定的目录
            filename_mode: 文件名模式（filename 或 filename_timestamp）
            directory_mode: 目录模式（no_subdirectory, yyyy_mm_dd_hierarchy, yyyy_mm_dd_combined）
            
        Returns:
            str: 生成的对象key
        """
        # 获取文件扩展名
        extension = get_file_extension(file)
        
        # 处理文件名
        if filename:
            # 使用指定的文件名
            if not filename.endswith(extension):
                filename = f"{filename}{extension}"
        else:
            # 使用原始文件名
            if hasattr(file, 'filename') and file.filename:
                original_filename = os.path.splitext(file.filename)[0]
                filename = f"{original_filename}{extension}"
            elif hasattr(file, 'name') and file.name:
                original_filename = os.path.splitext(file.name)[0]
                filename = f"{original_filename}{extension}"
            else:
                # 使用时间戳作为文件名
                timestamp = int(time.time())
                filename = f"file_{timestamp}{extension}"
        
        # 处理文件名模式
        if filename_mode == "filename_timestamp":
            # 添加时间戳
            timestamp = int(time.time())
            name_without_ext = os.path.splitext(filename)[0]
            filename = f"{name_without_ext}_{timestamp}{extension}"
        
        # 处理目录
        if directory_mode == "no_subdirectory":
            # 不使用子目录
            if directory:
                object_key = f"{directory}{filename}"
            else:
                object_key = filename
        elif directory_mode == "yyyy_mm_dd_hierarchy":
            # 使用年/月/日目录结构
            today = datetime.now()
            date_dir = today.strftime("%Y/%m/%d")
            if directory:
                object_key = f"{directory}{date_dir}/{filename}"
            else:
                object_key = f"{date_dir}/{filename}"
        elif directory_mode == "yyyy_mm_dd_combined":
            # 使用年月日组合目录
            today = datetime.now()
            date_dir = today.strftime("%Y%m%d")
            if directory:
                object_key = f"{directory}{date_dir}/{filename}"
            else:
                object_key = f"{date_dir}/{filename}"
        else:
            # 默认不使用子目录
            if directory:
                object_key = f"{directory}{filename}"
            else:
                object_key = filename
        
        return object_key