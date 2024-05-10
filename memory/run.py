import os

from memory import memory
from memory.think import think


async def run():
    _memory = memory.LLMMemory()
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

    _memory.perceive(utterance, artefact)
    _memory.rethink()
    _memory.disconnect()


if __name__ == "__main__":
    run()