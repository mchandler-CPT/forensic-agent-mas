import pandas as pd
from pathlib import Path
from src.common.base_agent import BaseAgent
from src.common.logger import get_agent_logger

class CollectorAgent(BaseAgent):
    def __init__(self, event_bus, watch_dir, manifest_path="data/output/forensic_manifest.csv"):
        super().__init__("CollectorAgent")
        self.event_bus = event_bus
        self.watch_dir = Path(watch_dir)
        self.manifest_path = Path(manifest_path)
        
        # Initialize memory of processed files
        self.beliefs['seen_files'] = set()
        self.desires.append("discover_new_evidence")
        
        # PRO-GRADE: Load history to prevent redundant scanning
        self._load_existing_beliefs()

    def _load_existing_beliefs(self):
        """Rebuilds the agent's memory from the persistent manifest."""
        if self.manifest_path.exists():
            try:
                df = pd.read_csv(self.manifest_path)
                # Add all previously logged filenames to the 'seen' list
                if 'File_Name' in df.columns:
                    past_files = set(df['File_Name'].tolist())
                    self.beliefs['seen_files'].update(past_files)
                    self.logger.info(f"Synchronized beliefs: {len(past_files)} historical records loaded.")
            except Exception as e:
                self.logger.error(f"Failed to synchronize historical beliefs: {e}")

    def act(self):
        """Scans the directory for files not already in the agent's memory."""
        self.intention = "scanning_directory"
        
        current_files = list(self.watch_dir.glob("*"))
        for file_path in current_files:
            if file_path.is_file() and file_path.name not in self.beliefs['seen_files']:
                self.logger.info(f"New evidence discovered: {file_path.name}")
                
                # Update belief and publish event
                self.beliefs['seen_files'].add(file_path.name)
                self.event_bus.publish("FILE_FOUND", file_path)
        
        self.intention = "idle"

    def perceive(self): pass