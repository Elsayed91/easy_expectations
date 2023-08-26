import os
import shutil
import tempfile
import unittest

import pandas as pd
import yaml

from easy_expectations.main import main


class TestIntegrationInMemory(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.temp_dir = tempfile.mkdtemp()

        # Make a copy of your original YAML files in the temporary directory
        # and update their paths
        self.copy_and_update_yaml(
            "tests/integration/config_files/in_memory_success.yaml"
        )
        self.copy_and_update_yaml(
            "tests/integration/config_files/in_memory_fail.yaml"
        )

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def copy_and_update_yaml(self, original_yaml_path):
        # Copy the file to the temporary directory
        base_name = os.path.basename(original_yaml_path)
        temp_yaml_path = os.path.join(self.temp_dir, base_name)
        shutil.copyfile(original_yaml_path, temp_yaml_path)

        # Load and update the config from the copied file
        with open(temp_yaml_path) as file:
            config = yaml.safe_load(file)

        # Assuming you have a key like 'Artifacts' -> 'Location' to update
        # Modify this as per your actual YAML structure
        config["Artifacts"]["Location"] = f"local://{self.temp_dir}"

        # Save the modified config back to the copied file
        with open(temp_yaml_path, "w") as file:
            yaml.safe_dump(config, file)

    def test_success(self):
        # Create some data that should fail one of the expectations
        data_pass = {
            "Name": ["Anna", "Erik", "Beth", "Liam"],
            "Age": [25, 27, 28, 30],
            "Salary": [55000, 60000, 65000, 70000],
            "Department": ["HR", "IT", "Finance", "IT"],
        }
        # Setting the dataframe in global scope
        globals()["df_pass"] = pd.DataFrame(data_pass)

        try:
            wrapper = main(f"{self.temp_dir}/in_memory_success.yaml")

            results = wrapper.validation_results["_run_results"][
                next(iter(wrapper.validation_results["_run_results"]))
            ]["validation_result"]["results"]

            # Now we'll check if all expectations were successful
            all_successful = all(result["success"] for result in results)
            self.assertTrue(all_successful)

        finally:
            # Remove the dataframe from global scope
            del globals()["df_pass"]

    def test_specific_expectation_failure(self):
        # Create some data that should fail one of the expectations
        data_fail = {
            "Name": [None, "Erik", "Beth", "Alice"],
            "Age": [25, 55, 28, 30],
            "Department": ["HR", "IT", "Finance", "Marketing"],
        }
        # Setting the dataframe in global scope
        globals()["df_fail"] = pd.DataFrame(data_fail)

        try:
            wrapper = main(f"{self.temp_dir}/in_memory_fail.yaml")

            # Check the failure of the specific expectation
            failed_expectation_row = wrapper.summary_df[
                wrapper.summary_df["expectation_type"]
                == "expect_column_values_to_not_be_null"
            ].iloc[0]

            self.assertFalse(failed_expectation_row["success"])

        except Exception as e:
            exception_message = str(e)
            # Check that the exception message contains the expected text
            self.assertIn("Validation failed", exception_message)
            self.assertIn("success rate 66.66666666666666%", exception_message)
            self.assertIn("below the threshold 100.0%", exception_message)
        else:
            self.fail("Expected Exception not raised")
        finally:
            # Remove the dataframe from global scope
            del globals()["df_fail"]


if __name__ == "__main__":
    unittest.main()
