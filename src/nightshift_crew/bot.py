"""Telegram Bot — trigger the dream team from your phone."""

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
    raise SystemExit("ALLOWED_USER_IDS not set. Add your Telegram user ID to .env.")
ALLOWED_USER_IDS = [int(x) for x in _raw_ids.split(",") if x.strip()]


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


@authorized
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text.strip()
    if not prompt:
        return

    await update.message.reply_text("⏳ Got it. 13 agents coordinating...\nEstimated 3-5 minutes.")

    try:
        result = await run_crew_async(prompt)
        for i in range(0, len(result), 4000):
            await update.message.reply_text(result[i:i + 4000])
    except Exception as e:
        logger.exception("Crew run failed")
        err_msg = f"❌ Failed: {e}"
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
