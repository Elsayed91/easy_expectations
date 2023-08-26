from .base_strategy import BaseStrategy


class BatchIdentifiersStrategy(BaseStrategy):
    def compute(self, context):
        """
        Compute function that takes in a context dictionary and updates it if
        "batch_identifiers" key is missing or empty.

        Args:
            context (dict): A dictionary representing the context.

        Returns:
            None
        """
        batch_identifiers = context.get("batch_identifiers", None)
        if not batch_identifiers:
            context["batch_identifiers"] = {
                "default_identifier_name": "default_identifier"
            }
