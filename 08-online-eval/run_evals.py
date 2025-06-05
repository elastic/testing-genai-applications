# type: ignore
"""
Queries Phoenix for spans within the last minute. Computes and logs evaluations
back to Phoenix. This script is intended to run once a minute as a cron job.
"""

import phoenix as px
from phoenix.evals import (
    HallucinationEvaluator,
    QAEvaluator,
    OpenAIModel,
    run_evals,
)
from phoenix.trace import SpanEvaluations
from phoenix.trace.dsl import SpanQuery

def main():
    phoenix_client = px.Client(endpoint="http://localhost:6006")
    eval_model = OpenAIModel(
        model="gpt-4o",
    )

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
    trace_df = phoenix_client.query_spans(query)
    if trace_df.empty:
        print("No spans found for evaluation.")
        return

    trace_df["reference"] = "Atlantic Ocean"

    qa_eval, hallucination_eval = run_evals(
        dataframe=trace_df,
        evaluators=[
            QAEvaluator(eval_model),
            HallucinationEvaluator(eval_model),
        ],
        provide_explanation=True,
    )
    phoenix_client.log_evaluations(
        SpanEvaluations(eval_name="QA Eval", dataframe=qa_eval),
        SpanEvaluations(eval_name="Hallucination Eval", dataframe=hallucination_eval),
    )
    print("Evaluations logged to Phoenix")

if __name__ == "__main__":
    main()
