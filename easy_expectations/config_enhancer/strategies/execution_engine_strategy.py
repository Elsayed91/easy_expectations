from .base_strategy import BaseStrategy


class ExecutionEngineStrategy(BaseStrategy):
    def compute(self, context):
        data_connector_type = context["data_connector_type"]
        if data_connector_type.endswith("_database"):
            context["data_connector_execution_engine"] = "SqlAlchemyExecutionEngine"
        elif data_connector_type == "dbfs" or (
            context.get("data_connector_execution_engine") == "Spark"
        ):
            context["data_connector_execution_engine"] = "SparkDFExecutionEngine"
        else:
            context["data_connector_execution_engine"] = "PandasExecutionEngine"
