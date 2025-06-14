#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
import pytest
from user_feedback import add_user_feedback


@pytest.mark.vcr
@pytest.mark.parametrize("good", [True, False])
def test_add_user_feedback(default_otlp_env, good):
    add_user_feedback(span_id=1234567890, good=good)
