import tiktoken
from typing import List, Dict

def get_tokenizer(model_name: str):
    try:
        # Many modern models use cl100k_base compatible tokenization for estimation
        return tiktoken.get_encoding("cl100k_base")
    except Exception:
        return tiktoken.get_encoding("cl100k_base")

def count_tokens(messages: List[Dict[str, str]], model_name: str) -> int:
    encoding = get_tokenizer(model_name)
    num_tokens = 0
    for message in messages:
        num_tokens += 4  # estimation overhead
        for key, value in message.items():
            if isinstance(value, str):
                num_tokens += len(encoding.encode(value))
    num_tokens += 2  # priming
    return num_tokens

def trim_messages(messages: List[Dict[str, str]], max_tokens: int, model_name: str) -> List[Dict[str, str]]:
    """
    Trim messages to fit within max_tokens. 
    Always keeps the system message if present.
    """
    if not messages:
        return messages

    # Separate system message
    system_msg = None
    other_msgs = []
    for msg in messages:
        if msg.get("role") == "system":
            system_msg = msg
        else:
            other_msgs.append(msg)

    # Initial token count
    current_tokens = count_tokens(messages, model_name)
    
    if current_tokens <= max_tokens:
        return messages

    # Start removing from the oldest (top) non-system messages
    while current_tokens > max_tokens and other_msgs:
        other_msgs.pop(0)
        temp_messages = ([system_msg] if system_msg else []) + other_msgs
        current_tokens = count_tokens(temp_messages, model_name)

    return ([system_msg] if system_msg else []) + other_msgs
