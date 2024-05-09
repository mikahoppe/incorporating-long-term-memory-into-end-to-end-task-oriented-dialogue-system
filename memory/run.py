import logging
import os
import threading

from memory import memory
from memory.llm import Client, Provider
from memory.memory import Artefact


async def run():
    client = Client(Provider.OPENAI, 'gpt-4-turbo')
    result = client.complete([
        {
            "role": "user",
            "content": "this is a test request, write a short poem"
        }
    ])
    logging.info(result)

    #########################################################

    _memory = memory.Memory()
    _memory.connect(
        "postgresql",
        os.getenv("POSTGRES_USER"),
        os.getenv("POSTGRES_PASSWORD"),
        "postgres",
        os.getenv("POSTGRES_PORT"),
        os.getenv("POSTGRES_NAME")
    )

    observation = "What is my name?"
    memories = _memory.recall(observation)

    artefact = think(observation, memories)

    _memory.perceive(artefact)
    _memory.rethink()


def think(observation, memories) -> Artefact:
    return observation # llm()


if __name__ == "__main__":
    run()