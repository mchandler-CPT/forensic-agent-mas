from pathlib import Path
from src.common.base_agent import BaseAgent

class CollectorAgent(BaseAgent):
    def __init__(self, event_bus, watch_dir):
        super().__init__("CollectorAgent")
        self.event_bus = event_bus
        self.watch_dir = Path(watch_dir)
        
        # BDI: Internal beliefs about the environment
        self.beliefs['seen_files'] = []

    def perceive(self):
        """Sensors: Scans directory for files."""
        self.intention = "scanning"
        if not self.watch_dir.exists():
            return []
        return [f for f in self.watch_dir.iterdir() if f.is_file()]

    def act(self):
        """Actuators: Notifies the system of new files."""
        found_files = self.perceive()
        
        for file_path in found_files:
            # Only act if the belief state confirms it's a new file
            if file_path.name not in self.beliefs['seen_files']:
                self.logger.info(f"New evidence: {file_path.name}")
                
                # Update Intention and Notify (Observer Pattern)
                self.intention = f"reporting_{file_path.name}"
                self.event_bus.publish("FILE_FOUND", file_path)
                
                # Update Beliefs
                self.beliefs['seen_files'].append(file_path.name)
        
        self.intention = "idle"