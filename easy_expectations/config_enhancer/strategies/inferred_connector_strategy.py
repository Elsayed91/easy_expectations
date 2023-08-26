from easy_expectations.config_enhancer.system_config import ConstantsConfig

from .base_strategy import BaseStrategy


class ResolveDataConnectorInferredConnectorStrategy(BaseStrategy):
    inferred_connector_mapping = ConstantsConfig().get_inferred_connector_mapping()

    def compute(self, context):
        data_connector_type = context.get("data_connector_type", None)
        if data_connector_type:
            inferred_connector = self.inferred_connector_mapping.get(
                data_connector_type, None
            )
            if inferred_connector:
                context["data_connector_inferred_connector"] = inferred_connector
