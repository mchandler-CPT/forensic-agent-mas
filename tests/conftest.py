import pytest
from unittest.mock import MagicMock

# This fixture mocks the EventBus so we can verify if agents 
# are actually sending messages without needing the real bus.
@pytest.fixture
def mock_event_bus():
    """
    Creates a mock EventBus to verify interactions.
    Rationale: Isolates unit tests from the messaging infrastructure (Meszaros, 2007).
    """
    return MagicMock()