#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#

import pytest
from client import OpenAIClient
from main import message


@pytest.fixture
def instrumented_openai():
    from opentelemetry.sdk.trace import TracerProvider
    from openinference.instrumentation.openai import OpenAIInstrumentor

    OpenAIInstrumentor().instrument(tracer_provider=TracerProvider())
    yield
    OpenAIInstrumentor().uninstrument()


@pytest.mark.vcr
def test_chat(default_openai_env):
    response = OpenAIClient().chat(message)

    assert response.content == "South Atlantic Ocean."
    assert response.span_id == 0


@pytest.mark.vcr
def test_chat_with_span_id(default_openai_env, instrumented_openai):
    response = OpenAIClient().chat(message)
    assert response.content == "South Atlantic Ocean."
    assert response.span_id != 0
