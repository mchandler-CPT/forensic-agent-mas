import pytest
import time
from src.agents.collector import CollectorAgent

class TestCollectorAgent:
    """
    Unit tests for the CollectorAgent based on the BDI model specifications.
    """

    def test_perceive_identifies_files(self, mock_event_bus, tmp_path):
        """
        Verifies that the agent's sensors (perceive method) correctly identify
        files in the environment.
        """
        # 1. Arrange: Setup the Environment (A fake folder with 2 files)
        d = tmp_path / "forensic_data"
        d.mkdir()
        p1 = d / "evidence_1.txt"
        p1.write_text("content")
        p2 = d / "evidence_2.jpg"
        p2.write_text("image_data")

        # Initialize the Agent pointing to this fake folder
        agent = CollectorAgent(mock_event_bus, str(d))

        # 2. Act: Force the agent to 'perceive' the environment
        files_found = agent.perceive()

        # 3. Assert: The agent should see 2 files
        assert len(files_found) == 2
        # Verify internal Beliefs (BDI) were updated
        assert agent.intention == "scanning"

    def test_act_publishes_event_for_new_files(self, mock_event_bus, tmp_path):
        """
        Verifies that the agent's actuators trigger the correct events
        when new data is found (Observer Pattern).
        """
        # 1. Arrange: Create a file
        d = tmp_path / "forensic_data"
        d.mkdir()
        p1 = d / "suspect_file.docx"
        p1.write_text("secret data")

        agent = CollectorAgent(mock_event_bus, str(d))

        # 2. Act: Run the agent's main logic loop
        agent.act()

        # 3. Assert: Verify the EventBus was notified
        # This checks: Did we call publish("FILE_FOUND", <path>)?
        mock_event_bus.publish.assert_called_with("FILE_FOUND", p1)
        
        # Verify BDI State: The agent should now 'believe' it has seen this file
        assert "suspect_file.docx" in agent.beliefs['seen_files']

    def test_act_ignores_already_seen_files(self, mock_event_bus, tmp_path):
        """
        Verifies that the agent does not process the same file twice.
        Efficiency requirement for large datasets.
        """
        # 1. Arrange
        d = tmp_path / "forensic_data"
        d.mkdir()
        p1 = d / "repeat.txt"
        p1.write_text("data")

        agent = CollectorAgent(mock_event_bus, str(d))
        
        # Inject a pre-existing belief that we already saw this file
        agent.beliefs['seen_files'] = ["repeat.txt"]

        # 2. Act
        agent.act()

        # 3. Assert: EventBus should NOT be called
        mock_event_bus.publish.assert_not_called()