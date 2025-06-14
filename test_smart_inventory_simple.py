#!/usr/bin/env python
"""
Simple test for Smart Inventory Alerts functionality
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Books4Geeks.settings')
django.setup()

from django.utils import timezone
from B4G.models import *
from B4G.smart_inventory import SmartInventoryManager

def create_simple_test_data():
    """Create minimal test data"""
    print("🔧 Creating simple test data...")
    
    # Get or create basic entities
    publisher = Publishers.objects.first()
    if not publisher:
        publisher = Publishers.objects.create(
            pubname="Test Publisher",
            description="Test publisher for smart inventory"
        )
    
    customer = Customers.objects.first()
    if not customer:
        customer = Customers.objects.create(
            cusname="Test Customer",
            gender="M",
            phone="1234567890"
        )
    
    # Get books that have sales data
    books_with_sales = Books.objects.filter(
        billdetails__isnull=False
    ).distinct()[:3]
    
    if books_with_sales.exists():
        print(f"✅ Found {books_with_sales.count()} books with existing sales data")
        return list(books_with_sales)
    else:
        print("ℹ️ No books with sales data found. Create some sales first.")
        return []

def test_basic_functionality():
    """Test basic Smart Inventory functionality"""
    print("\n🧠 Testing Smart Inventory basic functionality...")
    
    try:
        manager = SmartInventoryManager()
        
        # Test 1: Get all recommendations
        recommendations = manager.smart_restock_alert()
        print(f"✅ Generated {len(recommendations)} recommendations")
        
        if recommendations:
            # Show top 3 recommendations
            print("\n📋 Top 3 Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"  {i}. {rec['book_name']}")
                print(f"     Stock: {rec['current_stock']} | Order: {rec['suggested_order_qty']}")
                print(f"     Urgency: {rec['urgency_level']} ({rec['urgency_score']}/10)")
        
        # Test 2: Generate report
        report = manager.generate_inventory_report()
        summary = report['summary']
        
        print(f"\n📊 Inventory Report Summary:")
        print(f"   Books Analyzed: {summary['total_books_analyzed']}")
        print(f"   Critical Alerts: {summary['critical_alerts']}")
        print(f"   High Alerts: {summary['high_alerts']}")
        print(f"   Total Order Qty: {summary['total_suggested_order_qty']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_individual_book():
    """Test individual book analysis"""
    print("\n📚 Testing individual book analysis...")
    
    try:
        # Get a book with some sales
        book = Books.objects.filter(billdetails__isnull=False).first()
        
        if not book:
            print("ℹ️ No books with sales data found")
            return False
        
        manager = SmartInventoryManager()
        
        # Test velocity calculation
        velocity = manager.calculate_sales_velocity(book.id)
        print(f"📈 Book: {book.bookname or f'Book {book.id}'}")
        print(f"   Daily Velocity: {velocity['daily_velocity']}")
        print(f"   Total Sold (30d): {velocity['total_sold']}")
        print(f"   Transactions: {velocity['transactions_count']}")
        
        # Test seasonal analysis
        seasonal = manager.analyze_seasonal_patterns(book.id)
        print(f"   Seasonal Multiplier: {seasonal['seasonal_multiplier']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_api_functions():
    """Test API helper functions"""
    print("\n🔌 Testing API functions...")
    
    try:
        from B4G.views import get_inventory_dashboard_data
        
        dashboard_data = get_inventory_dashboard_data()
        print("✅ Dashboard data retrieved:")
        print(f"   Critical: {dashboard_data['critical_count']}")
        print(f"   High: {dashboard_data['high_count']}")
        print(f"   Total: {dashboard_data['total_alerts']}")
        
        return True
        
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Smart Inventory Alerts - Quick Test")
    print("=" * 45)
    
    # Check if we have basic data
    books_count = Books.objects.count()
    sales_count = Billdetails.objects.count()
    
    print(f"📊 Current Data Status:")
    print(f"   Books: {books_count}")
    print(f"   Sales Records: {sales_count}")
    
    if books_count == 0:
        print("❌ No books found. Please add some books first.")
        return
    
    # Run tests
    test_results = []
    
    # Test 1: Basic functionality
    test_results.append(test_basic_functionality())
    
    # Test 2: Individual book analysis
    test_results.append(test_individual_book())
    
    # Test 3: API functions
    test_results.append(test_api_functions())
    
    # Summary
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"\n✅ Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Smart Inventory system is working.")
        print("\n🌐 You can test the web interface:")
        print("   📊 Dashboard: http://127.0.0.1:8000/")
        print("   🔔 Alerts: http://127.0.0.1:8000/inventory/alerts/")
        print("   📈 Analytics: http://127.0.0.1:8000/inventory/analytics/")
    else:
        print("⚠️ Some tests failed. Check the error messages above.")

if __name__ == '__main__':
    main()
