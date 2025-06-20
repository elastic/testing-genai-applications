#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#

from client import OpenAIClient
from dotenv import load_dotenv
from opentelemetry.instrumentation import auto_instrumentation

message = "Answer in up to 3 words: Which ocean contains Bouvet Island?"


def main():
    # Load environment variables used by OpenTelemetry and OpenAIClient().
    load_dotenv(dotenv_path="../.env", override=False)

    # Auto-instrument this file for OpenTelemetry logs, metrics and traces.
    # You can opt out by setting the ENV variable `OTEL_SDK_DISABLED=true`.
    auto_instrumentation.initialize()

    client = OpenAIClient()
    response = client.chat(message=message)
    print(response)


if __name__ == "__main__":
    main()
