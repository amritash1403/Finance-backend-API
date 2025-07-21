"""
Flask Application for Finance SMS Logger.
Provides API endpoint to log SMS transactions to Google Sheets.
"""

import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify
import psutil
import objgraph
from werkzeug.exceptions import BadRequest

from config import AppConfig, ValidationRules
from sheet_manager import SheetManager
from sms_parser import get_transaction_info


# Initialize Flask app
app = Flask(__name__)
app.config.from_object(AppConfig)

# Setup logging
logging.basicConfig(
    level=getattr(logging, AppConfig.LOG_LEVEL),
    format=AppConfig.LOG_FORMAT,
    handlers=[
        logging.FileHandler(os.path.join(AppConfig.LOGS_DIR, "app.log")),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

# Initialize Sheet Manager
try:
    sheet_manager = SheetManager()
    logger.info("Sheet Manager initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Sheet Manager: {e}")
    sheet_manager = None


# TODO: Temporary function to log memory usage
# This can be removed or modified later based on performance needs.
def log_memory_usage(tag=""):
    process = psutil.Process(os.getpid())
    mem_in_mb = process.memory_info().rss / (1024 * 1024)  # Resident Set Size in MB
    logger.info(f"[MEMORY] {tag} - {mem_in_mb:.2f} MB")


def log_objects(tag=""):
    """
    Log the number of objects in memory for debugging.
    """
    sheets_clients = len(objgraph.by_type("Resource"))
    logger.info(f"[OBJGRAPH] Sheets API Resource objects: {sheets_clients}")


@app.before_request
def authenticate_api_request():
    """
    Middleware to authenticate API requests using X-API-KEY header.
    Only applies to routes starting with config.API_PREFIX.
    """
    # Only check authentication for API routes
    # TODO: Temporary logging for memory usage
    log_memory_usage("Before Request")
    log_objects("Before Request")
    logger.info(f"Request path: {request.path}")

    if request.path.startswith(AppConfig.API_PREFIX):
        # Check if API key is configured
        if not AppConfig.API_KEY:
            logger.error("API_KEY environment variable not configured")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Authentication not configured",
                        "message": "Server configuration error - contact administrator",
                    }
                ),
                500,
            )

        # Get the API key from headers
        provided_key = request.headers.get("X-API-KEY")

        # Check if header is missing
        if not provided_key:
            logger.warning(
                f"Missing X-API-KEY header for {request.path} from {request.remote_addr}"
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Authentication required",
                        "message": "X-API-KEY header is required for API endpoints",
                    }
                ),
                403,
            )

        # Check if API key is valid
        if provided_key != AppConfig.API_KEY:
            logger.warning(
                f"Invalid X-API-KEY header for {request.path} from {request.remote_addr}"
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Authentication failed",
                        "message": "Invalid API key",
                    }
                ),
                403,
            )

        logger.debug(f"Valid API key provided for {request.path}")


# TODO: Temporary logging for memory usage
@app.after_request
def after_request(response):
    log_memory_usage("After Request")
    log_objects("After Request")
    return response


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return (
        jsonify(
            {
                "success": True,
                "message": "Finance SMS Logger is running",
                "data": {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "version": AppConfig.API_VERSION,
                },
            }
        ),
        200,
    )


@app.route(f"{AppConfig.API_PREFIX}/parse-sms", methods=["POST"])
def test_parser():
    """
    Test SMS parser without saving to sheets.
    Useful for testing and debugging.

    Expected JSON payload:
    {
        "text": "SMS text content"
    }
    """
    try:
        if not request.is_json:
            raise BadRequest("Request must be JSON")

        data = request.get_json()
        text = data.get("text")

        if not text:
            raise BadRequest("'text' field is required")

        # Parse SMS using sms_parser
        logger.info(f"Testing SMS parser: {text[:50]}...")

        try:
            transaction_info = get_transaction_info(text)
            transaction_data = transaction_info.to_dict() if transaction_info else {}

            is_valid = ValidationRules.is_valid_transaction(transaction_data, text)

            return (
                jsonify(
                    {
                        "success": True,
                        "data": {
                            "parsed_data": transaction_data,
                            "is_valid_transaction": is_valid,
                            "original_text": text,
                            "message": "SMS parsed successfully",
                        },
                    }
                ),
                200,
            )

        except Exception as e:
            logger.error(f"Error in test parser: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": str(e),
                        "message": "Parser error",
                    }
                ),
                500,
            )

    except BadRequest as e:
        logger.warning(f"Bad request in test parser: {e}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Bad request",
                }
            ),
            400,
        )

    except Exception as e:
        logger.error(f"Unexpected error in test_parser: {e}")
        return (
            jsonify(
                {"success": False, "error": str(e), "message": "Internal server error"}
            ),
            500,
        )


@app.route(f"{AppConfig.API_PREFIX}/sheets/<string:month_year>", methods=["GET"])
def get_sheet_info(month_year: str):
    """
    Get information about a specific monthly sheet.

    URL format: /api/v1/sheets/July-2025
    """
    try:
        # Parse month-year
        try:
            month_name, year = month_year.split("-")
            year = int(year)

            # Create datetime for the first day of the month
            date = datetime.strptime(f"{month_name} {year}", "%B %Y")

        except (ValueError, IndexError):
            raise BadRequest("Invalid month-year format. Use format: 'July-2025'")

        if not sheet_manager:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Service unavailable",
                        "message": "Google Sheets service is not available",
                    }
                ),
                503,
            )

        # Get sheet URL
        sheet_url = sheet_manager.get_sheet_url(date)

        if sheet_url:
            return (
                jsonify(
                    {
                        "success": True,
                        "data": {
                            "month_year": month_year,
                            "sheet_url": sheet_url,
                            "exists": True,
                        },
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "success": True,
                        "data": {
                            "month_year": month_year,
                            "sheet_url": None,
                            "exists": False,
                        },
                    }
                ),
                200,
            )

    except BadRequest as e:
        logger.warning(f"Bad request in get_sheet_info: {e}")
        return (
            jsonify({"success": False, "error": str(e), "message": "Bad request"}),
            400,
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_sheet_info: {e}")
        return (
            jsonify(
                {"success": False, "error": str(e), "message": "Internal server error"}
            ),
            500,
        )


@app.route(f"{AppConfig.API_PREFIX}/stats/<string:month_year>", methods=["GET"])
def get_monthly_spend_stats(month_year: str):
    """
    Get monthly spending statistics for a specific month.

    URL format: /api/v1/stats/July-2025

    Returns spending totals grouped by transaction type.
    """
    try:
        if not sheet_manager:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Service unavailable",
                        "message": "Google Sheets service is not available",
                    }
                ),
                503,
            )

        # Validate month_year format
        try:
            month_name, year_str = month_year.split("-")
            year = int(year_str)
            # Validate the month name
            datetime.strptime(f"{month_name} {year}", "%B %Y")
        except (ValueError, IndexError):
            raise BadRequest("Invalid month-year format. Use format: 'July-2025'")

        # Get spending statistics
        stats = sheet_manager.get_month_spends(month_name, year)

        if "error" in stats:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": stats["error"],
                        "message": "Sheet not found",
                    }
                ),
                404,
            )

        if "empty" in stats:
            return (
                jsonify(
                    {
                        "success": True,
                        "data": {
                            "month_year": month_year,
                            "total_spend": 0,
                            "total_transactions": 0,
                            "categories": {},
                        },
                        "message": "No transactions found for this month",
                    }
                ),
                200,
            )

        # Format response to match API structure
        response_data = {
            "month_year": stats["month"],
            "total_spend": stats["total_spend"],
            "transaction_count": stats["total_transactions"],
            "categories": stats["categories"],
            "generated_at": datetime.now().isoformat(),
        }

        return (
            jsonify(
                {
                    "success": True,
                    "data": response_data,
                    "message": "Monthly spend statistics retrieved successfully",
                }
            ),
            200,
        )

    except BadRequest as e:
        logger.warning(f"Bad request in get_monthly_spend_stats_by_month: {e}")
        return (
            jsonify({"success": False, "error": str(e), "message": "Bad request"}),
            400,
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_monthly_spend_stats_by_month: {e}")
        return (
            jsonify(
                {"success": False, "error": str(e), "message": "Internal server error"}
            ),
            500,
        )


@app.route(f"{AppConfig.API_PREFIX}/transactions", methods=["POST"])
def log_sms_transaction():
    """
    Log SMS transaction to Google Sheets.

    Expected JSON payload:
    {
        "text": "SMS text content",
        "date": "2025-07-14T10:30:00"  # ISO format
    }
    """
    try:
        # Validate request
        if not request.is_json:
            raise BadRequest("Request must be JSON")

        data = request.get_json()

        # Validate required fields
        if not data:
            raise BadRequest("Request body is empty")

        text = data.get("text")
        date_str = data.get("date")

        if not text:
            raise BadRequest("'text' field is required")

        if not date_str:
            raise BadRequest("'date' field is required")

        # Parse date first (before text validation)
        try:
            date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            print(f"Parsed date: {date}")
        except ValueError:
            raise BadRequest(
                "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
            )

        # Validate text length
        if len(text) < AppConfig.MIN_SMS_LENGTH:
            raise BadRequest(
                f"SMS text too short (minimum {AppConfig.MIN_SMS_LENGTH} characters)"
            )

        if len(text) > AppConfig.MAX_SMS_LENGTH:
            raise BadRequest(
                f"SMS text too long (maximum {AppConfig.MAX_SMS_LENGTH} characters)"
            )

        # Parse SMS using sms_parser
        logger.info(f"Parsing SMS: {text[:50]}...")

        try:
            transaction_info = get_transaction_info(text)
        except Exception as e:
            logger.error(f"Error parsing SMS: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": str(e),
                        "message": "Failed to parse SMS",
                    }
                ),
                500,
            )

        # Convert transaction info to dict
        transaction_data = transaction_info.to_dict() if transaction_info else {}

        # Validate parsed transaction
        if not ValidationRules.is_valid_transaction(transaction_data, text):
            logger.warning(f"Invalid transaction data from SMS: {text[:50]}...")
            return (
                jsonify(
                    {
                        "success": True,
                        "message": "SMS does not contain valid transaction information",
                        "parsed_data": transaction_data,
                    }
                ),
                200,
            )

        # Check if sheet manager is available
        if not sheet_manager:
            logger.error("Sheet Manager not initialized")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Service unavailable",
                        "message": "Google Sheets service is not available",
                    }
                ),
                503,
            )

        # Insert into Google Sheets
        success = sheet_manager.insert_transaction_data(transaction_data, date)

        if success:
            sheet_url = sheet_manager.get_sheet_url(date)
            response = {
                "success": True,
                "message": "Transaction logged successfully",
                "data": {
                    "transaction_data": transaction_data,
                    "date": date.isoformat(),
                    "sheet_url": sheet_url,
                },
            }
            logger.info(f"Transaction logged successfully for date: {date}")
            return jsonify(response), 201
        else:
            logger.error("Failed to insert transaction into Google Sheets")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Database error",
                        "message": "Failed to insert transaction into Google Sheets",
                    }
                ),
                500,
            )

    except BadRequest as e:
        logger.warning(f"Bad request: {e}")
        return (
            jsonify({"success": False, "error": str(e), "message": "Bad request"}),
            400,
        )

    except Exception as e:
        logger.error(f"Unexpected error in log_sms_transaction: {e}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Internal server error",
                }
            ),
            500,
        )


@app.route(f"{AppConfig.API_PREFIX}/transactions/<string:date>", methods=["GET"])
def get_transactions_by_date(date: str):
    """
    Get all transactions for a specific date.

    URL format: /api/v1/transactions/2025-09-05

    Returns all transactions for the specified date.
    """
    try:
        if not sheet_manager:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Service unavailable",
                        "message": "Google Sheets service is not available",
                    }
                ),
                503,
            )

        # Validate and parse date
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise BadRequest("Invalid date format. Use format: 'YYYY-MM-DD'")

        # Get transactions for the date
        transactions = sheet_manager.get_transactions_by_date(parsed_date)
        
        # Transform transactions to use row_index instead of _row_index
        formatted_transactions = []
        for transaction in transactions:
            formatted_transaction = dict(transaction)
            if "_row_index" in formatted_transaction:
                formatted_transaction["row_index"] = formatted_transaction.pop("_row_index")
            formatted_transactions.append(formatted_transaction)

        # Format response
        response_data = {
            "date": date,
            "transaction_count": len(formatted_transactions),
            "transactions": formatted_transactions,
            "generated_at": datetime.now().isoformat(),
        }

        return (
            jsonify(
                {
                    "success": True,
                    "data": response_data,
                    "message": f"Retrieved {len(transactions)} transactions for {date}",
                }
            ),
            200,
        )

    except BadRequest as e:
        logger.warning(f"Bad request in get_transactions_by_date: {e}")
        return (
            jsonify({"success": False, "error": str(e), "message": "Bad request"}),
            400,
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_transactions_by_date: {e}")
        return (
            jsonify(
                {"success": False, "error": str(e), "message": "Internal server error"}
            ),
            500,
        )


@app.route(f"{AppConfig.API_PREFIX}/transactions", methods=["PATCH"])
def update_transaction():
    """
    Update multiple fields in a transaction.

    URL format: /api/v1/transactions

    Expected JSON payload:
    {
        "sheet_name": "September-2025",
        "row_index": 3,
        "updates": {
            "Type": "Food Order",
            "Friend Split": "75.00",
            "Notes": "Updated notes"
        }
    }
    """
    try:
        if not sheet_manager:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Service unavailable",
                        "message": "Google Sheets service is not available",
                    }
                ),
                503,
            )

        # Validate request
        if not request.is_json:
            raise BadRequest("Request must be JSON")

        data = request.get_json()
        if not data:
            raise BadRequest("Request body is empty")

        # Extract required fields from payload
        sheet_name = data.get("sheet_name")
        row_index = data.get("row_index")
        updates = data.get("updates", {})

        # Validate required fields
        if not sheet_name:
            raise BadRequest("'sheet_name' field is required")
        
        if not row_index:
            raise BadRequest("'row_index' field is required")
        
        if not isinstance(row_index, int):
            raise BadRequest("'row_index' must be an integer")

        # Validate row index
        if row_index < 2:
            raise BadRequest("Invalid row index. Row index must be >= 2 (data rows only)")

        # Validate field updates
        field_updates = {}
        for field_name, value in updates.items():
            # Check if field name is valid (exists in header row)
            try:
                from config import SheetConfig
                SheetConfig.get_column_letter(field_name)
                field_updates[field_name] = value
            except ValueError:
                raise BadRequest(f"Invalid field name: '{field_name}'. Must be one of: {', '.join(SheetConfig.HEADER_ROW)}")

        if not field_updates:
            raise BadRequest("No valid field updates provided in 'updates' object")

        # Perform update
        success = sheet_manager.update_transaction_fields(sheet_name, row_index, field_updates)

        if success:
            response_data = {
                "sheet_name": sheet_name,
                "row_index": row_index,
                "updated_fields": field_updates,
                "updated_at": datetime.now().isoformat(),
            }

            logger.info(f"Transaction updated successfully: {sheet_name} row {row_index}")
            return (
                jsonify(
                    {
                        "success": True,
                        "data": response_data,
                        "message": f"Transaction updated successfully in {sheet_name} at row {row_index}",
                    }
                ),
                200,
            )
        else:
            logger.error(f"Failed to update transaction: {sheet_name} row {row_index}")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Update failed",
                        "message": "Failed to update transaction in Google Sheets",
                    }
                ),
                500,
            )

    except BadRequest as e:
        logger.warning(f"Bad request in update_transaction: {e}")
        return (
            jsonify({"success": False, "error": str(e), "message": "Bad request"}),
            400,
        )
    except Exception as e:
        logger.error(f"Unexpected error in update_transaction: {e}")
        return (
            jsonify(
                {"success": False, "error": str(e), "message": "Internal server error"}
            ),
            500,
        )


@app.route(f"{AppConfig.API_PREFIX}/transactions", methods=["DELETE"])
def delete_transaction():
    """
    Delete a transaction row.

    URL format: /api/v1/transactions

    Expected JSON payload:
    {
        "sheet_name": "September-2025",
        "row_index": 3
    }
    """
    try:
        if not sheet_manager:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Service unavailable",
                        "message": "Google Sheets service is not available",
                    }
                ),
                503,
            )

        # Validate request
        if not request.is_json:
            raise BadRequest("Request must be JSON")

        data = request.get_json()
        if not data:
            raise BadRequest("Request body is empty")

        # Extract required fields from payload
        sheet_name = data.get("sheet_name")
        row_index = data.get("row_index")

        # Validate required fields
        if not sheet_name:
            raise BadRequest("'sheet_name' field is required")
        
        if not row_index:
            raise BadRequest("'row_index' field is required")
        
        if not isinstance(row_index, int):
            raise BadRequest("'row_index' must be an integer")

        # Validate row index
        if row_index < 2:
            raise BadRequest("Invalid row index. Row index must be >= 2 (data rows only)")

        # Perform deletion
        success = sheet_manager.delete_transaction_row(sheet_name, row_index)

        if success:
            response_data = {
                "sheet_name": sheet_name,
                "deleted_row_index": row_index,
                "deleted_at": datetime.now().isoformat(),
            }

            logger.info(f"Transaction deleted successfully: {sheet_name} row {row_index}")
            return (
                jsonify(
                    {
                        "success": True,
                        "data": response_data,
                        "message": f"Transaction deleted successfully from {sheet_name} at row {row_index}",
                    }
                ),
                200,
            )
        else:
            logger.error(f"Failed to delete transaction: {sheet_name} row {row_index}")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Deletion failed",
                        "message": "Failed to delete transaction from Google Sheets",
                    }
                ),
                500,
            )

    except BadRequest as e:
        logger.warning(f"Bad request in delete_transaction: {e}")
        return (
            jsonify({"success": False, "error": str(e), "message": "Bad request"}),
            400,
        )
    except Exception as e:
        logger.error(f"Unexpected error in delete_transaction: {e}")
        return (
            jsonify(
                {"success": False, "error": str(e), "message": "Internal server error"}
            ),
            500,
        )


@app.errorhandler(BadRequest)
def handle_bad_request(error):
    """Handle BadRequest errors."""
    logger.warning(f"Bad request: {error}")
    return (
        jsonify({"success": False, "error": "Bad request", "message": str(error)}),
        400,
    )


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return (
        jsonify(
            {"success": False, "error": "Not found", "message": "Endpoint not found"}
        ),
        404,
    )


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return (
        jsonify(
            {
                "success": False,
                "error": "Method not allowed",
                "message": "HTTP method not allowed for this endpoint",
            }
        ),
        405,
    )


@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return (
        jsonify(
            {
                "success": False,
                "error": "Internal server error",
                "message": "An unexpected error occurred",
            }
        ),
        500,
    )


if __name__ == "__main__":
    # Create necessary directories
    os.makedirs(AppConfig.LOGS_DIR, exist_ok=True)

    # Run the Flask app
    logger.info("Starting Finance SMS Logger Flask Application")
