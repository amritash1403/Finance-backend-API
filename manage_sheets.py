#!/usr/bin/env python3
"""
Sheet management utility script.
"""

import sys
import os
from datetime import datetime
from pprint import pprint

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from sheet_manager import SheetManager
import dotenv

dotenv.load_dotenv()


def main():
    """Main function to handle sheet management operations."""
    if len(sys.argv) < 2:
        print("Usage: python manage_sheets.py <command>")
        print("Commands:")
        print("  stats      - Show sheet statistics")
        print("  list       - List all monthly sheets")
        print("  url <date> - Get URL for specific date (YYYY-MM-DD)")
        return

    command = sys.argv[1].lower()

    try:
        sheet_manager = SheetManager()

        if not sheet_manager.service:
            print("❌ Google Sheets service not initialized")
            print("Please check your credentials and configuration")
            return

        if command == "stats":
            print("📊 Sheet Statistics:")
            stats = sheet_manager.get_sheet_statistics()
            pprint(stats)

        elif command == "list":
            print("📋 All Monthly Sheets:")
            monthly_sheets = sheet_manager.get_all_monthly_sheets()
            for key, sheet_name in monthly_sheets.items():
                print(f"  {key}: {sheet_name}")

        elif command == "url":
            if len(sys.argv) < 3:
                print("❌ Please provide a date in YYYY-MM-DD format")
                return

            try:
                date_str = sys.argv[2]
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                url = sheet_manager.get_sheet_url(date_obj)
                if url:
                    print(f"📄 Sheet URL for {date_str}: {url}")
                else:
                    print(f"❌ No sheet found for {date_str}")
            except ValueError:
                print("❌ Invalid date format. Please use YYYY-MM-DD")

        else:
            print(f"❌ Unknown command: {command}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
