#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
import phoenix.client as px


def add_user_feedback(span_id: str, good: bool) -> None:
    """Add user feedback annotation to a span in Phoenix."""
    phoenix_client = px.Client()
    phoenix_client.annotations.add_span_annotation(
        annotation_name="user feedback",
        annotator_kind="HUMAN",
        span_id=span_id,
        label="thumbs-up" if good else "thumbs-down",
        score=1 if good else 0,
    )
