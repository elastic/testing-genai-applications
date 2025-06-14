#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
from contextlib import contextmanager
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
span_id_holder_var = contextvars.ContextVar("span_id_holder")
original_build_request = BaseClient._build_request


def span_id_capturing_build_request(self, *args, **kwargs):
    span_id_holder = span_id_holder_var.get(None)
    if span_id_holder is not None:
        ctx = trace.get_current_span().get_span_context()
        span_id_holder[0] = ctx.span_id
    return original_build_request(self, *args, **kwargs)


@contextmanager
def capture_span_id():
    span_id_holder = [0]
    token = span_id_holder_var.set(span_id_holder)

    def get_span_id():
        return span_id_holder[0]

    BaseClient._build_request = span_id_capturing_build_request
    try:
        yield get_span_id
    finally:
        BaseClient._build_request = original_build_request
        span_id_holder_var.reset(token)


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
        with capture_span_id() as get_span_id:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0,
            )
            content = response.choices[0].message.content
            return ChatResponse(content, get_span_id())
