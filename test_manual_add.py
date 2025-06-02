#!/usr/bin/env python
"""
Quick test script to manually add a book to session for testing Create Bill functionality
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Books4Geeks.settings')
django.setup()

from django.test import Client
from django.contrib.sessions.backends.db import SessionStore
from B4G.models import Books

def test_add_book_to_session():
    # Create a test client
    client = Client()
    
    # Get the first book
    book = Books.objects.first()
    if not book:
        print("No books found in database")
        return
    
    print(f"Adding book: {book.description} (ID: {book.id}, Price: ${book.price})")
    
    # Simulate a POST request to add manual barcode
    response = client.post('/bills/scan_barcode/', {
        'action': 'add_manual_barcode',
        'barcode_number': book.barcode_number
    })
    
    print(f"Response status: {response.status_code}")
    if response.status_code == 302:
        print("Redirect occurred (likely successful)")
    
    # Check the session
    session = client.session
    scanned_books = session.get('scanned_books', [])
    print(f"Books in session: {len(scanned_books)}")
    
    for i, book_data in enumerate(scanned_books):
        print(f"  Book {i+1}: {book_data['description']} - Price: ${book_data['price']} - Qty: {book_data['quantity']}")
    
    return client

if __name__ == "__main__":
    test_add_book_to_session()
