#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
import os
from openai import OpenAI
from opentelemetry import trace


class ChatResponse:
    def __init__(self, content: str, span_id: int):
        self.content = content
        self.span_id = span_id

    def __str__(self):
        return self.content


class _SpanIDCapturingList(list):
    """Defers capture of the OpenTelemetry span ID until it is iterated."""

    def __init__(self, iterable):
        super().__init__(iterable)
        self.span_id = 0

    def __iter__(self):
        ctx = trace.get_current_span().get_span_context()
        self.span_id = ctx.span_id
        return super().__iter__()


class OpenAIClient:
    """Provides chat completions for models accessed by the OpenAI API."""

    def __init__(self, model: str | None = None) -> None:
        self.client = OpenAI()
        self.model = model or os.getenv("CHAT_MODEL", "gpt-4o-mini")

    def chat(self, message: str) -> ChatResponse:
        messages = _SpanIDCapturingList(
            [
                {
                    "role": "user",
                    "content": message,
                },
            ]
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        content = response.choices[0].message.content
        return ChatResponse(content, messages.span_id)
