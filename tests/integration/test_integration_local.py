import os
import shutil
import tempfile
import unittest

import yaml

from easy_expectations.main import main


class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.temp_dir = tempfile.mkdtemp()

        # Make a copy of your original YAML files in the temporary directory
        # and update their paths
        self.copy_and_update_yaml(
            "tests/integration/config_files/local_success.yaml"
        )
        self.copy_csv_file("tests/integration/config_files/sample_data.csv")

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def copy_and_update_yaml(self, original_yaml_path):
        base_name = os.path.basename(original_yaml_path)
        temp_yaml_path = os.path.join(self.temp_dir, base_name)
        shutil.copyfile(original_yaml_path, temp_yaml_path)

        # Update the YAML file as needed
        with open(temp_yaml_path, "r") as file:
            config = yaml.safe_load(file)

        config["Artifacts"]["Location"] = f"local://{self.temp_dir}"
        config["Data Source"][
            "Source"
        ] = f"local://{self.temp_dir}/sample_data.csv"

        with open(temp_yaml_path, "w") as file:
            yaml.safe_dump(config, file)

    def copy_csv_file(self, original_csv_path):
        base_name = os.path.basename(original_csv_path)
        temp_csv_path = os.path.join(self.temp_dir, base_name)
        shutil.copyfile(original_csv_path, temp_csv_path)

    def test_success(self):
        wrapper = main(f"{self.temp_dir}/local_success.yaml")

        results = wrapper.validation_results["_run_results"][
            next(iter(wrapper.validation_results["_run_results"]))
        ]["validation_result"]["results"]

        # Now we'll check if all expectations were successful
        all_successful = all(result["success"] for result in results)
        self.assertTrue(all_successful)


if __name__ == "__main__":
    unittest.main()
