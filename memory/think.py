import logging

from memory.llm import Client, Provider
from memory.memory import Artefact


def think(utterance, memories) -> Artefact:
    client = Client(Provider.OPENAI, 'gpt-4-turbo')
    result = client.complete([
        {
            "role": "user",
            "content": "this is a test request, write a short poem"
        }
    ])
    logging.info(result)
    return result
