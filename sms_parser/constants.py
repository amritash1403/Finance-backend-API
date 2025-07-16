import re
from .models import IAccountType, ICombinedWords

AVAILABLE_BALANCE_KEYWORDS = [
    "avbl bal",
    "available balance",
    "available limit",
    "available credit limit",
    "avbl. credit limit",
    "limit available",
    "a/c bal",
    "ac bal",
    "available bal",
    "avl bal",
    "updated balance",
    "total balance",
    "new balance",
    "bal",
    "avl lmt",
    "available",
]

OUTSTANDING_BALANCE_KEYWORDS = ["outstanding"]

WALLETS = ["paytm", "simpl", "lazypay", "amazon_pay"]

UPI_KEYWORDS = ["upi", "ref no", "upi ref", "upi ref no"]

COMBINED_WORDS = [
    ICombinedWords(
        regex=re.compile(r"credit\scard", re.IGNORECASE),
        word="c_card",
        type_=IAccountType.CARD,
    ),
    ICombinedWords(
        regex=re.compile(r"amazon\spay", re.IGNORECASE),
        word="amazon_pay",
        type_=IAccountType.WALLET,
    ),
    ICombinedWords(
        regex=re.compile(r"uni\scard", re.IGNORECASE),
        word="uni_card",
        type_=IAccountType.CARD,
    ),
    ICombinedWords(
        regex=re.compile(r"niyo\scard", re.IGNORECASE),
        word="niyo",
        type_=IAccountType.ACCOUNT,
    ),
    ICombinedWords(
        regex=re.compile(r"slice\scard", re.IGNORECASE),
        word="slice_card",
        type_=IAccountType.CARD,
    ),
    ICombinedWords(
        regex=re.compile(r"one\s*card", re.IGNORECASE),
        word="one_card",
        type_=IAccountType.CARD,
    ),
]

UPI_HANDLES = [
    "@BARODAMPAY",
    "@rbl",
    "@idbi",
    "@upi",
    "@aubank",
    "@axisbank",
    "@bandhan",
    "@dlb",
    "@indus",
    "@kbl",
    "@federal",
    "@sbi",
    "@uco",
    "@citi",
    "@citigold",
    "@dlb",
    "@dbs",
    "@freecharge",
    "@okhdfcbank",
    "@okaxis",
    "@oksbi",
    "@okicici",
    "@yesg",
    "@hsbc",
    "@idbi",
    "@icici",
    "@indianbank",
    "@allbank",
    "@kotak",
    "@ikwik",
    "@unionbankofindia",
    "@uboi",
    "@unionbank",
    "@paytm",
    "@ybl",
    "@axl",
    "@ibl",
    "@sib",
    "@yespay",
]
