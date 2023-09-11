import tiktoken


def estimate_input_cost_optimized(model_name, token_count):
    model_cost_dict = {
        "gpt-3.5-turbo": 0.0015,
        "gpt-3.5-turbo-16k": 0.003,
        "gpt-4": 0.03,
    }

    try:
        cost_per_1000_tokens = model_cost_dict[model_name]
    except KeyError:
        raise ValueError(f"The model '{model_name}' is not recognized.")

    estimated_cost = (token_count / 1000) * cost_per_1000_tokens

    return estimated_cost


def count_tokens(text, selected_model):
    encoding = tiktoken.encoding_for_model(selected_model)
    num_tokens = encoding.encode(text)
    return len(num_tokens)
