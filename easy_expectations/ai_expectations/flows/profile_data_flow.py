from easy_expectations.ai_expectations.flows.base_conversation_flow import (
    ConversationFlow,
)
from easy_expectations.ai_expectations.profiler_utils import get_types_from_yaml


class ProfilerDataFlow(ConversationFlow):
    def __init__(self, dataframe, backend):
        super().__init__()
        self.dataframe = dataframe
        self.backend = backend
        self._build_flow()

    def _build_flow(self):
        self._add_system_message()
        self._add_user_bigquery_data_message()
        self._add_assistant_bigquery_expectations_message()
        self._add_user_redshift_data_message()
        self._add_assistant_redshift_expectations_message()
        self._add_user_custom_data_message()

    def _add_system_message(self):
        self.add_message(
            "system",
            """
            You will be given sample data and the system native datatypes. 
            You will produce a number of data type checks for the data.
        """,
        )

    def _add_user_bigquery_data_message(self):
        self.add_message(
            "user",
            f"""
            df:          
            PatientID,Diagnosis
            1234,Diabetes

            datatypes:
            {get_types_from_yaml(source='bigquery')}
        """,
        )

    def _add_assistant_bigquery_expectations_message(self):
        self.add_message(
            "assistant",
            """
            expect_column_values_to_be_of_type(column="PatientID",
            type_=INTEGER)
            expect_column_values_to_be_of_type(column="Diagnosis",
            type_=STRING)
        """,
        )

    def _add_user_redshift_data_message(self):
        self.add_message(
            "user",
            """
            df:          
            Age,Treatment
            60,Insulin

            datatypes:
            {get_types_from_yaml(source='redshift')}
        """,
        )

    def _add_assistant_redshift_expectations_message(self):
        self.add_message(
            "assistant",
            """
            expect_column_values_to_be_of_type(column="Age", type_=numeric)
            expect_column_values_to_be_of_type(column="Treatment",
            type_=varchar)
        """,
        )

    def _add_user_custom_data_message(self):
        self.add_message(
            "user",
            f"""
            df: {self.dataframe}
            datatypes: {get_types_from_yaml(source=self.backend)}
        """,
        )
