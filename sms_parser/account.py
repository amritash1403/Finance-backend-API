from typing import List

from .constants import COMBINED_WORDS, WALLETS
from .models import IAccountInfo, IAccountType, TMessageType
from .utils import (
    extract_bonded_account_no,
    get_processed_message,
    trim_leading_and_trailing_chars,
)


def get_card(message: List[str]) -> IAccountInfo:
    """Extract credit card information from the message."""
    combined_card_name = ""
    card = IAccountInfo()

    # Find the index of the word "card" or any combined word of card type
    card_index = -1
    for idx, word in enumerate(message):
        if word == "card":
            card_index = idx
            break

        # Check for combined words of card type
        for w in [cw for cw in COMBINED_WORDS if cw.type == IAccountType.CARD]:
            if w.word == word:
                combined_card_name = w.word
                card_index = idx
                break

        if card_index != -1:
            break

    # If "card" or a combined card word is found
    if card_index != -1:
        if card_index + 1 < len(message):
            card.number = message[card_index + 1]
            card.type = IAccountType.CARD

            # Check if number is valid
            try:
                int(card.number)
            except ValueError:
                # If data is false positive, return with just the combined card name if available
                return IAccountInfo(
                    type_=card.type if combined_card_name else None,
                    name=combined_card_name,
                    number=None,
                )

            return card

    # No card found
    return IAccountInfo()


def get_account(message: TMessageType) -> IAccountInfo:
    """Extract account information from the message."""
    processed_message = get_processed_message(message)
    account_index = -1
    account = IAccountInfo()

    # First look for explicit account references with "ac"
    for idx, word in enumerate(processed_message):
        if word == "ac":
            if idx + 1 < len(processed_message):
                account_no = trim_leading_and_trailing_chars(processed_message[idx + 1])
                try:
                    int(account_no)
                    account_index = idx
                    account.type = IAccountType.ACCOUNT
                    account.number = account_no
                    break
                except ValueError:
                    # continue searching for a valid account number
                    continue
        elif "ac" in word:
            extracted_account_no = extract_bonded_account_no(word)
            if extracted_account_no:
                account_index = idx
                account.type = IAccountType.ACCOUNT
                account.number = extracted_account_no
                break

    # No occurrence of the word "ac". Check for "card"
    if account_index == -1:
        account = get_card(processed_message)

    # Check for wallets
    if not account.type:
        for word in processed_message:
            if word in WALLETS:
                account.type = IAccountType.WALLET
                account.name = word
                break

    # Check for special accounts
    if not account.type:
        for word in COMBINED_WORDS:
            if word.type == IAccountType.ACCOUNT and word.word in processed_message:
                account.type = word.type
                account.name = word.word
                break

    # Extract last 4 digits of account number
    # E.g. 4334XXXXX4334
    if account.number and len(account.number) > 4:
        account.number = account.number[-4:]

    return account
