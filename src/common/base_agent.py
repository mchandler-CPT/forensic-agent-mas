from abc import ABC, abstractmethod
from src.common.logger import get_agent_logger

class BaseAgent(ABC):
    def __init__(self, name):
        self.name = name
        # Distinction Move: Centralized logger inherited by all agents
        self.logger = get_agent_logger(self.name)
        
        self.beliefs = {}
        self.desires = []
        self.intention = "idle"
        
        self.logger.info(f"Agent {self.name} initialized with BDI state.")

    @abstractmethod
    def perceive(self): pass

    @abstractmethod
    def act(self): pass