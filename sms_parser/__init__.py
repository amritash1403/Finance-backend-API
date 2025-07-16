"""
Transaction SMS Parser
A library to parse transaction SMS text to extract relevant information from it.
"""

from .account import get_account
from .balance import get_balance
from .engine import get_transaction_info, get_transaction_amount, get_transaction_type
from .merchant import extract_merchant_info
from .models import (
    IAccountInfo,
    IAccountType,
    IBalance,
    IBalanceKeyWordsType,
    ITransaction,
    ITransactionInfo,
    TMessageType,
    TTransactionType,
)

__all__ = [
    "get_account_info",
    "get_balance_info",
    "get_merchant_info",
    "get_transaction_info",
    "get_transaction_amount",
    "get_transaction_type",
    "IAccountInfo",
    "IAccountType",
    "IBalance",
    "IBalanceKeyWordsType",
    "ITransaction",
    "ITransactionInfo",
    "TMessageType",
    "TTransactionType",
]

# Alias the functions to match the TypeScript API
get_account_info = get_account
get_balance_info = get_balance
get_merchant_info = extract_merchant_info
