from collections import deque
from typing import Any, Dict, List, Type

from easy_expectations.config_enhancer.strategies.base_strategy import BaseStrategy
from easy_expectations.utils.logger import logger

from .strategies import end_strategies, start_strategies


class Enhancer:
    """
    The Enhancer class is used to enhance a given configuration dictionary
    using a set of strategies.
    It takes a list of start strategies, end strategies, and computes the
    result using these strategies along with the middle strategies.
    The process method processes the config_dict using the instantiated
    strategies and returns the modified config_dict.
    """

    def __init__(
        self,
        start_strategies: List[Type[BaseStrategy]] = start_strategies,
        end_strategies: List[Type[BaseStrategy]] = end_strategies,
    ) -> None:
        """
        Initializes an instance of the Enhancer class.

        Args:
            start_strategies (list): A list of start strategies.
            end_strategies (list): A list of end strategies.
        """
        self.start_strategies = deque(
            self._instantiate_strategies(start_strategies or [])
        )
        self.end_strategies = deque(self._instantiate_strategies(end_strategies or []))
        self.middle_strategies = deque(self._instantiate_middle_strategies())
        self.all_strategies = deque(
            self.start_strategies + self.middle_strategies + self.end_strategies
        )

    def _instantiate_strategies(
        self, strategies: List[Type[BaseStrategy]]
    ) -> List[BaseStrategy]:
        """
        Instantiates the given list of strategies.

        Args:
            strategies (list): A list of strategies.

        Returns:
            list: A list of instantiated strategy objects.
        """
        return [
            strategy() for strategy in strategies if issubclass(strategy, BaseStrategy)
        ]

    def _instantiate_middle_strategies(self) -> List[BaseStrategy]:
        """
        Instantiates the middle strategies.

        Returns:
            list: A list of instantiated middle strategy objects.
        """
        start_end_classes = {
            strategy.__class__
            for strategy in self.start_strategies + self.end_strategies
        }
        return [
            strategy()
            for strategy in BaseStrategy.get_subclasses()
            if strategy not in start_end_classes
        ]

    def process(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes the config_dict using the instantiated strategies.

        Args:
            config_dict (dict): The configuration dictionary to be processed.

        Returns:
            dict: The modified config_dict after processing it with all the
            strategies.
        """
        context = config_dict.copy()  # Make a copy of the passed-in dict
        for strategy in self.all_strategies:
            try:
                logger.info(strategy.__class__)  # Print the class name for debugging
                strategy.compute(context)  # Pass only context
            except Exception as e:
                logger.exception(f"Error occurred during strategy computation: {e}")
        return context  # Return the modified context
