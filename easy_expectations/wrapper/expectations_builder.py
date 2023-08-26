from great_expectations.core import ExpectationConfiguration, ExpectationSuite


class ExpectationSuiteBuilder:
    def build(self):
        raise NotImplementedError


class ColumnExpectationSuiteBuilder(ExpectationSuiteBuilder):
    # https://robertsahlin.substack.com/p/one-streamprocessor-to-rule-them
    def __init__(
        self,
        columns,
        ge_ver,
        expectation_suite_name,
        contract_column_set_matching,
    ):
        self.columns = columns
        self.ge_ver = ge_ver
        self.expectation_suite_name = expectation_suite_name
        self.contract_column_set_matching = contract_column_set_matching

    def _generate_expectations(self):
        expectations = []

        # Extract column names for the 'expect_table_columns_to_match_set' expectation
        column_names = [col["name"] for col in self.columns]

        # Add the expectation to ensure columns exist
        expectations.append(
            ExpectationConfiguration(
                expectation_type="expect_table_columns_to_match_set",
                kwargs={
                    "column_set": column_names,
                    "exact_match": self.contract_column_set_matching,
                },
            )
        )

        # Process each column and generate expectations based on its properties
        for col in self.columns:
            # Create meta if a description is provided
            meta = None
            if "description" in col and col["description"]:
                meta = {
                    "notes": {
                        "format": "markdown",
                        "content": [col["description"]],
                    }
                }

            # If the column mode is REQUIRED, expect values to not be null
            if col.get("mode", "NULLABLE") == "REQUIRED":
                expectations.append(
                    ExpectationConfiguration(
                        expectation_type="expect_column_values_to_not_be_null",
                        kwargs={"column": col["name"]},
                        meta=meta,
                    )
                )

            # Handling both lists and comma-separated strings for 'type'
            if isinstance(col["type"], str):
                types = [t.strip() for t in col["type"].split(",")]
            else:
                types = col["type"]

            # Choose the appropriate expectation based on the number of types
            if len(types) > 1:
                expectations.append(
                    ExpectationConfiguration(
                        expectation_type="expect_column_values_to_be_in_type_list",
                        kwargs={"column": col["name"], "type_list": types},
                        meta=meta,
                    )
                )
            else:
                expectations.append(
                    ExpectationConfiguration(
                        expectation_type="expect_column_values_to_be_of_type",
                        kwargs={"column": col["name"], "type_": types[0]},
                        meta=meta,
                    )
                )

        return expectations

    def build(self):
        expectations = self._generate_expectations()
        suite = ExpectationSuite(
            expectation_suite_name=self.expectation_suite_name,
            meta={"great_expectations_version": self.ge_ver},
            expectations=expectations,
        )
        return suite


from easy_expectations.utils.logger import logger


class TestsExpectationSuiteBuilder(ExpectationSuiteBuilder):
    def __init__(self, tests, ge_ver, expectation_suite_name):
        self.tests = tests
        self.ge_ver = ge_ver
        self.expectation_suite_name = expectation_suite_name

    def _generate_expectations(self):
        expectations = []
        for test in self.tests:
            expectation = ExpectationConfiguration(
                expectation_type=test["expectation"],
                kwargs=test["kwargs"],
                meta=test["meta"] if "meta" in test else {},
            )
            expectations.append(expectation)
        return expectations

    def build(self):
        expectations = self._generate_expectations()
        suite = ExpectationSuite(
            expectation_suite_name=self.expectation_suite_name,
            meta={"great_expectations_version": self.ge_ver},
            expectations=expectations,
        )
        return suite
