"""
Configuration file for the Finance SMS Logger Flask Application.
Contains paths, static data, and application settings.
"""

import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# First, try to load from .env file (development)
# This will only load variables that aren't already set
if os.path.exists(".env"):
    if load_dotenv(".env", override=False):
        logger.info("Loaded environment variables from .env file")
else:
    logger.warning(".env file not found, using system environment variables")
    logger.info(f"Available environment variables: {list(os.environ.keys())}")


def get_env_variable(key: str, default: str = None) -> str:
    """
    Get environment variable with fallback support.

    Priority order:
    1. .env file (if dotenv is available and file exists)
    2. Actual environment variables
    3. Default value

    Args:
        key: Environment variable name
        default: Default value if variable not found

    Returns:
        The environment variable value or default
    """
    value = os.environ.get(key, default)
    return value


def get_google_credentials_info():
    """
    Get Google Service Account credentials as a dictionary.
    This is useful for environments where file creation is restricted.

    Returns:
        dict: Google Service Account credentials dictionary

    Raises:
        ValueError: If required environment variables are missing
    """
    required_env_vars = [
        "GOOGLE_PROJECT_ID",
        "GOOGLE_PRIVATE_KEY_ID",
        "GOOGLE_PRIVATE_KEY",
        "GOOGLE_CLIENT_EMAIL",
        "GOOGLE_CLIENT_ID",
    ]

    # Check if all required environment variables are present
    missing_vars = [var for var in required_env_vars if not get_env_variable(var)]
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    # Build credentials dictionary
    credentials = {
        "type": "service_account",
        "project_id": get_env_variable("GOOGLE_PROJECT_ID"),
        "private_key_id": get_env_variable("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": get_env_variable("GOOGLE_PRIVATE_KEY"),
        "client_email": get_env_variable("GOOGLE_CLIENT_EMAIL"),
        "client_id": get_env_variable("GOOGLE_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{get_env_variable('GOOGLE_CLIENT_EMAIL').replace('@', '%40')}",
        "universe_domain": "googleapis.com",
    }

    print("✅ Google credentials loaded dynamically from environment variables")
    return credentials


class Paths:
    """File paths configuration."""

    @staticmethod
    def get_google_credentials_info():
        """Get Google credentials as dictionary from env vars."""
        return get_google_credentials_info()

    # Logs directory
    LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")

    # Google Sheets configuration
    SHARED_WORKBOOK_ID = get_env_variable(
        "GSHEET_SHARED_WORKBOOK_ID", "your-shared-workbook-id-here"
    )


class TransactionTypes:
    """Transaction types with associated colors for conditional formatting."""

    TYPES_WITH_COLORS = {
        "Food & Dining": "#FF6B6B",  # Red
        "Transportation": "#4ECDC4",  # Teal
        "Shopping": "#45B7D1",  # Blue
        "Entertainment": "#96CEB4",  # Green
        "Utilities": "#FFEAA7",  # Yellow
        "Healthcare": "#DDA0DD",  # Plum
        "Education": "#98D8C8",  # Mint
        "Investment": "#F7DC6F",  # Light Yellow
        "Transfer": "#AED6F1",  # Light Blue
        "Other": "#D5DBDB",  # Light Gray
        "Salary": "#58D68D",  # Light Green
        "Refund": "#F8C471",  # Orange
        "Cash Withdrawal": "#F1948A",  # Light Red
        "Bill Payment": "#BB8FCE",  # Light Purple
        "Subscription": "#85C1E9",  # Sky Blue
    }

    @classmethod
    def get_dropdown_options(cls) -> List[str]:
        """Get list of transaction types for dropdown."""
        return list(cls.TYPES_WITH_COLORS.keys())

    @classmethod
    def get_color_for_type(cls, transaction_type: str) -> str:
        """Get color for a specific transaction type."""
        return cls.TYPES_WITH_COLORS.get(
            transaction_type, cls.TYPES_WITH_COLORS["Other"]
        )


class SheetConfig:
    """Google Sheets configuration."""

    # Sheet names
    DASHBOARD_SHEET_NAME = "Dashboard"
    TRANSACTIONS_SHEET_NAME = "Transactions"

    # Header row definition (mapped to fixed columns)
    HD_DATE = "Date"  # Column A
    HD_DESCRIPTION = "Description"  # Column B
    HD_AMOUNT = "Amount"  # Column C
    HD_TYPE = "Type"  # Column D (dropdown)
    HD_ACCOUNT = "Account"  # Column E
    HD_FRIEND_SPLIT = "Friend Split"  # Column F
    HD_AMOUNT_BORNE = "Amount Borne"  # Column G (formula)
    HD_NOTES = "Notes"  # Column H (manual notes)

    HEADER_ROW = [
        HD_DATE,
        HD_DESCRIPTION,
        HD_AMOUNT,
        HD_TYPE,
        HD_ACCOUNT,
        HD_FRIEND_SPLIT,
        HD_AMOUNT_BORNE,
        HD_NOTES,
    ]

    HEADER_WIDTHS = {
        HD_DATE: 100,
        HD_DESCRIPTION: 250,
        HD_AMOUNT: 100,
        HD_TYPE: 120,
        HD_ACCOUNT: 150,
        HD_FRIEND_SPLIT: 120,
        HD_AMOUNT_BORNE: 120,
        HD_NOTES: 200,
    }

    # Formula for "Amount Borne by Me" column (I)
    AMOUNT_BORNE_FORMULA = "=IF(AND({amount_col}{row}>0,{friend_amount_col}{row}>=0),{amount_col}{row}-{friend_amount_col}{row},{amount_col}{row})"

    @staticmethod
    def get_column_letter(column_name: str) -> str:
        """Convert column name to letter (e.g., 'A', 'B', etc.)."""
        try:
            return chr(ord("A") + SheetConfig.HEADER_ROW.index(column_name))
        except ValueError:
            raise ValueError(f"Column name '{column_name}' not found in header row")


class AppConfig:
    """Flask application configuration."""

    # Flask settings (from environment)
    SECRET_KEY = get_env_variable(
        "SECRET_KEY", "your-secret-key-here-change-in-production"
    )
    DEBUG = get_env_variable("DEBUG", "True").lower() == "true"
    PORT = int(get_env_variable("PORT", "5000"))

    # API settings (mostly constants, version can be overridden)
    API_VERSION = get_env_variable("API_VERSION", "v1")
    API_PREFIX = f"/api/{API_VERSION}"

    # API Security settings
    API_KEY = get_env_variable("API_KEY")  # Required for API endpoints authentication

    # Google Sheets API settings (constants)
    GOOGLE_SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    # Logging settings (from environment)
    LOG_LEVEL = get_env_variable("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOGS_DIR = Paths.LOGS_DIR

    # Sheet naming format (constant)
    SHEET_NAME_FORMAT = "{month}-{year}"  # e.g., "July-2025"

    # Validation settings (from environment with defaults)
    MAX_SMS_LENGTH = int(get_env_variable("MAX_SMS_LENGTH", "1000"))
    MIN_SMS_LENGTH = int(get_env_variable("MIN_SMS_LENGTH", "10"))

    # Memory limit for SheetManager cache (in MB)
    MEMORY_LIMIT_MB = int(get_env_variable("MEMORY_LIMIT_MB", "300"))


class ValidationRules:
    """Validation rules for incoming data."""

    # Fields that indicate a valid transaction
    VALID_TRANSACTION_INDICATORS = {
        "account": ["type", "number"],
        "transaction": ["amount"],
    }

    # Keywords for not valid transactions
    INVALID_TRANSACTION_KEYWORDS = ["failed", "declined", "otp", "secret"]

    @staticmethod
    def is_valid_transaction(
        transaction_data: Dict[str, Any], transaction_text: str
    ) -> bool:
        """Check if transaction data is valid for insertion."""
        if (
            not transaction_data
            or transaction_data.get("transaction", {}).get("type", "") == "credit"
        ):
            return False

        # Check for invalid keywords in transaction text
        transaction_text = transaction_text.lower()
        for keyword in ValidationRules.INVALID_TRANSACTION_KEYWORDS:
            if keyword in transaction_text:
                return False

        # Check if transaction has required fields
        for field, subfields in ValidationRules.VALID_TRANSACTION_INDICATORS.items():
            if field not in transaction_data:
                return False
            for subfield in subfields:
                if (
                    subfield not in transaction_data[field]
                    or not transaction_data[field][subfield]
                ):
                    return False

        return True


# Create necessary directories
def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        Paths.LOGS_DIR,
        os.path.join(os.path.dirname(__file__), "credentials"),
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)


# Initialize directories when module is imported
create_directories()
