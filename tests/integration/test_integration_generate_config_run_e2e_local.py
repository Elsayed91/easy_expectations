import csv
import os
import subprocess
import sys
import tempfile
import unittest

from easy_expectations import CONFIG_DATA

os.environ["PYTHONPATH"] = os.getcwd()

import csv
import os
import subprocess
import sys
import tempfile
import unittest

from easy_expectations import CONFIG_DATA


class TestGenerateConfig(unittest.TestCase):
    @unittest.skipUnless(
        os.environ.get("OPENAI_API_KEY"),
        "Requires OPENAI_API_KEY set in environment.",
    )
    def test_generate_config(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Create sample CSV file
            csv_path = os.path.join(
                tmpdirname, "local_tests", "sample_data.csv"
            )
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)

            csv_data = [
                ["Name", "Age", "Salary", "Department"],
                ["Alice", 25, 50000, "HR"],
                ["Bob", 30, 60000, "IT"],
                ["Charlie", 35, 70000, "Finance"],
                # ... add more rows as needed
            ]

            with open(csv_path, "w", newline="") as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerows(csv_data)

            # Create ge directory
            ge_dir = os.path.join(tmpdirname, "local_tests", "ge")
            os.makedirs(ge_dir, exist_ok=True)
            input_str = f"2\nlocal:local_tests/sample_data.csv\n1\nlocal:local_tests/ge\n1\n1\nno\n1\n2\n2\n1. expect Name values to be unique. 2. expect Age to be between 0 and 100 3. expect Salary to be between 0 and 5000000 4. expect Department to be one of HR, IT, Finance\ncc\ny"
            cmd = f"echo '{input_str}' | {sys.executable} -m easy_expectations"
            subprocess.run(cmd, shell=True, check=True, cwd=tmpdirname)

            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                cwd=tmpdirname,
                text=True,
                capture_output=True,
            )

            output = result.stdout

            # Check for the expected output in the printed results
            expected_lines = [
                "expect_column_values_to_be_unique     True",
                "expect_column_values_to_be_between     True",
                "expect_column_values_to_be_between     True",
                "expect_column_values_to_be_in_set     True",
            ]
            for line in expected_lines:
                self.assertIn(line, output)


if __name__ == "__main__":
    unittest.main()
