#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
import sys
from user_feedback import add_user_feedback

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

    if "--feedback" in sys.argv and response.span_id:
        while True:
            rating = input("Are you satisfied? (y/n) ").strip().lower()
            if rating in ["y", "n"]:
                break
            print("Invalid input. Please enter 'y' or 'n'.")
        add_user_feedback(response.span_id, rating == "y")


if __name__ == "__main__":
    main()
