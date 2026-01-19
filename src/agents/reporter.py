import pandas as pd
from pathlib import Path
from src.common.base_agent import BaseAgent

class ReporterAgent(BaseAgent):
    """
    Agent responsible for archiving forensic data.
    Fulfills the 'Output Layer' requirement of the MAS and 
    establishes a formal Chain of Custody.
    """
    def __init__(self, event_bus, report_path="data/output/forensic_manifest.csv"):
        super().__init__("ReporterAgent")
        self.event_bus = event_bus
        self.report_path = Path(report_path)
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.desires.append("archive_processed_data")
        self.beliefs['record_count'] = 0

    def record_evidence(self, data):
        """
        Commits enhanced metadata to a persistent forensic log.
        """
        self.intention = f"logging_{data['path'].name}"
        
        # PRO-GRADE: Expanded metadata for the MSc 'Chain of Custody' requirement
        new_record = pd.DataFrame([{
            'Timestamp': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Processing_Agent': self.name,
            'File_Name': data['path'].name,
            'SHA256_Hash': data['hash'],
            'Hash_Type': 'SHA-256',
            'File_Size_Bytes': data['metadata'].st_size,
            'Full_Path': str(data['path'])
        }])

        # Standard append logic
        mode = 'a' if self.report_path.exists() else 'w'
        header = not self.report_path.exists()
        new_record.to_csv(self.report_path, mode=mode, header=header, index=False)
        
        self.beliefs['record_count'] += 1
        self.logger.info(f"Chain of custody updated: {data['path'].name}")
        self.intention = "idle"

    def perceive(self): pass
    def act(self): pass