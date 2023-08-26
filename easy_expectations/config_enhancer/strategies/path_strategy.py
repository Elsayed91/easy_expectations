from .base_strategy import BaseStrategy


class ResolvePathDefaultsStrategy(BaseStrategy):
    def __init__(
        self,
        keys=[
            "expectations_store_path",
            "validations_store_path",
            "checkpoint_store_path",
        ],
        default_key="artifacts_path",
    ):
        self.keys = keys
        self.default_key = default_key

    def compute(self, context):
        default_value = context.get(self.default_key, None)
        self._iterate_keys_and_set_values(context, default_value)

    def _iterate_keys_and_set_values(self, context, default_value):
        for key in self.keys:
            value = context.get(key, None)
            if value is None and default_value is not None:
                context[key] = default_value
