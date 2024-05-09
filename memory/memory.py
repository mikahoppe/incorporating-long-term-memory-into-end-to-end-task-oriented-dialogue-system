import logging
from enum import Enum

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Artefact(str):
    pass


class Memo(str):
    pass


class Timeframe(Enum):
    Week = 'week'
    Month = 'month'
    Year = 'year'


class Memory:
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

    def __init__(self):
        self._engine = None
        self._session = None

    def connect(self, type: str, user: str, password: str, uri: str, port: int | str, database: str):
        logging.info("Connecting to Database.")
        uri = f"{type}://{user}:{password}@{uri}:{str(port)}/{database}"
        logging.info(uri)
        self.engine = create_engine(uri, pool_pre_ping=True)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        logging.info("Successfully connected to Database.")

    def recall(self, observation: str) -> list[Memo]:
        logging.info(f"Recall: \"{observation}\"")

        clarified = self._clarify(observation)
        memories = ["Mika"] # self.session.get(clarified)

        return memories

    def _clarify(self, observation: str) -> str:
        logging.info(f"Clarify.")
        return observation

    def perceive(self, artefact: Artefact):
        logging.info(f"Perceive")
        memories = self._parse(artefact)
        for memory in memories:
            self.insert(memory)

    def _parse(self, artefact: Artefact) -> list[Memo]:
        logging.info(f"Parse.")
        return artefact.split(' ')

    def insert(self, memory: Memo):
        logging.info(f"Insert Memory")
        # self.session.add(memory)
        self.session.commit()

    def rethink(self):
        logging.info(f"Rethink")
        self.merge()
        self.forget(Timeframe.Week, 0.2)

    def merge(self):
        logging.info(f"Merge")

    def forget(self, timeframe: Timeframe, rate: float):
        logging.info(f"Forget: {str(timeframe)} : {rate}")
