##
## Copyright Elasticsearch B.V. and contributors
## SPDX-License-Identifier: Apache-2.0
##

# Use glibc-based image with pre-compiled wheels for psutil
FROM python:3.13-slim AS main

COPY requirements.txt /tmp
RUN --mount=type=cache,target=/root/.cache/pip pip install -r /tmp/requirements.txt

# main.py looks for ../.env, so switch to a subdirectory
WORKDIR /app
COPY *.py ./

ENTRYPOINT [ "python", "main.py" ]

FROM main AS eval

COPY requirements-dev.txt /tmp
RUN --mount=type=cache,target=/root/.cache/pip pip install -r /tmp/requirements-dev.txt

ENTRYPOINT [ "python", "run_evals.py" ]
