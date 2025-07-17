#!/usr/bin/env python3
"""
Comprehensive test suite for Finance SMS Logger Flask Application.
Tests SMS parser, Google Sheets integration, API endpoints, and caching functionality.
"""

import os
import sys
import json
import time
import requests
import csv
from datetime import datetime
from typing import Dict, Any, Optional
from pprint import pprint

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from sheet_manager import SheetManager
from sms_parser import get_transaction_info
from config import ValidationRules
import dotenv

dotenv.load_dotenv()


class TestSuite:
    """Comprehensive test suite for the Finance SMS Logger application."""

    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.sheet_manager = None
        self.test_results = {
            "parser": {"passed": 0, "failed": 0},
            "sheets": {"passed": 0, "failed": 0},
            "api": {"passed": 0, "failed": 0},
            "cache": {"passed": 0, "failed": 0},
            "auth": {"passed": 0, "failed": 0},
        }

    def run_all_tests(self):
        """Run all test suites."""
        print("🚀 STARTING COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print()

        # Test 1: SMS Parser
        self.test_sms_parser_direct()
        print()

        # Test 2: Google Sheets Integration
        self.test_google_sheets_integration()
        print()

        # Test 3: Monthly Spending Statistics
        self.test_monthly_spending_stats()
        print()

        # Test 4: Authentication Middleware
        self.test_authentication_middleware()
        print()

        # Test 5: API Endpoints
        self.test_api_endpoints()
        print()

        # Test 6: Performance and Caching
        self.test_performance_and_caching()
        print()

        # Summary
        self.print_test_summary()

    def test_sms_parser_direct(self):
        """Test the SMS parser directly with various message formats."""
        print("📱 TESTING SMS PARSER DIRECTLY")
        print("=" * 60)

        test_messages = [
            "INR 2000 debited from A/c no. XX3423 on 05-02-19 07:27:11 IST at ECS PAY. Avl Bal- INR 2343.23.",
            "Your a/c no. XX1234 has been credited with INR 5,000.00 on 10-03-23 through NEFT. Avl Bal: INR 12,435.50",
            "INR 1,500.00 spent on HDFC Card XX7890 at AMAZON RETAIL on 15-04-23. Avl limit: INR 35,000.00",
            "Your Paytm wallet was debited for Rs. 299.00 for payment to NETFLIX. Avl Bal: Rs. 1,211.50",
            "Rs.435.00 debited from your Slice Card for Swiggy order on 28-06-23. Outstanding: Rs.1,235.00",
        ]

        for i, sms in enumerate(test_messages, 1):
            print(f"\n🔍 Test {i}:")
            print(f"SMS: {sms}")

            try:
                transaction_info = get_transaction_info(sms)
                if transaction_info:
                    transaction_data = transaction_info.to_dict()
                    is_valid = ValidationRules.is_valid_transaction(
                        transaction_data, sms
                    )

                    print("✅ Parsed successfully:")
                    print(json.dumps(transaction_data, indent=2))
                    print(f"🔍 Valid transaction: {is_valid}")

                    self.test_results["parser"]["passed"] += 1
                else:
                    print("❌ Failed to parse SMS")
                    self.test_results["parser"]["failed"] += 1

            except Exception as e:
                print(f"❌ Error parsing SMS: {e}")
                self.test_results["parser"]["failed"] += 1

            print("-" * 50)

    def test_google_sheets_integration(self):
        """Test Google Sheets integration."""
        print("📊 TESTING GOOGLE SHEETS INTEGRATION")
        print("=" * 60)

        try:
            # Initialize sheet manager
            self.sheet_manager = SheetManager()

            # Check if services are initialized
            if not self.sheet_manager.service:
                print("❌ Google services not initialized")
                print("Please check your Google API credentials at:")
                print("   credentials/google-credentials.json")
                self.test_results["sheets"]["failed"] += 1
                return False

            print("✅ Google Sheets service initialized successfully")
            print(f"📄 Using shared workbook: {self.sheet_manager.shared_workbook_id}")
            self.test_results["sheets"]["passed"] += 1

            # Test creating a monthly sheet
            test_date = datetime(2025, 7, 14)
            print(f"\n🔍 Testing sheet creation for {test_date.strftime('%B %Y')}...")

            sheet_id = self.sheet_manager.get_or_create_monthly_sheet(test_date)
            print(f"✅ Sheet created/retrieved in workbook: {sheet_id}")
            self.test_results["sheets"]["passed"] += 1

            # Test transaction insertion
            test_sms = "INR 2000 debited from A/c no. XX3423 on 05-02-19 07:27:11 IST at ECS PAY. Avl Bal- INR 2343.23."
            print(f"\n🔍 Testing transaction insertion...")
            print(f"SMS: {test_sms}")

            # Parse transaction
            transaction_info = get_transaction_info(test_sms)
            if transaction_info:
                transaction_data = transaction_info.to_dict()
                success = self.sheet_manager.insert_transaction_data(
                    transaction_data, test_date
                )

                if success:
                    print("✅ Transaction inserted successfully")
                    sheet_url = self.sheet_manager.get_sheet_url(test_date)
                    print(f"📊 Sheet URL: {sheet_url}")
                    self.test_results["sheets"]["passed"] += 1
                else:
                    print("❌ Transaction insertion failed")
                    self.test_results["sheets"]["failed"] += 1
            else:
                print("❌ Failed to parse test SMS")
                self.test_results["sheets"]["failed"] += 1

            # Check sheet statistics
            stats = self.sheet_manager.get_sheet_statistics()
            print(f"\n📈 Sheet statistics: {stats}")

            return True

        except Exception as e:
            print(f"❌ Google Sheets integration test failed: {e}")
            self.test_results["sheets"]["failed"] += 1
            return False

    def test_monthly_spending_stats(self):
        """Test monthly spending statistics functionality."""
        print("💰 TESTING MONTHLY SPENDING STATISTICS")
        print("=" * 60)

        if not self.sheet_manager:
            print("❌ Sheet manager not initialized, skipping spending stats test")
            return

        # Test current month
        current_date = datetime.now()
        month = current_date.strftime("%B")
        year = current_date.year

        print(f"🔍 Testing spending stats for {month} {year}...")

        try:
            # First call (no cache)
            start_time = time.time()
            result = self.sheet_manager.get_month_spends(month, year)
            first_call_time = time.time() - start_time

            print(f"⏱️  First call took: {first_call_time:.3f} seconds")

            if "error" in result:
                print(f"⚠️  Sheet not found: {result['error']}")
                self.test_results["cache"]["failed"] += 1
            else:
                print("✅ Success!")
                print(f"📊 Total Spend: ₹{result['total_spend']:.2f}")
                print(f"📋 Categories: {len(result['categories'])}")

                if result["categories"]:
                    print("📈 Top 3 categories:")
                    sorted_cats = sorted(
                        result["categories"].items(),
                        key=lambda x: x[1]["amount"],
                        reverse=True,
                    )
                    for i, (cat, cat_data) in enumerate(sorted_cats[:3]):
                        print(f"   {i+1}. {cat}: ₹{cat_data['amount']:.2f}")

                self.test_results["cache"]["passed"] += 1

                # Test cache (second call)
                print("\n🔄 Testing cache (second call)...")
                start_time = time.time()
                result2 = self.sheet_manager.get_month_spends(month, year)
                second_call_time = time.time() - start_time

                print(f"⏱️  Second call took: {second_call_time:.3f} seconds")

                if result == result2:
                    print("✅ Cache working correctly - same results returned")
                    if second_call_time < first_call_time:
                        if second_call_time > 0:
                            print(
                                f"⚡ Cache speedup: {first_call_time/second_call_time:.1f}x faster"
                            )
                        else:
                            print("⚡ Cache speedup: Instant response!")
                    self.test_results["cache"]["passed"] += 1
                else:
                    print("❌ Cache not working - different results returned")
                    self.test_results["cache"]["failed"] += 1

                # Test cache statistics
                print(
                    f"\n📦 Cache entries: {len(self.sheet_manager.monthly_spends_cache)}"
                )
                for sheet_name, (
                    data,
                    timestamp,
                ) in self.sheet_manager.monthly_spends_cache.items():
                    cache_age = time.time() - timestamp
                    print(f"   🔸 {sheet_name}: cached {cache_age:.1f} seconds ago")

        except Exception as e:
            print(f"❌ Error testing spending stats: {e}")
            self.test_results["cache"]["failed"] += 1

    def test_authentication_middleware(self):
        """Test authentication middleware for API endpoints."""
        print("🔐 TESTING AUTHENTICATION MIDDLEWARE")
        print("=" * 60)

        # Check if API key is configured
        api_key = os.getenv("API_KEY")
        if not api_key:
            print(
                "⚠️  API_KEY environment variable not set. Using test key for testing."
            )
            api_key = "test-api-key"

        # Test 1: Health endpoint should not require auth
        print("\n🏥 Testing health endpoint (no auth required)...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health endpoint accessible without authentication")
                self.test_results["auth"]["passed"] += 1
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                self.test_results["auth"]["failed"] += 1
        except Exception as e:
            print(f"❌ Health endpoint error: {e}")
            self.test_results["auth"]["failed"] += 1

        # Test 2: API endpoints should require auth
        print("\n🚫 Testing API endpoints without authentication...")
        test_endpoints = [
            ("GET", "/api/v1/stats"),
            ("POST", "/api/v1/test-parser", {"text": "Test SMS"}),
        ]

        for method, endpoint, *data in test_endpoints:
            try:
                if method == "POST":
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        json=data[0] if data else None,
                        timeout=5,
                    )
                else:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)

                if response.status_code == 403:
                    print(f"✅ {method} {endpoint} correctly requires authentication")
                    self.test_results["auth"]["passed"] += 1
                else:
                    print(
                        f"❌ {method} {endpoint} should require auth (got {response.status_code})"
                    )
                    self.test_results["auth"]["failed"] += 1
            except Exception as e:
                print(f"❌ {method} {endpoint} test error: {e}")
                self.test_results["auth"]["failed"] += 1

        # Test 3: API endpoints with valid auth should work
        print("\n✅ Testing API endpoints with valid authentication...")
        headers = {"X-API-KEY": api_key}

        for method, endpoint, *data in test_endpoints:
            try:
                if method == "POST":
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        json=data[0] if data else None,
                        headers=headers,
                        timeout=5,
                    )
                else:
                    response = requests.get(
                        f"{self.base_url}{endpoint}", headers=headers, timeout=5
                    )

                # Should not get 403 with valid auth
                if response.status_code != 403:
                    print(f"✅ {method} {endpoint} accepts valid authentication")
                    self.test_results["auth"]["passed"] += 1
                else:
                    print(f"❌ {method} {endpoint} rejected valid auth")
                    self.test_results["auth"]["failed"] += 1
            except Exception as e:
                print(f"❌ {method} {endpoint} valid auth test error: {e}")
                self.test_results["auth"]["failed"] += 1

        # Test 4: API endpoints with invalid auth should fail
        print("\n🔑 Testing API endpoints with invalid authentication...")
        invalid_headers = {"X-API-KEY": "invalid-key-123"}

        try:
            response = requests.get(
                f"{self.base_url}/api/v1/stats", headers=invalid_headers, timeout=5
            )
            if response.status_code == 403:
                response_data = response.json()
                if "Authentication failed" in response_data.get("error", ""):
                    print("✅ Invalid API key correctly rejected")
                    self.test_results["auth"]["passed"] += 1
                else:
                    print("❌ Wrong error message for invalid key")
                    self.test_results["auth"]["failed"] += 1
            else:
                print(f"❌ Invalid key should return 403 (got {response.status_code})")
                self.test_results["auth"]["failed"] += 1
        except Exception as e:
            print(f"❌ Invalid auth test error: {e}")
            self.test_results["auth"]["failed"] += 1

    def test_api_endpoints(self):
        """Test API endpoints."""
        print("🌐 TESTING API ENDPOINTS")
        print("=" * 60)

        # Get API key for authenticated requests
        self.api_key = os.getenv("API_KEY", "test-api-key")
        self.auth_headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }

        # Test health check
        self._test_health_endpoint()

        # Test SMS logging endpoint
        self._test_sms_logging_endpoint()

        # Test parser test endpoint
        self._test_parser_endpoint()

        # Test sheet info endpoint
        self._test_sheet_info_endpoint()

        # Test stats endpoints
        self._test_stats_endpoints()

    def _test_health_endpoint(self):
        """Test health check endpoint."""
        print("\n🔍 Testing health endpoint...")

        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)

            if response.status_code == 200:
                print("✅ Health endpoint working")
                self.test_results["api"]["passed"] += 1
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                self.test_results["api"]["failed"] += 1

        except requests.exceptions.RequestException as e:
            print(f"❌ Health endpoint connection error: {e}")
            print("💡 Make sure Flask server is running: python app.py")
            self.test_results["api"]["failed"] += 1

    def _test_sms_logging_endpoint(self):
        """Test SMS logging endpoint."""
        print("\n🔍 Testing SMS logging endpoint...")

        test_payload = {
            "text": "INR 2000 debited from A/c no. XX3423 on 05-02-19 07:27:11 IST at ECS PAY. Avl Bal- INR 2343.23.",
            "date": "2025-07-14T10:30:00",
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/log",
                json=test_payload,
                headers=self.auth_headers,
                timeout=10,
            )

            if response.status_code == 200:
                print("✅ SMS logging endpoint working")
                result = response.json()
                print(f"📊 Response: {result['success']}")
                self.test_results["api"]["passed"] += 1
            else:
                print(f"❌ SMS logging endpoint failed: {response.status_code}")
                print(f"Response: {response.text}")
                self.test_results["api"]["failed"] += 1

        except requests.exceptions.RequestException as e:
            print(f"❌ SMS logging endpoint connection error: {e}")
            self.test_results["api"]["failed"] += 1

    def _test_parser_endpoint(self):
        """Test parser test endpoint."""
        print("\n🔍 Testing parser test endpoint...")

        test_payload = {
            "text": "INR 1500 debited from A/c no. XX1234 on 10-03-23 at AMAZON. Avl Bal: INR 5000"
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/test-parser",
                json=test_payload,
                headers=self.auth_headers,
                timeout=10,
            )

            if response.status_code == 200:
                print("✅ Parser test endpoint working")
                result = response.json()
                print(f"📊 Valid transaction: {result['data']['is_valid_transaction']}")
                self.test_results["api"]["passed"] += 1
            else:
                print(f"❌ Parser test endpoint failed: {response.status_code}")
                self.test_results["api"]["failed"] += 1

        except requests.exceptions.RequestException as e:
            print(f"❌ Parser test endpoint connection error: {e}")
            self.test_results["api"]["failed"] += 1

    def _test_sheet_info_endpoint(self):
        """Test sheet info endpoint."""
        print("\n🔍 Testing sheet info endpoint...")

        try:
            response = requests.get(
                f"{self.base_url}/api/v1/sheets/July-2025",
                headers=self.auth_headers,
                timeout=5,
            )

            if response.status_code == 200:
                print("✅ Sheet info endpoint working")
                result = response.json()
                print(f"📊 Sheet exists: {result['data']['exists']}")
                self.test_results["api"]["passed"] += 1
            else:
                print(f"❌ Sheet info endpoint failed: {response.status_code}")
                self.test_results["api"]["failed"] += 1

        except requests.exceptions.RequestException as e:
            print(f"❌ Sheet info endpoint connection error: {e}")
            self.test_results["api"]["failed"] += 1

    def _test_stats_endpoints(self):
        """Test stats endpoints."""
        print("\n🔍 Testing stats endpoints...")

        # Test current month stats
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/stats", headers=self.auth_headers, timeout=10
            )

            if response.status_code == 200:
                print("✅ Current month stats endpoint working")
                result = response.json()
                if result["success"]:
                    print(f"📊 Total spend: ₹{result['data']['total_spend']:.2f}")
                    print(f"📋 Categories: {result['data']['transaction_count']}")
                self.test_results["api"]["passed"] += 1
            else:
                print(f"❌ Current month stats endpoint failed: {response.status_code}")
                self.test_results["api"]["failed"] += 1

        except requests.exceptions.RequestException as e:
            print(f"❌ Current month stats endpoint connection error: {e}")
            self.test_results["api"]["failed"] += 1

        # Test specific month stats
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/stats/July-2025",
                headers=self.auth_headers,
                timeout=10,
            )

            if response.status_code == 200:
                print("✅ Specific month stats endpoint working")
                result = response.json()
                if result["success"]:
                    print(
                        f"📊 July 2025 total spend: ₹{result['data']['total_spend']:.2f}"
                    )
                self.test_results["api"]["passed"] += 1
            else:
                print(
                    f"❌ Specific month stats endpoint failed: {response.status_code}"
                )
                self.test_results["api"]["failed"] += 1

        except requests.exceptions.RequestException as e:
            print(f"❌ Specific month stats endpoint connection error: {e}")
            self.test_results["api"]["failed"] += 1

    def test_performance_and_caching(self):
        """Test performance and caching behavior."""
        print("⚡ TESTING PERFORMANCE AND CACHING")
        print("=" * 60)

        if not self.sheet_manager:
            print("❌ Sheet manager not initialized, skipping performance tests")
            return

        # Test multiple API calls to same endpoint
        print("\n🔍 Testing API endpoint caching...")

        endpoint = f"{self.base_url}/api/v1/stats"
        times = []

        for i in range(3):
            try:
                start_time = time.time()
                response = requests.get(endpoint, headers=self.auth_headers, timeout=10)
                end_time = time.time()

                if response.status_code == 200:
                    times.append(end_time - start_time)
                    print(f"   Call {i+1}: {end_time - start_time:.3f} seconds")
                else:
                    print(f"   Call {i+1}: Failed ({response.status_code})")

            except requests.exceptions.RequestException as e:
                print(f"   Call {i+1}: Connection error")

        if len(times) >= 2:
            print(f"\n📈 Performance analysis:")
            print(f"   First call: {times[0]:.3f} seconds")
            print(
                f"   Subsequent calls: {sum(times[1:])/len(times[1:]):.3f} seconds average"
            )

            if times[1] < times[0]:
                print("✅ Caching appears to be working")
                self.test_results["cache"]["passed"] += 1
            else:
                print("⚠️  Caching might not be working as expected")
                self.test_results["cache"]["failed"] += 1

    def test_csv_data(self):
        """Test with actual CSV data if available."""
        print("📄 TESTING WITH CSV DATA")
        print("=" * 60)

        csv_file = "sms-20250713002830.csv"

        if not os.path.exists(csv_file):
            print(f"❌ CSV file not found: {csv_file}")
            return

        try:
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                messages = [(row[1], row[-1]) for row in reader]

            print(f"📊 Found {len(messages)} messages in CSV")

            # Test first 5 messages
            for i, (date, sms) in enumerate(messages[:5], 1):
                print(f"\n🔍 CSV Test {i}:")
                print(f"Date: {date}")
                print(f"SMS: {sms}")

                try:
                    transaction_info = get_transaction_info(sms)
                    if transaction_info:
                        transaction_data = transaction_info.to_dict()
                        print("✅ Parsed successfully")
                        print(
                            f"   Amount: {transaction_data.get('transaction', {}).get('amount', 'N/A')}"
                        )
                        print(
                            f"   Account: {transaction_data.get('account', {}).get('number', 'N/A')}"
                        )
                        self.test_results["parser"]["passed"] += 1
                    else:
                        print("❌ Failed to parse")
                        self.test_results["parser"]["failed"] += 1

                except Exception as e:
                    print(f"❌ Error: {e}")
                    self.test_results["parser"]["failed"] += 1

                print("-" * 30)

        except Exception as e:
            print(f"❌ Error reading CSV: {e}")

    def print_test_summary(self):
        """Print comprehensive test summary."""
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)

        total_passed = sum(result["passed"] for result in self.test_results.values())
        total_failed = sum(result["failed"] for result in self.test_results.values())
        total_tests = total_passed + total_failed

        print(f"📈 Overall Results:")
        print(f"   ✅ Passed: {total_passed}")
        print(f"   ❌ Failed: {total_failed}")
        print(f"   📊 Total: {total_tests}")

        if total_tests > 0:
            success_rate = (total_passed / total_tests) * 100
            print(f"   🎯 Success Rate: {success_rate:.1f}%")

        print(f"\n📋 Category Breakdown:")
        for category, results in self.test_results.items():
            total = results["passed"] + results["failed"]
            if total > 0:
                rate = (results["passed"] / total) * 100
                print(
                    f"   {category.title()}: {results['passed']}/{total} ({rate:.1f}%)"
                )

        print("\n" + "=" * 80)
        if total_failed == 0:
            print("🎉 ALL TESTS PASSED!")
        else:
            print(f"⚠️  {total_failed} TESTS FAILED - CHECK LOGS ABOVE")
        print("=" * 80)


def main():
    """Run the comprehensive test suite."""
    test_suite = TestSuite()

    # Add CSV data test
    test_suite.test_csv_data()

    # Run all tests
    test_suite.run_all_tests()


if __name__ == "__main__":
    main()
