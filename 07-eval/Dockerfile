##
## Copyright Elasticsearch B.V. and contributors
## SPDX-License-Identifier: Apache-2.0
##

# Use glibc-based image with pre-compiled wheels for psutil
FROM python:3.12-slim AS main

RUN --mount=type=cache,target=/root/.cache/pip python -m pip install --upgrade pip

COPY requirements.txt /tmp
RUN --mount=type=cache,target=/root/.cache/pip pip install -r /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip edot-bootstrap --action=install

# main.py looks for ../.env, so switch to a subdirectory
WORKDIR /app
COPY *.py ./

ENTRYPOINT [ "python", "main.py" ]

FROM main AS test

COPY requirements-dev.txt /tmp
RUN --mount=type=cache,target=/root/.cache/pip pip install -r /tmp/requirements-dev.txt
COPY pytest.ini ./
COPY cassettes ./cassettes

ENTRYPOINT [ "pytest" ]
