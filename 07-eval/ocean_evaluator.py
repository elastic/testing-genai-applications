#
# Copyright Elasticsearch B.V. and contributors
# SPDX-License-Identifier: Apache-2.0
#
from collections import OrderedDict

from phoenix.evals import ClassificationTemplate, LLMEvaluator
from phoenix.evals.models import BaseModel

OCEAN_PROMPT_RAILS_MAP = OrderedDict({True: "correct", False: "incorrect"})
OCEAN_PROMPT_TEMPLATE_PREFIX = """
You are given a question and answer. You must determine whether the given
answer includes a "correct" ocean. 

"correct" is an answer with an ocean name defined by the NOAA (Atlantic,
Pacific, Indian, Arctic and Southern Ocean), which is relevant to the question
asked. The answer may include qualifiers like "South" or "North" if they are
relevant to the question. For example: a "correct" answer to the question
"Which ocean contains Tahiti?" is "Pacific Ocean" or "South Pacific Ocean".

"incorrect" is an answer with an incorrect ocean, irrelevant part of the ocean,
a made up ocean name, or an irrelevant answer.

Here is the data:
    [BEGIN DATA]
    ************
    [Question]: {input}
    ************
    [Answer]: {output}
    [END DATA]
"""

OCEAN_PROMPT_BASE_TEMPLATE = f"""{OCEAN_PROMPT_TEMPLATE_PREFIX}

Your response must be a single word, either "correct" or "incorrect", and
should not contain any text or characters aside from that word.
"""
OCEAN_PROMPT_TEMPLATE_WITH_EXPLANATION  = f"""{OCEAN_PROMPT_TEMPLATE_PREFIX}
Please read the question and answer carefully, then write out in a step by step
manner an EXPLANATION to show how to determine if the answer is "correct" or
"incorrect". Avoid simply stating the correct answer at the outset. Your
response LABEL must be a single word, either "correct" or "incorrect", and
should not contain any text or characters aside from that word.

Example response:
************
EXPLANATION: An explanation of your reasoning for why the label is "correct" or "incorrect"
LABEL: "correct" or "incorrect"
************

EXPLANATION:"""


OCEAN_PROMPT_TEMPLATE = ClassificationTemplate(
    rails=list(OCEAN_PROMPT_RAILS_MAP.values()),
    template=OCEAN_PROMPT_BASE_TEMPLATE,
    explanation_template=OCEAN_PROMPT_TEMPLATE_WITH_EXPLANATION,
    scores=[1, 0],
)
"""
A template for evaluating if an answer correctly addresses a question about
oceans. This template distinguishes between 'correct' and 'incorrect' answers
and includes a detailed explanation template for reasoned evaluations.
"""

class OceanEvaluator(LLMEvaluator):
    """
    Leverages an LLM to evaluate whether a response (stored under an "output"
    column) to a question involving oceans is correct or incorrect given a
    query (stored under an "input" column).
    """

    def __init__(self, model: BaseModel) -> None:
        """
        Initializer for OceanEvaluator.

        Args:
            model (BaseEvalModel): The LLM model to use for evaluation.
        """

        super().__init__(model=model, template=OCEAN_PROMPT_TEMPLATE)
