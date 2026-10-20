"""TikHub API Tool for CrewAI — search TikTok & Douyin trends."""

import json
import os
from typing import Any

import httpx
from crewai.tools import BaseTool
from pydantic import Field


class TikHubSearchTool(BaseTool):
    name: str = "TikHub Search"
    description: str = (
        "Search TikTok and Douyin for trending videos, hashtag analytics, "
        "and creator data. Use this to get real platform data — view counts, "
        "engagement metrics, trending content. "
        "Input should be a JSON string with 'action' and 'query' keys. "
        "Actions: 'search_videos', 'hashtag_info', 'trending', 'user_videos'. "
        "Example: {\"action\": \"search_videos\", \"query\": \"horror short drama\"}"
    )
    api_base: str = Field(default="https://api.tikhub.io")
    api_key: str = Field(default="")

    def __init__(self, **data: Any):
        super().__init__(**data)
        if not self.api_key:
            key_path = os.path.expanduser("~/.config/tikhub/key")
            if os.path.exists(key_path):
                self.api_key = open(key_path).read().strip()
            else:
                self.api_key = os.environ.get("TIKHUB_API_KEY", "")

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _run(self, argument: str) -> str:
        try:
            params = json.loads(argument)
        except json.JSONDecodeError:
            params = {"action": "search_videos", "query": argument}

        action = params.get("action", "search_videos")
        query = params.get("query", "")

        try:
            if action == "search_videos":
                return self._search_videos(query)
            elif action == "hashtag_info":
                return self._hashtag_info(query)
            elif action == "trending":
                return self._trending(params.get("platform", "tiktok"))
            elif action == "user_videos":
                return self._user_videos(query)
            else:
                return f"Unknown action: {action}. Use: search_videos, hashtag_info, trending, user_videos"
        except Exception as e:
            return f"TikHub API error: {e}"

    def _search_videos(self, keyword: str) -> str:
        resp = httpx.get(
            f"{self.api_base}/api/v1/tiktok/web/fetch_tiktok_search_videos",
            params={"keyword": keyword, "count": 10, "offset": 0},
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return self._format_video_results(data)

    def _hashtag_info(self, hashtag: str) -> str:
        resp = httpx.get(
            f"{self.api_base}/api/v1/tiktok/web/fetch_tiktok_hashtag",
            params={"ch_id": hashtag},
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return json.dumps(resp.json(), ensure_ascii=False, indent=2)[:4000]

    def _trending(self, platform: str = "tiktok") -> str:
        endpoint = (
            f"{self.api_base}/api/v1/douyin/web/fetch_douyin_hot_search_list"
            if platform == "douyin"
            else f"{self.api_base}/api/v1/tiktok/web/fetch_tiktok_trending"
        )
        resp = httpx.get(endpoint, headers=self._headers(), timeout=30)
        resp.raise_for_status()
        return json.dumps(resp.json(), ensure_ascii=False, indent=2)[:4000]

    def _user_videos(self, sec_uid: str) -> str:
        resp = httpx.get(
            f"{self.api_base}/api/v1/tiktok/web/fetch_user_post_videos",
            params={"secUid": sec_uid, "count": 10},
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return json.dumps(resp.json(), ensure_ascii=False, indent=2)[:4000]

    def _format_video_results(self, data: dict) -> str:
        items = data.get("data", {}).get("videos", [])
        if not items:
            return "No videos found."
        lines = []
        for v in items[:10]:
            stats = v.get("stats", {})
            lines.append(
                f"- {v.get('desc', 'No title')[:80]}\n"
                f"  Views: {stats.get('playCount', 'N/A')} | "
                f"Likes: {stats.get('diggCount', 'N/A')} | "
                f"Comments: {stats.get('commentCount', 'N/A')} | "
                f"Shares: {stats.get('shareCount', 'N/A')}"
            )
        return "\n".join(lines)
