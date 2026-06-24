Claude:
bot.py

```python
import os
import sys
import logging
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from config import Config
from storage import GroupStorage
from ai_engine import AIEngine
from github_client import GitHubClient

Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(name)

Global instances
storage: GroupStorage = None
ai: AIEngine = None
github: GitHubClient = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /start"""
    await update.message.reply_text(
        "🤖 ربات فعال است ✅\n\n"
        "دستورات:\n"
        "• /start — وضعیت ربات\n"
        "• /get <msg_id> — دریافت فایل از گروه\n"
        "• /aicode <توضیحات> — ساخت کد با AI + آپلود به گیت‌هاب\n"
        "• /status — وضعیت سرویس‌ها",
        parse_mode="HTML"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /status — وضعیت همه سرویس‌ها"""
    lines = [
        "📊 وضعیت ربات\n",
        f"✅ ربات: فعال",
        f"✅ AI Engine: {'فعال' if ai and ai.clients else '⛔ غیرفعال'}",
        f"   مدل‌ها: {', '.join(ai.clients.keys()) if ai else '—'}",
        f"✅ GitHub: {'فعال' if github and github.token else '⛔ غیرفعال'}",
        f"✅ Group Storage: فعال",
        f"\n⏱ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ]
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ذخیره فایل در گروه — بدون ذخیره روی گوشی"""
    doc = (update.message.document or update.message.photo
           or update.message.video or update.message.audio)
    if not doc:
        return

    file_obj = doc
    file = await file_obj.get_file()
    file_bytes = await file.download_as_bytearray()
    filename = getattr(file_obj, "file_name", f"file_{file.file_id}.bin")

    await update.message.reply_text("⏳ در حال ذخیره در گروه...")

    try:
        msg_id = await storage.save_file(file_bytes, filename)
        await update.message.reply_text(
            f"✅ فایل در گروه ذخیره شد!\n"
            f"📎 آیدی فایل: {msg_id}\n"
            f"💡 برای دریافت: /get {msg_id}",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"File save error: {e}")
        await update.message.reply_text("❌ خطا در ذخیره فایل")

async def get_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /get <message_id> — فوروارد فایل از گروه به کاربر"""
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❌ آیدی فایل رو بزن: /get 123")
        return

    msg_id = int(context.args[0])
    try:
        await storage.get_file_by_msg_id(msg_id, update.effective_chat.id)
    except Exception as e:
        logger.error(f"Get file error: {e}")
        await update.message.reply_text("❌ فایل پیدا نشد یا خطا خورد")

async def aicode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /aicode <توضیحات> — AI کد میسازه و میره تو گیت‌هاب"""
    if not context.args:
        await update.message.reply_text(
            "❌ توضیح بده چه کدی میخوای:\n"
            "مثال: /aicode یه دکمه اینلاین به bot.py اضافه کن که وقت رو نشون بده"
        )
        return

prompt = " ".join(context.args)
    await update.message.reply_text("🧠 در حال تولید کد با ۳ هوش مصنوعی (ChatGPT + DeepSeek + Groq)...")

    try:
گرفتن کد فعلی bot.py از گیت‌هاب
        current_code = None
        if github and github.token:
            current_code, _ = await github.get_file("bot.py")
        else:
            if os.path.exists("bot.py"):
                with open("bot.py", "r") as f:
                    current_code = f.read()

ساختن پرامپت کامل
        full_prompt = f"Task: {prompt}"
        if current_code:
            full_prompt = (
                f"I have this existing bot.py code:\n\n"
                f"\n{current_code}\n\n\n"
                f"Modify it to: {prompt}\n\n"
                f"Output the COMPLETE updated bot.py file."
            )

تولید کد با AI
        generated_code = await ai.generate_code(full_prompt)
        await update.message.reply_text("✅ کد ساخته شد! در حال آپلود به گیت‌هاب...")

آپلود به گیت‌هاب
        if github and github.token:
            success = await github.update_file(
                path="bot.py",
                content=generated_code,
                commit_message=f"🤖 AI update: {prompt[:50]}..."
            )
            if success:
                await context.bot.send_message(
                    chat_id=Config.GROUP_ID,
                    text=f"📦 کد جدید ساخته شد ✅\n"
                         f"📝 {prompt[:100]}...\n"
                         f"🕐 {datetime.now().strftime('%H:%M:%S')}",
                    parse_mode="HTML"
                )
                await update.message.reply_text(
                    "✅ کد تو گیت‌هاب آپلود شد!\n"
                    "🔄 ترموکس تا یکی دو دقیقه دیگه آپدیت رو پول میکنه و ربات ری‌استارت میشه."
                )
            else:
                await update.message.reply_text("❌ گیت‌هاب خطا داد. کد ذخیره نشد.")
        else:
            with open("bot_new.py", "w") as f:
                f.write(generated_code)
            await update.message.reply_text(
                "⚠️ گیت‌هاب کانفیگ نشده. کد تو فایل bot_new.py ذخیره شد."
            )

    except Exception as e:
        logger.error(f"AI code generation error: {e}")
        await update.message.reply_text(f"❌ خطا: {str(e)[:200]}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر خطا"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    Config.validate()

    global ai, github, storage
    try:
        ai = AIEngine()
        logger.info(f"AI Engine ready: {list(ai.clients.keys())}")
    except ValueError as e:
        logger.warning(f"AI Engine not available: {e}")
        ai = None

    github = GitHubClient()
    app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    storage = GroupStorage(app.bot)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("get", get_file))
    app.add_handler(CommandHandler("aicode", aicode))
    app.add_handler(MessageHandler(
        filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO,
        handle_file
    ))
    app.add_error_handler(error_handler)

    logger.info("🚀 Bot is starting...")
    print("ربات فعال است ✅")
    app.run_polling()

if name == "main":
    main()
```
