<a name="readme-top"></a>


<div align="center">
  <a href=""> <img src="docs/images/gewrap.png" alt="Logo" width="150" height="150"> </a>
  <h3 align="center">Easy Expectations — A Great Expectations Wrapper</h3>
  <p align="center">Great Expectations made easy!</p>
  <a href=""> <img src="docs/images/demo.gif" alt="x" height="450"> </a>
  </div>


## Features
Easy Expectations is a wrapper to streamline your Great Expectations experience.
<br>In essence the core functionality of the package is map rudimentary input into proper GX configuration.

  -   No GX knowledge needed
  -   Human readable configuration file that allows better collaboration
  -   OpenAI GPT can be used to profile the data and generate viable tests
  -   OpenAI GPT can be used to generate an expectations suite as per requirements
  -   Supports all integrations and connectors supported by GX
  -   Bash syntax can be used for templating
  -   Flexible schema; extra fields have no impact and existing fields can be renamed, nested, unnested, reformatted.
  -   Config file can be split into multiple parts and loaded at runtime.
  -   Generate `great_expectations.yaml` and `checkpoint.yaml`
  -   Docker & Kubernetes friendly


## Not – yet – supported GE features:
  -   Metric Stores
  -   Database Backends
  -   Multiple Batch requests


## Connectors
To simplify the process, knowledge of things like `Inferred Connector` or `Tuple Backend` is not necessary.
This is because by passing the target source or artifact location, the type is detected, as well as any other information required; bucket, prefix, base_dir, and even wildcard regex patterns.

| Name                 | Pattern                                          |
|----------------------|--------------------------------------------------|
| gcs                  | `^gs://`                                         |
| s3                   | `^s3://`                                         |
| azure                | `^https://.*\\.blob\\.core\\.windows\\.net`      |
| local                | `^local:`                                        |
| dbfs                 | `^/dbfs/`                                        |
| in_memory (ex. df)   | `^[^/.]+$`                                       |
| postgresql_database  | `postgresql+psycopg2://`                         |
| bigquery_database    | `bigquery://`                                    |
| athena_database      | `awsathena+rest://@athena`                       |
| mssql_database       | `mssql+pyodbc://`                                |
| mysql_database       | `mysql+pymysql://`                               |
| redshift_database    | `redshift.amazonaws.com`                         |
| snowflake_database   | `snowflake://`                                   |
| sqlite_database      | `sqlite://`                                      |
| trino_database       | `trino://`                                       |



## Example Config

Lets say we want to create a config file to use in a data validation pipeline.
the data is on gcs and we want to save the artifacts locally.
We want to setup slack alerting as well as Datahub integration for metadata tracking.

```yaml
version: 1.0

Metadata:
  Data Product: HR Pipeline
  Created: 2023-08-26
  Modified: 2023-08-26
  Ownership:
    Maintainer: Islam Elsayed
    Email: Elsayed91@outlook.com
  Description: |
    Data Validation for HR data originating from GCS.
    Altering via Slack on channel #alerts.

Data Source:
  Source: gs://mybucket/myfile/myfiles-*.parquet
  Engine: Spark
Artifacts:
  Location: local:/home/lestrang/final_expectations_v2/ge_local
Options:
  GCP Defaults:
    GCP Project: default_project
  Success Threshold: 95

Integrations:
  Slack:
    Webhook: https://hooks.slack.com/services/xxxxx
    Notify On: failure
    Channel: DJ Khaled
  Datahub:
    URL: www.datahubserverurl.com


Validation:
  Suite Name: my_suite
  Tests:
    - expectation: expect_column_values_to_not_be_null
      kwargs:
        column: Name
      meta: {}
    - Expectation: expect_column_values_to_be_of_type
      kwargs:
        column: Name
        type_: StringType
    - Expectation: expect_column_values_to_be_between
      kwargs:
        column: Age
        min_value: 25
        max_value: 40
    - Expectation: expect_column_values_to_be_between
      kwargs:
        column: Salary
        min_value: 50000
        max_value: 80000
    - Expectation: expect_column_values_to_be_in_set
      kwargs:
        column: Department
        value_set: ["HR", "IT", "Finance"]
```
A data contract structure inspired by [this post](https://robertsahlin.substack.com/p/one-streamprocessor-to-rule-them) by Robert Sahlin is also usable.
Simply replace the `Validation` block with the below.

```yaml
Schema:
  Columns:
    - name: Name
      description: "Username"
      mode: REQUIRED
      type: StringType

    - name: Age
      description: "User Age"
      mode: NULLABLE
      type: IntegerType

    - name: Salary
      description: "Salary"
      mode: REQUIRED
      type: IntegerType

    - name: Department
      description: "Department"
      mode: REQUIRED
      type: StringType
```

## How to

### Run within python

```python
from easy_expectations import run_ex

results = run_ex('/path/to/config/file/')

```
### Split my configuration
Lets say you only want to share the tests and the metadata with specific members of your team and keep other data hidden, but load all at runtime.

```python
from easy_expectations import run_ex

results = run_ex(['/path/to/config/file/1','/path/to/config/file/2'...])
```
This will concatenate all the files.
Note: Ensure that the mandatory keys have no duplicates.

### How to use Spark
I cannot add PySpark as a dependency as it will limit the Spark versions that can be used.
Install PySpark and Spark and ensure they are working, choose Engine as Spark for non-database sources and you are good to go.

### Change Styling/Formatting/Nesting/Structure
You do this via:
1. Provide mapping file/dict
2. Provide a mapping key

eitherway, you need to somehow provide a way to map the base variables to your structure.
Check [this](easy_expectations/config_mapper/var_mapping.yaml).
Simply do the same for the values you want to change.

in cli
```bash
python -m easy_expectations run \
    --config-file /path/to/file \
    --mapping /path/to/mapping/yaml \
    --mapping-key name of mapping key
```

Lets say I want to add my default GCP Project to a GCP dedicated field with the help of a mapping key.

Inside the configuration file
```yaml
GCP:
  Project: myproject

Mappings
  default_gcp_project: GCP/Project
```
then
```python
from easy_expectations import run_ex

results = run_ex('/path/to/config/file/', mapping_key="Mappings")

```
Now the variable will be found despite the different structure.



## Roadmap

These features are planned or already implemented but require testing.

- Azure Support
- Config file styling to allow snake case & pascal case as different ways to provide the configuration
- [Multiple Batch Request](https://docs.greatexpectations.io/docs/guides/validation/checkpoints/how_to_add_validations_data_or_suites_to_a_checkpoint)
- [Litellm](https://github.com/BerriAI/litellm/tree/main) Support for non-openai models
- Batch_Spec_passthrough options
- Validate AI Generated Expectations against a list of existing expectations.

## Notes

A lot of features have not been tested, but should be working.
For example databricks as a source is included, but was never tested.

