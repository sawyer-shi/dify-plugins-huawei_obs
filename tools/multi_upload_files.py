import os
import time
from datetime import datetime
from typing import Any, Union, List
from obs import ObsClient, ObsException
from dify_plugin import Tool
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from .utils import get_file_extension, get_file_type


class MultiUploadFilesTool(Tool):
    """
    华为云OBS工具类 - 批量上传文件
    """
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Tool.ToolInvokeMessage:
        """
        调用工具批量上传文件
        
        Args:
            tool_parameters: 工具参数字典，包含文件列表、目录等信息
            
        Returns:
            ToolInvokeMessage: 包含上传结果的工具调用消息
        """
        # 获取文件列表
        files = tool_parameters.get("files", [])
        if not files:
            raise ToolProviderCredentialValidationError("文件列表不能为空")
        
        # 限制文件数量
        if len(files) > 10:
            raise ToolProviderCredentialValidationError("一次最多只能上传10个文件")
        
        # 获取目录
        directory = tool_parameters.get("directory", "")
        
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
            
            # 获取bucket名称
            bucket_name = self.runtime.credentials.get("bucket")
            
            # 处理每个文件
            results = []
            for file in files:
                try:
                    # 生成文件名
                    object_key = self._generate_object_key(file, directory, filename_mode, directory_mode)
                    
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
                        
                        # 添加到结果列表
                        results.append({
                            "status": "success",
                            "filename": os.path.basename(object_key),
                            "file_size": file_size,
                            "file_type": file_type,
                            "file_url": file_url
                        })
                    else:
                        results.append({
                            "status": "error",
                            "filename": getattr(file, 'filename', 'unknown') or getattr(file, 'name', 'unknown'),
                            "error": resp.errorMessage
                        })
                        
                except Exception as e:
                    results.append({
                        "status": "error",
                        "filename": getattr(file, 'filename', 'unknown') or getattr(file, 'name', 'unknown'),
                        "error": str(e)
                    })
            
            # 统计结果
            success_count = sum(1 for r in results if r["status"] == "success")
            error_count = len(results) - success_count
            
            # 构建结果消息
            message = f"批量上传完成\n"
            message += f"成功: {success_count} 个文件\n"
            message += f"失败: {error_count} 个文件\n\n"
            
            # 添加成功文件详情
            if success_count > 0:
                message += "成功文件:\n"
                for result in results:
                    if result["status"] == "success":
                        message += f"- {result['filename']} ({result['file_size']} bytes, {result['file_type']})\n"
                message += "\n"
            
            # 添加失败文件详情
            if error_count > 0:
                message += "失败文件:\n"
                for result in results:
                    if result["status"] == "error":
                        message += f"- {result['filename']}: {result['error']}\n"
            
            # 创建文本消息
            return self.create_text_message(message)
                
        except ObsException as e:
            raise ToolProviderCredentialValidationError(f"OBS操作失败: {e.message}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"批量上传失败: {str(e)}")
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
    
    def _generate_object_key(self, file: Any, directory: str, 
                           filename_mode: str, directory_mode: str) -> str:
        """
        生成对象key
        
        Args:
            file: 文件对象
            directory: 指定的目录
            filename_mode: 文件名模式（filename 或 filename_timestamp）
            directory_mode: 目录模式（no_subdirectory, yyyy_mm_dd_hierarchy, yyyy_mm_dd_combined）
            
        Returns:
            str: 生成的对象key
        """
        # 获取文件扩展名
        extension = get_file_extension(file)
        
        # 获取原始文件名
        if hasattr(file, 'filename') and file.filename:
            original_filename = os.path.splitext(file.filename)[0]
        elif hasattr(file, 'name') and file.name:
            original_filename = os.path.splitext(file.name)[0]
        else:
            # 使用时间戳作为文件名
            timestamp = int(time.time())
            original_filename = f"file_{timestamp}"
        
        # 处理文件名模式
        if filename_mode == "filename_timestamp":
            # 添加时间戳
            timestamp = int(time.time())
            filename = f"{original_filename}_{timestamp}{extension}"
        else:
            # 使用原始文件名
            filename = f"{original_filename}{extension}"
        
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