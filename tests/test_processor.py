import pytest
import hashlib
from unittest.mock import ANY
from src.agents.processor import ProcessorAgent

class TestProcessorAgent:
    """
    Tests for ProcessorAgent focusing on data integrity and BDI status.
    """

    def test_processing_calculates_correct_hash(self, mock_event_bus, tmp_path):
        """
        Verifies that the agent correctly hashes a file for forensic integrity.
        """
        # 1. Arrange: Setup the Environment
        # We create a temporary directory and a file named 'evidence.txt'
        d = tmp_path / "staging"
        d.mkdir()
        evidence = d / "evidence.txt"  # <--- This defines the 'evidence' variable
        content = b"Forensic Evidence Data"
        evidence.write_bytes(content)
        
        # Calculate the expected hash for verification
        expected_hash = hashlib.sha256(content).hexdigest()

        # Initialize the agent
        agent = ProcessorAgent(mock_event_bus)

        # 2. Act: Force the agent to process the file
        agent.process_file(evidence)

        # 3. Assert: Verify Beliefs (BDI Model)
        assert agent.beliefs.get('last_hash') == expected_hash
        
        # 4. Assert: Verify Observer Pattern (Event Publication)
        # Match the exact dictionary structure used in processor.py
        mock_event_bus.publish.assert_called_with("FILE_PROCESSED", {
            'path': evidence,
            'hash': expected_hash,
            'metadata': ANY
        })