from easy_expectations.ai_expectations.flows.base_conversation_flow import (
    ConversationFlow,
)
from easy_expectations.ai_expectations.profiler_utils import (
    get_supported_functions,
    get_types_from_yaml,
)


class ProfilerFlow(ConversationFlow):
    DEFAULT_EXPECTATIONS_MSG = """
    Use only valid Great Expectations Expectations and their args as reference
    do not make up any expectations that are not documented. The checks MUST
    EXCLUDE TYPE, NULL, EXISTANCE CHECKS. THIS MEANS:
    expect_column_values_to_be_of_type,
    expect_column_values_to_be_of_type_list,
    expect_column_values_to_not_be_null, expect_column_to_exist CANNOT BE USED.
    """
    PROVIDED_EXPECTATIONS_SUFFIX = """\n
    The checks MUST EXCLUDE TYPE, NULL, EXISTANCE CHECKS. THIS MEANS:
    expect_column_values_to_be_of_type,
    expect_column_values_to_be_of_type_list,
    expect_column_values_to_not_be_null, expect_column_to_exist CANNOT BE USED.
    """

    PROVIDED_EXPECTATIONS_PREFIX = """\n
    "Use these expectations as guideline and dont use your previous knowledge
    immediately. for instance validating dates should be done using
    expect_column_values_to_be_dateutil_parseable or
    expect_column_values_to_match_strftime_format: \n"
    """

    def __init__(self, usr_msg, backend="Pandas", use_reference=False):
        super().__init__()
        self.backend = backend
        self.use_reference = use_reference
        if not self.use_reference:
            self.supported_expectations = self.DEFAULT_EXPECTATIONS_MSG
        else:
            self.supported_expectations = (
                self.PROVIDED_EXPECTATIONS_PREFIX
                + get_supported_functions(self.backend)
                + self.PROVIDED_EXPECTATIONS_SUFFIX
            )
        self.usr_msg = usr_msg
        self._build_flow()

    def _build_flow(self):
        self._add_system_message()
        self._add_sample_data_message()
        self._add_assistant_expectations_message()
        self._add_user_message()

    def _add_system_message(self):
        self.add_message(
            "system",
            f"""
            You are an expert tasked with providing data quality checks given a
            data sample, the checks must generalize well.
            {self.supported_expectations}
        """,
        )

    def _add_sample_data_message(self):
        self.add_message(
            "user",
            """
            PatientID,Diagnosis,Age,Treatment
            1234,Diabetes,60,Insulin
            5678,Heart Disease,55,Beta-blockers
            9012,Asthma,35,Inhaler
            3456,Migraine,40,Anti-inflammatory
            7890,Anemia,50,Iron Supplement""",
        )

    def _add_assistant_expectations_message(self):
        self.add_message(
            "assistant",
            """
            expect_column_values_to_be_increasing(column='PatientID')
            expect_column_values_to_be_unique(column='PatientID')
            expect_column_values_to_be_between(column='Age', min_value=0,
            max_value=100)
            expect_column_values_to_be_in_set(column='Diagnosis',
            value_set=['Diabetes', 'Heart Disease', 'Asthma', 'Migraine',
            'Anemia'])
            expect_column_values_to_be_in_set(column='Treatment',
            value_set=['Insulin', 'Beta-blockers', 'Inhaler',
            'Anti-inflammatory', 'Iron Supplements'])""",
        )

    def _add_user_message(self):
        self.add_message("user", self.usr_msg)
