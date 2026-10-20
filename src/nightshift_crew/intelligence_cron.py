"""Automated Creative Intelligence — runs via cron, rotates focus daily."""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

KNOWLEDGE_BASE = Path(os.environ.get("KNOWLEDGE_BASE_DIR", "knowledge_base"))

DAILY_PROMPTS = {
    0: {  # Monday
        "focus": "TikTok Trends",
        "prompt": (
            "Search for trending horror and suspense short dramas on TikTok "
            "from the past week. For each notable find, analyze: "
            "1) What hook technique does the opening use? "
            "2) What's the narrative structure? "
            "3) What's the estimated engagement level and why? "
            "Also check TikHub for #horrorshortfilm #scpfoundation #backrooms "
            "hashtag performance data this week."
        ),
    },
    1: {  # Tuesday
        "focus": "Douyin Trends",
        "prompt": (
            "Search for trending 规则怪谈 and suspense short dramas on Douyin "
            "from the past week. Douyin is 2-3 years ahead of TikTok in short "
            "drama — what patterns emerging there could predict TikTok trends? "
            "Check TikHub for Douyin hot search data related to short dramas. "
            "Output in English but research in both languages."
        ),
    },
    2: {  # Wednesday
        "focus": "Competitor & AI CG Analysis",
        "prompt": (
            "Search for new AI-generated CG short drama series launched "
            "in the past week. How is visual quality evolving? "
            "What character consistency techniques are creators using? "
            "Any new creators entering the horror/suspense space? "
            "Compare production quality trends."
        ),
    },
    3: {  # Thursday
        "focus": "AI Tool Updates",
        "prompt": (
            "Search for updates to AI video and image generation tools: "
            "Seedance, Kling, Runway, Midjourney, Stable Diffusion, Pika. "
            "Any new features, model versions, or workflow improvements "
            "relevant to CG short drama production? "
            "Also check for new character consistency or face-lock techniques."
        ),
    },
    4: {  # Friday
        "focus": "Classic Technique Analysis",
        "prompt": (
            "Pick one acclaimed horror, thriller, or suspense work "
            "(film, series, anime, or game) and do a deep structural analysis. "
            "Focus on techniques adaptable to 8-minute short-form: "
            "how it builds tension, reveals information, uses silence, "
            "misdirects the audience. Extract 3 concrete lessons."
        ),
    },
    5: {  # Saturday
        "focus": "Cross-Domain Inspiration",
        "prompt": (
            "Search for innovative storytelling techniques from games, "
            "interactive fiction, anime, or experimental film from the past month. "
            "What novel narrative structures could work in short-form drama? "
            "What's new in horror/suspense that hasn't reached TikTok yet?"
        ),
    },
    6: {  # Sunday — Weekly Synthesis
        "focus": "Weekly Synthesis",
        "prompt": (
            "You are writing the weekly intelligence synthesis. "
            "Based on your search of this week's developments, produce: "
            "1) TOP 3 ACTIONABLE INSIGHTS — specific things we should apply "
            "2) EMERGING PATTERNS — what's shifting in the market "
            "3) THREAT/OPPORTUNITY — anything that changes our strategy "
            "4) INSPIRATION HIGHLIGHT — one technique worth studying deeper "
            "Be specific and practical. No generic observations."
        ),
    },
}

MONTHLY_PROMPT = (
    "Produce the monthly creative intelligence report. Search broadly: "
    "1) MARKET SHIFTS — how has the TikTok short drama landscape changed? "
    "2) TOP PERFORMERS — which series grew fastest and why? "
    "3) TECHNOLOGY EVOLUTION — AI generation quality and capability changes "
    "4) FAILURES WORTH STUDYING — what looked promising but didn't work? "
    "5) STRATEGIC RECOMMENDATIONS — what should we adjust in our approach? "
    "Check TikHub for monthly hashtag trend data."
)


def get_today_prompt() -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    if now.day == 1:
        return "Monthly Report", MONTHLY_PROMPT
    daily = DAILY_PROMPTS[now.weekday()]
    return daily["focus"], daily["prompt"]


def ensure_dirs():
    for subdir in ["daily", "weekly", "monthly", "library"]:
        (KNOWLEDGE_BASE / subdir).mkdir(parents=True, exist_ok=True)


def save_report(focus: str, result: str):
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")

    if now.day == 1:
        path = KNOWLEDGE_BASE / "monthly" / f"{now.strftime('%Y-%m')}_report.md"
    elif now.weekday() == 6:
        week = now.strftime("%Y-W%W")
        path = KNOWLEDGE_BASE / "weekly" / f"{week}_summary.md"
    else:
        path = KNOWLEDGE_BASE / "daily" / f"{date_str}_{focus.lower().replace(' ', '_')}.md"

    content = f"# {focus} — {date_str}\n\n{result}\n"
    path.write_text(content, encoding="utf-8")
    return path


def run_intelligence():
    from nightshift_crew.crew import NightshiftCrew

    focus, prompt = get_today_prompt()
    print(f"[{datetime.now(timezone.utc).isoformat()}] Running: {focus}")

    ensure_dirs()
    result = NightshiftCrew().crew().kickoff(inputs={"prompt": prompt})
    result_text = str(result)

    path = save_report(focus, result_text)
    print(f"Saved to {path}")

    return focus, result_text


def send_telegram_summary(focus: str, result: str):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    raw_ids = os.environ.get("ALLOWED_USER_IDS", "")
    if not token or not raw_ids:
        return

    import httpx

    user_ids = [int(x.strip()) for x in raw_ids.split(",") if x.strip()]
    summary = result[:3900]
    text = f"📊 Daily Intel: {focus}\n\n{summary}"

    for uid in user_ids:
        try:
            httpx.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": uid, "text": text},
                timeout=10,
            )
        except Exception:
            pass


def main():
    focus, result = run_intelligence()
    send_telegram_summary(focus, result)


if __name__ == "__main__":
    main()
