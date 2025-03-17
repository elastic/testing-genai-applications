#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
import pytest
from client import OpenAIClient
from main import message, model


@pytest.mark.vcr
def test_chat(default_openai_env):
    reply = OpenAIClient().chat(model, message)

    assert "South Atlantic Ocean." == reply
