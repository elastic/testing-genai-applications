#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
import os
from openai import OpenAI
from openinference.instrumentation import capture_span_context
from typing import Optional


class ChatResponse:
    def __init__(self, content: str, span_id: Optional[str]):
        self.content = content
        self.span_id = span_id

    def __str__(self):
        return self.content


class OpenAIClient:
    """Provides chat completions for models accessed by the OpenAI API."""

    def __init__(self, model: str | None = None) -> None:
        self.client = OpenAI()
        self.model = model or os.getenv("CHAT_MODEL", "gpt-4o-mini")

    def chat(self, message: str) -> ChatResponse:
        messages = [
            {
                "role": "user",
                "content": message,
            },
        ]
        with capture_span_context() as capture:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0,
            )
            content = response.choices[0].message.content
            return ChatResponse(content, capture.get_last_span_id())
