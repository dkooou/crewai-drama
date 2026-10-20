"""Telegram Bot 入口 — 手机触发 CrewAI 任务"""

import asyncio
import logging
import os
from textwrap import dedent

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

# ── 权限检查 ──────────────────────────────

def authorized(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user is None or user.id not in ALLOWED_USER_IDS:
            await update.message.reply_text("无权限。")
            return
        return await func(update, context)
    return wrapper


# ── CrewAI 调用（在线程池中跑，避免阻塞bot） ──

def _run_crew_sync(task_type: str, inputs: dict) -> str:
    from nightshift_crew.crew import NightshiftCrew

    crew_instance = NightshiftCrew()
    c = crew_instance.crew()
    result = c.kickoff(inputs=inputs)
    return str(result)


async def run_crew_async(task_type: str, inputs: dict) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _run_crew_sync, task_type, inputs)


# ── Bot 命令 ──────────────────────────────

@authorized
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(dedent("""\
        🎬 《夜班守则》创作 Crew

        命令：
        /game <天数> <要求> — 设计游戏机制
        /scene <场景描述> — 创作具体场景
        /discuss <问题> — 世界观讨论
        /help — 查看帮助

        示例：
        /game Day 2 测试证据协作能力
        /scene Day 6终局，女友握住笔
        /discuss 锚定后意识是什么状态
    """))


@authorized
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cmd_start(update, context)


@authorized
async def cmd_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/game", "").strip()
    if not text:
        await update.message.reply_text("用法：/game Day 2 测试证据协作能力")
        return

    parts = text.split(maxsplit=1)
    day = parts[0] if parts else "Day 2"
    constraint = parts[1] if len(parts) > 1 else "自由设计"

    await update.message.reply_text(f"⏳ 正在设计 {day} 游戏机制，三个 agent 协作中...\n预计 3-5 分钟。")

    try:
        result = await run_crew_async("game", {
            "day_number": day,
            "previous_day_summary": "（请补充前一天摘要，或留空让编剧自由发挥）",
            "constraint": constraint,
        })
        # Telegram 消息长度限制 4096 字符，分段发
        for i in range(0, len(result), 4000):
            await update.message.reply_text(result[i:i+4000])
    except Exception as e:
        logger.exception("Crew 运行失败")
        await update.message.reply_text(f"❌ 运行失败：{e}")


@authorized
async def cmd_scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/scene", "").strip()
    if not text:
        await update.message.reply_text("用法：/scene Day 6终局，女友主动握住笔")
        return

    await update.message.reply_text("⏳ 正在创作场景...\n预计 2-3 分钟。")

    try:
        result = await run_crew_async("scene", {"scene_brief": text})
        for i in range(0, len(result), 4000):
            await update.message.reply_text(result[i:i+4000])
    except Exception as e:
        logger.exception("Crew 运行失败")
        await update.message.reply_text(f"❌ 运行失败：{e}")


@authorized
async def cmd_discuss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/discuss", "").strip()
    if not text:
        await update.message.reply_text("用法：/discuss 锚定后意识是什么状态")
        return

    await update.message.reply_text("⏳ 三个 agent 正在讨论...\n预计 3-5 分钟。")

    try:
        result = await run_crew_async("discuss", {"question": text})
        for i in range(0, len(result), 4000):
            await update.message.reply_text(result[i:i+4000])
    except Exception as e:
        logger.exception("Crew 运行失败")
        await update.message.reply_text(f"❌ 运行失败：{e}")


@authorized
async def handle_free_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """自由输入 → 当作世界观讨论"""
    text = update.message.text.strip()
    if not text:
        return

    await update.message.reply_text("⏳ 收到，当作世界观讨论处理...\n预计 3-5 分钟。")

    try:
        result = await run_crew_async("discuss", {"question": text})
        for i in range(0, len(result), 4000):
            await update.message.reply_text(result[i:i+4000])
    except Exception as e:
        logger.exception("Crew 运行失败")
        await update.message.reply_text(f"❌ 运行失败：{e}")


# ── 启动 ──────────────────────────────────

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("game", cmd_game))
    app.add_handler(CommandHandler("scene", cmd_scene))
    app.add_handler(CommandHandler("discuss", cmd_discuss))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_free_text))

    logger.info("Bot 启动")
    app.run_polling()


if __name__ == "__main__":
    main()
