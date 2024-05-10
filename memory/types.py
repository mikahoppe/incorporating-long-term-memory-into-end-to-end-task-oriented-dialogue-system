from collections import namedtuple

BaseMemory = namedtuple('Memory', ['id', 'subject', 'verb', 'object', 'description'])


class Memory(BaseMemory):
    def __str__(self):
        return f"{self.description} ({self.subject}, {self.verb}, {self.object})"