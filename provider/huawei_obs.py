from typing import Any, Dict
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

try:
    from obs import ObsClient
except ImportError:
    ObsClient = None


class HuaweiObsProvider(ToolProvider):
    def _validate_credentials(self, credentials: Dict[str, Any]) -> None:
        if ObsClient is None:
            raise ToolProviderCredentialValidationError("华为云OBS SDK未安装，请安装esdk-obs-python包")
        
        try:
            # 1. 检查必要凭据是否存在
            required_fields = ['access_key_id', 'secret_access_key', 'endpoint', 'bucket']
            for field in required_fields:
                if not credentials.get(field):
                    raise ToolProviderCredentialValidationError(f"{field} 不能为空")

            # 2. 验证directory和filename格式
            if 'directory' in credentials and credentials['directory']:
                dir_value = credentials['directory']
                if dir_value.startswith((' ', '/', '\\')):
                    raise ToolProviderCredentialValidationError("directory不能以空格、/或\\开头")

            if 'filename' in credentials and credentials['filename']:
                file_value = credentials['filename']
                if file_value.startswith((' ', '/', '\\')):
                    raise ToolProviderCredentialValidationError("filename不能以空格、/或\\开头")

            # 3. 创建OBS客户端
            endpoint = credentials['endpoint']
            if not endpoint.startswith(('http://', 'https://')):
                endpoint = f"https://{endpoint}"
            obs_client = ObsClient(
                access_key_id=credentials['access_key_id'],
                secret_access_key=credentials['secret_access_key'],
                server=endpoint
            )

            # 4. 进行远程校验，检查bucket是否存在
            resp = obs_client.headBucket(credentials['bucket'])
            status = getattr(resp, 'status', None)
            message = getattr(resp, 'message', '')
            if status is None:
                raise ToolProviderCredentialValidationError("OBS验证失败: 无法获取响应状态")
            if status >= 300:
                if status == 403:
                    raise ToolProviderCredentialValidationError("无效的Access Key ID或Secret Access Key")
                elif status == 404:
                    raise ToolProviderCredentialValidationError("Bucket不存在")
                elif status == 401:
                    raise ToolProviderCredentialValidationError("拒绝访问，请检查凭据权限")
                else:
                    raise ToolProviderCredentialValidationError(f"OBS验证失败: {message}")
            
            # 5. 关闭客户端
            obs_client.close()

        except Exception as e:
            raise ToolProviderCredentialValidationError(f"凭据验证发生未知错误: {str(e)}")
