import pandas as pd
from pathlib import Path
from src.common.base_agent import BaseAgent

class ReporterAgent(BaseAgent):
    """
    Agent responsible for archiving forensic data.
    Fulfills the 'Output Layer' requirement of the MAS.
    """
    def __init__(self, event_bus, report_path="data/output/forensic_report.csv"):
        super().__init__("ReporterAgent")
        self.event_bus = event_bus
        self.report_path = Path(report_path)
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.desires.append("archive_processed_data")
        self.beliefs['record_count'] = 0

    def record_evidence(self, data):
        """
        Logs evidence data (path, hash, metadata) into a persistent CSV.
        """
        self.intention = f"logging_{data['path'].name}"
        
        new_record = pd.DataFrame([{
            'Timestamp': pd.Timestamp.now(),
            'File_Name': data['path'].name,
            'SHA256_Hash': data['hash'],
            'Full_Path': str(data['path'])
        }])

        # Append logic (Agile Iterative Development requirement)
        mode = 'a' if self.report_path.exists() else 'w'
        header = not self.report_path.exists()
        new_record.to_csv(self.report_path, mode=mode, header=header, index=False)
        
        self.beliefs['record_count'] += 1
        self.logger.info(f"Evidence archived: {data['path'].name}")
        self.intention = "idle"

    def perceive(self): pass
    def act(self): pass