import base64
import logging
from github import Github, GithubIntegration, Auth
from github import GithubException

from config import Config

logger = logging.getLogger(__name__)

class GitHubClient:
    """کلاینت گیت‌هاب — آپلود و آپدیت فایل‌های ربات"""

    def __init__(self):
        self.token = Config.GITHUB_TOKEN
        self.repo_name = Config.GITHUB_REPO
        self.branch = Config.GITHUB_BRANCH

        self._client = None
        self._repo = None

        if self.token and self.repo_name:
            try:
                auth = Auth.Token(self.token)
                self._client = Github(auth=auth)
                self._repo = self._client.get_repo(self.repo_name)
                logger.info(f"✅ GitHub connected: {self.repo_name}")
            except Exception as e:
                logger.error(f"GitHub auth failed: {e}")
                self._client = None
                self._repo = None
        else:
            logger.warning("⚠️ GitHub not configured — token or repo missing")

    @property
    def ready(self) -> bool:
        return self._repo is not None

    async def get_file(self, path: str) -> tuple[str, str] | tuple[None, None]:
        """دریافت محتوای یک فایل از ریپو — برمیگردونه (content, sha)"""
        if not self.ready:
            return None, None
        try:
            contents = self._repo.get_contents(path, ref=self.branch)
            content = base64.b64decode(contents.content).decode("utf-8")
            return content, contents.sha
        except GithubException as e:
            if e.status == 404:
                logger.info(f"File {path} not found in repo")
                return None, None
            logger.error(f"GitHub get_file error: {e}")
            return None, None

    async def update_file(
        self, path: str, content: str, commit_message: str = "🤖 Auto-update by bot"
    ) -> bool:
        """آپدیت یا ساخت فایل جدید تو ریپو"""
        if not self.ready:
            logger.error("GitHub not ready")
            return False

        try:
            # چک کن فایل وجود داره یا نه
            existing_content, sha = await self.get_file(path)

            if sha:
                self._repo.update_file(
                    path=path,
                    message=commit_message,
                    content=content,
                    sha=sha,
                    branch=self.branch,
                )
                logger.info(f"✅ File updated: {path}")
            else:
                self._repo.create_file(
                    path=path,
                    message=commit_message,
                    content=content,
                    branch=self.branch,
                )
                logger.info(f"✅ File created: {path}")

            return True

        except GithubException as e:
            logger.error(f"GitHub update_file error: {e}")
            return False

    async def get_archive_link(self) -> str | None:
        """لینک دانلود زیپ آخرین commit رو برمیگردونه"""
        if not self.ready:
            return None
        try:
            return self._repo.get_archive_link("zipball", ref=self.branch)
        except Exception as e:
            logger.error(f"Archive link error: {e}")
            return None
