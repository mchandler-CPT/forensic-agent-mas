from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, agent_name):
        self.name = agent_name
        self.beliefs = {}
        self.desires = []
        self.intentions = ""
        import logging
        self.logger = logging.getLogger(self.name)

    @abstractmethod
    def perceive(self): pass

    @abstractmethod
    def act(self): pass