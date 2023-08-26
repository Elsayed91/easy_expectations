from textwrap import dedent

from profiler_utils import get_supported_functions, get_types_from_yaml


class ConversationFlow:
    def __init__(self):
        self.flow = []

    def add_message(self, role, content):
        self.flow.append({"role": role, "content": content})

    def get_flow(self):
        return self.flow

    @classmethod
    def from_messages(cls, messages):
        """
        flow_instance = ConversationFlow.from_messages(messages)
        print(flow_instance.get_flow())
        """
        instance = cls()
        for message in messages:
            instance.add_message(message["role"], message["content"])
        return instance


class ProfilerFlow(ConversationFlow):
    DEFAULT_EXPECTATIONS_MSG = """
    Use only valid Great Expectations Expectations and their args as reference do not make up any expectations that are not documented.
    The checks MUST EXCLUDE TYPE, NULL, EXISTANCE CHECKS. THIS MEANS: expect_column_values_to_be_of_type, expect_column_values_to_be_of_type_list, expect_column_values_to_not_be_null, expect_column_to_exist CANNOT BE USED.
    """
    PROVIDED_EXPECTATIONS_SUFFIX = """\n
    The checks MUST EXCLUDE TYPE, NULL, EXISTANCE CHECKS. THIS MEANS: expect_column_values_to_be_of_type, expect_column_values_to_be_of_type_list, expect_column_values_to_not_be_null, expect_column_to_exist CANNOT BE USED.
    """

    def __init__(self, usr_msg, backend="Pandas", use_reference=False):
        super().__init__()
        self.backend = backend
        self.use_reference = use_reference
        if not self.use_reference:
            self.supported_expectations = self.DEFAULT_EXPECTATIONS_MSG
        else:
            self.supported_expectations = (
                "Use these expectations as guideline and dont use your previous knowledge immediately. for instance validating dates should be done using expect_column_values_to_be_dateutil_parseable or expect_column_values_to_match_strftime_format:"
                + get_supported_functions(self.backend)
                + self.PROVIDED_EXPECTATIONS_SUFFIX
            )
        self.usr_msg = usr_msg
        self._build_flow()

    def _build_flow(self):
        self.add_message(
            "system",
            f"""
                You are an expert tasked with providing data quality checks given a data sample, the checks must generalize well.
                {self.supported_expectations}
                
                """,
        )
        self.add_message(
            "user",
            """
                PatientID,Diagnosis,Age,Treatment
                1234,Diabetes,60,Insulin
                5678,Heart Disease,55,Beta-blockers
                9012,Asthma,35,Inhaler
                3456,Migraine,40,Anti-inflammatory
                7890,Anemia,50,Iron Supplementsg""",
        )
        self.add_message(
            "assistant",
            """
expect_column_values_to_be_increasing(column='PatientID')
expect_column_values_to_be_unique(column='PatientID')
expect_column_values_to_be_between(column='Age', min_value=0, max_value=100)
expect_column_values_to_be_in_set(column='Diagnosis', value_set=['Diabetes', 'Heart Disease', 'Asthma', 'Migraine', 'Anemia'])
expect_column_values_to_be_in_set(column='Treatment', value_set=['Insulin', 'Beta-blockers', 'Inhaler', 'Anti-inflammatory', 'Iron Supplements'])""",
        )
        self.add_message("user", self.usr_msg)


# flow = ProfilerFlow()
# print(flow.get_flow())


class ProfilerDataFlow(ConversationFlow):
    def __init__(self, dataframe, backend):
        super().__init__()
        self.dataframe = dataframe
        self.backend = backend
        self._build_flow()

    def _build_flow(self):
        self.add_message(
            "system",
            f"""
                You will be given sample data and the system native datatypes. You will produce a number of data type checks for the data.
                """,
        )
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
        self.add_message(
            "assistant",
            f"""
expect_column_values_to_be_of_type(column="PatientID", type_=INTEGER)
expect_column_values_to_be_of_type(column="Diagnosis", type_=STRING)
                """,
        )
        self.add_message(
            "user",
            f"""
df:          
Age,Treatment
60,Insulin

datatypes:
{get_types_from_yaml(source='redshift')}
                """,
        )
        self.add_message(
            "assistant",
            f"""
expect_column_values_to_be_of_type(column="Age", type_=numeric)
expect_column_values_to_be_of_type(column="Treatment", type_=varchar)
                """,
        )
        self.add_message(
            "user",
            f"""
df: {self.dataframe}
datatypes: {get_types_from_yaml(source=self.backend)}
                """,
        )


class RequirementFlow(ConversationFlow):
    def __init__(self, usr_msg, backend="Pandas", use_reference=False):
        super().__init__()
        self.backend = backend
        self.use_reference = use_reference
        if not self.use_reference:
            self.supported_expectations = "Use only valid and verified Great Expectations expectations. Do not use any that are not documented. If a request does not have a matching expectation, simply skip it."
        else:
            self.supported_expectations = (
                get_supported_functions(self.backend)
                + "\nUnderstand the above expectations and use them to fulfill user requests. If a corresponding expectation doesn't exist, simply skip the request, do not use an expectation that doesnt exist above. For date format validation use expect_column_values_to_be_dateutil_parseable or expect_column_values_to_match_strftime_format "
            )
        self.usr_msg = usr_msg
        self._build_flow()

    def _build_flow(self):
        self.add_message(
            "system",
            f"""
                {self.supported_expectations}
                
                for type checks use the native datatypes for {self.backend} which are: {get_types_from_yaml(source=self.backend)}
                """,
        )
        self.add_message(
            "user",
            """
1. PatientID, Visit Date cannot be null.
2. All columns set must exist.
3. Gender must be either M or F
4. All columns must be of a logically acceptable type supported by bigquery
5. Treatment must be within a set of logical values
6. Visit Date must be in parsable date format
7. PatientID must be increasing value
8. Age must be between 0 and 100
9. table must have 6 columns
10. table must have 5000 rows
11. sum of values of age column must be between 4000 and 5000""",
        )
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
expect_column_values_to_be_in_set(column='Gender', value_set=['M', 'F'])
expect_column_values_to_be_in_set(column='Treatment', value_set=['TreatmentValue1', 'TreatmentValue2'])  
expect_column_values_to_be_of_type(column='Visit Date', type_='DATE')
expect_column_values_to_be_increasing(column='PatientID')
expect_column_values_to_be_between(column='Age', min_value=0, max_value=100)
expect_table_column_count_to_be(column_count=6)
expect_table_row_count_to_be(row_count=5000)
expect_column_sum_to_be_between(column='Age', min_sum=4000, max_sum=5000)""",
        )
        self.add_message("user", self.usr_msg)
