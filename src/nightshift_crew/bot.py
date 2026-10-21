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


_META_PATTERNS = [
    re.compile(r"^Now I have all the components.*?(?:\n|$)", re.IGNORECASE),
    re.compile(r"^Let me compile.*?(?:\n|$)", re.IGNORECASE),
    re.compile(r"^Here(?:'s| is) the (?:final|complete|comprehensive).*?(?:\n|$)", re.IGNORECASE),
    re.compile(r"^I(?:'ll| will) now (?:compile|put together|assemble).*?(?:\n|$)", re.IGNORECASE),
    re.compile(r"^Based on (?:our|the|my) (?:memory|research|analysis).*?(?:\n|$)", re.IGNORECASE),
]


def _strip_meta(text: str) -> str:
    """Remove the manager's internal thinking that leaks into output."""
    for pat in _META_PATTERNS:
        text = pat.sub("", text)
    text = re.sub(r"^[─━──]{2,}\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^---+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def md_to_telegram_html(text: str) -> str:
    """Convert crew markdown output to Telegram-compatible HTML."""
    text = _strip_meta(text)
    text = html.escape(text)
    text = re.sub(r"^#{1,3}\s+(.+)$", r"<b>\1</b>", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    text = re.sub(r"\|[-\s|]+\|", "", text)
    text = re.sub(r"\|(.+?)\|", lambda m: "  •  ".join(c.strip() for c in m.group(1).split("|") if c.strip()), text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _split_into_chunks(text: str) -> list[str]:
    """Split long text into phone-friendly chunks (~1 screen each)."""
    parts = re.split(r"\n\n+(?=<b>)", text)

    chunks: list[str] = []
    current = ""
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if current and len(current) + len(part) + 2 > 400:
            chunks.append(current.strip())
            current = part
        else:
            current = current + "\n\n" + part if current else part
    if current.strip():
        chunks.append(current.strip())

    final: list[str] = []
    for chunk in (chunks or [text]):
        while len(chunk) > 4000:
            cut = chunk[:4000].rfind("\n")
            if cut < 200:
                cut = 4000
            final.append(chunk[:cut].strip())
            chunk = chunk[cut:].strip()
        if chunk:
            final.append(chunk)

    return final or [text]


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
        "🎬 梦之队 — 13位AI短剧专家\n\n"
        "直接发消息就行，比如：\n"
        "• 写一个悬疑短剧的开场场景\n"
        "• 国内AI短剧目前什么阶段？\n"
        "• 帮我检查前5集的逻辑漏洞\n"
        "• 抖音上最近什么类型火？\n\n"
        "也可以随便聊天 ☕\n"
        "/help 查看帮助"
    )


def _pick_ack(prompt: str) -> str:
    """Pick a context-aware acknowledgment based on the prompt."""
    lower = prompt.lower()

    if any(w in lower for w in ["写", "剧本", "台词", "场景", "对话", "开场", "write", "scene"]):
        openers = [
            "🎬 收到！编剧团队集合中…",
            "✍️ 明白，让写手们开始构思…",
            "🎭 好的，编剧和钩子工程师就位了…",
        ]
    elif any(w in lower for w in ["趋势", "热门", "流行", "抖音", "快手", "爆款", "什么火", "trend"]):
        openers = [
            "🔍 收到！情报组正在扫描最新趋势…",
            "📊 好的，让情报官去调研…",
            "🌐 明白，正在搜集最新数据…",
        ]
    elif any(w in lower for w in ["检查", "审", "查", "漏洞", "逻辑", "合规", "review"]):
        openers = [
            "🔎 收到！审计员正在逐帧检查…",
            "🧐 好的，质检团队开始审核…",
            "✅ 明白，让审核组过一遍…",
        ]
    elif any(w in lower for w in ["架构", "设计", "规划", "大纲", "策划", "plan", "arc"]):
        openers = [
            "📐 收到！架构师正在规划蓝图…",
            "🏗️ 好的，开始设计整体结构…",
            "🗺️ 明白，让我先画个全局地图…",
        ]
    elif any(w in lower for w in ["什么阶段", "怎么做", "成本", "变现", "案例", "工具", "团队", "行业", "市场", "调研", "分析"]):
        openers = [
            "📋 收到！让我整理一份行业简报…",
            "🔬 好的，情报组正在梳理…",
            "💡 明白，帮你做个快速调研…",
        ]
    else:
        openers = [
            "👍 收到！团队协作中…",
            "🧠 明白，专家们开始讨论了…",
            "⚡ 好的，梦之队已启动…",
            "🎯 收到，正在处理…",
        ]

    return random.choice(openers) + "\n预计 3-5 分钟，稍等 ☕"


@authorized
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text.strip()
    if not prompt:
        return

    await update.message.chat.send_action(ChatAction.TYPING)
    await update.message.reply_text(_pick_ack(prompt))

    try:
        result = await run_crew_async(prompt)
        formatted = md_to_telegram_html(result)
        chunks = _split_into_chunks(formatted)
        for i, chunk in enumerate(chunks):
            await update.message.chat.send_action(ChatAction.TYPING)
            if i > 0:
                await asyncio.sleep(0.8)
            await update.message.reply_text(chunk, parse_mode="HTML")
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
