import re
from typing import List, Optional, Union

from .constants import AVAILABLE_BALANCE_KEYWORDS, OUTSTANDING_BALANCE_KEYWORDS
from .models import IBalanceKeyWordsType, TMessageType
from .utils import get_processed_message, pad_currency_value


def extract_balance(index: int, message: str, length: int) -> str:
    """Extract balance amount from text starting at the given index."""
    balance = ""
    saw_number = False
    invalid_char_count = 0
    start = index

    while start < length:
        char = message[start]

        if "0" <= char <= "9":
            saw_number = True
            balance += char
        elif saw_number:
            if char == ".":
                if invalid_char_count == 1:
                    break
                balance += char
                invalid_char_count += 1
            elif char != ",":
                break

        start += 1

    return balance


def find_non_standard_balance(
    message: str, keyword_type: IBalanceKeyWordsType = IBalanceKeyWordsType.AVAILABLE
) -> Optional[str]:
    """Find balance in messages with non-standard formats."""
    balance_keywords = (
        AVAILABLE_BALANCE_KEYWORDS
        if keyword_type == IBalanceKeyWordsType.AVAILABLE
        else OUTSTANDING_BALANCE_KEYWORDS
    )

    # Create regex patterns
    bal_keyword_regex = f"({'|'.join(balance_keywords)})"
    amount_regex = r"([\d]+\.[\d]+|[\d]+)"

    # Case 1: "balance 100.00"
    regex = re.compile(f"{bal_keyword_regex}\\s*{amount_regex}", re.IGNORECASE)
    matches = regex.findall(message)
    if matches:
        for match in matches:
            if isinstance(match, tuple) and len(match) > 1:
                balance = match[1]
            else:
                words = matches[0].split()
                balance = words[-1] if words else None

            if balance and balance.replace(".", "", 1).isdigit():
                return balance

    # Case 2: "100.00 available"
    regex = re.compile(f"{amount_regex}\\s*{bal_keyword_regex}", re.IGNORECASE)
    matches = regex.findall(message)
    if matches:
        for match in matches:
            if isinstance(match, tuple) and len(match) > 0:
                balance = match[0]
            else:
                words = matches[0].split()
                balance = words[0] if words else None

            if balance and balance.replace(".", "", 1).isdigit():
                return balance

    return None


def get_balance(
    message: TMessageType,
    keyword_type: IBalanceKeyWordsType = IBalanceKeyWordsType.AVAILABLE,
) -> Optional[str]:
    """Extract balance information from the message."""
    processed_message = get_processed_message(message)
    message_string = " ".join(processed_message)
    index_of_keyword = -1
    balance = ""

    balance_keywords = (
        AVAILABLE_BALANCE_KEYWORDS
        if keyword_type == IBalanceKeyWordsType.AVAILABLE
        else OUTSTANDING_BALANCE_KEYWORDS
    )

    # Find the first keyword
    for word in balance_keywords:
        index_of_keyword = message_string.find(word)
        if index_of_keyword != -1:
            index_of_keyword += len(word)
            break

    # Find "rs." occurring after the keyword
    index = index_of_keyword
    index_of_rs = -1

    if index != -1:
        while index + 3 <= len(message_string):
            next_three_chars = message_string[index : index + 3]
            if next_three_chars == "rs.":
                index_of_rs = index + 2
                break
            index += 1

    # No occurrence of 'rs.'
    if index_of_rs == -1:
        # Try non-standard balance format
        balance = find_non_standard_balance(message_string, keyword_type)
        return pad_currency_value(balance) if balance else None

    # Extract balance after 'rs.'
    balance = extract_balance(index_of_rs, message_string, len(message_string))

    return pad_currency_value(balance) if balance else None
