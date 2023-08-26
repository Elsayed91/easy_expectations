import uuid
from typing import Dict, List, Tuple

from easy_expectations.utils.logger import logger


def get_openai_model_cost(model_name: str, is_completion: bool = False) -> float:
    """Retrieve the cost associated with a given OpenAI model."""

    MODEL_COST_MAPPING = {
        "gpt-4": 0.03,
        "gpt-4-0314": 0.03,
        "gpt-4-completion": 0.06,
        "gpt-4-0314-completion": 0.06,
        "gpt-4-32k": 0.06,
        "gpt-4-32k-0314": 0.06,
        "gpt-4-32k-completion": 0.12,
        "gpt-4-32k-0314-completion": 0.12,
        "gpt-3.5-turbo": 0.002,
        "gpt-3.5-turbo-0301": 0.002,
        "gpt-3.5-turbo-0613": 0.002,
        "gpt-3.5-turbo-16k": 0.004,
        "gpt-3.5-turbo-16k-0613": 0.004,
    }
    try:
        model_key = model_name.lower()
        if is_completion and model_name.startswith("gpt-4"):
            model_key += "-completion"

        cost = MODEL_COST_MAPPING.get(model_key)
        if cost is None:
            print(
                f"Unknown model: {model_name}. Known models are: {', '.join(MODEL_COST_MAPPING.keys())}, using 0.003 as default value"
            )
            cost = 0.003
        return cost
    except Exception as e:
        logger.error(f"Error retrieving cost for model {model_name}: {e}")
        raise


def get_single_response_cost(response: Dict) -> float:
    """Calculate the cost for a single OpenAI API response."""
    prompt_tokens = response["usage"]["prompt_tokens"]
    completion_tokens = response["usage"]["completion_tokens"]

    prompt_cost = get_openai_model_cost(response["model"]) * (prompt_tokens / 1000)
    completion_cost = get_openai_model_cost(response["model"], True) * (
        completion_tokens / 1000
    )
    stopping_reason = response["choices"][0]["finish_reason"]
    if stopping_reason == "length":
        logger.warning(
            "Generation was prematurely terminated due to reaching length limit."
        )
        logger.warning(
            "Consider using a larger model or dividing your data into smaller segments."
        )
        logger.warning(
            "For instance, if you have multiple columns, you can process them in separate batches."
        )
    return prompt_cost + completion_cost


def multi_call_stats(responses: List[Dict]) -> None:
    """Display statistics for multiple OpenAI API calls."""
    total_cost = sum(get_single_response_cost(response) for response in responses)

    total_tokens = sum(
        response["usage"]["prompt_tokens"] + response["usage"]["completion_tokens"]
        for response in responses
    )
    total_prompt_tokens = sum(
        response["usage"]["prompt_tokens"] for response in responses
    )
    total_completion_tokens = sum(
        response["usage"]["completion_tokens"] for response in responses
    )

    stats_str = f"""
OpenAI Run Statistics
Tokens:
    Total Used: {total_tokens}
    Prompt Tokens: {total_prompt_tokens}
    Completion Tokens: {total_completion_tokens}
Successful Requests: {len(responses)}
Total Cost (USD): ${total_cost:.7f}
"""
    logger.info(stats_str)
    print(stats_str)
