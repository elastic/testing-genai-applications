##
## Copyright Elasticsearch B.V. and contributors
## SPDX-License-Identifier: Apache-2.0
##

# Use glibc-based image with pre-compiled wheels for psutil
FROM python:3.12-slim

RUN --mount=type=cache,target=/root/.cache/pip python -m pip install --upgrade pip

COPY requirements.txt /tmp
RUN --mount=type=cache,target=/root/.cache/pip pip install -r /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip edot-bootstrap --action=install

ENTRYPOINT ["dotenv", "run", "--no-override", "--"]
# Same as ../01-start/Dockerfile except the opentelemetry-instrument prefix
CMD ["sh", "-c", "opentelemetry-instrument openai api chat.completions.create -t 0 -m ${CHAT_MODEL} --message user 'Answer in up to 3 words: Which ocean contains Bouvet Island?'"]
