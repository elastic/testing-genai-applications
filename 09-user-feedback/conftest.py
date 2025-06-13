#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
import os
import traceback

import pytest
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode


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


@pytest.fixture
def vcr_cassette_name(request):
    test_name = request.node.name
    if test_name == "test_chat_with_span_id":
        return "test_chat"
    return test_name


@pytest.fixture
def traced_test(request):
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span(request.node.name)
    # pytest_runtest_makereport needs to update the span, so attach it.
    request.node.span = span
    # Make the span current, but don't end it until the test completes.
    with trace.use_span(span, end_on_exit=False):
        yield span
    span.end()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield

    if call.when != "call":
        return  # we don't trace setup and teardown phases
    if not (span := getattr(item, "span", None)):
        return  # test didn't use the traced_test fixture

    report = outcome.get_result()
    if report.skipped:
        return span.set_status(
            Status(status_code=StatusCode.UNSET, description="Test skipped")
        )

    if not report.failed:
        return span.set_status(Status(status_code=StatusCode.OK))

    span.add_event(
        "exception",
        attributes={
            "exception.type": call.excinfo.type.__name__,
            "exception.message": str(call.excinfo.value),
            "exception.stacktrace": "".join(
                traceback.format_exception(
                    call.excinfo.type, call.excinfo.value, call.excinfo.tb
                )
            ),
        },
    )
    span.set_status(
        Status(
            status_code=StatusCode.ERROR, description=str(call.excinfo.value)
        )
    )
