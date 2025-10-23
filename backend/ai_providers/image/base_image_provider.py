from abc import ABC, abstractmethod

class BaseImageProvider(ABC):
    """
    Abstract base class for all image generation providers.
    """

    @abstractmethod
    def generate_image(self, prompt):
        """
        Generate an image URL given a text prompt.

        Args:
            prompt (str): Text describing the desired image

        Returns:
            str: URL of generated image
        """
        pass
