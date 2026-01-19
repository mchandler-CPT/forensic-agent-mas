import hashlib
from src.common.base_agent import BaseAgent
from src.common.logger import get_agent_logger

class ProcessorAgent(BaseAgent):
    """
    Agent responsible for data integrity verification and processing.
    """
    def __init__(self, event_bus):
        super().__init__("ProcessorAgent")
        self.event_bus = event_bus
        self.beliefs = {'status': 'ready', 'last_hash': None}

    def process_file(self, file_path):
        """Calculates SHA-256 hash for forensic integrity."""
        # BDI Intention
        self.intention = f"hashing_{file_path.name}"
        
        # ADD THIS LINE: Explicit logging so you see it in the console
        self.logger.info(f"Hashing evidence for integrity: {file_path.name}")
        
        try:
            with open(file_path, "rb") as f:
                bytes_data = f.read()
                file_hash = hashlib.sha256(bytes_data).hexdigest()
            
            # Fix: Update the dictionary directly
            self.beliefs['last_hash'] = file_hash
            self.beliefs['status'] = 'processing_complete'
            
            # Publish to the bus so the Reporter can finally work
            self.event_bus.publish("FILE_PROCESSED", {
                'path': file_path,
                'hash': file_hash,
                'metadata': file_path.stat()
            })
            
        except Exception as e:
            self.logger.error(f"Integrity check failed: {e}")

    # --- MANDATORY ABSTRACT METHOD IMPLEMENTATIONS ---
    
    def perceive(self):
        """
        Sensors: In an event-driven MAS, perception is handled by the EventBus
        rather than a continuous polling loop.
        """
        pass

    def act(self):
        """
        Actuators: Actions are reactive, triggered when a 'FILE_FOUND' 
        event is received.
        """
        pass