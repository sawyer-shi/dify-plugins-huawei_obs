# Huawei Cloud OBS Plugin

A powerful Dify plugin providing seamless integration with Huawei Cloud Object Storage Service (OBS). Enables direct file uploads to Huawei Cloud OBS and efficient file retrieval using URLs, with rich configuration options.

### Version Information

- **Current Version**: v0.0.2
- **Release Date**: 2025-12-27
- **Compatibility**: Dify Plugin Framework
- **Python Version**: 3.12

#### Version History
- **v0.0.2** (2025-12-27): Added batch file download, public file download, and fix bugs
- **v0.0.1** (2025-09-30): Initial release with file upload and retrieval capabilities, support for multiple directory structures and filename modes

### Quick Start

1. Download the huawei_obs plugin from the Dify marketplace
2. Configure Huawei Cloud OBS authorization information
3. After completing the above configuration, you can immediately use the plugin

### Core Features

#### File Upload to OBS
- **Direct File Upload**: Upload any file type directly to Huawei Cloud OBS
- **Flexible Directory Structure**: Multiple storage directory organization options
  - Flat structure (no_subdirectory)
  - Hierarchical date structure (yyyy_mm_dd_hierarchy)
  - Combined date structure (yyyy_mm_dd_combined)
- **Filename Customization**: Control how filenames are stored in OBS
  - Use original filename
  - Append timestamp to original filename
- **Source File Tracking**: Automatically captures and returns the original filename
- **Smart Extension Detection**: Automatically determine file extensions based on content type

#### File Retrieval by URL
- **Direct Content Access**: Retrieve file content directly using OBS URLs
- **Cross-Region Support**: Works with all Huawei Cloud OBS regions worldwide

#### Batch File Operations
- **Batch File Upload**: Upload multiple files at once (up to 10 files)
- **Batch File Download**: Download multiple files using URLs separated by semicolons (;)
- **Public File Download**: Download publicly accessible files from any platform without API key or authorization

### Technical Advantages

- **Secure Authentication**: Robust credential handling with support for HTTPS
- **Efficient Storage Management**: Intelligent file organization options
- **Comprehensive Error Handling**: Detailed error messages and status reporting
- **Multiple File Type Support**: Works with all common file formats
- **Rich Parameter Configuration**: Extensive options for customized workflows
- **Source File Tracking**: Preserves original filename information

### Requirements

- Python 3.12
- Huawei Cloud OBS account with valid AK/SK credentials
- Dify Platform access
- Required Python packages (installed via requirements.txt)

### Installation & Configuration

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure the plugin in Dify with the following parameters:
   - **Endpoint**: Your Huawei Cloud OBS endpoint (e.g., obs.cn-north-4.myhuaweicloud.com)
   - **Bucket Name**: Your OBS bucket name
   - **Access Key**: Your Huawei Cloud Access Key
   - **Secret Key**: Your Huawei Cloud Secret Key

### Usage

The plugin provides five powerful tools for interacting with Huawei Cloud OBS:

#### 1. Upload File to OBS (upload_file)

Dedicated tool for uploading files to Huawei Cloud OBS.
- **Parameters**:
  - `file`: The local file to upload (required)
  - `directory`: First-level directory under the bucket (required)
  - `directory_mode`: Optional directory structure mode (default: `no_subdirectory`)
    - `no_subdirectory`: Store directly in specified directory
    - `yyyy_mm_dd_hierarchy`: Store in date-based hierarchical structure
    - `yyyy_mm_dd_combined`: Store in combined date directory
  - `filename`: Optional custom filename for OBS storage
  - `filename_mode`: Optional filename composition mode (default: `filename`)
    - `filename`: Use original filename
    - `filename_timestamp`: Use original filename plus timestamp

#### 2. Get File by URL (get_file_by_url)

Dedicated tool for retrieving files from Huawei Cloud OBS using URLs.
- **Parameters**:
  - `file_url`: The URL of the file in Huawei Cloud OBS

#### 3. Multi Upload Files to OBS (multi_upload_files)

Dedicated tool for uploading multiple files to Huawei Cloud OBS.
- **Parameters**:
  - `files`: The local files to upload (required)
  - `directory`: First-level directory under the bucket (required)
  - `directory_mode`: Optional directory structure mode (default: `no_subdirectory`)
    - `no_subdirectory`: Store directly in specified directory
    - `yyyy_mm_dd_hierarchy`: Store in date-based hierarchical structure
    - `yyyy_mm_dd_combined`: Store in combined date directory
  - `filename_mode`: Optional filename composition mode (default: `filename`)
    - `filename`: Use original filename
    - `filename_timestamp`: Use original filename plus timestamp

#### 4. Get Multiple Files by URLs (get_files_by_urls)

Dedicated tool for retrieving multiple files from Huawei Cloud OBS using URLs.
- **Parameters**:
  - `file_urls`: Multiple URLs of files in Huawei Cloud OBS, separated by semicolons (;). Maximum 10 files at once.

#### 5. Get Public File by URL (get_public_file_by_url)

Dedicated tool for downloading publicly accessible files from any platform.
- **Parameters**:
  - `file_url`: The URL of a publicly accessible file from any platform (e.g., Huawei Cloud OBS, Aliyun OSS, AWS S3, etc.)

### Examples

#### Upload File
<img width="2097" height="972" alt="upload-01" src="https://github.com/user-attachments/assets/1bf79e06-4631-4521-bce5-6533d6337f19" />

#### Batch Upload Files
<img width="2017" height="814" alt="upload-02" src="https://github.com/user-attachments/assets/cf25735a-187a-448b-b4ef-aa9bddd3dbfb" />

#### Get File by URL
<img width="2254" height="570" alt="download-01" src="https://github.com/user-attachments/assets/51c7ac37-80f7-4585-9bf7-12eb84bf1ec5" />
<img width="2155" height="544" alt="download-02" src="https://github.com/user-attachments/assets/0d22a3d5-563d-4068-99ac-d7306545aba2" />

### Notes

- Ensure your OBS bucket has the correct permissions configured
- The plugin requires valid Huawei Cloud credentials with appropriate OBS access permissions
- For very large files, consider using multipart upload functionality (not currently implemented)

### Developer Information

- **Author**: `https://github.com/sawyer-shi`
- **Email**: sawyer36@foxmail.com
- **License**: MIT License
- **Souce Code**: `https://github.com/sawyer-shi/dify-plugins-huawei-obs`
- **Support**: Through Dify platform and GitHub Issues

---

**Ready to seamlessly integrate with Huawei Cloud OBS?**



