#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
from openai import OpenAI


class OpenAIClient:
    """Provides chat completions for models accessed by the OpenAI API"""

    def __init__(self) -> None:
        super().__init__()
        self.client = OpenAI()

    def chat(self, model: str, message: str) -> str:
        messages = [
            {
                "role": "user",
                "content": message,
            },
        ]
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content
