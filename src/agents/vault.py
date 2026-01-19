import shutil
import os
from pathlib import Path
from src.common.base_agent import BaseAgent

class VaultAgent(BaseAgent):
    def __init__(self, event_bus, vault_dir):
        super().__init__("VaultAgent")
        self.event_bus = event_bus
        # Force absolute path to avoid 'ghost' copies
        self.vault_dir = Path(vault_dir).resolve()
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.beliefs['total_vaulted'] = 0

    def archive_file(self, data):
        source_path = Path(data['path']).resolve()
        destination_path = self.vault_dir / source_path.name
        
        self.intention = f"vaulting_{source_path.name}"
        
        try:
            # copy2 preserves metadata (timestamps), vital for forensics
            shutil.copy2(str(source_path), str(destination_path))
            
            # PRO-GRADE: Verification check
            if destination_path.exists():
                self.beliefs['total_vaulted'] += 1
                self.logger.info(f"Verified: {source_path.name} copied to {self.vault_dir}")
            else:
                self.logger.error(f"Copy failed: {destination_path} does not exist after shutil.copy2")
                
        except Exception as e:
            self.logger.error(f"Vaulting exception for {source_path.name}: {str(e)}")
        finally:
            self.intention = "idle"

    def perceive(self): pass
    def act(self): pass