import os
import unittest

from dotenv import load_dotenv

from easy_expectations.main import main

load_dotenv()


class TestIntegrationGCS(unittest.TestCase):
    @unittest.skipUnless(
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
        "Requires GOOGLE_APPLICATION_CREDENTIALS environment variable",
    )
    @unittest.skipUnless(
        os.environ.get("EE_BUCKET"), "Requires EE_BUCKET environment variable"
    )
    @unittest.skipUnless(
        os.environ.get("SOURCE"), "Requires SOURCE environment variable"
    )
    def test_conditional(self):
        wrapper = main("tests/integration/config_files/gcs_success.yaml")

        results = wrapper.validation_results["_run_results"][
            next(iter(wrapper.validation_results["_run_results"]))
        ]["validation_result"]["results"]

        # Now we'll check if all expectations were successful
        all_successful = all(result["success"] for result in results)
        self.assertTrue(all_successful)
