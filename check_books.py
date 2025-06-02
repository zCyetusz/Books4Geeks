#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Books4Geeks.settings')
django.setup()

from B4G.models import Books

# Check books with barcodes
books_with_barcodes = Books.objects.filter(barcode_number__isnull=False).exclude(barcode_number='')
print(f"Books with barcodes: {books_with_barcodes.count()}")

if books_with_barcodes.exists():
    print("\nFirst 3 books with barcodes:")
    for book in books_with_barcodes[:3]:
        print(f"ID: {book.id}, Description: {book.description}, Barcode: {book.barcode_number}")
else:
    print("No books found with barcode numbers")
    
# Check all books
all_books = Books.objects.all()
print(f"\nTotal books in database: {all_books.count()}")

if all_books.exists():
    print("\nFirst 3 books (any):")
    for book in all_books[:3]:
        print(f"ID: {book.id}, Description: {book.description}, Barcode: {book.barcode_number or 'None'}")
