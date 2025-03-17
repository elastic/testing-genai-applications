#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
import asyncio
import os

import pytest
from client import OpenAIClient
from deepeval.constants import KEY_FILE
from deepeval.key_handler import KEY_FILE_HANDLER, KeyValues
from deepeval.metrics import AnswerRelevancyMetric, HallucinationMetric
from deepeval.test_case import LLMTestCase
from deepeval.models import GPTModel
from main import message, model

if os.getenv("OTEL_SDK_DISABLED") == "true":
    os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"

# Below writes configuration as file until there's a programmatic way
# See https://github.com/confident-ai/deepeval/issues/1439
if os.path.exists(KEY_FILE):
    os.remove(KEY_FILE)

openai_base_url = os.getenv("OPENAI_BASE_URL")
eval_model = os.getenv("EVAL_MODEL", "gpt-4o")
if openai_base_url:  # local model
    KEY_FILE_HANDLER.write_key(KeyValues.LOCAL_MODEL_NAME, eval_model)
    KEY_FILE_HANDLER.write_key(KeyValues.LOCAL_MODEL_BASE_URL, openai_base_url)
    KEY_FILE_HANDLER.write_key(KeyValues.USE_LOCAL_MODEL, "YES")
    KEY_FILE_HANDLER.write_key(KeyValues.USE_AZURE_OPENAI, "NO")
    KEY_FILE_HANDLER.write_key(KeyValues.LOCAL_MODEL_FORMAT, "json")


async def evaluate_metrics(metrics, test_case, actual_output):
    tasks = [metric.a_measure(test_case, False) for metric in metrics]
    await asyncio.gather(*tasks)
    failures = [
        f"{type(metric).__name__} scored {metric.score:.1f}: {actual_output}"
        for metric in metrics
        if not metric.success
    ]
    return failures


@pytest.mark.eval
@pytest.mark.asyncio
async def test_chat_eval(traced_test):
    actual_output = OpenAIClient().chat(model, message)

    test_case = LLMTestCase(
        input=message,
        actual_output=actual_output,
        context=["Atlantic Ocean"],
    )

    # Evaluation defaults to use gpt-4o, this allows us to override as desired.
    eval_llm = GPTModel(model=eval_model)
    metrics = [
        AnswerRelevancyMetric(model=eval_llm, threshold=0.7),
        HallucinationMetric(model=eval_llm, threshold=0.8),
    ]

    failures = await evaluate_metrics(metrics, test_case, actual_output)
    assert not failures, "{} metrics failed:\n".format(
        len(failures)
    ) + "\n".join(failures)
