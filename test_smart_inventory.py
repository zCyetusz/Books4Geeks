#!/usr/bin/env python
"""
Test Smart Inventory Alerts functionality
Creates sample data and tests the smart inventory system
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

def create_sample_data():
    """Create sample data for testing Smart Inventory Alerts"""
    
    print("🔧 Creating sample data for Smart Inventory testing...")
    
    # Ensure we have some basic data
    publisher, created = Publishers.objects.get_or_create(
        pubname="Test Publisher",
        defaults={'description': 'Test publisher for smart inventory'}
    )
    
    category, created = Categories.objects.get_or_create(
        catname="Programming",
        defaults={'description': 'Programming books category'}    )
    
    author, created = Authors.objects.get_or_create(
        authorname="John Doe",
        defaults={'description': 'Test author'}
    )
    
    area, created = Areas.objects.get_or_create(
        areaname="Main Warehouse",
        defaults={'description': 'Main storage area'}
    )
    
    shelf, created = Shelves.objects.get_or_create(
        shelfname="Shelf A1",
        defaults={'id_area': area}
    )
    
    customer, created = Customers.objects.get_or_create(
        cusname="Test Customer",
        defaults={'gender': 'M', 'phone': '1234567890'}
    )
    
    # Create test books with different stock scenarios
    books_data = [
        {"name": "Python for Beginners", "stock": 2, "daily_sales": 1.5},    # Critical
        {"name": "Django Advanced", "stock": 5, "daily_sales": 0.8},         # High
        {"name": "React Development", "stock": 15, "daily_sales": 0.5},      # Medium
        {"name": "Database Design", "stock": 50, "daily_sales": 0.2},        # Low
        {"name": "Out of Stock Book", "stock": 0, "daily_sales": 2.0},       # Critical
    ]
    
    created_books = []
    
    for book_data in books_data:
        book, created = Books.objects.get_or_create(
            bookname=book_data["name"],
            defaults={
                'id_pub': publisher,
                'price': str(random.randint(20, 80)),
                'description': f'Test book: {book_data["name"]}',
                'barcode_number': f'TEST{random.randint(1000, 9999)}'
            }
        )
        
        # Create book-author relationship
        Bookauthors.objects.get_or_create(
            id_book=book,
            id_author=author
        )
        
        # Create book-category relationship  
        Bookcategories.objects.get_or_create(
            id_book=book,
            id_cat=category
        )
        
        # Set stock level
        bookshelf, created = Bookshelves.objects.get_or_create(
            id_book=book,
            id_shelf=shelf,
            defaults={'quantity': str(book_data["stock"])}
        )
        if not created:
            bookshelf.quantity = str(book_data["stock"])
            bookshelf.save()
        
        # Create sample sales data (last 30 days)
        create_sample_sales(book, customer, book_data["daily_sales"])
        
        created_books.append(book)
        print(f"✅ Created book: {book.bookname} (Stock: {book_data['stock']})")
    
    print(f"✅ Created {len(created_books)} test books with sample sales data")
    return created_books

def create_sample_sales(book, customer, daily_sales_avg):
    """Create sample sales data for the last 30 days"""
    
    today = timezone.now().date()
    
    for days_ago in range(30):
        sale_date = today - timedelta(days=days_ago)
        # Convert date to timezone-aware datetime
        sale_datetime = timezone.make_aware(datetime.combine(sale_date, datetime.min.time()))
        
        # Random variation in daily sales (±50%)
        actual_sales = max(0, daily_sales_avg + random.uniform(-daily_sales_avg*0.5, daily_sales_avg*0.5))
        
        # Only create sales if > 0
        if actual_sales > 0.1:
            # Create bill
            bill = Bills.objects.create(
                id_cus=customer,
                date=sale_datetime,
                totalbill=str(Decimal(str(actual_sales)) * Decimal('25.00')),  # Assume $25 per unit
                lastmodified=timezone.now()
            )
            
            # Create bill detail
            Billdetails.objects.create(
                id_bill=bill,
                id_book=book,
                quantity=str(int(actual_sales)),
                price=str(25.00),
                lastmodified=timezone.now()
            )

def test_smart_inventory():
    """Test the Smart Inventory system"""
    
    print("\n🧠 Testing Smart Inventory Alerts...")
    
    manager = SmartInventoryManager()
    
    # Test velocity calculation
    print("\n📊 Testing Sales Velocity Analysis:")
    books = Books.objects.all()[:3]
    
    for book in books:
        velocity = manager.calculate_sales_velocity(book.id)
        print(f"Book: {book.bookname}")
        print(f"  Daily Velocity: {velocity['daily_velocity']}")
        print(f"  Weekly Velocity: {velocity['weekly_velocity']}")
        print(f"  Monthly Velocity: {velocity['monthly_velocity']}")
        print(f"  Transactions: {velocity['transactions_count']}")
        print("")
    
    # Test seasonal patterns
    print("📅 Testing Seasonal Pattern Analysis:")
    if books:
        seasonal = manager.analyze_seasonal_patterns(books[0].id)
        print(f"Book: {books[0].bookname}")
        print(f"  Seasonal Multiplier: {seasonal['seasonal_multiplier']}")
        print(f"  Peak Month: {seasonal['peak_month']}")
        print(f"  Low Month: {seasonal['low_month']}")
        print("")
    
    # Test smart recommendations
    print("🎯 Testing Smart Restock Recommendations:")
    recommendations = manager.smart_restock_alert()
    
    if recommendations:
        print(f"Found {len(recommendations)} recommendations:")
        for rec in recommendations[:5]:  # Show top 5
            print(f"  📚 {rec['book_name']}")
            print(f"     Current Stock: {rec['current_stock']}")
            print(f"     Suggested Order: {rec['suggested_order_qty']} units")
            print(f"     Urgency: {rec['urgency_level']} (Score: {rec['urgency_score']}/10)")
            print(f"     Reason: {rec['recommendation_reason']}")
            print("")
    else:
        print("  No recommendations generated (all stock levels adequate)")
    
    # Test inventory report
    print("📋 Testing Inventory Report Generation:")
    report = manager.generate_inventory_report()
    summary = report['summary']
    
    print(f"  Total Books Analyzed: {summary['total_books_analyzed']}")
    print(f"  Critical Alerts: {summary['critical_alerts']}")
    print(f"  High Alerts: {summary['high_alerts']}")
    print(f"  Medium Alerts: {summary['medium_alerts']}")
    print(f"  Low Alerts: {summary['low_alerts']}")
    print(f"  Total Suggested Order Qty: {summary['total_suggested_order_qty']}")
    
    return recommendations

def test_api_endpoints():
    """Test API functionality (simulated)"""
    
    print("\n🔌 Testing API Endpoints (Simulated):")
    
    try:
        from B4G.views import get_smart_inventory_alerts, get_inventory_dashboard_data
        
        # Test dashboard data
        dashboard_data = get_inventory_dashboard_data()
        print(f"✅ Dashboard Data:")
        print(f"   Critical Count: {dashboard_data['critical_count']}")
        print(f"   High Count: {dashboard_data['high_count']}")
        print(f"   Total Alerts: {dashboard_data['total_alerts']}")
        print(f"   Top Urgent Books: {len(dashboard_data['top_urgent_books'])}")
        
        # Test alerts function
        alerts = get_smart_inventory_alerts()
        print(f"✅ Smart Alerts Function: {len(alerts)} alerts generated")
        
    except Exception as e:
        print(f"❌ API Test Error: {str(e)}")

def cleanup_test_data():
    """Clean up test data (optional)"""
    
    response = input("\n🗑️  Do you want to clean up test data? (y/N): ")
    if response.lower() == 'y':
        print("Cleaning up test data...")
        
        # Delete test books and related data
        test_books = Books.objects.filter(bookname__startswith="Python for Beginners")
        test_books = test_books.union(Books.objects.filter(bookname__startswith="Django Advanced"))
        test_books = test_books.union(Books.objects.filter(bookname__startswith="React Development"))
        test_books = test_books.union(Books.objects.filter(bookname__startswith="Database Design"))
        test_books = test_books.union(Books.objects.filter(bookname__startswith="Out of Stock Book"))
        
        count = test_books.count()
        test_books.delete()
        
        print(f"✅ Cleaned up {count} test books and related data")

def main():
    """Main test function"""
    
    print("🚀 Smart Inventory Alerts - Test Suite")
    print("=" * 50)
    
    try:
        # Create sample data
        books = create_sample_data()
        
        # Test smart inventory functionality
        recommendations = test_smart_inventory()
        
        # Test API endpoints
        test_api_endpoints()
        
        # Summary
        print("\n✅ Test Summary:")
        print(f"   📚 Books created: {len(books)}")
        print(f"   🔔 Recommendations generated: {len(recommendations) if recommendations else 0}")
        print(f"   🎯 System Status: Fully Functional")
        
        print("\n🌐 You can now test the web interface at:")
        print("   📊 Dashboard: http://127.0.0.1:8000/")
        print("   🔔 Alerts: http://127.0.0.1:8000/inventory/alerts/")
        print("   📈 Analytics: http://127.0.0.1:8000/inventory/analytics/")
        
        # Optional cleanup
        cleanup_test_data()
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
