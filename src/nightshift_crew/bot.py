"""Telegram Bot — trigger the dream team from your phone."""

import asyncio
import html
import logging
import os
import random
import re

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
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
    raise SystemExit("ALLOWED_USER_IDS not set. Add your Telegram user ID to .env.")
ALLOWED_USER_IDS = [int(x) for x in _raw_ids.split(",") if x.strip()]


def md_to_telegram_html(text: str) -> str:
    """Convert crew markdown output to Telegram-compatible HTML."""
    text = html.escape(text)
    text = re.sub(r"^#{1,3}\s+(.+)$", r"<b>\1</b>", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    text = re.sub(r"\|[-\s|]+\|", "", text)
    text = re.sub(r"\|(.+?)\|", lambda m: "  •  ".join(c.strip() for c in m.group(1).split("|") if c.strip()), text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def authorized(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user is None or user.id not in ALLOWED_USER_IDS:
            await update.message.reply_text("Unauthorized.")
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
        "🎬 Dream Team — 13 AI Agents\n\n"
        "Send any message to start. Examples:\n"
        "• Design the season arc for a rule-horror office series\n"
        "• Write the opening scene: she finds the lock changed\n"
        "• Check E1-E5 for logic holes\n"
        "• What's trending in horror on TikTok this week?\n\n"
        "/help for help"
    )


def _pick_ack(prompt: str) -> str:
    """Pick a context-aware acknowledgment based on the prompt."""
    lower = prompt.lower()

    if any(w in lower for w in ["write", "scene", "script", "dialogue", "写", "剧本", "台词"]):
        openers = [
            "🎬 收到！正在召集编剧团队…",
            "✍️ 明白，让我的写手们开始构思…",
            "🎭 好的，Scene Writer 和 Hook Engineer 已经就位…",
        ]
    elif any(w in lower for w in ["trend", "热门", "流行", "tiktok", "抖音", "what's hot"]):
        openers = [
            "🔍 收到！情报组正在扫描最新趋势…",
            "📊 好的，让 Creative Intel 去调研…",
            "🌐 明白，正在搜集最新数据…",
        ]
    elif any(w in lower for w in ["check", "review", "logic", "审", "检查", "漏洞", "hole"]):
        openers = [
            "🔎 收到！Logic Auditor 正在逐帧检查…",
            "🧐 好的，质检团队已经开始审核…",
            "✅ 明白，让审核组仔细过一遍…",
        ]
    elif any(w in lower for w in ["design", "arc", "架构", "设计", "season", "规划"]):
        openers = [
            "📐 收到！Story Architect 正在规划蓝图…",
            "🏗️ 好的，架构师开始设计整体结构…",
            "🗺️ 明白，让我先画个全局地图…",
        ]
    else:
        openers = [
            "👍 收到！团队正在协作中…",
            "🧠 明白，13个专家开始讨论了…",
            "⚡ 好的，Dream Team 已启动…",
            "🎯 收到，正在处理你的需求…",
        ]

    return random.choice(openers) + "\n预计需要 3-5 分钟，请稍候 ☕"


@authorized
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text.strip()
    if not prompt:
        return

    await update.message.chat.send_action(ChatAction.TYPING)
    await update.message.reply_text(_pick_ack(prompt))

    try:
        result = await run_crew_async(prompt)
        await update.message.chat.send_action(ChatAction.TYPING)
        formatted = md_to_telegram_html(result)
        for i in range(0, len(formatted), 4000):
            await update.message.reply_text(formatted[i:i + 4000], parse_mode="HTML")
    except Exception as e:
        logger.exception("Crew run failed")
        err_msg = f"❌ 出错了: {e}"
        await update.message.reply_text(err_msg[:4000])


def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot started — 13-agent dream team ready")
    app.run_polling()


if __name__ == "__main__":
    main()
