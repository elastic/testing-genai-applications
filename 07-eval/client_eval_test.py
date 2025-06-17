#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
import os
import textwrap

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
from ocean_evaluator import OceanEvaluator


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
@pytest.mark.eval
def test_chat_eval(traced_test):
    # Share the same model output across all evaluators.
    actual_output = OpenAIClient().chat(message)

    test_case = pd.DataFrame(
        {
            "input": [message],
            "output": [actual_output],
            "reference": ["Atlantic Ocean"],  # ignored by OceanEvaluator
        }
    )

    eval_model = OpenAIModel(
        model=os.getenv("EVAL_MODEL", "o3-mini"), temperature=0.0
    )

    # Define evaluators and their corresponding expected labels
    evaluators_with_labels = [
        # "Generic" (built-in) evaluators
        (QAEvaluator(eval_model), "correct"),
        (HallucinationEvaluator(eval_model), "factual"),
        # "Application-specific" (from error analysis) evaluators
        (OceanEvaluator(eval_model), "correct"),
    ]

    # Run evaluations on the test case
    evals = run_evals(
        dataframe=test_case,
        evaluators=[e[0] for e in evaluators_with_labels],
        provide_explanation=True,
    )

    # If any evaluator returned an unexpected label, include its explanation in
    # the corresponding failure message.
    failures = []
    for (evaluator, expected_label), eval_result in zip(
        evaluators_with_labels, evals
    ):
        row = eval_result.iloc[0]
        if row["label"] != expected_label:
            failure_message = (
                f"{evaluator.__class__.__name__}: label {row['label']} != {expected_label}:\n"
                f"{indent_text(row['explanation'])}"
            )
            failures.append(failure_message)

    failure_count = len(failures)
    assert failure_count == 0, (
        f"{failure_count} evals failed for output: {actual_output}\n"
        + "\n".join(failures)
    )


def indent_text(text):
    return textwrap.indent(str(text), "\t")
