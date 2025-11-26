"""
Google Cloud API密钥批量生成服务
用于通过Google Cloud API自动创建项目并生成YouTube API密钥
"""

import asyncio
import secrets
import string
import logging
from typing import List, Dict, Optional, Callable
from datetime import datetime

from google.cloud import resourcemanager_v3
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GoogleCloudService:
    """Google Cloud API密钥批量生成服务"""

    # OAuth所需权限范围
    SCOPES = [
        'https://www.googleapis.com/auth/cloud-platform',
        'https://www.googleapis.com/auth/cloudplatformprojects'
    ]

    # OAuth凭据文件路径
    CREDENTIALS_FILE = 'google_oauth_credentials.json'

    def __init__(self, credentials: Credentials = None):
        """
        初始化服务

        Args:
            credentials: Google OAuth凭据，如果为None则需要先授权
        """
        self.credentials = credentials

    def get_oauth_url(self, redirect_uri: str) -> tuple[str, str]:
        """
        获取OAuth授权URL

        Args:
            redirect_uri: OAuth回调地址

        Returns:
            (auth_url, state): 授权URL和state参数
        """
        try:
            flow = Flow.from_client_secrets_file(
                self.CREDENTIALS_FILE,
                scopes=self.SCOPES,
                redirect_uri=redirect_uri
            )

            auth_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'  # 强制显示同意界面以获取refresh_token
            )

            return auth_url, state

        except Exception as e:
            logger.error(f"Error generating OAuth URL: {e}", exc_info=True)
            raise

    def exchange_code_for_credentials(self, code: str, redirect_uri: str, state: str = None) -> Credentials:
        """
        用授权码换取凭据

        Args:
            code: OAuth授权码
            redirect_uri: OAuth回调地址（必须与授权时一致）
            state: OAuth state参数

        Returns:
            Credentials: Google OAuth凭据对象
        """
        try:
            flow = Flow.from_client_secrets_file(
                self.CREDENTIALS_FILE,
                scopes=self.SCOPES,
                redirect_uri=redirect_uri,
                state=state
            )

            flow.fetch_token(code=code)

            return flow.credentials

        except Exception as e:
            logger.error(f"Error exchanging code for credentials: {e}", exc_info=True)
            raise

    def create_gcp_project(self, project_id: str = None, display_name: str = None) -> Dict[str, str]:
        """
        创建GCP项目

        Args:
            project_id: 项目ID（可选，不提供则自动生成）
            display_name: 项目显示名称（可选）

        Returns:
            Dict: {'project_id': str, 'display_name': str}
        """
        if not self.credentials:
            raise ValueError("No credentials available. Please authorize first.")

        try:
            # 生成唯一的项目ID
            if not project_id:
                random_suffix = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(8))
                project_id = f"youtube-kol-{random_suffix}"

            if not display_name:
                display_name = f"YouTube KOL Tools {project_id}"

            # 创建项目
            client = resourcemanager_v3.ProjectsClient(credentials=self.credentials)

            project = resourcemanager_v3.Project(
                project_id=project_id,
                display_name=display_name
            )

            operation = client.create_project(project=project)
            result = operation.result(timeout=120)  # 等待最多2分钟

            logger.info(f"Created GCP project: {project_id}")

            return {
                'project_id': result.project_id,
                'display_name': result.display_name
            }

        except Exception as e:
            logger.error(f"Error creating GCP project: {e}", exc_info=True)
            raise

    def enable_youtube_api(self, project_id: str) -> bool:
        """
        启用YouTube Data API v3

        Args:
            project_id: GCP项目ID

        Returns:
            bool: 是否成功启用
        """
        if not self.credentials:
            raise ValueError("No credentials available. Please authorize first.")

        try:
            service = build('serviceusage', 'v1', credentials=self.credentials)
            service_name = f"projects/{project_id}/services/youtube.googleapis.com"

            # 启用API
            request = service.services().enable(name=service_name)
            operation = request.execute()

            logger.info(f"Enabled YouTube API for project: {project_id}")

            return True

        except HttpError as e:
            logger.error(f"HTTP error enabling YouTube API: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Error enabling YouTube API: {e}", exc_info=True)
            raise

    def create_api_key(self, project_id: str, display_name: str = None) -> str:
        """
        创建API密钥（仅限YouTube API）

        Args:
            project_id: GCP项目ID
            display_name: 密钥显示名称（可选）

        Returns:
            str: API密钥字符串
        """
        if not self.credentials:
            raise ValueError("No credentials available. Please authorize first.")

        try:
            # 使用API Keys API v2
            service = build('apikeys', 'v2', credentials=self.credentials)

            if not display_name:
                display_name = f"YouTube API Key {secrets.token_hex(4)}"

            # 创建密钥请求体
            key_body = {
                'displayName': display_name,
                'restrictions': {
                    'apiTargets': [
                        {
                            'service': 'youtube.googleapis.com'
                        }
                    ]
                }
            }

            parent = f"projects/{project_id}/locations/global"

            # 创建密钥
            request = service.projects().locations().keys().create(
                parent=parent,
                body=key_body
            )
            operation = request.execute()

            # 等待操作完成
            operation_name = operation['name']
            while True:
                result = service.operations().get(name=operation_name).execute()
                if result.get('done'):
                    break
                asyncio.sleep(1)

            # 获取密钥字符串
            if 'response' in result:
                key_string = result['response'].get('keyString')
                logger.info(f"Created API key for project: {project_id}")
                return key_string
            else:
                raise Exception(f"Failed to create API key: {result}")

        except Exception as e:
            logger.error(f"Error creating API key: {e}", exc_info=True)
            raise

    async def batch_generate_keys(
        self,
        count: int,
        progress_callback: Optional[Callable] = None
    ) -> List[Dict]:
        """
        批量生成API密钥

        Args:
            count: 要生成的密钥数量
            progress_callback: 进度回调函数，接收进度消息字符串

        Returns:
            List[Dict]: 生成结果列表，每项包含:
                - project_id: 项目ID
                - api_key: API密钥（如果成功）
                - status: 'success' 或 'failed'
                - error: 错误信息（如果失败）
                - created_at: 创建时间
        """
        if not self.credentials:
            raise ValueError("No credentials available. Please authorize first.")

        results = []

        for i in range(count):
            project_id = None
            try:
                # 1. 创建项目
                if progress_callback:
                    await progress_callback(f"[{i+1}/{count}] Creating GCP project...")

                project_info = self.create_gcp_project()
                project_id = project_info['project_id']

                # 2. 启用YouTube API
                if progress_callback:
                    await progress_callback(f"[{i+1}/{count}] Enabling YouTube API for {project_id}...")

                self.enable_youtube_api(project_id)

                # 等待API启用生效（通常需要几秒）
                await asyncio.sleep(10)

                # 3. 创建API密钥
                if progress_callback:
                    await progress_callback(f"[{i+1}/{count}] Creating API key for {project_id}...")

                api_key = self.create_api_key(project_id)

                results.append({
                    'project_id': project_id,
                    'api_key': api_key,
                    'status': 'success',
                    'created_at': datetime.now().isoformat(),
                    'error': None
                })

                if progress_callback:
                    await progress_callback(f"[{i+1}/{count}] ✓ Successfully created: {api_key[:20]}...")

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Failed to generate API key {i+1}: {error_msg}")

                results.append({
                    'project_id': project_id,
                    'api_key': None,
                    'status': 'failed',
                    'created_at': datetime.now().isoformat(),
                    'error': error_msg
                })

                if progress_callback:
                    await progress_callback(f"[{i+1}/{count}] ✗ Failed: {error_msg}")

        return results
