# Integration test your application

In this exercise, you’ll write an integration test for your OpenAI application
`main.py` to handle LLM response variability and hallucinations when answering:
> Answer in up to 3 words: Which ocean contains Bouvet Island?

[main_test.py](main_test.py) tests `main()` by capturing its stdout. It
includes features to compensate for LLM pitfalls.

## Running tests

Choose one of the following ways to run tests defined in
[main_test.py](main_test.py) using [pytest][pytest].

<details>
<summary>Docker</summary>

```bash
docker compose run --build --rm test
```

</details>

<details>
<summary>Shell</summary>

First, install the same packages as the [previous exercise][prev], except in
this case we don't need the `dotenv` CLI, since we are using it as a library.
```bash
pip install -r requirements.txt
```

Then, install [pytest][pytest] and [pytest-retry][pytest-retry], which we've
added to [requirements-dev.txt](requirements-dev.txt).
```bash
pip install -r requirements-dev.txt
```

Finally, run `pytest`
```bash
pytest
# or to opt-out of OpenTelemetry
OTEL_SDK_DISABLED=true pytest
```

</details>

## Making a test

In [main_test.py](main_test.py), test_main() uses pytest’s `capsys` fixture to
capture `main()`’s console output for assertions. Example:
```python
from main import main

@pytest.mark.integration
def test_main(capsys):
    main()
    reply = capsys.readouterr().out.strip()
```

This mark allows us to skip this test later, and requires defining it in
[pytest.ini](pytest.ini).

## LLM Testing Nuance

Even with `temperature=0` (no creativity), the LLM may respond with any of the
following correctly, so we cannot assert exactly an answer.
* Atlantic Ocean
* South Atlantic Ocean

It may also answer relevantly, but not honor the 3 word maximum like this:
* Bouvet Island is located in the Atlantic Ocean.

For our purposes, we want a correct answer, and are less concerned with prompt
alignment. Hence, we write the assertion like this:

```python
# Cannot guarantee a specific string, but it should include Atlantic
assert "atlantic" in reply.lower()
```

## Hallucination

Small LLMs may hallucinate (e.g., wrong ocean). For now,
[pytest-retry][pytest-retry] reruns the test up to 3 times. Later exercises
explore robust hallucination handling

```python
# Tiny models can sometime hallucinate, so retry a few times
@pytest.mark.flaky(reruns=5)
def test_main(capsys):
```

---
[prev]: ../04-main
[pytest]: https://docs.pytest.org
[pytest-retry]: https://github.com/str0zzapreti/pytest-retry
