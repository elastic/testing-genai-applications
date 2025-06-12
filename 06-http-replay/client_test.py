#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
import pytest
from client import OpenAIClient
from main import message


@pytest.mark.vcr
def test_chat(default_openai_env):
    response = OpenAIClient().chat(message)

    assert "South Atlantic Ocean." == response
