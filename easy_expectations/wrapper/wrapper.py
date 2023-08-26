import inspect
from typing import Any, Optional

import pandas as pd
import yaml
from great_expectations.core.expectation_configuration import (
    ExpectationConfiguration,
)
from great_expectations.core.expectation_suite import ExpectationSuite
from great_expectations.data_context import BaseDataContext
from great_expectations.data_context.types.base import DataContextConfig

from easy_expectations.utils.logger import logger
from easy_expectations.wrapper.expectations_builder import (
    ColumnExpectationSuiteBuilder,
    TestsExpectationSuiteBuilder,
)


def get_dataframe_from_caller(name: str):
    """
    Fetch a variable by its name from the caller's global namespace.

    Args:
        name (str): The name of the variable/dataframe.

    Returns:
        The variable/dataframe if found, None otherwise.
    """
    frame = inspect.currentframe()

    # Start from the current frame and move upwards
    while frame is not None:
        # If the variable is found in the current frame's global scope, check its type
        variable = frame.f_globals.get(name)
        if variable is not None:
            type_name = type(variable).__name__
            module_name = type(variable).__module__

            # If the variable is a Pandas DataFrame
            if type_name == "DataFrame" and module_name == "pandas.core.frame":
                return variable
            # If the variable is a Spark DataFrame without importing Spark
            elif (
                type_name == "DataFrame"
                and module_name == "pyspark.sql.dataframe"
            ):
                return variable

        # Move one level up in the call stack
        frame = frame.f_back

    return None


class GreatExpectationsWrapper:
    def __init__(
        self,
        ge_config_dict: dict[str, Any],
        cp_config_dict: dict[str, Any],
        context_dict: dict[str, Any],
        generate_docs: bool,
    ):
        self.ge_config_dict = ge_config_dict
        self.cp_config_dict = cp_config_dict
        self.context_dict = context_dict
        self.generate_docs = generate_docs
        self.data_context = None
        self.validation_results = None

    def with_data_context(self):
        logger.info("Preparing data context...")
        ge_config = yaml.safe_load(self.ge_config_dict)
        try:
            self.data_context = BaseDataContext(DataContextConfig(**ge_config))
        except Exception as e:
            logger.error(f"Error while preparing data context: {e}")
            raise e
        return self

    def with_checkpoint(self):
        logger.info("Preparing checkpoint...")
        cp_config = yaml.safe_load(self.cp_config_dict)
        self.data_context.add_or_update_checkpoint(**cp_config)
        return self

    def with_run_checkpoint(self):
        logger.info("Running checkpoint...")
        batch_type, batch_input = self._get_runtime_batch_request_parameters()
        checkpoint_name = self.context_dict.get("checkpoint_name")
        run_checkpoint_args = {"checkpoint_name": checkpoint_name}

        if batch_type is not None and batch_input is not None:
            run_checkpoint_args["batch_request"] = {
                "runtime_parameters": {batch_type: batch_input},
            }

        self.validation_results = dict(
            self.data_context.run_checkpoint(**run_checkpoint_args)
        )

        return self

    def with_data_docs(self):
        logger.info("Building data docs...")
        self.data_context.build_data_docs()
        return self

    def with_check_success_threshold(self):
        success_threshold: Optional[float] = self.context_dict.get(
            "success_threshold", 100.0
        )
        logger.info("Checking success threshold...")
        results = self.validation_results["_run_results"][
            next(iter(self.validation_results["_run_results"]))
        ]["validation_result"]["results"]
        success_count = sum(result["success"] for result in results)
        success_rate = (success_count / len(results)) * 100
        if success_rate < success_threshold:
            error_message = f"Validation failed: success rate {success_rate}% is below the threshold {success_threshold}%"
            logger.error(error_message)
            raise Exception(error_message)
        return self

    def with_summary_table(self):
        generate_summary_csv = self.context_dict.get(
            "generate_summary_csv", False
        )

        results = self.validation_results["_run_results"][
            next(iter(self.validation_results["_run_results"]))
        ]["validation_result"]["results"]
        rows = []
        for result in results:
            row = {
                "expectation_type": result["expectation_config"][
                    "expectation_type"
                ],
                "success": result["success"],
            }
            row_data = result["result"]
            for key, value in row_data.items():
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                row[key] = value
            rows.append(row)
        df = pd.DataFrame(rows)
        print(df.iloc[:, :2])

        if generate_summary_csv:
            csv_path = (
                "summary.csv"  # Set the appropriate path to save the CSV
            )
            df.to_csv(csv_path, index=False)

        return self

    def with_expectations_suite(self):
        builder = self._get_expectation_suite_builder()
        if builder:  # If builder is not None
            suite = builder.build()
            self.data_context.add_or_update_expectation_suite(
                expectation_suite=suite
            )
        return self

    def with_clean_temp(self):
        actual_path = self.context_dict.get("artifacts_path", "").replace(
            "local:", ""
        )
        if "/tmp/" in actual_path:
            import shutil

            shutil.rmtree(actual_path, ignore_errors=True)

        return self

    def _get_expectation_suite_builder(self):
        expectations_file = self.context_dict.get("expectations_file")
        expectations_suite_name = self.context_dict.get(
            "expectations_suite_name", None
        )
        if (
            expectations_file and expectations_file.strip()
        ):  # Check if it exists and is not empty
            return None
        elif "contract_tests" in self.context_dict:
            columns = self.context_dict["contract_tests"]
            print(columns)
            if not columns:
                raise ValueError(
                    "The 'columns' list in 'data_contract_schema' cannot be empty."
                )
            return ColumnExpectationSuiteBuilder(
                columns,
                "0.17.9",
                self.context_dict.get("expectations_suite_name"),
                self.context_dict.get("contract_column_set_matching", False),
            )
        elif expectations_suite_name:
            logger.info("failing here? _get_expectation_suite_builder")
            tests = self.context_dict.get("tests", [])
            return TestsExpectationSuiteBuilder(
                tests, "0.17.9", expectations_suite_name
            )

        else:
            raise ValueError(
                "Unable to determine the correct builder for expectations suite."
            )

    def build(self):
        return self

    # def _get_runtime_batch_request_parameters(self):
    #     logger.info("Getting runtime batch request parameters...")
    #     data_connector = self.context_dict.get("data_connector", {})
    #     data_connector_type = data_connector.get("type")
    #     checkpoint_connector = data_connector.get("checkpoint_connector")

    #     if checkpoint_connector == "default_runtime_data_connector_name":
    #         if data_connector_type == "in_memory":
    #             df_name = data_connector.get("dataframe") or data_connector.get("path")
    #             return "batch_data", globals()[df_name]

    #         if data_connector_type in ["local", "gcs", "azure", "s3", "dbfs"]:
    #             path = data_connector.get("path")
    #             path = path.replace("local://", "")
    #             return "path", path

    #         if "_database" in data_connector_type:
    #             return "query", data_connector.get("query")

    #     logger.warning(
    #         "No runtime batch request parameters found in the configuration."
    #     )
    #     return None, None

    def _get_runtime_batch_request_parameters(self):
        logger.info("Getting runtime batch request parameters...")
        data_connector = self.context_dict.get("data_connector", {})
        data_connector_type = data_connector.get("type")
        checkpoint_connector = data_connector.get("checkpoint_connector")

        if checkpoint_connector == "default_runtime_data_connector_name":
            if data_connector_type == "in_memory":
                df_name = data_connector.get(
                    "dataframe"
                ) or data_connector.get("path")

                # Use the function to fetch the dataframe from caller's namespace
                dataframe = get_dataframe_from_caller(df_name)
                if dataframe is None:
                    raise ValueError(
                        f"No dataframe exists in caller's global scope with name {df_name}"
                    )

                return "batch_data", dataframe

            if data_connector_type in ["local", "gcs", "azure", "s3", "dbfs"]:
                path = data_connector.get("path")
                path = path.replace("local:", "")
                return "path", path

            if "_database" in data_connector_type:
                return "query", data_connector.get("query")

        logger.warning(
            "No runtime batch request parameters found in the configuration."
        )
        return None, None
