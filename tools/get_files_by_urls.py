import os
from typing import Any, Union
from urllib.parse import urlparse
from obs import ObsClient
from dify_plugin import Tool
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class GetFilesByUrlsTool(Tool):
    """
    华为云OBS工具类 - 批量通过URL获取文件
    """

    def _invoke(self, tool_parameters: dict[str, Any]) -> Any:
        """
        调用工具批量获取文件

        Args:
            tool_parameters: 工具参数字典，包含文件URL列表

        Returns:
            ToolInvokeMessage: 包含文件数据的工具调用消息
        """
        # 获取文件URL字符串
        file_urls_str = tool_parameters.get("file_urls")
        if not file_urls_str:
            raise ToolProviderCredentialValidationError("文件URL列表不能为空")

        # 使用分号分隔多个URL
        file_urls = [url.strip() for url in file_urls_str.split(";") if url.strip()]

        if not file_urls:
            raise ToolProviderCredentialValidationError("文件URL列表不能为空")

        # 限制文件数量
        if len(file_urls) > 10:
            raise ToolProviderCredentialValidationError("一次最多只能下载10个文件")

        # 验证凭证
        self._validate_credentials()

        # 创建OBS客户端
        client = None
        try:
            endpoint_cfg = self.runtime.credentials.get("endpoint")
            server = endpoint_cfg if endpoint_cfg and (endpoint_cfg.startswith("http://") or endpoint_cfg.startswith("https://")) else f"https://{endpoint_cfg}" if endpoint_cfg else ""
            client = ObsClient(
                access_key_id=self.runtime.credentials.get("access_key_id"),
                secret_access_key=self.runtime.credentials.get("secret_access_key"),
                server=server
            )

            # 处理每个文件
            results = []
            for file_url in file_urls:
                try:
                    # 解析URL获取bucket和object key
                    bucket_name, object_key = self._parse_url(file_url)

                    # 获取文件
                    resp = client.getObject(bucket_name, object_key)

                    if resp.status < 300:
                        # 获取文件内容
                        file_content = resp.body.response.read()

                        # 获取文件元数据
                        metadata = resp.body.metadata if hasattr(resp.body, 'metadata') and resp.body.metadata else {}

                        # 获取文件大小
                        file_size = len(file_content)
                        file_size_mb = round(file_size / (1024 * 1024), 2)

                        # 获取文件名 - 从原始URL中提取
                        file_name = os.path.basename(urlparse(file_url).path)

                        # 获取文件扩展名
                        file_extension = os.path.splitext(file_name)[1].lower().lstrip('.')

                        # 设置MIME类型
                        mime_type = metadata.get("contenttype", "application/octet-stream")

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

                        # 创建link消息
                        yield self.create_link_message(file_url)

                        # 添加到结果列表
                        results.append({
                            "status": "success",
                            "filename": file_name,
                            "file_size_bytes": file_size,
                            "file_size_mb": file_size_mb,
                            "file_type": mime_type,
                            "file_url": file_url
                        })
                    else:
                        results.append({
                            "status": "error",
                            "file_url": file_url,
                            "error": resp.message
                        })

                except Exception as e:
                    results.append({
                        "status": "error",
                        "file_url": file_url,
                        "error": str(e)
                    })

            # 统计结果
            success_count = sum(1 for r in results if r["status"] == "success")
            error_count = len(results) - success_count

            # 准备JSON结果
            json_result = {
                "status": "completed",
                "success_count": success_count,
                "error_count": error_count,
                "files": results
            }

            # 创建JSON消息
            yield self.create_json_message(json_result)

            # 构建结果消息
            message = f"Batch download completed\n"
            message += f"Success: {success_count} files\n"
            message += f"Failed: {error_count} files\n\n"

            # 添加成功文件详情
            if success_count > 0:
                message += "Successful files:\n"
                for result in results:
                    if result["status"] == "success":
                        message += f"- File name: {result['filename']}\n"
                        message += f"  File size: {result['file_size_mb']} MB ({result['file_size_bytes']} bytes)\n"
                        message += f"  File type: {result['file_type']}\n"
                        message += f"  File URL: {result['file_url']}\n"
                message += "\n"

            # 添加失败文件详情
            if error_count > 0:
                message += "Failed files:\n"
                for result in results:
                    if result["status"] == "error":
                        message += f"- {result['file_url']}: {result['error']}\n"

            # 创建文本消息
            yield self.create_text_message(message)

        except Exception as e:
            raise ToolProviderCredentialValidationError(f"批量下载失败: {str(e)}")
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

    def _parse_url(self, url: str) -> tuple[str, str]:
        """
        解析OBS URL获取bucket名称和对象key

        支持两种URL形式：
        1) 路径风格：https://obs.cn-xxx.myhuaweicloud.com/<bucket>/<object>
        2) 虚拟主机风格：https://<bucket>.obs.cn-xxx.myhuaweicloud.com/<object>
        """
        try:
            parsed = urlparse(url)

            endpoint = self.runtime.credentials.get("endpoint")
            if not endpoint:
                raise ToolProviderCredentialValidationError("缺少endpoint配置")

            # 统一补充协议
            if not endpoint.startswith("http://") and not endpoint.startswith("https://"):
                endpoint = f"https://{endpoint}"

            endpoint_parsed = urlparse(endpoint)
            endpoint_host = (endpoint_parsed.netloc or endpoint_parsed.path).lower()
            url_host = (parsed.netloc or parsed.path).lower()

            bucket_name = ""
            object_key = ""

            if url_host == endpoint_host:
                # 路径风格：从路径中解析 bucket 和 object
                path = parsed.path.lstrip("/")
                path_parts = path.split("/", 1)
                if not path_parts or not path_parts[0]:
                    raise ToolProviderCredentialValidationError("无法从URL中解析bucket名称")
                bucket_name = path_parts[0]
                object_key = path_parts[1] if len(path_parts) > 1 else ""
            elif url_host.endswith("." + endpoint_host):
                # 虚拟主机风格：主机名前缀为 bucket
                bucket_name = url_host[: -(len(endpoint_host) + 1)]
                object_key = parsed.path.lstrip("/")
            else:
                raise ToolProviderCredentialValidationError(f"URL与endpoint不匹配: {parsed.netloc} != {endpoint_host}")

            if not object_key:
                raise ToolProviderCredentialValidationError("无法从URL中解析对象key")

            return bucket_name, object_key

        except Exception as e:
            raise ToolProviderCredentialValidationError(f"URL解析失败: {str(e)}")
