#!/usr/bin/env python3
"""
API Test Script for AMTC Lab Management System
Tests all available API endpoints and displays results
"""

import json
import urllib.request
import urllib.error
import sys
from datetime import datetime

def test_api_endpoint(url, endpoint_name):
    """Test a single API endpoint"""
    try:
        print(f"\n📡 Testing {endpoint_name}...")
        print(f"   URL: {url}")
        
        with urllib.request.urlopen(url, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                print(f"   ✅ SUCCESS - Status: {response.status}")
                
                # Display relevant information based on endpoint
                if 'items' in data:
                    print(f"   📦 Items found: {len(data['items'])}")
                elif 'current' in data and 'archived' in data:
                    print(f"   📦 Current items: {data['current']['count']}")
                    print(f"   📦 Archived items: {data['archived']['count']}")
                elif 'data' in data and 'notification_summary' in data['data']:
                    summary = data['data']['notification_summary']
                    print(f"   📦 Total items: {summary['total_items']}")
                    print(f"   ⚠️  Overdue: {summary['overdue_count']}")
                    print(f"   ⏰ Due soon: {summary['due_soon_count']}")
                elif 'service' in data:
                    print(f"   🏥 Service: {data['service']}")
                    print(f"   📊 Version: {data['version']}")
                
                return True
            else:
                print(f"   ❌ FAILED - Status: {response.status}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"   ❌ HTTP ERROR - Status: {e.code}")
        try:
            error_data = json.loads(e.read().decode('utf-8'))
            print(f"   📝 Error: {error_data.get('error', 'Unknown error')}")
        except:
            pass
        return False
    except urllib.error.URLError as e:
        print(f"   ❌ CONNECTION ERROR - {e.reason}")
        return False
    except Exception as e:
        print(f"   ❌ UNEXPECTED ERROR - {e}")
        return False

def main():
    """Run all API tests"""
    base_url = "http://localhost:8084"
    
    print("🔬 AMTC Lab Management System - API Test Suite")
    print("=" * 55)
    print(f"🌐 Testing API server at: {base_url}")
    print(f"🕒 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define all endpoints to test
    endpoints = [
        ("/api/health", "Health Check"),
        ("/api/inventory/current", "Current Inventory"),
        ("/api/inventory/archived", "Archived Inventory"),
        ("/api/inventory/all", "All Inventory Data"),
        ("/api/inventory/notifications", "Notification Data")
    ]
    
    results = []
    
    for endpoint, name in endpoints:
        url = base_url + endpoint
        success = test_api_endpoint(url, name)
        results.append((name, success))
    
    # Summary
    print("\n" + "=" * 55)
    print("📊 TEST SUMMARY")
    print("=" * 55)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check if:")
        print("   1. The API server is running (run start-api-server.bat)")
        print("   2. Port 8084 is available")
        print("   3. No firewall is blocking the connection")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        
        print(f"\n🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n" + "=" * 55)
        
        if sys.platform.startswith('win'):
            input("\nPress Enter to close...")
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        sys.exit(1)