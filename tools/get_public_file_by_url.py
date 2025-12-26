import os
from typing import Any, Union
from urllib.parse import urlparse
import requests
from dify_plugin import Tool
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class GetPublicFileByUrlTool(Tool):
    """
    公共文件下载工具类 - 通过URL获取公开文件
    """

    def _invoke(self, tool_parameters: dict[str, Any]) -> Any:
        """
        调用工具获取公开文件

        Args:
            tool_parameters: 工具参数字典，包含文件URL

        Returns:
            ToolInvokeMessage: 包含文件数据的工具调用消息
        """
        # 获取文件URL
        file_url = tool_parameters.get("file_url")
        if not file_url:
            raise ToolProviderCredentialValidationError("文件URL不能为空")

        try:
            # 下载文件
            response = requests.get(file_url, timeout=30)
            response.raise_for_status()

            # 获取文件内容
            file_content = response.content

            # 获取文件大小
            file_size = len(file_content)
            file_size_mb = round(file_size / (1024 * 1024), 2)

            # 获取文件名 - 从URL中提取
            file_name = os.path.basename(urlparse(file_url).path)

            # 如果无法从URL提取文件名，使用默认名称
            if not file_name or file_name == "/":
                file_name = "downloaded_file"

            # 获取文件扩展名
            file_extension = os.path.splitext(file_name)[1].lower().lstrip('.')

            # 从响应头获取MIME类型
            mime_type = response.headers.get("content-type", "application/octet-stream")

            # 根据文件扩展名修正MIME类型
            if file_extension:
                extension_to_mime = {
                    'png': 'image/png',
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'gif': 'image/gif',
                    'bmp': 'image/bmp',
                    'svg': 'image/svg+xml',
                    'webp': 'image/webp',
                    'pdf': 'application/pdf',
                    'txt': 'text/plain',
                    'json': 'application/json',
                    'xml': 'application/xml',
                    'html': 'text/html',
                    'css': 'text/css',
                    'js': 'application/javascript',
                    'zip': 'application/zip',
                    'rar': 'application/x-rar-compressed',
                    'doc': 'application/msword',
                    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'xls': 'application/vnd.ms-excel',
                    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'ppt': 'application/vnd.ms-powerpoint',
                    'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                    'mp3': 'audio/mpeg',
                    'mp4': 'video/mp4',
                    'avi': 'video/x-msvideo',
                    'mov': 'video/quicktime',
                    'wmv': 'video/x-ms-wmv',
                    'flv': 'video/x-flv',
                    'mkv': 'video/x-matroska'
                }
                mime_type = extension_to_mime.get(file_extension, mime_type)

            # 构建文件元数据
            file_metadata = {
                'filename': file_name,
                'content_type': mime_type,
                'size': file_size,
                'mime_type': mime_type,
                'extension': file_extension
            }

            # 如果是图片类型，添加特定标志
            if mime_type.startswith('image/'):
                file_metadata['is_image'] = True
                file_metadata['display_as_image'] = True
                file_metadata['type'] = 'image'

            # 创建blob消息
            yield self.create_blob_message(
                blob=file_content,
                meta=file_metadata
            )

            # 创建链接消息
            yield self.create_link_message(file_url)

            # 创建文本消息，显示文件信息
            yield self.create_text_message(
                f"File downloaded successfully: {file_name}\n"
                f"File size: {file_size_mb} MB ({file_size} bytes)\n"
                f"File type: {mime_type}\n"
                f"Source URL: {file_url}"
            )

        except requests.exceptions.RequestException as e:
            raise ToolProviderCredentialValidationError(f"下载文件失败: {str(e)}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"下载文件失败: {str(e)}")
