from abc import ABC, abstractmethod

class BaseImageProvider(ABC):
    @abstractmethod
    def generate_image(self, prompt: str) -> str:
        """
        Generate an image URL for the given prompt.
        """
        pass
