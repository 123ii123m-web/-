import logging
from telegram import Bot, InputFile
from telegram.ext import ContextTypes

from config import Config

logger = logging.getLogger(__name__)

class GroupStorage:
    """ذخیره‌سازی فایل‌ها مستقیم تو گروه — بدون هیچ فایلی رو گوشی"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.group_id = Config.GROUP_ID

    async def save_file(self, file_obj, filename: str, caption: str = "") -> int:
        """ذخیره فایل تو گروه و برگردوندن message_id"""
        try:
            msg = await self.bot.send_document(
                chat_id=self.group_id,
                document=file_obj,
                filename=filename,
                caption=caption
            )
            logger.info(f"File saved to group: {filename} (msg_id: {msg.message_id})")
            return msg.message_id
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            raise

    async def get_file_by_msg_id(self, msg_id: int, target_chat_id: int):
        """فوروارد فایل از گروه به کاربر (بدون ذخیره)"""
        try:
            await self.bot.forward_message(
                chat_id=target_chat_id,
                from_chat_id=self.group_id,
                message_id=msg_id
            )
        except Exception as e:
            logger.error(f"Failed to forward msg {msg_id}: {e}")
            raise
