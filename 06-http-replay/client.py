#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
import os
from openai import OpenAI


class OpenAIClient:
    """Provides chat completions for models accessed by the OpenAI API."""

    def __init__(self, model: str | None = None) -> None:
        self.client = OpenAI()
        self.model = model or os.getenv("CHAT_MODEL", "gpt-4o-mini")

    def chat(self, message: str) -> str:
        messages = [
            {
                "role": "user",
                "content": message,
            },
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content
