#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
import pytest
from main import main


# Models can sometimes return irrelevant answers or hallucinate. Retry instead
# of breaking the build.
@pytest.mark.flaky(reruns=5)
@pytest.mark.integration
def test_main(capsys):
    main()
    reply = capsys.readouterr().out.strip()

    # Cannot guarantee a specific string, but it should include Atlantic
    assert "atlantic" in reply.lower()
