import logging
from typing import List

import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, Sequence
from sqlalchemy.orm import sessionmaker

from datasketch import MinHash, MinHashLSH

from transformers import AutoTokenizer, AutoModel
import torch

from memory.prompts import prompts, Prompts
from memory.llm import Client, Provider

import uuid
import re

Base = sqlalchemy.orm.declarative_base()


class MemoryModel(Base):
    __tablename__ = "memories"

    id = Column(Integer, Sequence('memory_id_seq'), primary_key=True)
    subject = Column(String)
    verb = Column(String)
    object = Column(String)
    description = Column(String)
    embedding = Column(LargeBinary)

    def __init__(self, subject, verb, object, description = None, embedding = None):
        self.subject = subject
        self.verb = verb
        self.object = object
        self.description = description
        self.embedding = embedding

    def __repr__(self):
        return f"Memory('{self.subject}', '{self.verb}', '{self.object}')"


class Memory:
    def __init__(self):
        self.engine = None
        self.session = None
        self.lsh = MinHashLSH(threshold=0.5, num_perm=128)

    def connect(self, type, path):
        database_url = f'{type}:///{path}'
        engine = create_engine(database_url)
        session_factory = sessionmaker(bind=engine)
        session = session_factory()

        self.engine = engine
        self.session = session

    def create_table(self):
        Base.metadata.create_all(self.engine)

    def recall(self, observation):
        retrieved_memories = self.get_memories(observation)
        return retrieved_memories

    def get_memories(self, observation: str) -> List[MemoryModel]:
        neighbors = self.find_nearest_neighbors(observation)

        for neighbor in neighbors:
            logging.info(neighbor)

        memory_model = self.session.query(MemoryModel).filter_by(id=1).first()
        if memory_model:
            return [memory_model]
        return []

    def find_nearest_neighbors(self, observation):
        embedding = self.get_embedding(observation)
        vector = embedding.numpy()

        minhash = MinHash(num_perm=128)
        minhash.update(vector.tobytes())

        # Query for the top 5 nearest neighbors
        result = self.lsh.query(minhash)[:5]

        # Retrieve items from the database
        neighbors = self.session.query(MemoryModel).filter(MemoryModel.id.in_(result)).all()
        return neighbors

    def get_embedding(self, text):
        model_name = "distilbert-base-uncased"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)

        inputs = tokenizer(text, return_tensors="pt")

        # Generate embeddings
        with torch.no_grad():
            outputs = model(**inputs)

        # Get the embeddings from the last hidden state
        # Here, we use the mean of all token embeddings for simplicity.
        embeddings = outputs.last_hidden_state.mean(dim=1)

        return embeddings

    def observe(self, observation, artefact):
        memories = self.parse(observation, artefact)
        self.insert_memories(memories)

        return memories

    def parse(self, observation, artefact):
        client = Client(Provider.OPENAI, 'gpt-4-turbo')
        text = client.complete([
            {
                "role": "system",
                "content": prompts[Prompts.GENERATE_THOUGHTS]["system"]()
            },
            {
                "role": "user",
                "content": prompts[Prompts.GENERATE_THOUGHTS]["user"](observation, artefact)
            }
        ])

        pattern = r"\(([^(),]+),\s*([^(),]+),\s*([^(),]+)\)"
        memories_as_text = re.findall(pattern, text)

        pattern = r"\([^)]+\)\.\s*(.*?[.!?])"
        answer = re.findall(pattern, text)

        memories = list(
            map(
                lambda memory:
                    MemoryModel(memory[0][0], memory[0][1], memory[0][2], memory[1]),
                    zip(memories_as_text, answer)
            )
        )

        return memories

    def insert_memories(self, memories):
        for memory in memories:
            embedding = self.get_embedding(str(memory))

            embedding_ready = embedding.detach().cpu()
            embedding_bytes = embedding_ready.numpy().tobytes()

            memory.embedding = embedding_bytes
            self.session.add(memory)

            minhash = MinHash(num_perm=128)
            minhash.update(embedding_bytes)

            self.lsh.insert(uuid.uuid4(), minhash)

        self.session.commit()


def think(observation: str, retrieved_memories: List[MemoryModel]):
    client = Client(Provider.OPENAI, 'gpt-4-turbo')
    result = client.complete([
        {
            "role": "system",
            "content": prompts[Prompts.THINK]["system"]()
        },
        {
            "role": "user",
            "content": prompts[Prompts.THINK]["user"](question=observation, memories=retrieved_memories)
        }
    ])
    logging.info(result)
    return result


def run():
    _memory = Memory()
    _memory.connect("sqlite", "memory.db")
    _memory.create_table()

    while True:
        observation = input("Enter: ")

        retrieved_memories = _memory.recall(observation)
        print(retrieved_memories)

        artefact = think(observation, retrieved_memories)
        answer = artefact.split("Answer: ", 1)
        print(answer[1] if len(answer) > 1 else artefact)

        extracted_memories = _memory.observe(observation, artefact)
        print(extracted_memories)


if __name__ == '__main__':
    run()
