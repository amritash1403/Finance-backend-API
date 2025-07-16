import re
from typing import List, Optional

from .account import get_account
from .balance import get_balance
from .merchant import extract_merchant_info
from .models import (
    IAccountType,
    IBalance,
    IBalanceKeyWordsType,
    ITransactionInfo,
    TMessageType,
    TTransactionType,
    ITransaction,
    IAccountInfo,
)
from .utils import get_processed_message, pad_currency_value, process_message


def get_transaction_amount(message: TMessageType) -> str:
    """Extract transaction amount from the message."""
    processed_message = get_processed_message(message)

    # Find the index of "rs."
    try:
        index = processed_message.index("rs.")
    except ValueError:
        return ""

    # If "rs." exists, get the money value
    if index + 1 < len(processed_message):
        money = processed_message[index + 1]
        money = money.replace(",", "")

        # Check if it's a valid money value
        try:
            float(money)
            return pad_currency_value(money)
        except ValueError:
            # Look ahead one index and check for valid money
            if index + 2 < len(processed_message):
                money = processed_message[index + 2]
                money = money.replace(",", "") if money else ""

                try:
                    float(money)
                    return pad_currency_value(money)
                except ValueError:
                    return ""

    return ""


def get_transaction_type(message: TMessageType) -> TTransactionType:
    """Determine the type of transaction (debit or credit) from the message."""
    credit_pattern = re.compile(
        r"(?:credited|credit|deposited|added|received|refund|repayment)", re.IGNORECASE
    )
    debit_pattern = re.compile(r"(?:debited|debit|deducted)", re.IGNORECASE)
    misc_pattern = re.compile(
        r"(?:payment|spent|paid|used\s+at|charged|transaction\son|transaction\sfee|"
        r"tran|booked|purchased|sent\s+to|purchase\s+of|spent\s+on)",
        re.IGNORECASE,
    )

    message_str = " ".join(message) if not isinstance(message, str) else message

    if debit_pattern.search(message_str):
        return "debit"
    if misc_pattern.search(message_str):
        return "debit"
    if credit_pattern.search(message_str):
        return "credit"

    return None


def get_transaction_info(message: str) -> ITransactionInfo:
    """Extract transaction information from the SMS message."""
    if not message or not isinstance(message, str):
        return ITransactionInfo(
            account=IAccountInfo(),
            balance=None,
            transaction=ITransaction(),
        )

    # Process the message
    processed_message = process_message(message)

    # Extract account information
    account = get_account(processed_message)

    # Extract available balance
    available_balance = get_balance(processed_message, IBalanceKeyWordsType.AVAILABLE)

    # Extract transaction amount
    transaction_amount = get_transaction_amount(processed_message)

    # Determine if we have enough information to determine transaction type
    is_valid = (
        len([x for x in [available_balance, transaction_amount, account.number] if x])
        >= 2
    )

    # Get transaction type
    transaction_type = get_transaction_type(processed_message) if is_valid else None

    # Create balance object
    balance = IBalance(available=available_balance, outstanding=None)

    # For cards, also check for outstanding balance
    if account and account.type == IAccountType.CARD:
        outstanding_balance = get_balance(
            processed_message, IBalanceKeyWordsType.OUTSTANDING
        )
        balance.outstanding = outstanding_balance

    # Extract merchant information and reference number
    merchant_info = extract_merchant_info(message)

    # Return transaction info
    return ITransactionInfo(
        account=account,
        balance=balance,
        transaction=ITransaction(
            type_=transaction_type,
            amount=transaction_amount,
            reference_no=merchant_info["referenceNo"],
            merchant=merchant_info["merchant"],
        ),
    )
