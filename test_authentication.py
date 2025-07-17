"""
Test suite for API authentication middleware.
Tests X-API-KEY header validation for protected routes.
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import AppConfig


class AuthenticationTestSuite:
    """Test suite for API authentication."""

    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.valid_api_key = os.getenv("API_KEY", "test-api-key")
        self.invalid_api_key = "invalid-key-123"
        self.test_results = {"passed": 0, "failed": 0, "errors": []}

    def run_all_tests(self):
        """Run all authentication tests."""
        print("🔐 AUTHENTICATION MIDDLEWARE TEST SUITE")
        print("=" * 60)

        try:
            # Test health endpoint (should be accessible without auth)
            self.test_health_endpoint_no_auth_required()

            # Test API endpoints without authentication
            self.test_api_endpoints_without_auth()

            # Test API endpoints with invalid authentication
            self.test_api_endpoints_with_invalid_auth()

            # Test API endpoints with valid authentication
            self.test_api_endpoints_with_valid_auth()

            # Test authentication error responses
            self.test_authentication_error_responses()

        except Exception as e:
            print(f"❌ Test suite failed with error: {e}")
            self.test_results["errors"].append(f"Test suite error: {e}")

        self._print_summary()

    def test_health_endpoint_no_auth_required(self):
        """Test that health endpoint doesn't require authentication."""
        print("\n🏥 Testing Health Endpoint (No Auth Required)")
        print("-" * 50)

        try:
            response = requests.get(f"{self.base_url}/health")

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    print("✅ Health endpoint accessible without authentication")
                    self.test_results["passed"] += 1
                else:
                    print("❌ Health endpoint returned unexpected response")
                    self.test_results["failed"] += 1
            else:
                print(f"❌ Health endpoint returned status {response.status_code}")
                self.test_results["failed"] += 1

        except Exception as e:
            print(f"❌ Health endpoint test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Health endpoint error: {e}")

    def test_api_endpoints_without_auth(self):
        """Test that API endpoints require authentication."""
        print("\n🚫 Testing API Endpoints Without Authentication")
        print("-" * 50)

        test_cases = [
            ("POST", "/api/v1/log", {"text": "Test SMS"}),
            ("POST", "/api/v1/test-parser", {"text": "Test SMS"}),
            ("GET", "/api/v1/stats", None),
            ("GET", "/api/v1/stats/July-2025", None),
            ("GET", "/api/v1/sheets/July-2025", None),
        ]

        for method, endpoint, data in test_cases:
            try:
                url = f"{self.base_url}{endpoint}"

                if method == "POST":
                    response = requests.post(url, json=data)
                else:
                    response = requests.get(url)

                if response.status_code == 403:
                    response_data = response.json()
                    if response_data.get(
                        "error"
                    ) == "Authentication required" and "X-API-KEY" in response_data.get(
                        "message", ""
                    ):
                        print(
                            f"✅ {method} {endpoint} - correctly requires authentication"
                        )
                        self.test_results["passed"] += 1
                    else:
                        print(f"❌ {method} {endpoint} - wrong error message")
                        self.test_results["failed"] += 1
                else:
                    print(
                        f"❌ {method} {endpoint} - expected 403, got {response.status_code}"
                    )
                    self.test_results["failed"] += 1

            except Exception as e:
                print(f"❌ {method} {endpoint} - test failed: {e}")
                self.test_results["failed"] += 1
                self.test_results["errors"].append(f"{method} {endpoint} error: {e}")

    def test_api_endpoints_with_invalid_auth(self):
        """Test API endpoints with invalid authentication."""
        print("\n🔑 Testing API Endpoints With Invalid Authentication")
        print("-" * 50)

        test_cases = [
            ("POST", "/api/v1/log", {"text": "Test SMS"}),
            ("POST", "/api/v1/test-parser", {"text": "Test SMS"}),
            ("GET", "/api/v1/stats", None),
        ]

        headers = {"X-API-KEY": self.invalid_api_key}

        for method, endpoint, data in test_cases:
            try:
                url = f"{self.base_url}{endpoint}"

                if method == "POST":
                    response = requests.post(url, json=data, headers=headers)
                else:
                    response = requests.get(url, headers=headers)

                if response.status_code == 403:
                    response_data = response.json()
                    if response_data.get(
                        "error"
                    ) == "Authentication failed" and "Invalid API key" in response_data.get(
                        "message", ""
                    ):
                        print(
                            f"✅ {method} {endpoint} - correctly rejects invalid API key"
                        )
                        self.test_results["passed"] += 1
                    else:
                        print(
                            f"❌ {method} {endpoint} - wrong error message for invalid key"
                        )
                        self.test_results["failed"] += 1
                else:
                    print(
                        f"❌ {method} {endpoint} - expected 403, got {response.status_code}"
                    )
                    self.test_results["failed"] += 1

            except Exception as e:
                print(f"❌ {method} {endpoint} - test failed: {e}")
                self.test_results["failed"] += 1
                self.test_results["errors"].append(
                    f"{method} {endpoint} invalid auth error: {e}"
                )

    def test_api_endpoints_with_valid_auth(self):
        """Test API endpoints with valid authentication."""
        print("\n✅ Testing API Endpoints With Valid Authentication")
        print("-" * 50)

        headers = {"X-API-KEY": self.valid_api_key}

        # Test endpoints that should work with valid auth
        test_cases = [
            ("POST", "/api/v1/test-parser", {"text": "Test SMS"}),
            ("GET", "/api/v1/stats", None),
        ]

        for method, endpoint, data in test_cases:
            try:
                url = f"{self.base_url}{endpoint}"

                if method == "POST":
                    response = requests.post(url, json=data, headers=headers)
                else:
                    response = requests.get(url, headers=headers)

                # We expect these to NOT return 403 (authentication should pass)
                if response.status_code != 403:
                    print(
                        f"✅ {method} {endpoint} - authentication passed (status: {response.status_code})"
                    )
                    self.test_results["passed"] += 1
                else:
                    print(f"❌ {method} {endpoint} - valid auth rejected")
                    self.test_results["failed"] += 1

            except Exception as e:
                print(f"❌ {method} {endpoint} - test failed: {e}")
                self.test_results["failed"] += 1
                self.test_results["errors"].append(
                    f"{method} {endpoint} valid auth error: {e}"
                )

    def test_authentication_error_responses(self):
        """Test authentication error response formats."""
        print("\n📋 Testing Authentication Error Response Formats")
        print("-" * 50)

        try:
            # Test missing API key response format
            response = requests.get(f"{self.base_url}/api/v1/stats")

            if response.status_code == 403:
                data = response.json()
                required_fields = ["success", "error", "message"]

                if all(field in data for field in required_fields):
                    if (
                        data["success"] is False
                        and data["error"] == "Authentication required"
                        and "X-API-KEY" in data["message"]
                    ):
                        print("✅ Missing API key error response format is correct")
                        self.test_results["passed"] += 1
                    else:
                        print("❌ Missing API key error response content is incorrect")
                        self.test_results["failed"] += 1
                else:
                    print("❌ Missing API key error response missing required fields")
                    self.test_results["failed"] += 1
            else:
                print(
                    f"❌ Expected 403 for missing API key, got {response.status_code}"
                )
                self.test_results["failed"] += 1

            # Test invalid API key response format
            headers = {"X-API-KEY": self.invalid_api_key}
            response = requests.get(f"{self.base_url}/api/v1/stats", headers=headers)

            if response.status_code == 403:
                data = response.json()

                if (
                    data.get("success") is False
                    and data.get("error") == "Authentication failed"
                    and "Invalid API key" in data.get("message", "")
                ):
                    print("✅ Invalid API key error response format is correct")
                    self.test_results["passed"] += 1
                else:
                    print("❌ Invalid API key error response content is incorrect")
                    self.test_results["failed"] += 1
            else:
                print(
                    f"❌ Expected 403 for invalid API key, got {response.status_code}"
                )
                self.test_results["failed"] += 1

        except Exception as e:
            print(f"❌ Error response format test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Error response format test: {e}")

    def _print_summary(self):
        """Print test results summary."""
        print("\n" + "=" * 60)
        print("🔐 AUTHENTICATION TEST RESULTS SUMMARY")
        print("=" * 60)

        total_tests = self.test_results["passed"] + self.test_results["failed"]
        success_rate = (
            (self.test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
        )

        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {success_rate:.1f}%")

        if self.test_results["errors"]:
            print(f"\n🚨 Errors encountered:")
            for error in self.test_results["errors"]:
                print(f"   • {error}")

        print("\n" + "=" * 60)

        if self.test_results["failed"] == 0:
            print("🎉 All authentication tests passed!")
        else:
            print("⚠️  Some authentication tests failed. Check the details above.")


def main():
    """Main function to run authentication tests."""
    # Check if server is running
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code != 200:
            print(
                "❌ Server is not responding correctly. Please start the Flask app first."
            )
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Please start the Flask app first.")
        print("   Run: python app.py")
        return

    # Check if API key is set
    if not os.getenv("API_KEY"):
        print("⚠️  API_KEY environment variable not set. Using default 'test-api-key'")
        os.environ["API_KEY"] = "test-api-key"

    # Run tests
    test_suite = AuthenticationTestSuite()
    test_suite.run_all_tests()


if __name__ == "__main__":
    main()
