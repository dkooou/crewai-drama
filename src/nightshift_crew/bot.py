"""Telegram Bot — 手机触发 CrewAI 任务"""

import asyncio
import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
_raw_ids = os.environ.get("ALLOWED_USER_IDS", "").strip()
if not _raw_ids:
    raise SystemExit("ALLOWED_USER_IDS 未设置，bot 拒绝启动。请在 .env 中填入你的 Telegram user ID。")
ALLOWED_USER_IDS = [int(x) for x in _raw_ids.split(",") if x.strip()]


def authorized(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user is None or user.id not in ALLOWED_USER_IDS:
            await update.message.reply_text("无权限。")
            return
        return await func(update, context)
    return wrapper


def _run_crew_sync(prompt: str) -> str:
    from nightshift_crew.crew import NightshiftCrew
    result = NightshiftCrew().crew().kickoff(inputs={"prompt": prompt})
    return str(result)


async def run_crew_async(prompt: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _run_crew_sync, prompt)


@authorized
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 创作 Crew\n\n"
        "直接发文字就行，什么都可以问：\n"
        "• 设计 Day 2 游戏机制\n"
        "• 写一个场景：女友握住笔\n"
        "• 这个设定有没有漏洞\n"
        "• 讨论：意识锚定后是什么状态\n\n"
        "/help 查看帮助"
    )


@authorized
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text.strip()
    if not prompt:
        return

    await update.message.reply_text(f"⏳ 收到，三个 agent 协作中...\n预计 3-5 分钟。")

    try:
        result = await run_crew_async(prompt)
        for i in range(0, len(result), 4000):
            await update.message.reply_text(result[i:i + 4000])
    except Exception as e:
        logger.exception("Crew 运行失败")
        await update.message.reply_text(f"❌ 运行失败：{e}")


def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot 启动")
    app.run_polling()


if __name__ == "__main__":
    main()
