"""
Simple test for SMS parser without external dependencies.
"""

from sms_parser import get_transaction_info
from config import ValidationRules
import json
import requests
import csv


def test_sms_parser():
    """Test the SMS parser with sample messages."""
    print("Testing SMS Parser")
    print("=" * 50)

    test_messages = csv.reader(open("sms-20250713002830.csv", "r", encoding="utf-8"))
    test_messages = [(row[1], row[-1]) for row in test_messages]
    for i, (date, sms) in enumerate(test_messages, 1):
        try:
            print(f"\nTest {i}:")
            print(f"SMS: {sms}")

            transaction_info = get_transaction_info(sms)
            transaction_data = transaction_info.to_dict()

            print("Parsed successfully:")
            print(json.dumps(transaction_data, indent=2))

            # Test API endpoint
            response = requests.post(
                "http://localhost:5000/api/v1/log",
                json={"text": sms, "date": "2025-07-14T10:30:00"},
                headers={"Content-Type": "application/json"},
            )
            print(f"API Response: {response.status_code} - {response.json()}")

        except Exception as e:
            print(f"Error parsing SMS: {e}")
        except UnicodeDecodeError:
            continue  # Skip any decoding errors
        except UnicodeEncodeError:
            continue  # Skip any encoding errors

        print("-" * 50)


if __name__ == "__main__":
    test_sms_parser()
