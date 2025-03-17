#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
import os

from client import OpenAIClient
from dotenv import load_dotenv
from opentelemetry.instrumentation import auto_instrumentation

model = os.getenv("CHAT_MODEL", "gpt-4o-mini")
message = "Answer in up to 3 words: Which ocean contains Bouvet Island?"


def main():
    # Load environment variables used by OpenTelemetry and OpenAIClient().
    load_dotenv(dotenv_path="../.env", override=False)

    # Auto-instrument this file for OpenTelemetry logs, metrics and traces.
    # You can opt out by setting the ENV variable `OTEL_SDK_DISABLED=true`.
    auto_instrumentation.initialize()

    client = OpenAIClient()
    reply = client.chat(model=model, message=message)
    print(reply)


if __name__ == "__main__":
    main()
