#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
import os

from dotenv import load_dotenv
from openai import OpenAI
from opentelemetry.instrumentation import auto_instrumentation

model = os.getenv("CHAT_MODEL", "gpt-4o-mini")
message = "Answer in up to 3 words: Which ocean contains Bouvet Island?"


def main():
    # Load environment variables used by OpenTelemetry and OpenAI().
    load_dotenv(dotenv_path="../.env", override=False)

    # Auto-instrument this file for OpenTelemetry logs, metrics and traces.
    # You can opt out by setting the ENV variable `OTEL_SDK_DISABLED=true`.
    auto_instrumentation.initialize()

    client = OpenAI()
    chat_completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": message}],
        temperature=0,
    )
    print(chat_completion.choices[0].message.content)


if __name__ == "__main__":
    main()
