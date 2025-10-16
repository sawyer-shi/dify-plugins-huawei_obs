# 华为云OBS对象存储插件

一个功能强大的Dify插件，提供与华为云对象存储服务（OBS）的无缝集成。支持将文件直接上传到华为云OBS，并使用URL高效检索文件，提供丰富的配置选项。

### 版本信息

- **当前版本**: v0.0.1
- **发布日期**: 2025-09-30
- **兼容性**: Dify Plugin Framework
- **Python版本**: 3.12

#### 版本历史
- **v0.0.1** (2025-09-30): 初始版本，支持文件上传和检索功能，支持多种目录结构和文件名模式

### 快速开始

1. 从Dify市场下载该插件huawei_obs
2. 配置华为云OBS的授权信息
3. 完成上述配置即可马上使用该插件

### 核心特性

#### 文件上传至OBS
- **直接文件上传**: 将任何类型的文件直接上传到华为云OBS
- **灵活的目录结构**: 多种存储目录组织选项
  - 扁平结构 (no_subdirectory)
  - 分层日期结构 (yyyy_mm_dd_hierarchy)
  - 合并日期结构 (yyyy_mm_dd_combined)
- **文件名自定义**: 控制文件在OBS中的存储名称
  - 使用原始文件名
  - 在原始文件名后附加时间戳
- **源文件追踪**: 自动捕获并返回原始文件名
- **智能扩展名检测**: 基于内容类型自动确定文件扩展名

#### 通过URL获取文件
- **直接内容访问**: 使用OBS URL直接检索文件内容
- **跨区域支持**: 适用于全球所有华为云OBS区域

### 技术优势

- **安全认证**: 强大的凭证处理，支持HTTPS
- **高效存储管理**: 智能文件组织选项
- **全面的错误处理**: 详细的错误消息和状态报告
- **多种文件类型支持**: 适用于所有常见文件格式
- **丰富的参数配置**: 用于自定义工作流程的广泛选项
- **源文件追踪**: 保留原始文件名信息

### 要求

- Python 3.12
- 具有有效AK/SK凭证的华为云OBS账户
- Dify平台访问权限
- 所需的Python包（通过requirements.txt安装）

### 安装与配置

1. 安装所需依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 在Dify中配置插件，输入以下参数：
   - **Endpoint**: 您的华为云OBS端点（例如：obs.cn-north-4.myhuaweicloud.com）
   - **Bucket Name**: 您的OBS存储桶名称
   - **Access Key**: 您的华为云Access Key
   - **Secret Key**: 您的华为云Secret Key

### 使用方法

该插件提供三个强大的工具用于与华为云OBS交互：

#### 1. 上传文件至OBS (upload_file)

用于将文件上传到华为云OBS的专用工具。
- **参数**:
  - `file`: 要上传的本地文件（必填）
  - `directory`: 存储桶下的一级目录（必填）
  - `directory_mode`: 可选的目录结构模式（默认：`no_subdirectory`）
    - `no_subdirectory`: 直接存储在指定目录中
    - `yyyy_mm_dd_hierarchy`: 存储在基于日期的分层结构中
    - `yyyy_mm_dd_combined`: 存储在合并日期目录中
  - `filename`: 用于OBS存储的可选自定义文件名
  - `filename_mode`: 可选的文件名组成模式（默认：`filename`）
    - `filename`: 使用原始文件名
    - `filename_timestamp`: 使用原始文件名加上时间戳

#### 2. 通过URL获取文件 (get_file_by_url)

用于使用URL从华为云OBS检索文件的专用工具。
- **参数**:
  - `file_url`: 华为云OBS中文件的URL

#### 3. 批量上传文件至OBS (multi_upload_files)

用于将多个文件批量上传到华为云OBS的专用工具。
- **参数**:
  - `files`: 要上传的本地文件（必填）
  - `directory`: 存储桶下的一级目录（必填）
  - `directory_mode`: 可选的目录结构模式（默认：`no_subdirectory`）
    - `no_subdirectory`: 直接存储在指定目录中
    - `yyyy_mm_dd_hierarchy`: 存储在基于日期的分层结构中
    - `yyyy_mm_dd_combined`: 存储在合并日期目录中
  - `filename_mode`: 可选的文件名组成模式（默认：`filename`）
    - `filename`: 使用原始文件名
    - `filename_timestamp`: 使用原始文件名加上时间戳

### 样例

#### 文件上传
<img width="2097" height="972" alt="upload-01" src="https://github.com/user-attachments/assets/1bf79e06-4631-4521-bce5-6533d6337f19" />

#### 文件批量上传
<img width="2017" height="814" alt="upload-02" src="https://github.com/user-attachments/assets/cf25735a-187a-448b-b4ef-aa9bddd3dbfb" />

#### 文件获取(下载)
<img width="2254" height="570" alt="download-01" src="https://github.com/user-attachments/assets/51c7ac37-80f7-4585-9bf7-12eb84bf1ec5" />
<img width="2155" height="544" alt="download-02" src="https://github.com/user-attachments/assets/0d22a3d5-563d-4068-99ac-d7306545aba2" />

### 注意事项

- 确保您的OBS存储桶配置了正确的权限
- 该插件需要具有适当OBS访问权限的有效华为云凭证
- 对于非常大的文件，请考虑使用分片上传功能（目前未实现）

### 开发者信息

- **作者**: `https://github.com/sawyer-shi`
- **邮箱**: sawyer36@foxmail.com
- **许可证**: MIT License
- **源码地址**: `https://github.com/sawyer-shi/dify-plugins-huawei-obs`
- **支持**: 通过Dify平台和GitHub Issues

---

**准备好与华为云OBS无缝集成了吗？**