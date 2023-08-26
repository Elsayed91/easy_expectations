#!/usr/bin/env python

import datetime
import json
import os
import shutil

import click
import yaml
from rich.console import Console

from easy_expectations.cli.cli_utils import (
    append_results_to_yaml,
    choose_expectations_source,
    get_column_details,
    handle_output_customization,
    initialize_openai_setup,
    prune_empty_values,
    select_backend,
    yaml_content_from_json,
)
from easy_expectations.main import main

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        os.environ["EE_INTERACTIVE_MODE"] = "1"
        while True:
            click.echo(
                """

   ____                ____                   __       __  _
  / __/__ ____ __ __  / __/_ __ ___  ___ ____/ /____ _/ /_(_)__  ___  ___
 / _// _ `(_-</ // / / _/ \ \ // _ \/ -_) __/ __/ _ `/ __/ / _ \/ _ \(_-<
/___/\_,_/___/\_, / /___//_\_\/ .__/\__/\__/\__/\_,_/\__/_/\___/_//_/___/
             /___/           /_/

Welcome to Easy Expectations! Choose one of the following options:
1. Generate Empty Config
2. Generate Easy Expectations Config file
3. Generate great_expectations.yaml & checkpoint.yaml files
4. Profile Data/Generate Expectations with AI
5. Run tests using Easy Expectations config file
6. Exit
            """
            )
            choice = click.prompt("Please enter your choice", type=int)
            if choice == 1:
                generate_empty()
            elif choice == 2:
                generate_config()
            elif choice == 3:
                generate_ge_yaml()
            elif choice == 4:
                profile_data()
            elif choice == 5:
                run_config()
            elif choice == 6:
                break
            else:
                click.echo("Invalid choice, please try again.")


@cli.command("generate-empty")
def generate_empty():
    """Generate Empty Easy Expectations Config File with commentary"""
    click.echo("Generating Empty Easy Expectations Config File...")
    from easy_expectations import CONFIG_DATA

    template_path = CONFIG_DATA["easy_expectations_skeleton"]

    config_path = click.prompt(
        "Enter the path to save the config file (press Enter to save"
        + " to current directory):",
        default="",
    )

    if not config_path:
        config_path = "easy_expectations_config.yaml"

    shutil.copy(template_path, config_path)

    click.echo(
        f"Empty Easy Expectations Config File saved"
        + f" at {os.path.abspath(config_path)}"
    )


@cli.command("profiler")
def profile_data():
    """Profile Data/ Generate Expectations Suite with AI"""
    return profile_data_core()


def profile_data_core(from_config_creation=False):
    """Profile Data/ Generate Expectations Suite with AI"""
    from easy_expectations.ai_expectations.core import (
        profiler,
        requirements_handler,
    )

    # Step 1: Initialization and Customization of OpenAI Model Interaction
    model_type, temperature, max_tokens = initialize_openai_setup()

    # Step 2: Backend Selection
    selected_backend = select_backend()
    if selected_backend is None:
        return

    # Step 3: Choose Expectations Source
    use_reference_expectations = choose_expectations_source()

    console.print("AI Generated Expectations options are:")
    console.print(
        "1. Provide a csv represenation of data and have it profiled "
        + "and get an elementary expectations suite for it."
    )
    console.print(
        "2. Provide human-like instructions for the desired checks only."
    )
    ai_choice = click.prompt("Please choose an option (1 or 2)", type=int)

    if ai_choice == 1:
        df_path = click.prompt("Please provide path to sample csv file")
        with console.status(
            "Waiting for [bold green]GPT's[/bold green] response..."
        ):
            results = profiler(
                df_path,
                selected_backend,
                use_reference_expectations,
                model_type,
                temperature,
                max_tokens,
            )
    else:
        requirements_description = click.prompt(
            "Provide instructions of the checks you want in form of "
            + "numbered bullet points"
        )
        with console.status(
            "Waiting for [bold green]GPT's[/bold green] response..."
        ):
            results = requirements_handler(
                requirements_description,
                selected_backend,
                use_reference_expectations,
                model_type,
                temperature,
                max_tokens,
            )
    suite_name = click.prompt(
        "Tests have been generated, what do you want to call this test suite?",
        type=str,
        default=None,
        show_default=False,
    )
    content_json = json.loads(results)
    if content_json:
        if not from_config_creation:
            handle_output_customization(content_json)
        else:
            return yaml_content_from_json(content_json, suite_name=suite_name)


@cli.command("run")
@click.option(
    "--config-file",
    type=click.Path(exists=True, file_okay=True, readable=True),
    help="Path to the Easy Expectations config file.",
)
@click.option(
    "--mapping",
    type=click.Path(exists=True, file_okay=True, readable=True),
    help="Path to the mapping file (optional).\
            Dicts are not supported in CLI mode.",
)
@click.option(
    "--mapping-key",
    type=str,
    help="Key in the config file to adjust mapping if \
            you are using a different schema.",
)
def run_config(config_file, mapping, mapping_key):
    """Runs Tests using Easy Expectations Config File"""

    # If the config_filepath is not provided, prompt the user for it
    if not config_file:
        config_file = click.prompt(
            "Please enter the path to the Easy Expectations \
                    config file",
            type=str,
        )

    # If the mapping file is not provided and the user wants to provide one,
    # prompt for it
    if os.environ.get("EE_INTERACTIVE_MODE"):
        if not mapping and click.confirm(
            "Do you want to provide \
                a mapping file?"
        ):
            mapping = click.prompt(
                "Please enter the path to the mapping file", type=str
            )
        if not mapping_key and click.confirm(
            "Do you want to provide a \
                mapping key?"
        ):
            mapping_key = click.prompt(
                "Please enter the mapping \
                key",
                type=str,
            )

    # Check if the provided file is a valid YAML file based on its extension
    if not config_file.endswith(".yaml") and not config_file.endswith(".yml"):
        click.echo("Error: The provided file is not a valid YAML file.")
        return
    try:
        main(config_file, mapping, mapping_key)
    except Exception as e:
        click.echo(f"An error occurred: {e}")


@cli.command("generate-config")
def generate_config():
    """Generate an Easy Expectations Config File"""

    # Step 1: Get data_connector_path from the user
    click.echo("Note: when providing a local path, prefix it with 'local:'")
    data_connector_path = click.prompt(
        "Path/Connection String to your data", type=str
    )
    # Step 2: If artifacts path starts with certain prefixes, ask for
    # data_connector_execution_engine
    if data_connector_path.startswith(("local:", "gs://", "s3://")):
        engine = click.prompt(
            "Select Execution Engine\n1. Pandas\n2. Spark",
            type=int,
            default=1,
        )
        engine = "Pandas" if engine == 1 else "Spark"
    else:
        engine = "Pandas"  # Default to Pandas

    if engine == "Spark":
        click.echo("You need to have spark & PySpark installed.")
    # Step 3: Ask for artifacts_path
    artifacts_path = click.prompt(
        "Where do you want run artifacts and docs to be saved?",
        type=str,
        default=".",
    )
    if artifacts_path == ".":
        artifacts_path = "local:" + os.getcwd()
    # Step 4: Ask what the user wants to do: Data Validation or Data Contract
    config_content = f"""
version: 1.0

Metadata:
  Data Product: Placeholder Data Product
  Created: {datetime.date.today()}
  Modified: Placeholder Date
  Ownership:
    Maintainer: Placeholder Maintainer
    Email: placeholder@example.com
  Description: Placeholder Description

Data Source:
  Source: {data_connector_path}
  Engine: {engine}
Artifacts:
   Location: {artifacts_path}
    """

    if artifacts_path.startswith("gs://"):
        # If artifacts_path starts with 'gs://', then it's a GCP bucket
        gcp_project = click.prompt("Enter your GCP Project", type=str)
        config_content += f"""
Options:
GCP Defaults:
    GCP Project: {gcp_project}
        """

    elif artifacts_path.startswith("s3://"):
        # If artifacts_path starts with 's3://', then it's an AWS S3 bucket
        aws_keys = {
            "default_assume_role_arn": "Assume Role Arn",
            "default_assume_role_duration": "Assume Role Duration",
            "default_aws_session_token": "AWS Session Token",
            "default_aws_secret_access_key": "AWS Secret Access Key",
            "default_aws_access_key_id": "AWS Access Key ID",
            "default_s3_region": "S3 Region",
            "default_boto_endpoint": "Boto Endpoint",
        }

        aws_defaults = {}

        click.echo(
            "Provide AWS configurations. Type 'q' to stop entering more keys."
        )
        click.echo("Press Enter to skip.")
        for key, human_readable in aws_keys.items():
            value = click.prompt(
                human_readable, default="", show_default=False
            )
            if value.lower() == "q":
                break
            if value:
                aws_defaults[human_readable] = value

        aws_defaults = prune_empty_values(aws_defaults)
        if aws_defaults:
            config_content += "\nOptions:\n  AWS Defaults:"
            for key, value in aws_defaults.items():
                config_content += f"\n    {key}: {value}"

    action = click.prompt(
        "What do you want to do?\n1. Data Validation\n2. Data Contract",
        type=int,
        default=1,
    )

    validation_choice = None
    if action == 1:  # Data Validation
        validation_choice = click.prompt(
            "Choose an option:\n1. Generate the test suite using AI\n2. Add them manually to the config file later\n3. Pass the expectations suite file name",
            type=int,
        )

        if validation_choice == 1:
            # Call function to generate the test suite using AI
            expectations_content = profile_data_core(from_config_creation=True)
            if expectations_content:  # Check if content is not empty
                config_content += "\n" + expectations_content

        elif validation_choice == 3:
            expectations_file = click.prompt(
                "Please provide the expectations suite file name (without extension). It should be in the artifacts_location/expectations directory.",
                type=str,
            )
            config_content += (
                f"\nOptions:\n  Expectations File: {expectations_file}"
            )

    if action == 2:  # Data Contract
        columns = get_column_details()
        schema = {"Schema": {"Columns": columns}}
        # Convert the schema dictionary to YAML format and append to the config_content
        config_content += "\n" + yaml.dump(
            schema, default_flow_style=False, sort_keys=False
        )

    # Save the config to a file
    config_filename = "easy_expectations_config.yaml"
    with open(config_filename, "w") as config_file:
        config_file.write(config_content)

    click.echo(f"Config file saved at {config_filename}")

    # Ask if user wants to give it a run
    if validation_choice is not None and validation_choice != 2:
        if click.confirm("Do you want to give it a run?"):
            main(config_filename)


@cli.command("generate-ge-config")
def generate_ge_yaml():
    """Generate great_expectations.yaml from an easy expectations config file"""

    # Prompt for connector path
    connector_path = click.prompt(
        "Path/Connection String to your data (Note: when providing a local path, prefix it with 'local:')"
    )

    # Prompt for artifact path
    artifact_path = click.prompt(
        "Where do you want run artifacts and docs to be saved?"
    )

    # Check if artifact_path starts with gs:// and ask for GCP project if it does
    gcp_project = None
    if artifact_path.startswith("gs://"):
        gcp_project = click.prompt(
            "Please provide your GCP project name for gs:// artifact path"
        )

    # Call the main function with the necessary parameters
    main(
        user_config={
            "connector_path": connector_path,
            "artifact_path": artifact_path,
            "gcp_project": gcp_project,
        },
        save_configs=True,
        build_wrapper=False,
    )

    # Notify the user that the configuration files have been generated
    click.echo("Generated great_expectations.yaml and checkpoint.yaml.")


if __name__ == "__main__":
    cli()
