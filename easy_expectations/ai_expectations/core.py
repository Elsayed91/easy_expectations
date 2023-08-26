import json
import os

import openai
import pandas as pd

from easy_expectations.ai_expectations.flows.profile_data_flow import ProfilerDataFlow
from easy_expectations.ai_expectations.flows.profiler_flow import ProfilerFlow
from easy_expectations.ai_expectations.flows.requirements_flow import RequirementFlow
from easy_expectations.ai_expectations.profiler_utils import (
    convert_text_to_expectations,
    generate_base_col_expectations,
)
from easy_expectations.ai_expectations.usage_tracking import multi_call_stats
from easy_expectations.utils.logger import logger


def profiler(
    df_path,
    backend="Pandas",
    use_reference=False,
    model_type="gpt-3.5-turbo",
    temperature=0.0,
    max_tokens=None,
):
    df = pd.read_csv(df_path)
    base_exp = generate_base_col_expectations(df.columns.tolist())
    usr_msg = f"{df.to_string()}"
    messages = ProfilerFlow(
        usr_msg=usr_msg, backend=backend, use_reference=use_reference
    ).get_flow()

    v1, exp = interact_with_openai(
        messages, model_type=model_type, temperature=temperature, max_tokens=max_tokens
    )
    logger.info(f"base profiler results:\n{exp}")
    dmessages = ProfilerDataFlow(dataframe=usr_msg, backend=backend).get_flow()
    v2, dexp = interact_with_openai(
        dmessages, model_type=model_type, temperature=temperature, max_tokens=max_tokens
    )
    logger.info(f"data type profiler results:\n{dexp}")
    expectations = str(exp) + str(base_exp) + str(dexp)
    logger.info(f"Generated Expectations:\n{expectations}")
    # print("These expectations will be created:\n" + expectations)

    exp = convert_text_to_expectations(expectations)

    multi_call_stats([v1, v2])
    return exp


def requirements_handler(
    requirements,
    backend="Pandas",
    use_reference=False,
    model_type="gpt-3.5-turbo",
    temperature=0.0,
    max_tokens=None,
):
    messages = RequirementFlow(
        usr_msg=requirements, backend=backend, use_reference=use_reference
    ).get_flow()
    v1, exp = interact_with_openai(
        messages, model_type=model_type, temperature=temperature, max_tokens=max_tokens
    )
    logger.info(f"Generated Expectations:\n{exp}")
    exp = convert_text_to_expectations(exp)
    multi_call_stats([v1])
    return exp


def interact_with_openai(
    messages, model_type="gpt-3.5-turbo", temperature=0.5, max_tokens=None
):
    if not openai.api_key:
        # If not set, then try to fetch the API key from the environment.
        api_key = os.getenv("OPENAI_API_KEY")

        # If it's neither in openai.api_key nor in the environment, prompt the user for it.
        if not api_key:
            api_key = input("Please provide your OpenAI API key: ")

        # Set the API key for openai.
        openai.api_key = api_key
        if not openai.api_key:
            raise ValueError("API key not provided!")

    messages = messages
    completion = openai.ChatCompletion.create(
        model=model_type,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=messages,
        presence_penalty=0.5,
    )
    return completion, completion["choices"][0]["message"]["content"]


# req = "1. GameID, Title, ReleaseDate, Genre, Rating, and TotalSales cannot be null. 2.All columns: GameID, Title, ReleaseDate, Genre, Rating, and TotalSales must exist. 3.All columns must be of a logically acceptable type. 4. Rating must be between 0 and 10. 5.ReleaseDate should be a valid date format 6.TotalSales should be a positive integer 7.GameID values should be unique. 8.Genre must be one of the following: Action-Adventure, Strategy, RPG, Puzzle, Simulation, Racing, Stealth, Fighting, VR, MMO.     "
# e = requirements_handler(req, backend='bigquery', use_reference=False)
