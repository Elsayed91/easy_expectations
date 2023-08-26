import os
import subprocess
import sys
import tempfile
import unittest

from easy_expectations import CONFIG_DATA


class TestGenerateSkeleton(unittest.TestCase):
    os.environ["PYTHONPATH"] = os.getcwd()

    def test_generate_empty(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Run the command
            cmd = f"echo '1\n' | {sys.executable} \
            {os.path.join(os.getcwd(), 'easy_expectations', 'cli', 'cli.py')}"
            subprocess.run(cmd, shell=True, check=True, cwd=tmpdirname)

            # Check if file is created
            expected_file = os.path.join(
                tmpdirname, "easy_expectations_config.yaml"
            )
            self.assertTrue(os.path.exists(expected_file))

            # Compare contents
            with open(expected_file, "r") as f:
                generated_content = f.read()

            with open(CONFIG_DATA["easy_expectations_skeleton"], "r") as f:
                expected_content = f.read()
            self.assertEqual(generated_content, expected_content)


if __name__ == "__main__":
    unittest.main()
