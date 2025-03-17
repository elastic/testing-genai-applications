#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
import os

import pytest


@pytest.fixture
def default_openai_env(monkeypatch):
    """Prevent offline tests from failing due to requiring the ENV OPENAI_API_KEY."""

    if "OPENAI_API_KEY" not in os.environ:
        monkeypatch.setenv("OPENAI_API_KEY", "test_openai_api_key")


@pytest.fixture(scope="module")
def vcr_config():
    """Scrub sensitive headers and gunzip responses so they are readable"""
    sensitive_request_headers = [
        "authorization",
        "cookie",
        "openai-organization",
        "openai-project",
    ]
    sensitive_response_headers = {"openai-organization", "set-cookie"}
    return {
        "decode_compressed_response": True,
        "filter_headers": sensitive_request_headers,
        "before_record_response": lambda r: {
            **r,
            "headers": {
                k: v
                for k, v in r["headers"].items()
                if k.lower() not in sensitive_response_headers
            },
        },
    }
