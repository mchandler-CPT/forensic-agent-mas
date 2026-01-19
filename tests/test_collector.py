import pytest
from src.agents.collector import CollectorAgent

class TestCollectorAgent:
    """
    Unit tests for the CollectorAgent based on the BDI model specifications.
    Verification of sensors (perceive) and actuators (act).
    """

    def test_perceive_identifies_files(self, mock_event_bus, tmp_path):
        """
        Verifies that the agent's sensors (perceive method) correctly identify
        files in the environment.
        """
        # 1. Arrange: Setup the Environment
        d = tmp_path / "forensic_data"
        d.mkdir()
        p1 = d / "evidence_1.txt"
        p1.write_text("content")
        p2 = d / "evidence_2.jpg"
        p2.write_text("image_data")

        agent = CollectorAgent(mock_event_bus, str(d))

        # 2. Act: Force the agent to 'perceive' the environment
        files_found = agent.perceive()

        # 3. Assert: The agent should see 2 files
        assert len(files_found) == 2
        
        # NOTE: Removed transient state assertion here because 'perceive' 
        # in your current code doesn't set an intention; 'act' does.

    def test_act_publishes_event_for_new_files(self, mock_event_bus, tmp_path):
        """
        Verifies that the agent's actuators trigger the correct events
        and updates internal BDI beliefs.
        """
        # 1. Arrange
        d = tmp_path / "forensic_data"
        d.mkdir()
        p1 = d / "suspect_file.docx"
        p1.write_text("secret data")

        agent = CollectorAgent(mock_event_bus, str(d))

        # Use a side_effect to catch the 'scanning' intention while the agent is actually working.
        intentions_captured = []
        def capture_intention(*args, **kwargs):
            intentions_captured.append(agent.intention)

        mock_event_bus.publish.side_effect = capture_intention

        # 2. Act
        agent.act()

        # 3. Assert: Verify EventBus notification
        mock_event_bus.publish.assert_called_with("FILE_FOUND", p1)
        
        # Verify BDI State: Intentions was 'scanning_directory' during work
        assert "scanning_directory" in intentions_captured
        # Verify BDI State: Final state is 'idle'
        assert agent.intention == "idle"
        # Verify Beliefs: File added to memory
        assert "suspect_file.docx" in agent.beliefs['seen_files']

    def test_act_ignores_already_seen_files(self, mock_event_bus, tmp_path):
        """
        Verifies that the agent does not process the same file twice.
        """
        d = tmp_path / "forensic_data"
        d.mkdir()
        p1 = d / "repeat.txt"
        p1.write_text("data")

        agent = CollectorAgent(mock_event_bus, str(d))
        
        # Inject a pre-existing belief
        agent.beliefs['seen_files'].add("repeat.txt")

        # 2. Act
        agent.act()

        # 3. Assert: No events should fire for seen files
        mock_event_bus.publish.assert_not_called()