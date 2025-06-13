#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
import os
import contextvars
from openai import OpenAI
from openai._base_client import BaseClient
from opentelemetry import trace


class ChatResponse:
    def __init__(self, content: str, span_id: int):
        self.content = content
        self.span_id = span_id

    def __str__(self):
        return self.content


# We need the OpenTelemetry span ID created automatically by OpenInference
# instrumentation. Since this instrumentation applies at a low level, the
# `request` function, we need to patch some function called inside that.
span_id_var = contextvars.ContextVar("span_id", default=0)
original_build_request = BaseClient._build_request


def span_id_capturing_build_request(self, *args, **kwargs):
    ctx = trace.get_current_span().get_span_context()
    span_id_var.set(ctx.span_id)
    return original_build_request(self, *args, **kwargs)


BaseClient._build_request = span_id_capturing_build_request


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
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        content = response.choices[0].message.content
        return ChatResponse(content, span_id_var.get())
