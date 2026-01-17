class EventBus:
    """
    Observer Pattern Implementation.
    Acts as the communication mediator between agents.
    """
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type, callback):
        """Agents call this to listen for specific tasks."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event_type, data):
        """Agents call this to broadcast findings."""
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback(data)