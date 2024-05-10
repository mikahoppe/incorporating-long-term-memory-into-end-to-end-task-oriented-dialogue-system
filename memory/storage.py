import logging

from sqlalchemy import Column, Integer, String, Sequence, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.reflection import Inspector
from datasketch import MinHash

from memory.get_embedding import get_embedding
from memory.types import Memory

Base = declarative_base()


class MemoryModel(Base):
    __tablename__ = 'memories'

    id = Column(Integer, Sequence('memory_id_seq'), primary_key=True)
    subject = Column(String)
    verb = Column(String)
    object = Column(String)
    description = Column(String)
    embedding = Column(LargeBinary)

    def __repr__(self):
        return f"[{self.id}] MemoryModel({self.subject} {self.verb} {self.object})"


def recreate(_memory):
    Base.metadata.drop_all(_memory.engine)
    Base.metadata.create_all(_memory.engine)


def create_if_not_exists(engine):
    """Create database tables if they do not already exist."""
    inspector = Inspector.from_engine(engine)
    existing_tables = inspector.get_table_names()

    if 'memories' not in existing_tables:
        Base.metadata.create_all(engine)


def store_memory(_memory, memory):
    """
    Stores a new memory in the database.
    :param _memory
    :param memory
    """
    create_if_not_exists(_memory.engine)
    embedding = get_embedding(str(memory))

    embedding_ready = embedding.detach().cpu()
    embedding_bytes = embedding_ready.numpy().tobytes()

    memory_model = MemoryModel(
        subject=memory.subject,
        verb=memory.verb,
        object=memory.object,
        description=memory.description,
        embedding=embedding_bytes
    )
    _memory.session.add(memory_model)
    _memory.session.commit()

    minhash = MinHash(num_perm=128)
    minhash.update(embedding_bytes)

    _memory.lsh.insert(memory.id, minhash)
    logging.info(f"Stored: {memory_model}")


def find_nearest_neighbors(_memory, memory):
    embedding = get_embedding(memory)
    vector = embedding.numpy()

    minhash = MinHash(num_perm=128)
    minhash.update(vector.tobytes())

    # Query for the top 5 nearest neighbors
    result = _memory.lsh.query(minhash)[:5]

    # Retrieve items from the database
    neighbors = _memory.session.query(MemoryModel).filter(MemoryModel.id.in_(result)).all()
    return neighbors


def get_memory(_memory, observation: str):
    """
    Retrieves a specific memory by ID from the database.
    :param memory_id: The ID of the memory to retrieve.
    :return: A Memory namedtuple or None if not found.
    """
    create_if_not_exists(_memory.engine)

    neighbors = find_nearest_neighbors(_memory, observation)
    for neighbor in neighbors:
        logging.info(neighbor)

    memory_model = _memory.session.query(MemoryModel).filter_by(id=1).first()
    if memory_model:
        return Memory(id=memory_model.id, subject=memory_model.subject, verb=memory_model.verb, object=memory_model.object, description=memory_model.description)
    return None
