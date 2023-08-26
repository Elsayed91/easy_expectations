import tempfile

from .base_strategy import BaseStrategy


class ArtifactsPathStrategy(BaseStrategy):
    def compute(self, context):
        """
        Compute function that checks if "artifacts_path" is None or missing.
        If so, it sets it to the path of a temporary directory.

        Args:
            context (dict): A dictionary representing the context.

        Returns:
            None
        """
        if context.get("artifacts_path") is None:
            # Get a new temp directory path
            temp_dir_path = tempfile.mkdtemp()
            context["artifacts_path"] = "local:" + temp_dir_path
