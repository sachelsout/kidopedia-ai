from abc import ABC, abstractmethod

class BaseTextProvider(ABC):
    """
    Abstract base class for all text generation providers.
    """

    @abstractmethod
    def generate_text(self, conversation_history):
        """
        Generate a text response given conversation history.

        Args:
            conversation_history (list of dict): List of messages in format
                                                [{"role": "user/assistant", "content": "..."}]

        Returns:
            str: Generated assistant reply
        """
        pass
