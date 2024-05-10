import logging

from memory.prompts import prompts, Prompts
from memory.llm import Client, Provider
from memory.memory import Artefact


def think(utterance, memories) -> Artefact:
    client = Client(Provider.OPENAI, 'gpt-4-turbo')
    result = client.complete([
        {
            "role": "system",
            "content": prompts[Prompts.THINK]["system"]()
        },
        {
            "role": "user",
            "content": prompts[Prompts.THINK]["user"](question=utterance, memories=memories)
        }
    ])
    logging.info(result)
    return result
