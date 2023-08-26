from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    @classmethod
    def get_subclasses(cls):
        """
        Returns a list of all the subclasses of the current class.
        """
        return cls.__subclasses__()

    @abstractmethod
    def compute(self, context):
        """
        Computes the result using the provided configuration dictionary and context.
        """
