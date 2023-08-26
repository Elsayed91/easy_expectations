from easy_expectations.ai_expectations.flows.base_conversation_flow import (
    ConversationFlow,
)
from easy_expectations.ai_expectations.profiler_utils import (
    get_supported_functions,
    get_types_from_yaml,
)


class RequirementFlow(ConversationFlow):
    DEFAULT_EXPECTATIONS_MSG = """
    Use only valid and verified Great Expectations expectations. Do not use any
    that are not documented. If a request does not have a matching expectation,
    simply skip it.
    """
    EXPECATIONS_MSG_SUFFIX = """
    \nUse only the above provided expectations to fulfill user requests.
    

    Important: For date format validation use
    expect_column_values_to_be_dateutil_parseable or
    expect_column_values_to_match_strftime_format
    """

    def __init__(self, usr_msg, backend="Pandas", use_reference=False):
        super().__init__()
        self.backend = backend
        self.use_reference = use_reference
        if not self.use_reference:
            self.supported_expectations = self.DEFAULT_EXPECTATIONS_MSG
        else:
            self.supported_expectations = (
                get_supported_functions(self.backend) + self.EXPECATIONS_MSG_SUFFIX
            )
        self.usr_msg = usr_msg
        self._build_flow()

    def _build_flow(self):
        self._add_system_message()
        self._add_user_requirements_message()
        self._add_assistant_expectations_message()
        self._add_user_response_message()

    def _add_system_message(self):
        self.add_message(
            "system",
            f"""
            {self.supported_expectations}
            For type checks with expect_column_values_to_be_of_type, ONLY use native datatypes for the backend provided by user.
            
            If the provided expectations does not have one that can fulfill the user's request, DO NOT FULFILL REQUEST, simply skip it. 
        """,
        )

    def _add_user_requirements_message(self):
        self.add_message(
            "user",
            f"""
            only use existent expectations. If it doesnt exist, skip it. 
            
            native datatypes:  {get_types_from_yaml(source='bigquery')}
            
            requirements:
            1. PatientID, Visit Date cannot be null.
            2. All columns set must exist.
            3. Gender must be either M or F
            4. All columns must be of a logically acceptable type
            5. Treatment must be within a set of logical values
            6. Visit Date must be in parsable date format
            7. PatientID must be increasing value
            8. Age must be between 0 and 100
            9. table must have 6 columns
            10. table must have 5000 rows
            11. sum of values of age column must be between 4000 and 5000
            12. PatientID must be a positive integer

        """,
        )

    def _add_assistant_expectations_message(self):
        self.add_message(
            "assistant",
            """
            expect_column_values_to_not_be_null(column='PatientID')
            expect_column_values_to_not_be_null(column='Visit Date')
            expect_column_to_exist(column='PatientID')
            expect_column_to_exist(column='Visit Date')
            expect_column_to_exist(column='Gender')
            expect_column_to_exist(column='Treatment')
            expect_column_to_exist(column='Age')
            expect_column_values_to_be_in_set(column='Gender', value_set=['M',
            'F'])
            expect_column_values_to_be_in_set(column='Treatment',
            value_set=['TreatmentValue1', 'TreatmentValue2'])  
            expect_column_values_to_be_of_type(column='Visit Date',
            type_='DATE')
            expect_column_values_to_be_increasing(column='PatientID')
            expect_column_values_to_be_between(column='Age', min_value=0,
            max_value=100)
            expect_table_column_count_to_be(column_count=6)
            expect_table_row_count_to_be(row_count=5000)
            expect_column_sum_to_be_between(column='Age', min_sum=4000,
            max_sum=5000)
        """,
        )

    def _add_user_response_message(self):
        self.add_message(
            "user",
            f"""
            only use existent expectations. If it doesnt exist, skip it. 

            native datatypes: {get_types_from_yaml(source=self.backend)}
            requirements:
            {self.usr_msg}
                         """,
        )
