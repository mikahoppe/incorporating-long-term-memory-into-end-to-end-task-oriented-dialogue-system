import logging
import os
import threading

from memory import memory
from memory.llm import Client, Provider
from memory.think import think


async def run():
    _memory = memory.Memory()
    _memory.connect(
        "postgresql",
        os.getenv("POSTGRES_USER"),
        os.getenv("POSTGRES_PASSWORD"),
        "postgres",
        os.getenv("POSTGRES_PORT"),
        os.getenv("POSTGRES_NAME")
    )

    utterance = "What is my name?"
    memories = _memory.recall(utterance)

    artefact = think(utterance, memories)

    _memory.perceive(artefact)
    _memory.rethink()


if __name__ == "__main__":
    run()