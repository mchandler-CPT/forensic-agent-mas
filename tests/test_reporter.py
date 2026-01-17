import pytest
import pandas as pd
from unittest.mock import MagicMock
from src.agents.reporter import ReporterAgent

class TestReporterAgent:
    """
    Tests for ReporterAgent focusing on data persistence and reporting.
    """

    def test_report_generation_creates_csv(self, tmp_path):
        # 1. Arrange: Define a temporary report path
        report_file = tmp_path / "forensic_log.csv"
        mock_bus = MagicMock()
        
        # Initialize agent (this will fail if you haven't created the file yet)
        agent = ReporterAgent(mock_bus, report_path=report_file)
        
        # Mock the data structure coming from the Processor
        mock_evidence = {
            'path': tmp_path / "dodgy_file.exe",
            'hash': "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            'metadata': MagicMock(st_size=500)
        }

        # 2. Act: Tell the reporter to record the evidence
        agent.record_evidence(mock_evidence)

        # 3. Assert: Did the file get created and populated?
        assert report_file.exists()
        df = pd.read_csv(report_file)
        assert len(df) == 1
        assert df.iloc[0]['SHA256_Hash'] == mock_evidence['hash']