import re
from typing import List, Union, Any

from .constants import COMBINED_WORDS
from .models import TMessageType


def is_number(val: Any) -> bool:
    """Check if a value can be converted to a number."""
    try:
        float(val)
        return True
    except (ValueError, TypeError):
        return False


def trim_leading_and_trailing_chars(string: str) -> str:
    """Remove non-numeric characters from the beginning and end of the string."""
    if not string:
        return ""

    first, last = string[0], string[-1]

    final_str = string[:-1] if not is_number(last) else string
    final_str = final_str[1:] if not is_number(first) else final_str

    return final_str


def extract_bonded_account_no(account_no: str) -> str:
    """Extract account number from a string containing 'ac'."""
    stripped_account_no = account_no.replace("ac", "")
    return stripped_account_no if is_number(stripped_account_no) else ""


def process_message(message: str) -> List[str]:
    """Process the message to extract relevant information."""
    # convert to lower case
    message_str = message.lower()
    # remove '!'
    message_str = message_str.replace("!", "")
    # remove ':'
    message_str = message_str.replace(":", " ")
    # remove '/'
    message_str = message_str.replace("/", "")
    # remove '='
    message_str = message_str.replace("=", " ")
    # remove '{}'
    message_str = re.sub(r"[{}]", " ", message_str)
    # remove \n
    message_str = message_str.replace("\n", " ")
    # remove \r
    message_str = message_str.replace("\r", " ")
    # remove 'ending'
    message_str = message_str.replace("ending ", "")
    # replace 'x'
    message_str = re.sub(r"x|[*]", "", message_str)
    # replace 'is'
    message_str = message_str.replace("is ", "")
    # replace 'with'
    message_str = message_str.replace("with ", "")
    # remove 'no.'
    message_str = message_str.replace("no. ", "")
    # replace all ac, acct, account with ac
    message_str = re.sub(r"\bac\b|\bacct\b|\baccount\b", "ac", message_str)
    # replace all 'rs' with 'rs. '
    message_str = re.sub(r"rs(?=\w)", "rs. ", message_str)
    # replace all 'rs ' with 'rs. '
    message_str = message_str.replace("rs ", "rs. ")
    # replace all inr with rs.
    message_str = re.sub(r"inr(?=\w)", "rs. ", message_str)
    # replace all inr with rs.
    message_str = message_str.replace("inr ", "rs. ")
    # replace all 'rs. ' with 'rs.'
    message_str = message_str.replace("rs. ", "rs.")
    # replace all 'rs.' with 'rs. '
    message_str = re.sub(r"rs.(?=\w)", "rs. ", message_str)
    # replace all 'debited' with ' debited '
    message_str = message_str.replace("debited", " debited ")
    # replace all 'credited' with ' credited '
    message_str = message_str.replace("credited", " credited ")

    # combine words
    for word in COMBINED_WORDS:
        message_str = word.regex.sub(word.word, message_str)

    return [s for s in message_str.split(" ") if s]


def get_processed_message(message: TMessageType) -> List[str]:
    """Get a processed message split into words."""
    if isinstance(message, str):
        return process_message(message)
    return message


def pad_currency_value(val: str) -> str:
    """Ensure currency values have two decimal places."""
    if not val:
        return ""

    parts = val.split(".")
    if len(parts) == 1:
        return f"{parts[0]}.00"

    lhs, rhs = parts
    return f"{lhs}.{rhs.ljust(2, '0')}"


def get_next_words(source: str, search_word: str, count: int = 1) -> str:
    """Get the next words after a search word."""
    splits = source.split(search_word, 2)
    if len(splits) < 2:
        return ""

    next_group = splits[1]
    if next_group:
        word_split_regex = re.compile(r"[^0-9a-zA-Z]+", re.IGNORECASE)
        words = word_split_regex.split(next_group.strip())
        return " ".join(words[:count])

    return ""
