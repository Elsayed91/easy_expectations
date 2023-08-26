from .base_strategy import BaseStrategy


class DataConnectorCheckpointConnectorStrategy(BaseStrategy):
    """
    A strategy class for determining the appropriate checkpoint connector based
    on the data connector type.
    """

    def compute(self, context):
        """
        Compute the checkpoint connector based on the data connector type.

        Args:
            context (dict): The context dictionary containing the data
            connector type and other relevant information.

        Returns:
            None
        """

        # Retrieve 'data_connector_type' from the context
        data_connector_type = context.get("data_connector_type")

        # Initialize the checkpoint_connector
        checkpoint_connector = None

        # Check the conditions based on 'data_connector_type'
        if data_connector_type == "in_memory":
            checkpoint_connector = "default_runtime_data_connector_name"
        elif "_database" in data_connector_type:
            if "data_connector_query" in context:
                checkpoint_connector = "default_runtime_data_connector_name"
            elif "data_connector_table" in context:
                checkpoint_connector = "default_inferred_data_connector_name"
        elif data_connector_type in ["s3", "local", "azure", "gcs"]:
            if context.get("data_connector_filename"):
                checkpoint_connector = "default_runtime_data_connector_name"
            else:
                checkpoint_connector = "default_inferred_data_connector_name"

        # If the checkpoint_connector is determined, update the context
        if checkpoint_connector is not None:
            key = "data_connector_checkpoint_connector"
            context[key] = checkpoint_connector
