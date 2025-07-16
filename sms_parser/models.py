from enum import Enum
from typing import Dict, List, Optional, TypeVar, Union


class IAccountType(str, Enum):
    CARD = "CARD"
    WALLET = "WALLET"
    ACCOUNT = "ACCOUNT"


class IBalanceKeyWordsType(str, Enum):
    AVAILABLE = "AVAILABLE"
    OUTSTANDING = "OUTSTANDING"


class IAccountInfo:
    def __init__(
        self,
        type_: Optional[IAccountType] = None,
        number: Optional[str] = None,
        name: Optional[str] = None,
    ):
        self.type = type_
        self.number = number
        self.name = name

    def to_dict(self) -> Dict:
        return {
            "type": self.type.value if self.type else None,
            "number": self.number,
            "name": self.name,
        }


class IBalance:
    def __init__(
        self,
        available: Optional[str] = None,
        outstanding: Optional[str] = None,
    ):
        self.available = available
        self.outstanding = outstanding

    def to_dict(self) -> Dict:
        return {"available": self.available, "outstanding": self.outstanding}


TMessageType = Union[str, List[str]]
TTransactionType = Optional[str]  # "debit" or "credit" or None


class ITransaction:
    def __init__(
        self,
        type_: Optional[TTransactionType] = None,
        amount: Optional[str] = None,
        reference_no: Optional[str] = None,
        merchant: Optional[str] = None,
    ):
        self.type = type_
        self.amount = amount
        self.reference_no = reference_no
        self.merchant = merchant

    def to_dict(self) -> Dict:
        return {
            "type": self.type,
            "amount": self.amount,
            "referenceNo": self.reference_no,
            "merchant": self.merchant,
        }


class ITransactionInfo:
    def __init__(
        self,
        account: IAccountInfo,
        balance: Optional[IBalance] = None,
        transaction: Optional[ITransaction] = None,
    ):
        self.account = account
        self.balance = balance
        self.transaction = transaction if transaction is not None else ITransaction()

    def to_dict(self) -> Dict:
        return {
            "account": self.account.to_dict(),
            "balance": self.balance.to_dict() if self.balance else None,
            "transaction": self.transaction.to_dict(),
        }


class ICombinedWords:
    def __init__(self, regex, word: str, type_: IAccountType):
        self.regex = regex
        self.word = word
        self.type = type_
