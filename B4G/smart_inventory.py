# -*- encoding: utf-8 -*-


from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json
import math
from collections import defaultdict
from .models import *

class SmartInventoryManager:
    """
    Smart Inventory Management System
    Analyzes sales patterns and provides intelligent restocking recommendations
    """
    
    def __init__(self):
        self.today = timezone.now().date()
        self.current_month = self.today.month
        self.current_year = self.today.year
        
    def calculate_sales_velocity(self, book_id, days=30):
        """
        Calculate average daily sales velocity for a book
        
        Args:
            book_id: ID of the book
            days: Number of days to analyze (default 30)
            
        Returns:
            dict: Sales velocity data
        """
        end_date = self.today
        start_date = end_date - timedelta(days=days)
        
        # Get sales data from BillDetails
        sales_data = Billdetails.objects.filter(
            id_book_id=book_id,
            id_bill__date__gte=start_date,
            id_bill__date__lte=end_date
        ).aggregate(
            total_sold=Sum('quantity'),
            num_transactions=Count('id'),
            avg_per_transaction=Avg('quantity')
        )
        
        total_sold = sales_data['total_sold'] or 0
        num_transactions = sales_data['num_transactions'] or 0
        avg_per_transaction = sales_data['avg_per_transaction'] or 0
        
        # Calculate daily velocity
        daily_velocity = total_sold / days if days > 0 else 0
        
        return {
            'book_id': book_id,
            'period_days': days,
            'total_sold': total_sold,
            'daily_velocity': round(daily_velocity, 2),
            'weekly_velocity': round(daily_velocity * 7, 2),
            'monthly_velocity': round(daily_velocity * 30, 2),
            'transactions_count': num_transactions,
            'avg_per_transaction': round(float(avg_per_transaction), 2),
            'analysis_date': self.today.isoformat()
        }
    
    def analyze_seasonal_patterns(self, book_id, years=2):
        """
        Analyze seasonal sales patterns for a book
        
        Args:
            book_id: ID of the book
            years: Number of years to analyze
            
        Returns:
            dict: Seasonal pattern analysis
        """
        end_date = self.today
        start_date = end_date - timedelta(days=years * 365)
        
        # Get monthly sales data
        monthly_sales = defaultdict(list)
        
        bills = Billdetails.objects.filter(
            id_book_id=book_id,
            id_bill__date__gte=start_date,
            id_bill__date__lte=end_date
        ).select_related('id_bill')
        
        for bill_detail in bills:
            month = bill_detail.id_bill.date.month
            quantity = int(bill_detail.quantity) if bill_detail.quantity else 0
            monthly_sales[month].append(quantity)
        
        # Calculate monthly averages
        seasonal_data = {}
        for month in range(1, 13):
            if monthly_sales[month]:
                avg_sales = sum(monthly_sales[month]) / len(monthly_sales[month])
                seasonal_data[month] = {
                    'month': month,
                    'avg_sales': round(avg_sales, 2),
                    'total_transactions': len(monthly_sales[month]),
                    'month_name': self._get_month_name(month)
                }
            else:
                seasonal_data[month] = {
                    'month': month,
                    'avg_sales': 0,
                    'total_transactions': 0,
                    'month_name': self._get_month_name(month)
                }
        
        # Calculate seasonal multiplier for current month
        current_month_avg = seasonal_data[self.current_month]['avg_sales']
        yearly_avg = sum(data['avg_sales'] for data in seasonal_data.values()) / 12
        
        seasonal_multiplier = current_month_avg / yearly_avg if yearly_avg > 0 else 1
        
        return {
            'book_id': book_id,
            'seasonal_data': seasonal_data,
            'current_month': self.current_month,
            'seasonal_multiplier': round(seasonal_multiplier, 2),
            'yearly_average': round(yearly_avg, 2),
            'peak_month': max(seasonal_data.keys(), key=lambda x: seasonal_data[x]['avg_sales']),
            'low_month': min(seasonal_data.keys(), key=lambda x: seasonal_data[x]['avg_sales'])
        }
    
    def calculate_supplier_lead_time(self, publisher_id):
        """
        Calculate average lead time for a supplier based on import history
        
        Args:
            publisher_id: ID of the publisher/supplier
            
        Returns:
            dict: Lead time analysis
        """
        # Get recent imports from this supplier
        recent_imports = Imports.objects.filter(
            id_pub_id=publisher_id,
            lastmodified__gte=self.today - timedelta(days=365)
        ).order_by('-lastmodified')[:10]
        
        if not recent_imports:
            return {
                'publisher_id': publisher_id,
                'avg_lead_time': 7,  # Default 7 days
                'min_lead_time': 5,
                'max_lead_time': 10,
                'confidence': 'low',
                'sample_size': 0
            }
        
        # For simplicity, we'll estimate lead time based on import frequency
        # In real scenario, you'd track order dates vs delivery dates
        lead_times = []
        for i in range(len(recent_imports) - 1):
            current_import = recent_imports[i]
            previous_import = recent_imports[i + 1]
            days_between = (current_import.lastmodified.date() - previous_import.lastmodified.date()).days
            if 1 <= days_between <= 90:  # Reasonable range
                lead_times.append(days_between)
        
        if lead_times:
            avg_lead_time = sum(lead_times) / len(lead_times)
            min_lead_time = min(lead_times)
            max_lead_time = max(lead_times)
            confidence = 'high' if len(lead_times) >= 5 else 'medium'
        else:
            # Default values
            avg_lead_time = 7
            min_lead_time = 5
            max_lead_time = 10
            confidence = 'low'
        
        return {
            'publisher_id': publisher_id,
            'avg_lead_time': round(avg_lead_time, 1),
            'min_lead_time': min_lead_time,
            'max_lead_time': max_lead_time,
            'confidence': confidence,
            'sample_size': len(lead_times)
        }
    
    def smart_restock_alert(self, book_id=None):
        """
        Generate smart restocking alerts for books
        
        Args:
            book_id: Specific book ID to analyze, or None for all books
            
        Returns:
            list: List of restock recommendations
        """
        recommendations = []
        
        if book_id:
            books_to_analyze = Books.objects.filter(id=book_id)
        else:
            # Analyze all books that have been sold in the last 90 days
            recent_sold_books = Billdetails.objects.filter(
                id_bill__date__gte=self.today - timedelta(days=90)
            ).values_list('id_book', flat=True).distinct()
            books_to_analyze = Books.objects.filter(id__in=recent_sold_books)
        
        for book in books_to_analyze:
            try:
                recommendation = self._analyze_book_restock_need(book)
                if recommendation:
                    recommendations.append(recommendation)
            except Exception as e:
                print(f"Error analyzing book {book.id}: {str(e)}")
                continue
        
        # Sort by urgency (highest priority first)
        recommendations.sort(key=lambda x: x['urgency_score'], reverse=True)
        
        return recommendations
    
    def _analyze_book_restock_need(self, book):
        """
        Analyze if a specific book needs restocking
        
        Args:
            book: Book object
            
        Returns:
            dict: Restock recommendation or None
        """
        # Get current stock level
        current_stock = self._get_current_stock(book.id)
        
        # Calculate sales velocity
        velocity_data = self.calculate_sales_velocity(book.id, days=30)
        daily_velocity = velocity_data['daily_velocity']
        
        # Get seasonal patterns
        seasonal_data = self.analyze_seasonal_patterns(book.id)
        seasonal_multiplier = seasonal_data['seasonal_multiplier']
        
        # Get supplier lead time
        lead_time_data = self.calculate_supplier_lead_time(book.id_pub.id)
        avg_lead_time = lead_time_data['avg_lead_time']
        
        # Apply seasonal adjustment to velocity
        adjusted_daily_velocity = daily_velocity * seasonal_multiplier
        
        # Calculate safety stock (1 week worth)
        safety_stock = adjusted_daily_velocity * 7
        
        # Calculate reorder point
        reorder_point = (adjusted_daily_velocity * avg_lead_time) + safety_stock
        
        # Calculate suggested order quantity (30 days worth)
        suggested_order_qty = adjusted_daily_velocity * 30
        
        # Calculate days until stockout
        days_until_stockout = current_stock / adjusted_daily_velocity if adjusted_daily_velocity > 0 else float('inf')
        
        # Determine urgency level
        urgency_score = self._calculate_urgency_score(
            current_stock, reorder_point, days_until_stockout, daily_velocity
        )
        
        # Only recommend if stock is below reorder point or high urgency
        if current_stock <= reorder_point or urgency_score >= 7:
            return {
                'book_id': book.id,
                'book_name': book.bookname or f"Book {book.id}",
                'publisher_name': book.id_pub.pubname if book.id_pub else "Unknown",
                'current_stock': current_stock,
                'reorder_point': round(reorder_point, 1),
                'suggested_order_qty': max(1, round(suggested_order_qty)),
                'daily_velocity': daily_velocity,
                'adjusted_daily_velocity': round(adjusted_daily_velocity, 2),
                'seasonal_multiplier': seasonal_multiplier,
                'lead_time_days': avg_lead_time,
                'safety_stock': round(safety_stock, 1),
                'days_until_stockout': round(days_until_stockout, 1) if days_until_stockout != float('inf') else None,
                'urgency_score': urgency_score,
                'urgency_level': self._get_urgency_level(urgency_score),
                'recommendation_reason': self._get_recommendation_reason(
                    current_stock, reorder_point, days_until_stockout, urgency_score
                ),
                'analysis_date': self.today.isoformat()
            }
        
        return None
    
    def _get_current_stock(self, book_id):
        """Get current stock level for a book"""
        stock_data = Bookshelves.objects.filter(id_book_id=book_id).aggregate(
            total_stock=Sum('quantity')
        )
        
        total_stock = 0
        if stock_data['total_stock']:
            try:
                # Handle quantity as string
                for bookshelf in Bookshelves.objects.filter(id_book_id=book_id):
                    if bookshelf.quantity:
                        total_stock += int(bookshelf.quantity)
            except (ValueError, TypeError):
                total_stock = 0
        
        return total_stock
    
    def _calculate_urgency_score(self, current_stock, reorder_point, days_until_stockout, daily_velocity):
        """Calculate urgency score from 1-10"""
        if daily_velocity == 0:
            return 1
        
        # Base score on how far below reorder point
        if current_stock <= 0:
            return 10
        elif current_stock <= reorder_point * 0.5:
            return 9
        elif current_stock <= reorder_point * 0.7:
            return 8
        elif current_stock <= reorder_point:
            return 7
        
        # Factor in days until stockout
        if days_until_stockout <= 3:
            return max(9, (10 - days_until_stockout))
        elif days_until_stockout <= 7:
            return 6
        elif days_until_stockout <= 14:
            return 4
        else:
            return 2
    
    def _get_urgency_level(self, urgency_score):
        """Convert urgency score to human-readable level"""
        if urgency_score >= 9:
            return "CRITICAL"
        elif urgency_score >= 7:
            return "HIGH"
        elif urgency_score >= 5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_recommendation_reason(self, current_stock, reorder_point, days_until_stockout, urgency_score):
        """Generate human-readable recommendation reason"""
        reasons = []
        
        if current_stock <= 0:
            reasons.append("Out of stock")
        elif current_stock <= reorder_point * 0.5:
            reasons.append("Stock critically low")
        elif current_stock <= reorder_point:
            reasons.append("Below reorder point")
        
        if days_until_stockout and days_until_stockout <= 7:
            reasons.append(f"Will run out in {round(days_until_stockout, 1)} days")
        
        if urgency_score >= 8:
            reasons.append("High sales velocity")
        
        return "; ".join(reasons) if reasons else "Preventive restocking recommended"
    
    def _get_month_name(self, month_num):
        """Get month name from number"""
        months = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        return months.get(month_num, f'Month {month_num}')
    
    def generate_inventory_report(self):
        """Generate comprehensive inventory analysis report"""
        all_recommendations = self.smart_restock_alert()
        
        # Summary statistics
        total_books_analyzed = len(all_recommendations)
        critical_alerts = len([r for r in all_recommendations if r['urgency_level'] == 'CRITICAL'])
        high_alerts = len([r for r in all_recommendations if r['urgency_level'] == 'HIGH'])
        
        # Calculate total suggested order value (simplified)
        total_order_value = sum(r['suggested_order_qty'] for r in all_recommendations)
        
        report = {
            'generated_date': self.today.isoformat(),
            'summary': {
                'total_books_analyzed': total_books_analyzed,
                'critical_alerts': critical_alerts,
                'high_alerts': high_alerts,
                'medium_alerts': len([r for r in all_recommendations if r['urgency_level'] == 'MEDIUM']),
                'low_alerts': len([r for r in all_recommendations if r['urgency_level'] == 'LOW']),
                'total_suggested_order_qty': total_order_value
            },
            'recommendations': all_recommendations[:20],  # Top 20 most urgent
            'alerts_by_publisher': self._group_alerts_by_publisher(all_recommendations)
        }
        
        return report
    
    def _group_alerts_by_publisher(self, recommendations):
        """Group recommendations by publisher for bulk ordering"""
        publisher_groups = defaultdict(list)
        
        for rec in recommendations:
            publisher_name = rec['publisher_name']
            publisher_groups[publisher_name].append(rec)
        
        # Sort publishers by number of alerts
        sorted_publishers = sorted(
            publisher_groups.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        
        return dict(sorted_publishers)


# Utility functions for use in views
def get_smart_inventory_alerts():
    """Quick function to get current inventory alerts"""
    manager = SmartInventoryManager()
    return manager.smart_restock_alert()

def get_book_restock_recommendation(book_id):
    """Get restock recommendation for a specific book"""
    manager = SmartInventoryManager()
    recommendations = manager.smart_restock_alert(book_id=book_id)
    return recommendations[0] if recommendations else None

def get_inventory_dashboard_data():
    """Get inventory data for dashboard widgets"""
    manager = SmartInventoryManager()
    report = manager.generate_inventory_report()
    
    return {
        'critical_count': report['summary']['critical_alerts'],
        'high_count': report['summary']['high_alerts'],
        'total_alerts': report['summary']['total_books_analyzed'],
        'top_urgent_books': report['recommendations'][:5]
    }
