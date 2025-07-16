import re
from typing import Dict, Optional, Tuple

from .constants import UPI_HANDLES, UPI_KEYWORDS
from .models import TMessageType
from .utils import get_next_words, get_processed_message, is_number


def extract_merchant_info(message: TMessageType) -> Dict[str, Optional[str]]:
    """Extract merchant information and reference number from the message."""
    processed_message = get_processed_message(message)
    message_string = " ".join(processed_message)
    transaction_details = {
        "merchant": None,
        "referenceNo": None,
    }

    # Check for VPA (Virtual Payment Address)
    if "vpa" in processed_message:
        idx = processed_message.index("vpa")
        # If keyword vpa is not the last one
        if idx < len(processed_message) - 1:
            next_str = processed_message[idx + 1]
            name = next_str.replace("(", " ").replace(")", " ").split(" ")[0]
            transaction_details["merchant"] = name

    # Check for UPI keywords
    match = ""
    for keyword in UPI_KEYWORDS:
        idx = message_string.find(keyword)
        if idx > 0:
            match = keyword
            break

    if match:
        next_word = get_next_words(message_string, match)
        if is_number(next_word):
            transaction_details["referenceNo"] = next_word
        elif transaction_details["merchant"]:
            # Try to extract numeric part as reference number
            numeric_parts = re.split(r"[^0-9]", next_word)
            numeric_parts = [p for p in numeric_parts if p]
            if numeric_parts:
                longest_numeric = max(numeric_parts, key=len)
                if longest_numeric:
                    transaction_details["referenceNo"] = longest_numeric
        else:
            transaction_details["merchant"] = next_word

        # If merchant is still not found, look for UPI handles
        if not transaction_details["merchant"]:
            upi_regex = re.compile(
                f"[a-zA-Z0-9_-]+({'|'.join(UPI_HANDLES)})", re.IGNORECASE
            )
            matches = upi_regex.findall(message_string)
            if matches:
                transaction_details["merchant"] = matches[0]

    # If merchant is still not found, look for "at * on" regex
    if not transaction_details["merchant"]:
        at_on_regex = re.compile(r"at\s+(.+?)\s+on\s+", re.IGNORECASE)
        at_on_match = at_on_regex.search(message_string)
        if at_on_match:
            transaction_details["merchant"] = at_on_match.group(1).strip()

    # If not look for "at *"
    if not transaction_details["merchant"]:
        at_regex = re.compile(r"at\s+(.+?)", re.IGNORECASE)
        at_match = at_regex.search(message_string)
        if at_match:
            transaction_details["merchant"] = at_match.group(1).strip()

    # If still not looking for "on *"
    if not transaction_details["merchant"]:
        on_regex = re.compile(r"on\s+(.+?)\s", re.IGNORECASE)
        on_match = on_regex.search(message_string)
        if on_match:
            transaction_details["merchant"] = on_match.group(1).strip()

    return transaction_details
