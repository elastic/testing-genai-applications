#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
import os
import phoenix.client as px


def add_user_feedback(span_id: int, good: bool) -> None:
    """Add user feedback annotation to a span in Phoenix."""
    phoenix_client = px.Client(
        base_url=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    )
    phoenix_client.annotations.add_span_annotation(
        annotation_name="user feedback",
        annotator_kind="HUMAN",
        span_id=f"{span_id:016x}",
        label="thumbs-up" if good else "thumbs-down",
        score=1 if good else 0,
    )
