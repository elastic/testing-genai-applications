#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
"""
Queries Phoenix for spans within the last minute. Computes and logs evaluations
back to Phoenix. This script is intended to run once a minute as a cron job.
"""

import os

import phoenix as px
from phoenix.evals import (
    HallucinationEvaluator,
    QAEvaluator,
    OpenAIModel,
    run_evals,
)
from dotenv import load_dotenv
from opentelemetry.instrumentation import auto_instrumentation

from phoenix.trace import SpanEvaluations
from phoenix.trace.dsl import SpanQuery


def main():
    # Load environment variables used by OpenTelemetry and Phoenix
    load_dotenv(dotenv_path="../.env", override=False)

    # Auto-instrument this file for OpenTelemetry logs, metrics and spans.
    # You can opt out by setting the ENV variable `OTEL_SDK_DISABLED=true`.
    auto_instrumentation.initialize()

    # Phoenix is also our otel collector, so re-use the ENV variable
    phoenix_client = px.Client(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    )
    eval_model = OpenAIModel(
        model=os.getenv("EVAL_MODEL", "o3-mini"), temperature=0.0
    )

    # Lookup LLM spans missing evals. A real job would be more specific in the
    # query and look up reference answers vs hard-coding one.
    reference = "Atlantic Ocean"
    query = (
        SpanQuery()
        .where(
            "span_kind == 'LLM' and evals['QA Eval'].label is None and evals['Hallucination Eval'].label is None",
        )
        .select(
            input="llm.input_messages",
            output="llm.output_messages",
        )
    )
    spans = phoenix_client.query_spans(query)
    if spans.empty:
        print("No spans found for evaluation.")
        return

    # All spans are evaluated against the same reference
    spans["reference"] = reference
    qa_eval, hallucination_eval = run_evals(
        dataframe=spans,
        evaluators=[
            QAEvaluator(eval_model),
            HallucinationEvaluator(eval_model),
        ],
        provide_explanation=True,
    )

    # Annotate the eval response, regardless of pass or fail to the trace. This
    # ensures we don't redundantly process the same trace later.
    phoenix_client.log_evaluations(
        SpanEvaluations(eval_name="QA Eval", dataframe=qa_eval),
        SpanEvaluations(
            eval_name="Hallucination Eval", dataframe=hallucination_eval
        ),
    )
    print("Evaluations logged to Phoenix")


if __name__ == "__main__":
    main()
