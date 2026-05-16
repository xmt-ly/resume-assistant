import json
import logging
from typing import Optional

from openai import OpenAI

from app.config import AI_PROXY_URL, AI_API_KEY, AI_MODEL

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.client = OpenAI(base_url=AI_PROXY_URL, api_key=AI_API_KEY)
        self.model = AI_MODEL

    def chat(self, system_prompt: str, user_text: str, response_json: bool = False) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ]
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 4096,
        }
        if response_json:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            resp = self.client.chat.completions.create(**kwargs, timeout=60)
            content = resp.choices[0].message.content or ""
            logger.info(f"AI response received, tokens: {resp.usage.total_tokens if resp.usage else 'N/A'}")
            return content
        except Exception as e:
            logger.error(f"AI call failed: {e}")
            raise

    def extract_structured(self, system_prompt: str, user_text: str) -> dict:
        content = self.chat(system_prompt, user_text, response_json=True)
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            import re
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise ValueError(f"Failed to parse AI response as JSON: {content[:200]}")
