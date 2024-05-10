import logging

from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.reflection import Inspector
from collections import namedtuple

# Create the namedtuple
Memory = namedtuple('Memory', ['subject', 'verb', 'object'])
Base = declarative_base()


class MemoryModel(Base):
    __tablename__ = 'memories'

    id = Column(Integer, Sequence('memory_id_seq'), primary_key=True)
    subject = Column(String)
    verb = Column(String)
    object = Column(String)

    def __repr__(self):
        return f"MemoryModel(id={self.id}, subject='{self.subject}', verb='{self.verb}', object='{self.object}')"


def create_table_if_not_exists(engine):
    """Create database tables if they do not already exist."""
    inspector = Inspector.from_engine(engine)
    existing_tables = inspector.get_table_names()

    if 'memories' not in existing_tables:
        Base.metadata.create_all(engine)
        print("Tables created.")
    else:
        print("Tables already exist.")


def store_memory(_memory, memory):
    """
    Stores a new memory in the database.
    :param _memory
    :param memory: A namedtuple of type Memory.
    """
    create_table_if_not_exists(_memory.engine)
    memory_model = MemoryModel(subject=memory.subject, verb=memory.verb, object=memory.object)
    _memory.session.add(memory_model)
    _memory.session.commit()
    logging.info(f"Stored: {memory_model}")


def get_memory(_memory, memory_id):
    """
    Retrieves a specific memory by ID from the database.
    :param memory_id: The ID of the memory to retrieve.
    :return: A Memory namedtuple or None if not found.
    """
    create_table_if_not_exists(_memory.engine)
    memory_model = _memory.session.query(MemoryModel).filter_by(id=memory_id).first()
    if memory_model:
        return Memory(subject=memory_model.subject, verb=memory_model.verb, object=memory_model.object)
    return None
