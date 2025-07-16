# Transaction SMS Parser (Python)

A Python library to parse transaction SMS text to extract relevant information. This is a Python port of the original TypeScript/JavaScript library.

## Installation

### As a standalone module (recommended for projects)

Simply copy the `sms_parser` folder to your project directory and import it directly:

```python
from sms_parser import get_transaction_info
```

### Via pip (if published)

```bash
pip install transaction-sms-parser
# Or directly from the directory
pip install .
```

## How to use

The main function to use is:

```python
get_transaction_info(message: str) -> ITransactionInfo
```

It takes SMS text as input and returns an object of `ITransactionInfo` type.

### Example

```python
from sms_parser import get_transaction_info

sms = 'INR 2000 debited from A/c no. XX3423 on 05-02-19 07:27:11 IST at ECS PAY. Avl Bal- INR 2343.23.'

transaction_info = get_transaction_info(sms)

# Access the parsed information
print(transaction_info.account.type)  # Output: ACCOUNT
print(transaction_info.account.number)  # Output: 3423
print(transaction_info.balance.available)  # Output: 2343.23
print(transaction_info.transaction.type)  # Output: debit
print(transaction_info.transaction.amount)  # Output: 2000.00

# Convert to dictionary
transaction_dict = transaction_info.to_dict()
print(transaction_dict)
```

The `to_dict()` method returns a dictionary structure that matches the original TypeScript/JavaScript library's output:

```python
{
    'account': {
        'type': 'ACCOUNT',
        'number': '3423',
        'name': None,
    },
    'balance': {
        'available': '2343.23',
        'outstanding': None
    },
    'transaction': {
        'type': 'debit',
        'amount': '2343.23',
        'referenceNo': None,
        'merchant': None,
    }
}
```

## Structure

The library uses the following class structure to represent transaction information:

```python
class ITransactionInfo:
    account: IAccountInfo
    balance: Optional[IBalance]
    transaction: ITransaction

class IAccountInfo:
    type: Optional[IAccountType]  # CARD, WALLET, or ACCOUNT
    number: Optional[str]
    name: Optional[str]

class IBalance:
    available: Optional[str]
    outstanding: Optional[str]

class ITransaction:
    type: Optional[str]  # "debit" or "credit"
    amount: Optional[str]
    reference_no: Optional[str]
    merchant: Optional[str]
```

## Using as a Standalone Module

To use this module in other projects:

1. Copy the entire `sms_parser` folder to your project
2. Import and use:

```python
from sms_parser import get_transaction_info

# Your SMS parsing code here
sms = "Your SMS text here"
result = get_transaction_info(sms)
```

## Dependencies

This module has no external dependencies - it uses only Python standard library modules:

- `re` (regular expressions)
- `typing` (type hints)
- `enum` (enumerations)

This makes it easy to copy and use in any Python project without worrying about dependency management.

## Testing

The Python library has been tested with SMS text from the same banks/cards/wallets as the original library:

Banks: Axis, ICICI, Kotak, HDFC, Standard Charted, IDFC, Niyo global, SBM Bank, Federal Bank

Credit Cards: HSBC, Citi Bank, Sodexo, ICICI, Uni Card, Indusind Bank, Slice, One card, HDFC, IDFC

Wallets: Paytm, Amazon pay, Lazypay, Simpl, Paytm postpaid
