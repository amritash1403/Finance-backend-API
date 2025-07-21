"""
Google Sheets Manager for handling sheet operations.
Manages monthly sheet creation within a shared workbook, formatting, and data insertion.
"""

import os
import logging
import psutil
from datetime import datetime
import time
from typing import Dict, List, Optional, Any, Tuple
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from google.auth.exceptions import GoogleAuthError

from config import Paths, SheetConfig, TransactionTypes, AppConfig, ValidationRules


class SheetManager:
    """Manages Google Sheets operations for the Finance SMS Logger."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.service = None
        self.shared_workbook_id = Paths.SHARED_WORKBOOK_ID
        self._initialize_services()  # Initialize Google Sheets API service

        self.monthly_spends_cache = {}  # Cache for monthly spends data
        # {sheet_name: (data, timestamp)}
        
        self.transactions_cache = {}  # Cache for transaction data by sheet
        # {sheet_name: (transactions_list, timestamp)}

    def _initialize_services(self):
        """Initialize Google Sheets API service."""
        try:
            # Get credentials info (dictionary) instead of file path
            credentials_info = Paths.get_google_credentials_info()

            credentials = Credentials.from_service_account_info(
                credentials_info, scopes=AppConfig.GOOGLE_SHEETS_SCOPES
            )

            self.service = build(
                "sheets", "v4", credentials=credentials, cache_discovery=False
            )

            self.logger.info("Google Sheets service initialized successfully")

        except ValueError as e:
            self.logger.error(
                f"Missing environment variables for Google credentials: {e}"
            )
            self.logger.error(
                "Please check your .env file has all required GOOGLE_* variables"
            )
            return
        except GoogleAuthError as e:
            self.logger.error(f"Google authentication error: {e}")
            return  # Don't raise, just return without initializing services
        except Exception as e:
            self.logger.error(f"Error initializing Google services: {e}")
            return  # Don't raise, just return without initializing services

    def _clean_up(self):
        """Clean up the memory by clearing cache and reinitializing services if needed."""
        process = psutil.Process(os.getpid())
        mem_in_mb = process.memory_info().rss / (1024 * 1024)
        if mem_in_mb > AppConfig.MEMORY_LIMIT_MB:
            self.monthly_spends_cache.clear()
            self.transactions_cache.clear()
            self._initialize_services()  # Reinitialize services to free up memory
            self.logger.info(
                f"Memory limit exceeded ({mem_in_mb:.2f} MB). Cleared cache and reinitialized services."
            )

    def _get_month_year_key(self, date: datetime) -> str:
        """Get month-year key for sheet mapping."""
        return f"{date.strftime('%B')}-{date.year}"

    def _generate_sheet_name(self, date: datetime) -> str:
        """Generate sheet name based on date."""
        return AppConfig.SHEET_NAME_FORMAT.format(
            month=date.strftime("%B"), year=date.year
        )

    def _create_new_sheet(self, sheet_name: str) -> str:
        """Create a new sheet within the shared workbook."""
        try:
            # Check if sheet already exists
            if self._sheet_exists(sheet_name):
                self.logger.warning(f"Sheet '{sheet_name}' already exists in workbook")
                return self.shared_workbook_id

            # Create new sheet within the shared workbook
            requests = [
                {
                    "addSheet": {
                        "properties": {
                            "title": sheet_name,
                            "index": 1,  # Insert as second sheet (after Dashboard)
                        }
                    }
                }
            ]

            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.shared_workbook_id, body={"requests": requests}
            ).execute()

            self.logger.info(f"Created new sheet '{sheet_name}' in shared workbook")

            # Setup the sheet with headers and formatting
            self._setup_new_sheet_structure(sheet_name)

            return self.shared_workbook_id

        except Exception as e:
            self.logger.error(f"Error creating new sheet: {e}")
            if "permission" in str(e).lower():
                self.logger.error(
                    "Permission denied. Please check if the service account has Editor permissions on the shared workbook."
                )
            raise

    def _sheet_exists(self, sheet_name: str) -> bool:
        """Check if a sheet exists in the shared workbook."""
        try:
            spreadsheet = (
                self.service.spreadsheets()
                .get(spreadsheetId=self.shared_workbook_id)
                .execute()
            )
            sheets = spreadsheet.get("sheets", [])

            for sheet in sheets:
                if sheet["properties"]["title"] == sheet_name:
                    return True
            return False

        except Exception as e:
            self.logger.error(f"Error checking if sheet exists: {e}")
            return False

    def _setup_new_sheet_structure(self, sheet_name: str):
        """Setup the new sheet structure with headers and formatting."""
        try:
            # Write header row - use dynamic range based on header row length
            header_end_col = chr(ord("A") + len(SheetConfig.HEADER_ROW) - 1)
            header_range = f"{sheet_name}!A1:{header_end_col}1"
            header_values = [SheetConfig.HEADER_ROW]

            self.service.spreadsheets().values().update(
                spreadsheetId=self.shared_workbook_id,
                range=header_range,
                valueInputOption="RAW",
                body={"values": header_values},
            ).execute()

            # Format header row (bold, background color)
            sheet_id = self._get_sheet_id_by_name(self.shared_workbook_id, sheet_name)

            requests = [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": len(SheetConfig.HEADER_ROW),
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "textFormat": {"bold": True},
                                "backgroundColor": {
                                    "red": 0.9,
                                    "green": 0.9,
                                    "blue": 0.9,
                                },
                            }
                        },
                        "fields": "userEnteredFormat",
                    }
                },
                {
                    "setBasicFilter": {
                        "filter": {
                            "range": {
                                "sheetId": sheet_id,
                                "startRowIndex": 0,
                                "endRowIndex": 1,
                                "startColumnIndex": 0,
                                "endColumnIndex": len(SheetConfig.HEADER_ROW),
                            }
                        }
                    }
                },
            ]

            # Set widths for each header column
            for col_index, header in enumerate(SheetConfig.HEADER_ROW):
                requests.append(
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheet_id,
                                "dimension": "COLUMNS",
                                "startIndex": col_index,
                                "endIndex": col_index + 1,
                            },
                            "properties": {
                                "pixelSize": SheetConfig.HEADER_WIDTHS.get(header, 100)
                            },
                            "fields": "pixelSize",
                        }
                    }
                )

            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.shared_workbook_id, body={"requests": requests}
            ).execute()

            self.logger.info(f"Sheet structure setup completed for '{sheet_name}'")

        except Exception as e:
            self.logger.error(f"Error setting up sheet structure: {e}")
            raise

    def _get_sheet_id_by_name(self, spreadsheet_id: str, sheet_name: str) -> int:
        """Get sheet ID by name."""
        try:
            spreadsheet = (
                self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            )
            sheets = spreadsheet.get("sheets", [])

            for sheet in sheets:
                if sheet["properties"]["title"] == sheet_name:
                    return sheet["properties"]["sheetId"]

            raise ValueError(f"Sheet '{sheet_name}' not found")

        except Exception as e:
            self.logger.error(f"Error getting sheet ID: {e}")
            raise

    def _setup_conditional_formatting(self, sheet_name: str):
        """Setup conditional formatting for the specified sheet."""
        try:
            sheet_id = self._get_sheet_id_by_name(self.shared_workbook_id, sheet_name)

            requests = []

            # Get column indices for Type column
            type_col_index = SheetConfig.HEADER_ROW.index(SheetConfig.HD_TYPE)
            type_col_char = chr(type_col_index + ord("A"))

            # Add conditional formatting rules for different transaction types
            for transaction_type, color in TransactionTypes.TYPES_WITH_COLORS.items():
                # Convert hex color to RGB
                color_rgb = self._hex_to_rgb(color)

                condition_request = {
                    "addConditionalFormatRule": {
                        "rule": {
                            "ranges": [
                                {
                                    "sheetId": sheet_id,
                                    "startRowIndex": 1,
                                    "endRowIndex": 1000,
                                    "startColumnIndex": 0,
                                    "endColumnIndex": len(SheetConfig.HEADER_ROW),
                                }
                            ],
                            "booleanRule": {
                                "condition": {
                                    "type": "CUSTOM_FORMULA",
                                    "values": [
                                        {
                                            "userEnteredValue": f'=${type_col_char}2="{transaction_type}"'
                                        }
                                    ],
                                },
                                "format": {
                                    "backgroundColor": {
                                        "red": color_rgb[0],
                                        "green": color_rgb[1],
                                        "blue": color_rgb[2],
                                        "alpha": 0.2,
                                    }
                                },
                            },
                        },
                        "index": 0,
                    }
                }
                requests.append(condition_request)

            # Add dropdown for Type column
            type_dropdown_request = {
                "setDataValidation": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 1,  # Start from row 2 (after header)
                        "endRowIndex": 1000,  # Apply to many rows
                        "startColumnIndex": type_col_index,  # Type column
                        "endColumnIndex": type_col_index + 1,
                    },
                    "rule": {
                        "condition": {
                            "type": "ONE_OF_LIST",
                            "values": [
                                {"userEnteredValue": t}
                                for t in TransactionTypes.get_dropdown_options()
                            ],
                        },
                        "showCustomUi": True,
                        "strict": True,
                    },
                }
            }
            requests.append(type_dropdown_request)

            if requests:
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.shared_workbook_id, body={"requests": requests}
                ).execute()

                self.logger.info(
                    f"Conditional formatting setup completed for '{sheet_name}'"
                )

        except Exception as e:
            self.logger.error(f"Error setting up conditional formatting: {e}")
            raise

    def _hex_to_rgb(self, hex_color: str) -> Tuple[float, float, float]:
        """Convert hex color to RGB tuple (0-1 range)."""
        hex_color = hex_color.lstrip("#")
        rgb_tuple = tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
        return (rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])

    def _find_vacant_row(self, sheet_name: str) -> int:
        """Find the first vacant row (where first two columns are empty)."""
        try:
            # Read data from the specified sheet
            range_name = f"{sheet_name}!A:B"
            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=self.shared_workbook_id, range=range_name)
                .execute()
            )

            values = result.get("values", [])

            # Return the last row
            return len(values) + 1

        except Exception as e:
            self.logger.error(f"Error finding vacant row: {e}")
            return 2  # Default to row 2 if error

    def get_or_create_monthly_sheet(self, date: datetime) -> str:
        """Get existing monthly sheet or create new one within the shared workbook."""
        sheet_name = self._generate_sheet_name(date)

        # Check if sheet already exists in the workbook
        if self._sheet_exists(sheet_name):
            self.logger.info(f"Using existing sheet: {sheet_name}")
            return self.shared_workbook_id

        # Create new sheet within the shared workbook
        sheet_id = self._create_new_sheet(sheet_name)

        # Setup conditional formatting
        self._setup_conditional_formatting(sheet_name)

        self.logger.info(f"Created and configured new sheet '{sheet_name}'")
        return sheet_id

    def insert_transaction_data(
        self, transaction_data: Dict[str, Any], date: datetime
    ) -> bool:
        """Insert transaction data into the appropriate monthly sheet."""
        self._clean_up()  # Clean up cache if memory limit exceeded
        try:
            # Check if services are initialized
            if not self.service:
                self.logger.error(
                    "Google services not initialized. Please check credentials."
                )
                return False

            # Get or create monthly sheet
            sheet_id = self.get_or_create_monthly_sheet(date)
            sheet_name = self._generate_sheet_name(date)

            # Find vacant row
            vacant_row = self._find_vacant_row(sheet_name)

            # Prepare data for insertion
            row_data = self._prepare_row_data(transaction_data, date, sheet_name)

            # Insert data
            end_col = chr(ord("A") + len(SheetConfig.HEADER_ROW) - 1)
            range_name = f"{sheet_name}!A{vacant_row}:{end_col}{vacant_row}"
            self.service.spreadsheets().values().update(
                spreadsheetId=self.shared_workbook_id,
                range=range_name,
                valueInputOption="USER_ENTERED",  # Allow formulas
                body={"values": [row_data]},
            ).execute()

            self.logger.info(
                f"Transaction data inserted into '{sheet_name}' at row {vacant_row}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error inserting transaction data: {e}")
            return False

    def _prepare_row_data(
        self, transaction_data: Dict[str, Any], date: datetime, sheet_name: str
    ) -> List[str]:
        """Prepare row data for insertion."""
        account = transaction_data.get("account", {})
        transaction = transaction_data.get("transaction", {})
        balance = transaction_data.get("balance", {})

        # Determine transaction type for Type column
        trans_type = transaction.get("type", "")
        category = "Select"

        # Format amount
        amount = transaction.get("amount", "0")
        if amount:
            # Remove currency symbols and clean up
            amount = (
                amount.replace("INR", "")
                .replace("Rs.", "")
                .replace("Rs", "")
                .replace(",", "")
                .strip()
            )
            try:
                amount_float = float(amount)
            except ValueError:
                amount = "0"

        # Get row number for formula (use the current vacant row)
        vacant_row = self._find_vacant_row(sheet_name)

        # Get column letters for formula
        amount_col = SheetConfig.get_column_letter(SheetConfig.HD_AMOUNT)
        friend_split_col = SheetConfig.get_column_letter(SheetConfig.HD_FRIEND_SPLIT)

        # Build the formula for Amount Borne by Me
        amount_borne_formula = f"=IF(AND({amount_col}{vacant_row}>0,{friend_split_col}{vacant_row}>=0),{amount_col}{vacant_row}-{friend_split_col}{vacant_row},{amount_col}{vacant_row})"

        # Prepare row data according to new 8-column structure
        row_data = [
            date.strftime("%Y-%m-%d"),  # Date (Column A)
            f"{transaction.get('merchant', '')} - {trans_type}",  # Description (Column B)
            amount,  # Amount (Column C)
            category,  # Type (Column D - dropdown)
            f"{account.get('type', 'Unknown')} - {account.get('number', 'Unknown')}",  # Account (Column E)
            "0",  # Friend Split (Column F - default)
            amount_borne_formula,  # Amount Borne by Me (Column G - formula)
            "",  # Notes (Column H - empty for manual entry)
        ]

        return row_data

    def get_sheet_url(self, date: datetime) -> Optional[str]:
        """Get the URL of the monthly sheet within the shared workbook."""
        sheet_name = self._generate_sheet_name(date)

        # Check if sheet exists in workbook
        if self._sheet_exists(sheet_name):
            # Get the sheet ID for direct linking
            try:
                sheet_id = self._get_sheet_id_by_name(
                    self.shared_workbook_id, sheet_name
                )
                return f"https://docs.google.com/spreadsheets/d/{self.shared_workbook_id}/edit#gid={sheet_id}"
            except Exception:
                # Fallback to general workbook URL
                return f"https://docs.google.com/spreadsheets/d/{self.shared_workbook_id}/edit"
        return None

    def get_all_monthly_sheets(self) -> Dict[str, str]:
        """Get all monthly sheets from the shared workbook."""
        try:
            spreadsheet = (
                self.service.spreadsheets()
                .get(spreadsheetId=self.shared_workbook_id)
                .execute()
            )
            sheets = spreadsheet.get("sheets", [])

            monthly_sheets = {}
            for sheet in sheets:
                sheet_title = sheet["properties"]["title"]
                # Skip Dashboard and other non-monthly sheets
                if sheet_title != "Dashboard" and "-" in sheet_title:
                    # Try to parse as monthly sheet (e.g., "July-2025")
                    try:
                        parts = sheet_title.split("-")
                        if len(parts) >= 2:
                            month = parts[0]
                            year = parts[1]
                            key = f"{month}-{year}"
                            monthly_sheets[key] = sheet_title
                    except Exception:
                        continue

            return monthly_sheets
        except Exception as e:
            self.logger.error(f"Error getting all monthly sheets: {e}")
            return {}

    def get_sheet_statistics(self) -> Dict[str, Any]:
        """Get statistics about the sheets."""
        try:
            stats = {
                "shared_workbook_id": self.shared_workbook_id,
                "service_initialized": self.service is not None,
            }

            if self.service:
                actual_sheets = self.get_all_monthly_sheets()
                stats["total_monthly_sheets"] = len(actual_sheets)
                stats["monthly_sheets"] = actual_sheets

            return stats

        except Exception as e:
            self.logger.error(f"Error getting sheet statistics: {e}")
            return {"error": str(e)}

    def get_transactions_by_date(self, date: datetime) -> List[Dict[str, Any]]:
        """
        Fetch all rows from the sheet corresponding to the month of the given date.
        Filter rows matching the given date in column A (Date column).
        Return as list of dictionaries with keys as per SheetConfig.HEADER_ROW.
        """
        self._clean_up()  # Clean up cache if memory limit exceeded
        try:
            sheet_name = self._generate_sheet_name(date)
            date_str = date.strftime("%Y-%m-%d")
            
            # Check if sheet exists
            if not self._sheet_exists(sheet_name):
                self.logger.warning(f"Sheet '{sheet_name}' does not exist")
                return []

            # Check cache first (valid for 1 minute)
            cache_key = f"{sheet_name}_{date_str}"
            if cache_key in self.transactions_cache:
                cached_data, cache_timestamp = self.transactions_cache[cache_key]
                if time.time() - cache_timestamp < 60:  # 1 minute cache
                    self.logger.info(f"Returning cached transactions for {cache_key}")
                    return cached_data
                
            self.logger

            # Read data from the sheet (skip header row)
            range_name = f"{sheet_name}!A2:{chr(ord('A') + len(SheetConfig.HEADER_ROW) - 1)}"
            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=self.shared_workbook_id, range=range_name)
                .execute()
            )

            values = result.get("values", [])
            matching_transactions = []

            for row_index, row in enumerate(values, start=2):  # Start from row 2 (1-based)
                # Ensure row has enough columns
                while len(row) < len(SheetConfig.HEADER_ROW):
                    row.append("")

                # Check if date matches
                row_date = row[0] if row else ""
                if row_date == date_str:
                    # Create transaction dictionary
                    transaction = {}
                    for col_index, header in enumerate(SheetConfig.HEADER_ROW):
                        transaction[header] = row[col_index] if col_index < len(row) else ""
                    
                    # Add row index for reference (1-based for Google Sheets)
                    transaction["_row_index"] = row_index
                    matching_transactions.append(transaction)

            # Cache the result
            self.transactions_cache[cache_key] = (matching_transactions, time.time())
            
            self.logger.info(f"Found {len(matching_transactions)} transactions for date {date_str} in sheet {sheet_name}")
            return matching_transactions

        except Exception as e:
            self.logger.error(f"Error getting transactions by date: {e}")
            return []

    def update_transaction_fields(self, sheet_name: str, row_index: int, field_updates: Dict[str, Any]) -> bool:
        """
        Update multiple fields in the given row (row_index, 1-based).
        field_updates is a dictionary where:
        - Key = Field name (from SheetConfig.HEADER_ROW)
        - Value = New value to be written
        """
        try:
            if not self.service:
                self.logger.error("Google services not initialized")
                return False

            # Check if sheet exists
            if not self._sheet_exists(sheet_name):
                self.logger.error(f"Sheet '{sheet_name}' does not exist")
                return False

            # Validate row_index
            if row_index < 2:  # Header is row 1, so data starts from row 2
                self.logger.error(f"Invalid row index {row_index}. Must be >= 2")
                return False

            # Prepare update data
            update_data = []
            for field_name, new_value in field_updates.items():
                try:
                    # Get column letter for the field
                    col_letter = SheetConfig.get_column_letter(field_name)
                    range_name = f"{sheet_name}!{col_letter}{row_index}"
                    
                    update_data.append({
                        "range": range_name,
                        "values": [[str(new_value)]]
                    })
                    
                    self.logger.info(f"Preparing update for {field_name} -> {new_value} at {range_name}")
                    
                except ValueError as e:
                    self.logger.error(f"Invalid field name '{field_name}': {e}")
                    continue

            if not update_data:
                self.logger.warning("No valid field updates to perform")
                return False

            # Perform batch update in a single API call
            body = {
                "valueInputOption": "USER_ENTERED",  # Allow formulas
                "data": update_data
            }

            result = self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.shared_workbook_id,
                body=body
            ).execute()

            # Log successful updates
            updated_cells = result.get("totalUpdatedCells", 0)
            self.logger.info(f"Successfully updated {updated_cells} cells in row {row_index} of sheet '{sheet_name}'")
            
            # Invalidate related cache entries
            self._invalidate_sheet_cache(sheet_name)
            
            return True

        except Exception as e:
            self.logger.error(f"Error updating transaction fields: {e}")
            return False

    def delete_transaction_row(self, sheet_name: str, row_index: int) -> bool:
        """
        Delete the entire row (row_index) from the given sheet_name.
        Adjusts Google Sheets accordingly (deletion shifts other rows up).
        """
        try:
            if not self.service:
                self.logger.error("Google services not initialized")
                return False

            # Check if sheet exists
            if not self._sheet_exists(sheet_name):
                self.logger.error(f"Sheet '{sheet_name}' does not exist")
                return False

            # Validate row_index
            if row_index < 2:  # Header is row 1, so data starts from row 2
                self.logger.error(f"Invalid row index {row_index}. Must be >= 2")
                return False

            # Get sheet ID
            sheet_id = self._get_sheet_id_by_name(self.shared_workbook_id, sheet_name)

            # Prepare delete request
            requests = [{
                "deleteDimension": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": row_index - 1,  # Convert to 0-based index
                        "endIndex": row_index  # End index is exclusive
                    }
                }
            }]

            # Execute the deletion
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.shared_workbook_id,
                body={"requests": requests}
            ).execute()

            self.logger.info(f"Successfully deleted row {row_index} from sheet '{sheet_name}'")
            
            # Invalidate related cache entries
            self._invalidate_sheet_cache(sheet_name)
            
            return True

        except Exception as e:
            self.logger.error(f"Error deleting transaction row: {e}")
            return False

    def _invalidate_sheet_cache(self, sheet_name: str):
        """Invalidate cache entries related to a specific sheet."""
        try:
            # Remove monthly spends cache for this sheet
            if sheet_name in self.monthly_spends_cache:
                del self.monthly_spends_cache[sheet_name]
                self.logger.debug(f"Invalidated monthly spends cache for {sheet_name}")

            # Remove transaction cache entries for this sheet
            keys_to_remove = [key for key in self.transactions_cache.keys() if key.startswith(sheet_name)]
            for key in keys_to_remove:
                del self.transactions_cache[key]
                self.logger.debug(f"Invalidated transaction cache for {key}")

        except Exception as e:
            self.logger.error(f"Error invalidating cache: {e}")

    def get_month_spends(self, month: str, year: int) -> Dict[str, Any]:
        """Get total spends for a specific month and year."""
        # Cleanup cache before adding new entry
        self._clean_up()
        try:
            sheet_name = AppConfig.SHEET_NAME_FORMAT.format(month=month, year=year)

            # Check cache first (simple time-based caching)
            if sheet_name in self.monthly_spends_cache:
                cached_data, cache_timestamp = self.monthly_spends_cache[sheet_name]
                # Cache is valid for 2 minutes (120 seconds)
                if time.time() - cache_timestamp < 120:
                    self.logger.info(f"Returning cached data for {sheet_name}")
                    return cached_data

            if not self._sheet_exists(sheet_name):
                return {"empty": f"Sheet for {sheet_name} does not exist."}

            # Read data from the sheet
            range_name = f"{sheet_name}!A2:{chr(64 + len(SheetConfig.HEADER_ROW))}"  # Skip header row
            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=self.shared_workbook_id, range=range_name)
                .execute()
            )

            values = result.get("values", [])
            total_spend = 0.0
            total_transaction_count = 0
            spends: Dict[str, Dict[str, float]] = {}

            amount_borne_col_index = SheetConfig.HEADER_ROW.index(
                SheetConfig.HD_AMOUNT_BORNE
            )
            type_col_index = SheetConfig.HEADER_ROW.index(SheetConfig.HD_TYPE)

            for row in values:
                if len(row) > max(amount_borne_col_index, type_col_index):
                    try:
                        amount = float(row[amount_borne_col_index])
                        type_ = row[type_col_index]
                        if type_ not in spends:
                            spends[type_] = {"amount": 0.0, "count": 0}
                        spends[type_]["amount"] += amount
                        spends[type_]["count"] += 1
                        total_spend += amount
                        total_transaction_count += 1
                    except (ValueError, IndexError):
                        continue

            spend_data: Dict[str, Any] = {
                "month": sheet_name,
                "total_spend": total_spend,
                "total_transactions": total_transaction_count,
                "categories": spends,
            }

            # Cache the result with current timestamp
            self.monthly_spends_cache[sheet_name] = (spend_data, time.time())
            return spend_data

        except Exception as e:
            self.logger.error(f"Error getting month spends: {e}")
            return {"error": str(e)}
