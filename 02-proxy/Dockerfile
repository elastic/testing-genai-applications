##
## Copyright Elasticsearch B.V. and contributors
## SPDX-License-Identifier: Apache-2.0
##

# Use an alpine image to make the runtime smaller
FROM python:3.12-alpine

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip && \
    pip install openai python-dotenv[cli]

ENTRYPOINT ["dotenv", "run", "--no-override", "--"]
CMD ["sh", "-c", "openai api chat.completions.create -m ${CHAT_MODEL} -t 0 --message user 'Answer in up to 3 words: Which ocean contains Bouvet Island?'"]
