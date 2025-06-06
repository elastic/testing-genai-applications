#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
import os

from delayed_assert.delayed_assert import assert_all, expect
import pandas as pd
import pytest
from client import OpenAIClient
from main import message
from phoenix.evals import (
    HallucinationEvaluator,
    QAEvaluator,
    OpenAIModel,
    run_evals,
)


@pytest.mark.eval
def test_chat_eval(traced_test):
    actual_output = OpenAIClient().chat(message)

    test_case = pd.DataFrame(
        {
            "input": [message],
            "output": [actual_output],
            "reference": ["Atlantic Ocean"],
        }
    )

    eval_model = OpenAIModel(
        model=os.getenv("EVAL_MODEL", "o4-mini"), temperature=0.0
    )

    qa_eval, hallucination_eval = run_evals(
        dataframe=test_case,
        evaluators=[
            QAEvaluator(eval_model),
            HallucinationEvaluator(eval_model),
        ],
        provide_explanation=True,
    )
    with assert_all():
        expect(qa_eval["label"][0] == "correct", qa_eval["explanation"][0])
        expect(
            hallucination_eval["label"][0] == "factual",
            hallucination_eval["explanation"][0],
        )
