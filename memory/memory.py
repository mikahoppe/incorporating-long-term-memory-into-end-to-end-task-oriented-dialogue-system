import logging
import re
from enum import Enum

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from memory.llm import Client, Provider
from memory.prompts import prompts, Prompts
from memory.storage import store_memory, get_memory, recreate
import uuid

from datasketch import MinHashLSH

from memory.types import Memory


class Artefact(str):
    pass


class Timeframe(Enum):
    Week = 'week'
    Month = 'month'
    Year = 'year'


class LLMMemory:
    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, value):
        self._engine = value

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    @property
    def lsh(self):
        return self._lsh

    @lsh.setter
    def lsh(self, value):
        self._lsh = value

    def __init__(self):
        self._engine = None
        self._session = None
        self._lsh = MinHashLSH(threshold=0.5, num_perm=128)

    def connect(self, type: str, user: str, password: str, uri: str, port: int | str, database: str):
        logging.info("Connecting to Database.")
        uri = f"{type}://{user}:{password}@{uri}:{str(port)}/{database}"
        logging.info(uri)
        self.engine = create_engine(uri, pool_pre_ping=True)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        recreate(self)
        logging.info("Successfully connected to Database.")

    def disconnect(self):
        logging.info("Disconnecting from Database.")
        self.session.close()
        self.engine.dispose()
        logging.info("Successfully disconnected from Database.")
        self._session = None
        self._engine = None

    def recall(self, observation: str) -> list[Memory]:
        logging.info(f"Recall: \"{observation}\"")

        clarified = self._clarify(observation)

        retrieved_memory = get_memory(self, observation)
        logging.info(f"Retrieved: {str(retrieved_memory)}")
        memories = [retrieved_memory]

        return memories


    def _clarify(self, observation: str) -> str:
        # TODO:
        logging.info(f"Clarify.")
        return observation

    def perceive(self, utterance: str, artefact: Artefact):
        logging.info(f"Perceive")
        memories = self._parse(utterance, artefact)
        for memory in memories:
            self.insert(memory)

    def _parse(self, utterance: str, artefact: Artefact) -> list[Memory]:
        logging.info(f"Parse.")
        client = Client(Provider.OPENAI, 'gpt-4-turbo')
        text = client.complete([
            {
                "role": "system",
                "content": prompts[Prompts.GENERATE_THOUGHTS]["system"]()
            },
            {
                "role": "user",
                "content": prompts[Prompts.GENERATE_THOUGHTS]["user"](utterance, artefact)
            }
        ])

        pattern = r"\(([^,]+),\s*([^,]+),\s*([^,]+)\)"
        memories_raw = re.findall(pattern, text)

        pattern = r"\([^)]+\)\.\s*(.*?[.!?])"
        answer = re.findall(pattern, text)

        memories = list(map(lambda memory: Memory(uuid.uuid4(), memory[0][0], memory[0][1], memory[0][2], memory[1]), zip(memories_raw, answer)))

        logging.info(f"Answers: {"\n".join(answer)}")
        logging.info(f"Memories: {"\n".join(map(lambda memory: str(memory), memories))}")
        return memories

    def insert(self, memory: Memory):
        logging.info(f"Insert Memory")
        store_memory(self, memory)

    def rethink(self):
        logging.info(f"Rethink")
        self.merge()
        self.forget(Timeframe.Week, 0.2)

    def merge(self):
        # TODO:
        logging.info(f"Merge")

    def forget(self, timeframe: Timeframe, rate: float):
        # TODO:
        logging.info(f"Forget: {str(timeframe)} : {rate}")
