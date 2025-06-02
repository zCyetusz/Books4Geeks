from B4G.forms import LoginForm, RegistrationForm, UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count
from .models import *
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
from django.conf import settings
import os
from django.contrib.auth import views as auth_views
import json
import requests
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
from django.db.models import Count
import cv2
from pyzbar.pyzbar import decode
import numpy as np
import threading
import time
from django.apps import apps
from django.core import serializers
from datetime import datetime
from django.utils import timezone as django_timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Create your views here.

# Authentication
def register(request):
  if request.method == 'POST':
    form = RegistrationForm(request.POST)
    if form.is_saved():
      form.save()
      print('Account created successfully!')
      return redirect('/accounts/login/')
    else:
      print("Registration failed!")
  else:
    form = RegistrationForm()
  
  context = {'form': form}
  return render(request, 'accounts/register.html', context)
  
def register_v1(request):
  if request.method == 'POST':
    form = RegistrationForm(request.POST)
    if form.is_valid():
      form.save()
      print('Account created successfully!')
      return redirect('/accounts/login/')
    else:
      print("Registration failed!")
  else:
    form = RegistrationForm()
  
  context = {'form': form}
  return render(request, 'pages/examples/register.html', context)

def register_v2(request):
  if request.method == 'POST':
    form = RegistrationForm(request.POST)
    if form.is_valid():
      form.save()
      print('Account created successfully!')
      return redirect('/accounts/login/')
    else:
      print("Registration failed!")
  else:
    form = RegistrationForm()
  
  context = {'form': form}
  return render(request, 'pages/examples/register-v2.html', context)

class UserLoginView(auth_views.LoginView):
  template_name = 'accounts/login.html'
  form_class = LoginForm
  success_url = '/'

class UserLoginViewV1(auth_views.LoginView):
  template_name = 'pages/examples/login.html'
  form_class = LoginForm
  success_url = '/'

class UserLoginViewV2(auth_views.LoginView):
  template_name = 'pages/examples/login-v2.html'
  form_class = LoginForm
  success_url = '/'

class UserPasswordResetView(auth_views.PasswordResetView):
  template_name = 'accounts/forgot-password.html'
  form_class = UserPasswordResetForm

class UserPasswordResetViewV1(auth_views.PasswordResetView):
  template_name = 'pages/examples/forgot-password.html'
  form_class = UserPasswordResetForm

class UserPasswordResetViewV2(auth_views.PasswordResetView):
  template_name = 'pages/examples/forgot-password-v2.html'
  form_class = UserPasswordResetForm

class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
  template_name = 'accounts/recover-password.html'
  form_class = UserSetPasswordForm

class UserPasswordChangeView(auth_views.PasswordChangeView):
  template_name = 'accounts/password_change.html'
  form_class = UserPasswordChangeForm

class UserPasswordChangeViewV1(auth_views.PasswordChangeView):
  template_name = 'pages/examples/recover-password.html'
  form_class = UserPasswordChangeForm

class UserPasswordChangeViewV2(auth_views.PasswordChangeView):
  template_name = 'pages/examples/recover-password-v2.html'
  form_class = UserPasswordChangeForm

def user_logout_view(request):
  logout(request)
  return redirect('/accounts/login/')


# pages
def index(request):
  context = {
    'parent': 'dashboard',
    'segment': 'dashboardv1'
  }
  return render(request, 'pages/index.html', context)

def index2(request):
  context = {
    'parent': 'dashboard',
    'segment': 'dashboardv2'
  }
  return render(request, 'pages/index2.html', context)

def index3(request):
  context = {
    'parent': 'dashboard',
    'segment': 'dashboardv3'
  }
  return render(request, 'pages/index3.html', context)

# Publisher Views
@login_required
def publisher_list(request):
    publishers = Publishers.objects.all()
    template = 'publisher/list.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'publisher/ajax_list.html'
        
    return render(request, template, {'publishers': publishers})

@login_required
def publisher_create(request):
    if request.method == 'POST':
        pubname = request.POST.get('pubname')
        description = request.POST.get('description')
        Publishers.objects.create(
            pubname=pubname,
            description=description
        )
        messages.success(request, 'Publisher created successfully!')
        return redirect('publisher_list')
    
    template = 'publisher/create.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'publisher/ajax_create.html'
        
    return render(request, template)

@login_required
def publisher_edit(request, pk):
    publisher = get_object_or_404(Publishers, pk=pk)
    if request.method == 'POST':
        publisher.pubname = request.POST.get('pubname')
        publisher.description = request.POST.get('description')
        publisher.save()
        messages.success(request, 'Publisher updated successfully!')
        return redirect('publisher_list')
    
    template = 'publisher/edit.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'publisher/ajax_edit.html'
        
    return render(request, template, {'publisher': publisher})

@login_required
def publisher_delete(request, pk):
    publisher = get_object_or_404(Publishers, pk=pk)
    publisher.delete()
    messages.success(request, 'Publisher deleted successfully!')
    return redirect('publisher_list')

# Category Views
@login_required
def category_list(request):
    categories = Categories.objects.all()
    template = 'category/list.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'category/ajax_list.html'
        
    return render(request, template, {'categories': categories})

@login_required
def category_create(request):
    if request.method == 'POST':
        catname = request.POST.get('catname')
        description = request.POST.get('description')
        Categories.objects.create(
            catname=catname,
            description=description
        )
        messages.success(request, 'Category created successfully!')
        return redirect('category_list')
    
    template = 'category/create.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'category/ajax_create.html'
        
    return render(request, template)

@login_required
def category_edit(request, pk):
    category = get_object_or_404(Categories, pk=pk)
    if request.method == 'POST':
        category.catname = request.POST.get('catname')
        category.description = request.POST.get('description')
        category.save()
        messages.success(request, 'Category updated successfully!')
        return redirect('category_list')
    
    template = 'category/edit.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'category/ajax_edit.html'
        
    return render(request, template, {'category': category})

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Categories, pk=pk)
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('category_list')

# Author Views
@login_required
def author_list(request):
    authors = Authors.objects.all()
    template = 'author/list.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'author/ajax_list.html'
        
    return render(request, template, {'authors': authors})

@login_required
def author_create(request):
    if request.method == 'POST':
        authorname = request.POST.get('authorname')
        description = request.POST.get('description')
        Authors.objects.create(
            authorname=authorname,
            description=description
        )
        messages.success(request, 'Author created successfully!')
        return redirect('author_list')
    
    template = 'author/create.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'author/ajax_create.html'
        
    return render(request, template)

@login_required
def author_edit(request, pk):
    author = get_object_or_404(Authors, pk=pk)
    if request.method == 'POST':
        author.authorname = request.POST.get('authorname')
        author.description = request.POST.get('description')
        author.save()
        messages.success(request, 'Author updated successfully!')
        return redirect('author_list')
    
    template = 'author/edit.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'author/ajax_edit.html'
        
    return render(request, template, {'author': author})

@login_required
def author_delete(request, pk):
    author = get_object_or_404(Authors, pk=pk)
    author.delete()
    messages.success(request, 'Author deleted successfully!')
    return redirect('author_list')

# Book Views
@login_required
def book_list(request):
    books = Books.objects.all()
    template = 'book/list.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'book/ajax_list.html'
        
    return render(request, template, {'books': books})

@login_required
def book_create(request):
    if request.method == 'POST':
        id_pub = get_object_or_404(Publishers, pk=request.POST.get('id_pub'))
        bookname = request.POST.get('bookname')
        publishdate = request.POST.get('publishdate')
        price = request.POST.get('price')
        description = request.POST.get('description')
        
        book = Books.objects.create(
            id_pub=id_pub,
            bookname=bookname,
            publishdate=publishdate,
            price=price,
            description=description
        )
        
        # Add authors
        author_ids = request.POST.getlist('authors[]') or []
        for author_id in author_ids:
            author = get_object_or_404(Authors, pk=author_id)
            Bookauthors.objects.create(
                id_book=book,
                id_author=author
            )
        
        # Add categories
        category_ids = request.POST.getlist('categories[]') or []
        for category_id in category_ids:
            category = get_object_or_404(Categories, pk=category_id)
            Bookcategories.objects.create(
                id_book=book,
                id_cat=category
            )
        
        # Generate barcode - EAN-13 requires 12 digits (13th is check digit)
        # Use a prefix (e.g., 978 for books) and pad with zeros
        barcode_base = f"978{book.id:09d}"  # 978 + 9 digits padded with zeros
        ean = barcode.get('ean13', barcode_base, writer=ImageWriter())
        buffer = BytesIO()
        ean.write(buffer)
        
        # Ensure barcode directory exists
        barcode_folder = os.path.join(settings.MEDIA_ROOT, 'barcodes')
        os.makedirs(barcode_folder, exist_ok=True)
        
        # Save barcode image
        filename = f'barcode_{book.id}.png'
        file_path = os.path.join('barcodes', filename)
        
        # Set barcode number to the FULL 13-digit code (including check digit)
        book.barcode_number = str(ean)
        
        # Save barcode file to the barcode directory
        book.barcode.save(file_path, File(buffer), save=True)
        
        messages.success(request, 'Book created successfully!')
        
        # If it's an AJAX request, return a simple success response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
            
        return redirect('book_list')
    
    publishers = Publishers.objects.all()
    authors = Authors.objects.all()
    categories = Categories.objects.all()
    
    template = 'book/create.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'book/ajax_create.html'
        
    return render(request, template, {
        'publishers': publishers,
        'authors': authors,
        'categories': categories
    })

@login_required
def book_edit(request, pk):
    book = get_object_or_404(Books, pk=pk)
    if request.method == 'POST':
        book.id_pub = get_object_or_404(Publishers, pk=request.POST.get('id_pub'))
        book.publishdate = request.POST.get('publishdate')
        book.price = request.POST.get('price')
        book.description = request.POST.get('description')
        
        # Update authors - first remove all existing authors
        Bookauthors.objects.filter(id_book=book).delete()
        
        # Add updated authors
        author_ids = request.POST.getlist('authors[]') or []
        for author_id in author_ids:
            author = get_object_or_404(Authors, pk=author_id)
            Bookauthors.objects.create(
                id_book=book,
                id_author=author
            )
        
        # Update categories - first remove all existing categories
        Bookcategories.objects.filter(id_book=book).delete()
        
        # Add updated categories
        category_ids = request.POST.getlist('categories[]') or []
        for category_id in category_ids:
            category = get_object_or_404(Categories, pk=category_id)
            Bookcategories.objects.create(
                id_book=book,
                id_cat=category
            )
        
        # Check if barcode needs to be generated or regenerated
        if not book.barcode or not book.barcode_number:
            # Generate barcode - EAN-13 requires 12 digits (13th is check digit)
            # Use a prefix (e.g., 978 for books) and pad with zeros
            barcode_base = f"978{book.id:09d}"  # 978 + 9 digits padded with zeros
            ean = barcode.get('ean13', barcode_base, writer=ImageWriter())
            buffer = BytesIO()
            ean.write(buffer)
            
            # Ensure barcode directory exists
            barcode_folder = os.path.join(settings.MEDIA_ROOT, 'barcodes')
            os.makedirs(barcode_folder, exist_ok=True)
            
            # Save barcode image
            filename = f'barcode_{book.id}.png'
            file_path = os.path.join('barcodes', filename)
            
            # Set barcode number to the FULL 13-digit code (including check digit)
            book.barcode_number = str(ean)
            
            # Save barcode file to the barcode directory
            book.barcode.save(file_path, File(buffer), save=True)
        else:
            # Just save updated fields
            book.save()
            
        messages.success(request, 'Book updated successfully!')
        
        # If it's an AJAX request, return a simple success response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
            
        return redirect('book_list')
    
    publishers = Publishers.objects.all()
    authors = Authors.objects.all()
    categories = Categories.objects.all()
    
    # Get book authors and categories for pre-selecting in the form
    book_authors = [ba.id_author.id for ba in Bookauthors.objects.filter(id_book=book)]
    book_categories = [bc.id_cat.id for bc in Bookcategories.objects.filter(id_book=book)]
    
    template = 'book/edit.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'book/ajax_edit.html'
        
    return render(request, template, {
        'book': book, 
        'publishers': publishers,
        'authors': authors,
        'categories': categories,
        'book_authors': book_authors,
        'book_categories': book_categories
    })

@login_required
def book_delete(request, pk):
    book = get_object_or_404(Books, pk=pk)
    
    # Delete related authors and categories
    Bookauthors.objects.filter(id_book=book).delete()
    Bookcategories.objects.filter(id_book=book).delete()
    
    book.delete()
    messages.success(request, 'Book deleted successfully!')
    
    # If it's an AJAX request, return a simple success response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
        
    return redirect('book_list')

# Import Views
@login_required
def import_list(request):
    imports = Imports.objects.all()
    return render(request, 'import/list.html', {'imports': imports})

@login_required
def import_create(request):
    if request.method == 'POST':
        id_book = get_object_or_404(Books, pk=request.POST.get('id_book'))
        id_pub = get_object_or_404(Publishers, pk=request.POST.get('id_pub'))
        quantity = request.POST.get('quantity')
        impprice = request.POST.get('impprice')
        total = float(quantity) * float(impprice)
        
        import_record = Imports.objects.create(
            id_book=id_book,
            id_pub=id_pub,
            quantity=quantity,
            impprice=impprice,
            total=total
        )
        
        # Update book quantity in Bookshelves
        bookshelf, created = Bookshelves.objects.get_or_create(
            id_book=id_book,
            defaults={'quantity': 0}
        )
        bookshelf.quantity = int(bookshelf.quantity) + int(quantity)
        bookshelf.save()
        
        messages.success(request, 'Import record created successfully!')
        return redirect('import_list')
    
    books = Books.objects.all()
    publishers = Publishers.objects.all()
    return render(request, 'import/create.html', {'books': books, 'publishers': publishers})

# Bill Views
@login_required
def bill_list(request):
    # Get all bills with related customer data and prefetch related bill details
    bills = Bills.objects.select_related('id_cus').prefetch_related(
        'billdetails_set__id_book'
    ).all()
    
    # Add bill details to each bill for template display
    for bill in bills:
        bill.details = bill.billdetails_set.all()
    
    template = 'bill/list.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'bill/ajax_list.html'
        
    return render(request, template, {'bills': bills})

@login_required
def bill_create(request):
    if request.method == 'POST':
        id_cus = get_object_or_404(Customers, pk=request.POST.get('id_cus'))
        totalbill = request.POST.get('totalbill')
        
        bill = Bills.objects.create(
            id_cus=id_cus,
            totalbill=totalbill
        )
        
        # Create bill details
        book_ids = request.POST.getlist('book_ids[]')
        quantities = request.POST.getlist('quantities[]')
        prices = request.POST.getlist('prices[]')
        
        for i in range(len(book_ids)):
            book = get_object_or_404(Books, pk=book_ids[i])
            quantity = int(quantities[i])
            price = float(prices[i])
            total = price * quantity
            
            Billdetails.objects.create(
                id_book=book,
                id_bill=bill,
                quantity=quantity,
                price=price,
                total=total
            )
            
            # Update book quantity in inventory
            try:
                bookshelf = Bookshelves.objects.get(id_book=book)
                current_quantity = int(bookshelf.quantity or 0)
                if current_quantity >= quantity:
                    bookshelf.quantity = current_quantity - quantity
                    bookshelf.save()
            except Bookshelves.DoesNotExist:
                pass  # Handle case where book isn't in inventory
        
        messages.success(request, 'Bill created successfully!')
        
        # If it's an AJAX request, return a simple success response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
            
        return redirect('bill_list')
    
    customers = Customers.objects.all()
    books = Books.objects.all()
    
    template = 'bill/create.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'bill/ajax_create.html'
        
    return render(request, template, {'customers': customers, 'books': books})

@login_required
def bill_edit(request, pk):
    bill = get_object_or_404(Bills, pk=pk)
    bill_details = Billdetails.objects.filter(id_bill=bill)
    
    if request.method == 'POST':
        id_cus = get_object_or_404(Customers, pk=request.POST.get('id_cus'))
        totalbill = request.POST.get('totalbill')
        
        bill.id_cus = id_cus
        bill.totalbill = totalbill
        bill.save()
        
        # First restore quantities to inventory
        for detail in bill_details:
            try:
                bookshelf = Bookshelves.objects.get(id_book=detail.id_book)
                current_quantity = int(bookshelf.quantity or 0)
                bookshelf.quantity = current_quantity + int(detail.quantity or 0)
                bookshelf.save()
            except Bookshelves.DoesNotExist:
                pass
        
        # Delete old bill details
        bill_details.delete()
        
        # Create new bill details
        book_ids = request.POST.getlist('book_ids[]')
        quantities = request.POST.getlist('quantities[]')
        prices = request.POST.getlist('prices[]')
        
        for i in range(len(book_ids)):
            book = get_object_or_404(Books, pk=book_ids[i])
            quantity = int(quantities[i])
            price = float(prices[i])
            total = price * quantity
            
            Billdetails.objects.create(
                id_book=book,
                id_bill=bill,
                quantity=quantity,
                price=price,
                total=total
            )
            
            # Update book quantity in inventory
            try:
                bookshelf = Bookshelves.objects.get(id_book=book)
                current_quantity = int(bookshelf.quantity or 0)
                if current_quantity >= quantity:
                    bookshelf.quantity = current_quantity - quantity
                    bookshelf.save()
            except Bookshelves.DoesNotExist:
                pass
        
        messages.success(request, 'Bill updated successfully!')
        
        # If it's an AJAX request, return a simple success response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
            
        return redirect('bill_list')
    
    customers = Customers.objects.all()
    books = Books.objects.all()
    
    bill_items = []
    for detail in bill_details:
        bill_items.append({
            'book': detail.id_book,
            'quantity': detail.quantity,
            'price': detail.price,
            'total': detail.total
        })
    
    template = 'bill/edit.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'bill/ajax_edit.html'
        
    return render(request, template, {
        'bill': bill,
        'bill_items': bill_items,
        'customers': customers,
        'books': books
    })

@login_required
def bill_delete(request, pk):
    bill = get_object_or_404(Bills, pk=pk)
    bill_details = Billdetails.objects.filter(id_bill=bill)
    
    # First restore quantities to inventory
    for detail in bill_details:
        try:
            bookshelf = Bookshelves.objects.get(id_book=detail.id_book)
            current_quantity = int(bookshelf.quantity or 0)
            bookshelf.quantity = current_quantity + int(detail.quantity or 0)
            bookshelf.save()
        except Bookshelves.DoesNotExist:
            pass
    
    # Then delete the bill and its details
    bill.delete()
    
    messages.success(request, 'Bill deleted successfully!')
    
    # If it's an AJAX request, return a simple success response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
        
    return redirect('bill_list')

@login_required
def bill_scan_barcode(request):
    """
    View to handle barcode scanning page with simplified interface
    """
    # Get all books for the form
    books = Books.objects.all()
    customers = Customers.objects.all()
    
    # Get scanned books from session (don't pop yet, we'll manage them differently)
    scanned_books = request.session.get('scanned_books', [])
    
    # Handle POST requests for manual barcode entry and other actions
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_manual_barcode':
            barcode_number = request.POST.get('barcode_number', '').strip()
            if barcode_number:
                try:
                    book = Books.objects.get(barcode_number=barcode_number)
                    # Get author and category information
                    authors = [ba.id_author.authorname for ba in Bookauthors.objects.filter(id_book=book)]
                    categories = [bc.id_cat.catname for bc in Bookcategories.objects.filter(id_book=book)]
                    
                    # Check if book already exists in scanned list
                    book_exists = False
                    for i, scanned_book in enumerate(scanned_books):
                        if scanned_book['id'] == book.id:
                            scanned_books[i]['quantity'] += 1
                            book_exists = True
                            break
                    
                    if not book_exists:
                        scanned_books.append({
                            'id': book.id,
                            'description': book.description,
                            'price': str(book.price),
                            'quantity': 1,
                            'publisher': book.id_pub.pubname if book.id_pub else None,
                            'authors': authors,
                            'categories': categories,                            'scanned_by': 'manual'
                        })
                    
                    request.session['scanned_books'] = scanned_books
                    messages.success(request, f"Added book: {book.description}")
                    
                except Books.DoesNotExist:
                    messages.error(request, f"Book with barcode {barcode_number} not found")
        
        elif action == 'remove_book':
            book_index = int(request.POST.get('book_index', -1))
            if 0 <= book_index < len(scanned_books):
                removed_book = scanned_books.pop(book_index)
                request.session['scanned_books'] = scanned_books
                messages.success(request, f"Removed book: {removed_book['description']}")
        
        elif action == 'clear_all':
            request.session['scanned_books'] = []
            scanned_books = []
            messages.success(request, "Cleared all scanned books")
        
        elif action == 'update_quantity':
            book_index = int(request.POST.get('book_index', -1))
            new_quantity = int(request.POST.get('quantity', 1))
            if 0 <= book_index < len(scanned_books) and new_quantity > 0:
                scanned_books[book_index]['quantity'] = new_quantity
                request.session['scanned_books'] = scanned_books
                messages.success(request, "Quantity updated successfully")
        
        elif action == 'create_bill':
            print(f"DEBUG: Create bill action triggered")
            customer_id = request.POST.get('customer_id')
            print(f"DEBUG: Customer ID received: {customer_id}")
            print(f"DEBUG: Scanned books count: {len(scanned_books)}")
            print(f"DEBUG: POST data: {request.POST}")
            
            if not customer_id or not scanned_books:
                if not customer_id:
                    print("DEBUG: No customer selected")
                if not scanned_books:
                    print("DEBUG: No scanned books")
                messages.error(request, "Please select a customer and add at least one book")
                return redirect('bill_scan_barcode')
            
            try:
                # Get customer
                customer = get_object_or_404(Customers, pk=customer_id)
                
                # Calculate total
                total_bill = 0
                for book_data in scanned_books:
                    total_bill += float(book_data.get('price', 0)) * int(book_data.get('quantity', 1))
                
                # Create bill
                bill = Bills.objects.create(
                    id_cus=customer,
                    totalbill=str(total_bill)
                )
                
                # Create bill details
                for book_data in scanned_books:
                    book = get_object_or_404(Books, pk=book_data.get('id'))
                    quantity = int(book_data.get('quantity', 1))
                    price = float(book_data.get('price', 0))
                    total = price * quantity
                    Billdetails.objects.create(
                        id_book=book,
                        id_bill=bill,
                        quantity=quantity,
                        price=price,
                        total=str(total)
                    )
                
                # Clear scanned books from session
                request.session['scanned_books'] = []
                
                messages.success(request, f"Bill #{bill.id} created successfully for {customer.cusname}! Total: ${total_bill:.2f}")
                return redirect('bill_list')
                
            except Exception as e:
                messages.error(request, f"Error creating bill: {str(e)}")
                return redirect('bill_scan_barcode')
        
        # Redirect to prevent form resubmission
        return redirect('bill_scan_barcode')
    
    # Check if there are desktop-scanned books from camera scanning
    desktop_scanned_books = request.session.pop('desktop_scanned_books', None)
    if desktop_scanned_books:
        # Merge desktop scanned books with existing scanned books
        for new_book in desktop_scanned_books:
            book_exists = False
            for i, existing_book in enumerate(scanned_books):
                if existing_book['id'] == new_book['id']:
                    scanned_books[i]['quantity'] += new_book['quantity']
                    book_exists = True
                    break
            
            if not book_exists:
                scanned_books.append(new_book)
        
        request.session['scanned_books'] = scanned_books
        messages.success(request, f"Added {len(desktop_scanned_books)} camera-scanned books")
      # Calculate total
    total_amount = 0
    for book in scanned_books:
        book_total = float(book['price']) * book['quantity']
        book['total'] = book_total  # Add total to each book for template use
        total_amount += book_total
    
    # Context for rendering the template
    context = {
        'books': books,
        'customers': customers,
        'page_title': 'Scan Barcode',
        'scanned_books': scanned_books,
        'total_amount': total_amount,
        'scanned_books_count': len(scanned_books)
    }
    
    return render(request, 'bill/scan_barcode.html', context)

@login_required
def process_barcode(request):
    """
    API endpoint to process barcode data
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            barcode = data.get('barcode')
            
            if not barcode:
                return JsonResponse({'success': False, 'error': 'No barcode provided'})
            
            # Look up the book by barcode
            try:
                book = Books.objects.get(barcode_number=barcode)
                
                # Get related information with prefetch to optimize database queries
                authors = Bookauthors.objects.filter(id_book=book).select_related('id_author')
                categories = Bookcategories.objects.filter(id_book=book).select_related('id_cat')
                
                # Return book data
                return JsonResponse({
                    'success': True,
                    'book': {
                        'id': book.id,
                        'description': book.description,
                        'price': book.price,
                        'publisher': book.id_pub.pubname if book.id_pub else None,
                        'authors': [ba.id_author.authorname for ba in authors],
                        'categories': [bc.id_cat.catname for bc in categories],
                    }
                })
            except Books.DoesNotExist:
                return JsonResponse({'success': False, 'error': f'Book not found with barcode: {barcode}'})
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Only POST requests are allowed'})

@login_required
def create_bill_from_scanned(request):
    """
    API endpoint to create a bill from scanned books
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            customer_id = data.get('customer_id')
            books = data.get('books', [])
            
            if not customer_id or not books:
                return JsonResponse({'success': False, 'error': 'Missing required data'})
            
            # Get customer
            customer = get_object_or_404(Customers, pk=customer_id)
            
            # Calculate total
            total_bill = 0
            for book_data in books:
                total_bill += float(book_data.get('price', 0)) * int(book_data.get('quantity', 1))
            
            # Create bill
            bill = Bills.objects.create(
                id_cus=customer,
                totalbill=total_bill
            )
            
            # Create bill details
            for book_data in books:
                book = get_object_or_404(Books, pk=book_data.get('id'))
                quantity = int(book_data.get('quantity', 1))
                price = float(book_data.get('price', 0))
                total = price * quantity
                
                Billdetails.objects.create(
                    id_book=book,
                    id_bill=bill,
                    quantity=quantity,
                    price=price,
                    total=total
                )
                
                # Update inventory
                try:
                    bookshelf = Bookshelves.objects.get(id_book=book)
                    current_quantity = int(bookshelf.quantity or 0)
                    if current_quantity >= quantity:
                        bookshelf.quantity = current_quantity - quantity
                        bookshelf.save()
                except Bookshelves.DoesNotExist:
                    pass
            
            return JsonResponse({
                'success': True, 
                'bill_id': bill.id,
                'message': 'Bill created successfully'
            })
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# API Views
@login_required
def get_book_by_barcode(request, barcode_number):
    try:
        book = Books.objects.get(barcode_number=barcode_number)
        authors = [ba.id_author.authorname for ba in Bookauthors.objects.filter(id_book=book)]
        categories = [bc.id_cat.catname for bc in Bookcategories.objects.filter(id_book=book)]
        data = {
            'id': book.id,
            'description': book.description,
            'price': book.price,
            'publisher': book.id_pub.pubname if book.id_pub else None,
            'authors': authors,
            'categories': categories,
            'success': True
        }
        return JsonResponse(data)
    except Books.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Book not found'}, status=404)

# Helper function to get database information
def get_database_context():
    """
    Retrieves summary data from the database to provide as context to Gemini
    """
    try:
        context = []
        
        # Get total counts from different models
        publisher_count = Publishers.objects.count()
        category_count = Categories.objects.count()
        author_count = Authors.objects.count()
        book_count = Books.objects.count() if 'Books' in globals() else 0
        
        context.append(f"Current database summary: {publisher_count} publishers, {category_count} categories, {author_count} authors, and {book_count} books.")
        
        # Get recent publishers with full information
        recent_publishers = Publishers.objects.order_by('-lastmodified')[:5]
        if recent_publishers:
            publisher_info = []
            for p in recent_publishers:
                pub_desc = p.description if p.description else "No description available"
                publisher_info.append(f"{p.pubname} (ID: {p.id}) - {pub_desc}")
            
            context.append("Recent publishers:")
            context.extend([f"- {info}" for info in publisher_info])
        
        # Get recent categories with full information
        recent_categories = Categories.objects.order_by('-lastmodified')[:5]
        if recent_categories:
            category_info = []
            for c in recent_categories:
                cat_desc = c.description if c.description else "No description available"
                category_info.append(f"{c.catname} (ID: {c.id}) - {cat_desc}")
            
            context.append("Recent categories:")
            context.extend([f"- {info}" for info in category_info])
        
        # Get recent authors with full information
        recent_authors = Authors.objects.order_by('-lastmodified')[:5]
        if recent_authors:
            author_info = []
            for a in recent_authors:
                auth_desc = a.description if a.description else "No description available"
                author_info.append(f"{a.authorname} (ID: {a.id}) - {auth_desc}")
            
            context.append("Recent authors:")
            context.extend([f"- {info}" for info in author_info])
        
        return "\n".join(context)
    except Exception as e:
        return f"Error retrieving database context: {str(e)}"

# Helper function to handle specific database queries
def handle_db_query(query):
    """
    Handles specific database queries based on the user's message
    Returns structured data that can be used to answer the query
    """
    query = query.lower()
    response = {}
    
    try:
        # Query for publishers
        if "publishers" in query or "publisher" in query:
            if "list" in query or "all" in query:
                publishers = Publishers.objects.all()
                response["publishers"] = [
                    {
                        "id": p.id,
                        "name": p.pubname,
                        "description": p.description or "No description available", 
                        "last_modified": p.lastmodified.strftime("%Y-%m-%d %H:%M:%S") if p.lastmodified else "Unknown"
                    } 
                    for p in publishers
                ]
                
        # Query for categories
        if "categories" in query or "category" in query:
            if "list" in query or "all" in query:
                categories = Categories.objects.all()
                response["categories"] = [
                    {
                        "id": c.id,
                        "name": c.catname,
                        "description": c.description or "No description available",
                        "last_modified": c.lastmodified.strftime("%Y-%m-%d %H:%M:%S") if c.lastmodified else "Unknown"
                    } 
                    for c in categories
                ]
                
        # Query for authors
        if "authors" in query or "author" in query:
            if "list" in query or "all" in query:
                authors = Authors.objects.all()
                response["authors"] = [
                    {
                        "id": a.id,
                        "name": a.authorname,
                        "description": a.description or "No description available",
                        "last_modified": a.lastmodified.strftime("%Y-%m-%d %H:%M:%S") if a.lastmodified else "Unknown"
                    } 
                    for a in authors
                ]
        
        # Query for books
        if "books" in query or "book" in query:
            if "list" in query or "all" in query:
                books = Books.objects.all()
                response["books"] = [
                    {
                        "id": b.id, 
                        "description": b.description or "No description available", 
                        "price": b.price,
                        "publisher": b.id_pub.pubname if b.id_pub else "Unknown publisher",
                        "publish_date": b.publishdate.strftime("%Y-%m-%d") if b.publishdate else "Unknown"
                    } 
                    for b in books
                ]
        
        return response
    except Exception as e:
        return {"error": str(e)}

# Function to execute custom database queries
def execute_custom_query(query):
    """
    Executes more complex database queries based on user intent
    Returns detailed information that can be used by Gemini to provide more accurate answers
    """
    query = query.lower()
    response = {}
    
    try:
        # Find books by a specific publisher
        if any(x in query for x in ["books by publisher", "publisher's books"]):
            # Extract publisher name from query (simplified approach)
            publisher_matches = [pub.pubname for pub in Publishers.objects.all() 
                               if pub.pubname and pub.pubname.lower() in query]
            
            if publisher_matches:
                publisher_name = publisher_matches[0]
                publisher = Publishers.objects.filter(pubname__icontains=publisher_name).first()
                if publisher:
                    books = Books.objects.filter(id_pub=publisher)
                    response["publisher_books"] = {
                        "publisher": {
                            "id": publisher.id,
                            "name": publisher.pubname,
                            "description": publisher.description or "No description available",
                            "last_modified": publisher.lastmodified.strftime("%Y-%m-%d %H:%M:%S") if publisher.lastmodified else "Unknown"
                        },
                        "books": [
                            {
                                "id": b.id, 
                                "description": b.description or "No description available", 
                                "price": b.price,
                                "publish_date": b.publishdate.strftime("%Y-%m-%d") if b.publishdate else "Unknown"
                            } 
                            for b in books
                        ]
                    }
        
        # Find books by a specific author
        if any(x in query for x in ["books by author", "author's books"]):
            # Extract author name from query (simplified approach)
            author_matches = [auth.authorname for auth in Authors.objects.all() 
                            if auth.authorname and auth.authorname.lower() in query]
            
            if author_matches:
                author_name = author_matches[0]
                author = Authors.objects.filter(authorname__icontains=author_name).first()
                if author:
                    book_authors = Bookauthors.objects.filter(id_author=author)
                    books = [ba.id_book for ba in book_authors]
                    response["author_books"] = {
                        "author": {
                            "id": author.id,
                            "name": author.authorname,
                            "description": author.description or "No description available",
                            "last_modified": author.lastmodified.strftime("%Y-%m-%d %H:%M:%S") if author.lastmodified else "Unknown"
                        },
                        "books": [
                            {
                                "id": b.id, 
                                "description": b.description or "No description available", 
                                "price": b.price,
                                "publisher": b.id_pub.pubname if hasattr(b, 'id_pub') and b.id_pub else "Unknown publisher",
                                "publish_date": b.publishdate.strftime("%Y-%m-%d") if b.publishdate else "Unknown"
                            } 
                            for b in books
                        ]
                    }
        
        # Find books by category
        if any(x in query for x in ["books in category", "category books"]):
            # Extract category name from query (simplified approach)
            category_matches = [cat.catname for cat in Categories.objects.all() 
                             if cat.catname and cat.catname.lower() in query]
            
            if category_matches:
                category_name = category_matches[0]
                category = Categories.objects.filter(catname__icontains=category_name).first()
                if category:
                    book_categories = Bookcategories.objects.filter(id_cat=category)
                    books = [bc.id_book for bc in book_categories]
                    response["category_books"] = {
                        "category": {
                            "id": category.id,
                            "name": category.catname,
                            "description": category.description or "No description available",
                            "last_modified": category.lastmodified.strftime("%Y-%m-%d %H:%M:%S") if category.lastmodified else "Unknown"
                        },
                        "books": [
                            {
                                "id": b.id, 
                                "description": b.description or "No description available", 
                                "price": b.price,
                                "publisher": b.id_pub.pubname if hasattr(b, 'id_pub') and b.id_pub else "Unknown publisher",
                                "publish_date": b.publishdate.strftime("%Y-%m-%d") if b.publishdate else "Unknown"
                            } 
                            for b in books
                        ]
                    }
                    
        # Add more custom queries as needed
        
        return response
    except Exception as e:
        return {"error": str(e)}

# Area Views
@login_required
def area_list(request):
    areas = Areas.objects.all()
    template = 'area/list.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'area/ajax_list.html'
        
    return render(request, template, {'areas': areas})

@login_required
def area_create(request):
    if request.method == 'POST':
        areaname = request.POST.get('areaname')
        description = request.POST.get('description')
        Areas.objects.create(
            areaname=areaname,
            description=description
        )
        messages.success(request, 'Area created successfully!')
        return redirect('area_list')
    
    template = 'area/create.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'area/ajax_create.html'
        
    return render(request, template)

@login_required
def area_edit(request, pk):
    area = get_object_or_404(Areas, pk=pk)
    if request.method == 'POST':
        area.areaname = request.POST.get('areaname')
        area.description = request.POST.get('description')
        area.save()
        messages.success(request, 'Area updated successfully!')
        return redirect('area_list')
    
    template = 'area/edit.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'area/ajax_edit.html'
        
    return render(request, template, {'area': area})

@login_required
def area_delete(request, pk):
    area = get_object_or_404(Areas, pk=pk)
    area.delete()
    messages.success(request, 'Area deleted successfully!')
    return redirect('area_list')

# Shelf Views
@login_required
def shelf_list(request):
    shelves = Shelves.objects.all()
    template = 'shelf/list.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'shelf/ajax_list.html'
        
    return render(request, template, {'shelves': shelves})

@login_required
def shelf_create(request):
    if request.method == 'POST':
        shelfname = request.POST.get('shelfname')
        id_area = get_object_or_404(Areas, pk=request.POST.get('id_area'))
        Shelves.objects.create(
            shelfname=shelfname,
            id_area=id_area
        )
        messages.success(request, 'Shelf created successfully!')
        return redirect('shelf_list')
    
    template = 'shelf/create.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'shelf/ajax_create.html'
    
    areas = Areas.objects.all()
    return render(request, template, {'areas': areas})

@login_required
def shelf_edit(request, pk):
    shelf = get_object_or_404(Shelves, pk=pk)
    if request.method == 'POST':
        shelf.shelfname = request.POST.get('shelfname')
        shelf.id_area = get_object_or_404(Areas, pk=request.POST.get('id_area'))
        shelf.save()
        messages.success(request, 'Shelf updated successfully!')
        return redirect('shelf_list')
    
    template = 'shelf/edit.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'shelf/ajax_edit.html'
    
    areas = Areas.objects.all()
    return render(request, template, {'shelf': shelf, 'areas': areas})

@login_required
def shelf_delete(request, pk):
    shelf = get_object_or_404(Shelves, pk=pk)
    shelf.delete()
    messages.success(request, 'Shelf deleted successfully!')
    return redirect('shelf_list')

# Bookshelf Views (Assign Books to Shelves)
@login_required
def bookshelf_list(request):
    bookshelves = Bookshelves.objects.all()
    template = 'bookshelf/list.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'bookshelf/ajax_list.html'
        
    return render(request, template, {'bookshelves': bookshelves})

@login_required
def bookshelf_create(request):
    if request.method == 'POST':
        id_book = get_object_or_404(Books, pk=request.POST.get('id_book'))
        id_shelf = get_object_or_404(Shelves, pk=request.POST.get('id_shelf'))
        quantity = request.POST.get('quantity')
        
        Bookshelves.objects.create(
            id_book=id_book,
            id_shelf=id_shelf,
            quantity=quantity
        )
        
        messages.success(request, 'Book assigned to shelf successfully!')
        
        # If it's an AJAX request, return a simple success response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
            
        return redirect('bookshelf_list')
    
    books = Books.objects.all()
    shelves = Shelves.objects.all()
    
    template = 'bookshelf/create.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'bookshelf/ajax_create.html'
        
    return render(request, template, {'books': books, 'shelves': shelves})

@login_required
def bookshelf_edit(request, pk):
    bookshelf = get_object_or_404(Bookshelves, pk=pk)
    if request.method == 'POST':
        bookshelf.id_book = get_object_or_404(Books, pk=request.POST.get('id_book'))
        bookshelf.id_shelf = get_object_or_404(Shelves, pk=request.POST.get('id_shelf'))
        bookshelf.quantity = request.POST.get('quantity')
        bookshelf.save()
        
        messages.success(request, 'Book shelf assignment updated successfully!')
        
        # If it's an AJAX request, return a simple success response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
            
        return redirect('bookshelf_list')
    
    books = Books.objects.all()
    shelves = Shelves.objects.all()
    
    template = 'bookshelf/edit.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'bookshelf/ajax_edit.html'
        
    return render(request, template, {'bookshelf': bookshelf, 'books': books, 'shelves': shelves})

@login_required
def bookshelf_delete(request, pk):
    bookshelf = get_object_or_404(Bookshelves, pk=pk)
    bookshelf.delete()
    messages.success(request, 'Book shelf assignment deleted successfully!')
    
    # If it's an AJAX request, return a simple success response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
        
    return redirect('bookshelf_list')

# Employee Views
@login_required
def employee_list(request):
    employees = Employees.objects.all()
    return render(request, 'employee/list.html', {'employees': employees})

@login_required
def employee_create(request):
    if request.method == 'POST':
        empname = request.POST.get('empname')
        role = request.POST.get('role')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        hiredate = request.POST.get('hiredate')
        
        # Create employee
        employee = Employees.objects.create(
            empname=empname,
            role=role,
            phone=phone,
            gender=gender,
            address=address,
            hiredate=hiredate
        )
        
        # Create user account
        username = f"emp_{employee.id}"
        password = request.POST.get('password')
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=empname
        )
        
        messages.success(request, 'Employee created successfully!')
        return redirect('employee_list')
    
    return render(request, 'employee/create.html')

@login_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employees, pk=pk)
    if request.method == 'POST':
        employee.empname = request.POST.get('empname')
        employee.role = request.POST.get('role')
        employee.phone = request.POST.get('phone')
        employee.gender = request.POST.get('gender')
        employee.address = request.POST.get('address')
        employee.hiredate = request.POST.get('hiredate')
        employee.save()
        
        messages.success(request, 'Employee updated successfully!')
        return redirect('employee_list')
    
    return render(request, 'employee/edit.html', {'employee': employee})

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employees, pk=pk)
    employee.delete()
    messages.success(request, 'Employee deleted successfully!')
    return redirect('employee_list')

# Customer Views
@login_required
def customer_list(request):
    customers = Customers.objects.all()
    template = 'customer/list.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'customer/ajax_list.html'
        
    return render(request, template, {'customers': customers})

@login_required
def customer_create(request):
    if request.method == 'POST':
        cusname = request.POST.get('cusname')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')
        
        Customers.objects.create(
            cusname=cusname,
            gender=gender,
            phone=phone
        )
        
        messages.success(request, 'Customer created successfully!')
        return redirect('customer_list')
    
    template = 'customer/create.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'customer/ajax_create.html'
        
    return render(request, template)

@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customers, pk=pk)
    if request.method == 'POST':
        customer.cusname = request.POST.get('cusname')
        customer.gender = request.POST.get('gender')
        customer.phone = request.POST.get('phone')
        customer.save()
        
        messages.success(request, 'Customer updated successfully!')
        return redirect('customer_list')
    
    template = 'customer/edit.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'customer/ajax_edit.html'
        
    return render(request, template, {'customer': customer})

@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customers, pk=pk)
    customer.delete()
    messages.success(request, 'Customer deleted successfully!')
    return redirect('customer_list')

# Reservation Views
@login_required
def reservation_list(request):
    # Get all reservations with prefetched related data for better performance
    reservations = Reservations.objects.all().select_related('id_cus')
    
    # Prepare data for display
    reservation_data = []
    for reservation in reservations:
        # Get all books for this reservation
        items = ReservationItems.objects.filter(id_reservation=reservation).select_related('id_book')
        books = [item.id_book for item in items]
        
        reservation_data.append({
            'reservation': reservation,
            'books': books,
            'customer_name': reservation.id_cus.cusname if reservation.id_cus else "Unknown",
            'book_count': len(books),
            'book_names': ", ".join([book.description for book in books])
        })
    
    template = 'reservation/list.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'reservation/ajax_list.html'
        
    return render(request, template, {'reservation_data': reservation_data})

@login_required
def reservation_create(request):
    if request.method == 'POST':
        id_cus = get_object_or_404(Customers, pk=request.POST.get('id_cus'))
        book_ids = request.POST.getlist('book_ids[]')
        pickupdate = request.POST.get('pickupdate')
        status = request.POST.get('status', 'Pending')
        
        # Import Django's timezone locally to avoid conflicts
        from django.utils import timezone as django_timezone
        
        # Create a single reservation for all selected books
        reservation = Reservations.objects.create(
            id_cus=id_cus,
            reservedate=django_timezone.now(),
            pickupdate=pickupdate,
            status=status
        )
        
        # Add all selected books as reservation items
        for book_id in book_ids:
            book = get_object_or_404(Books, pk=book_id)
            ReservationItems.objects.create(
                id_reservation=reservation,
                id_book=book
            )
        
        messages.success(request, 'Reservation created successfully!')
        
        # If it's an AJAX request, return a simple success response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
            
        return redirect('reservation_list')
    
    customers = Customers.objects.all()
    books = Books.objects.all()
    
    template = 'reservation/create.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'reservation/ajax_create.html'
        
    return render(request, template, {
        'customers': customers,
        'books': books
    })

@login_required
def reservation_edit(request, pk):
    reservation = get_object_or_404(Reservations, pk=pk)
    reservation_items = ReservationItems.objects.filter(id_reservation=reservation)
    
    if request.method == 'POST':
        # Update customer and general reservation details
        reservation.id_cus = get_object_or_404(Customers, pk=request.POST.get('id_cus'))
        reservation.pickupdate = request.POST.get('pickupdate')
        reservation.status = request.POST.get('status')
        reservation.save()
        
        # Get the list of books to include
        book_ids = request.POST.getlist('book_ids[]')
        
        # Remove all existing book items
        reservation_items.delete()
        
        # Create new book items
        for book_id in book_ids:
            book = get_object_or_404(Books, pk=book_id)
            ReservationItems.objects.create(
                id_reservation=reservation,
                id_book=book
            )
        
        messages.success(request, 'Reservation updated successfully!')
        
        # If it's an AJAX request, return a simple success response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
            
        return redirect('reservation_list')
    
    customers = Customers.objects.all()
    books = Books.objects.all()
    
    # Get current books for pre-selecting in the form
    reserved_books = [item.id_book.id for item in reservation_items]
    
    template = 'reservation/edit.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'reservation/ajax_edit.html'
        
    return render(request, template, {
        'reservation': reservation,
        'customers': customers,
        'books': books,
        'reserved_books': reserved_books
    })

@login_required
def reservation_delete(request, pk):
    reservation = get_object_or_404(Reservations, pk=pk)
    reservation.delete()
    messages.success(request, 'Reservation deleted successfully!')
    
    # If it's an AJAX request, return a simple success response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
        
    return redirect('reservation_list')

@login_required
def customer_reservations(request, customer_id):
    """
    View to show all reservations for a specific customer
    """
    customer = get_object_or_404(Customers, pk=customer_id)
    reservations = Reservations.objects.filter(id_cus=customer)
    
    template = 'reservation/customer_reservations.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'reservation/ajax_customer_reservations.html'
        
    return render(request, template, {
        'customer': customer,
        'reservations': reservations
    })

# Global variables for camera
camera = None
camera_thread = None
is_camera_running = False

def generate_frames():
    global camera, is_camera_running
    while is_camera_running:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Try to decode barcodes
            for barcode in decode(frame):
                barcode_data = barcode.data.decode('utf-8')
                barcode_type = barcode.type
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = f"{barcode_data} ({barcode_type})"
                cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                # You can also process the barcode here (e.g., lookup in DB)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)

@login_required
def start_camera(request):
    """
    View to handle camera access for barcode scanning
    """
    global camera, camera_thread, is_camera_running
    
    if request.method == 'POST':
        try:
            if not is_camera_running:
                # Initialize camera
                camera = cv2.VideoCapture(0)
                camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                
                if not camera.isOpened():
                    return JsonResponse({
                        'success': False,
                        'error': 'Could not open camera'
                    })
                
                is_camera_running = True
                
                # Start camera thread
                camera_thread = threading.Thread(target=generate_frames)
                camera_thread.daemon = True
                camera_thread.start()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Camera started successfully'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Camera is already running'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

@login_required
def stop_camera(request):
    """
    View to stop camera access
    """
    global camera, is_camera_running
    
    if request.method == 'POST':
        try:
            if is_camera_running and camera is not None:
                is_camera_running = False
                camera.release()
                cv2.destroyAllWindows()
                return JsonResponse({
                    'success': True,
                    'message': 'Camera stopped successfully'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Camera is not running'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

@login_required
def video_feed(request):
    return StreamingHttpResponse(generate_frames(),
                                content_type='multipart/x-mixed-replace; boundary=frame')

@login_required
def scan_barcode_desktop(request):
    """
    Desktop barcode scanner for Books4Geeks.
    Opens camera window on server, scans books, and adds them to the session.
    """
    try:
        # Initialize camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messages.error(request, "Could not open camera. Please check your hardware settings.")
            return redirect('bill_scan_barcode')
            
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Keep track of scanned books
        scanned_books = []
        scanned_barcodes = set()
        
        print("Starting barcode scanner...")
        print("Press 'c' to complete scanning and return to the web interface.")
        
        while True:
            success, frame = cap.read()
            if not success:
                break
                
            # Process frame for barcodes
            for barcode in decode(frame):
                barcode_data = barcode.data.decode('utf-8')
                
                # Draw rectangle around barcode
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Check if this is a new barcode
                if barcode_data not in scanned_barcodes:
                    try:
                        # Look up the book
                        book = Books.objects.get(barcode_number=barcode_data)
                        
                        # Get author and category information
                        authors = [ba.id_author.authorname for ba in Bookauthors.objects.filter(id_book=book)]
                        categories = [bc.id_cat.catname for bc in Bookcategories.objects.filter(id_book=book)]
                        
                        # Add to scanned books
                        scanned_books.append({
                            'id': book.id,
                            'description': book.description,
                            'price': str(book.price),
                            'quantity': 1,
                            'publisher': book.id_pub.pubname if book.id_pub else None,
                            'authors': authors,
                            'categories': categories,
                            'scanned_by': 'camera'
                        })
                        
                        # Mark as processed
                        scanned_barcodes.add(barcode_data)
                        
                        # Show success message on frame
                        success_text = f"Added: {book.description}"
                        cv2.putText(frame, success_text, (10, 30), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                        print(f"Book scanned: {book.description}")
                        
                    except Books.DoesNotExist:
                        # Show error on frame
                        error_text = f"Not found: {barcode_data}"
                        cv2.putText(frame, error_text, (10, 30), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        
                        print(f"Book not found: {barcode_data}")
                
                # Always show the barcode text
                cv2.putText(frame, barcode_data, (x, y - 10), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Show book count
            count_text = f"Books: {len(scanned_books)}"
            cv2.putText(frame, count_text, (10, frame.shape[0] - 10), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
              # Display the frame
            cv2.imshow("Books4Geeks Barcode Scanner", frame)
            
            # Break if 'c' is pressed or window is closed
            key = cv2.waitKey(1) & 0xFF
            if key == ord('c') or key == 27:  # 'c' or ESC key
                break
            
            # Check if window was closed
            if cv2.getWindowProperty("Books4Geeks Barcode Scanner", cv2.WND_PROP_VISIBLE) < 1:
                break
        
        # Clean up
        cap.release()
        cv2.destroyAllWindows()
          # Store scanned books in session
        if scanned_books:
            request.session['desktop_scanned_books'] = scanned_books
            print(f"DEBUG: Stored {len(scanned_books)} books in session")
            print(f"DEBUG: Sample book data: {scanned_books[0] if scanned_books else 'None'}")
            messages.success(request, f"Successfully scanned {len(scanned_books)} books")
        else:
            messages.info(request, "No books were scanned")
        
    except Exception as e:
        print(f"ERROR in scan_barcode_desktop: {str(e)}")
        messages.error(request, f"Error during barcode scanning: {str(e)}")
    
    # Always redirect back to the scan_barcode page
    return redirect('bill_scan_barcode')

@login_required
def test_barcode_scan(request):
    """
    Test function to simulate barcode scanning without camera
    """
    try:
        # Get some books with barcodes
        books = Books.objects.filter(barcode_number__isnull=False).exclude(barcode_number='')[:2]
        
        if not books.exists():
            messages.error(request, "No books with barcodes found for testing")
            return redirect('bill_scan_barcode')
        
        # Simulate scanned books
        scanned_books = []
        for book in books:
            # Get author and category information
            authors = [ba.id_author.authorname for ba in Bookauthors.objects.filter(id_book=book)]
            categories = [bc.id_cat.catname for bc in Bookcategories.objects.filter(id_book=book)]
            
            scanned_books.append({
                'id': book.id,
                'description': book.description,
                'price': str(book.price),
                'quantity': 1,
                'publisher': book.id_pub.pubname if book.id_pub else None,
                'authors': authors,
                'categories': categories,
                'scanned_by': 'camera'
            })
        
        # Store in session
        request.session['desktop_scanned_books'] = scanned_books
        print(f"DEBUG TEST: Stored {len(scanned_books)} test books in session")
        print(f"DEBUG TEST: Sample book: {scanned_books[0]}")
        
        messages.success(request, f"Test: Added {len(scanned_books)} books to session")
        
    except Exception as e:
        print(f"ERROR in test_barcode_scan: {str(e)}")
        messages.error(request, f"Error in test: {str(e)}")
    
    return redirect('bill_scan_barcode')

def export_full_database(changed_model=None):
    """
    Exports the ENTIRE database to JSON files for AI consumption,
    with optimization for frequent updates
    
    Args:
        changed_model: If provided, only this model will be re-exported
    """
    # Create data directory if it doesn't exist
    data_dir = os.path.join(settings.BASE_DIR, 'ai_data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Export timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Initialize exported models tracking
    exported_models = {}
    
    # Try to load existing metadata if available
    metadata_path = os.path.join(data_dir, 'metadata.json')
    try:
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                exported_models = metadata.get('exported_models', {})
    except:
        # If we can't load metadata, start fresh
        exported_models = {}
    
    # Determine which models to export
    if changed_model:
        # If a specific model changed, only export that one
        app_models = [apps.get_model('B4G', changed_model)]
    else:
        # Otherwise export all models
        app_models = apps.get_app_config('B4G').get_models()
    
    # Export each model to its own JSON file
    for model in app_models:
        model_name = model.__name__
        model_objects = model.objects.all()
        
        # Skip empty models
        if not model_objects.exists():
            exported_models[model_name] = 0
            continue
            
        # Serialize all objects from this model
        serialized_data = serializers.serialize('json', model_objects)
        
        # Save to file
        file_path = os.path.join(data_dir, f"{model_name.lower()}.json")
        with open(file_path, 'w') as f:
            f.write(serialized_data)
        
        # Track models we've exported
        exported_models[model_name] = model_objects.count()
    
    # Update the metadata file
    metadata = {
        "timestamp": timestamp,
        "exported_models": exported_models,
        "total_models": len(exported_models),
        "total_records": sum(exported_models.values())
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Also update the summary file for the AI
    with open(os.path.join(data_dir, 'database_summary.txt'), 'w') as f:
        f.write(f"Books4Geeks Database Export\n")
        f.write(f"========================\n")
        f.write(f"Exported on: {timestamp}\n\n")
        f.write(f"Total models: {len(exported_models)}\n")
        f.write(f"Total records: {sum(exported_models.values())}\n\n")
        
        f.write("Models and record counts:\n")
        for model_name, count in exported_models.items():
            f.write(f"- {model_name}: {count} records\n")
    
    return {
        "success": True,
        "timestamp": timestamp,
        "exported_models": exported_models,
        "total_models": len(exported_models),
        "total_records": sum(exported_models.values())
    }

# Keep track of export timing for debouncing
last_export_time = 0
export_lock = threading.Lock()
export_scheduled = False

def schedule_export():
    """
    Schedule a database export to happen soon, with debouncing
    """
    global export_scheduled, last_export_time
    
    with export_lock:
        current_time = time.time()
        # If an export was performed recently, skip this one
        if current_time - last_export_time < 30:  # 30 second cooldown
            return
            
        # If already scheduled, do nothing
        if export_scheduled:
            return
            
        # Schedule the export
        export_scheduled = True
        export_thread = threading.Thread(target=lambda: debounced_export())
        export_thread.daemon = True
        export_thread.start()

def debounced_export():
    """
    Perform the export after a short delay to avoid multiple exports
    when many models are updated at once
    """
    global export_scheduled, last_export_time
    
    # Wait a bit to allow other changes to accumulate
    time.sleep(5)  
    
    with export_lock:
        if export_scheduled:
            try:
                export_full_database()
                last_export_time = time.time()
            except Exception as e:
                print(f"Error exporting database: {e}")
            finally:
                export_scheduled = False

# Create a generic signal handler for any model change
@receiver([post_save, post_delete])
def handle_model_change(sender, **kwargs):
    """
    Signal handler that triggers when any model is saved or deleted
    """
    # Skip non-B4G models to avoid triggering on built-in Django models
    app_label = sender._meta.app_label
    if app_label != 'B4G':
        return
        
    # Schedule an export
    schedule_export()

# Register signals for all models in the B4G app
def register_signals():
    """
    Register signal handlers for all models in the B4G app
    """
    for model in apps.get_app_config('B4G').get_models():
        # Skip any models you don't want to trigger exports
        # For example, models that change very frequently might be excluded
        # if model.__name__ in ['FrequentlyChangingModel']:
        #     continue
            
        # Connect signals for this model
        post_save.connect(handle_model_change, sender=model)
        post_delete.connect(handle_model_change, sender=model)
        
        print(f"Registered export signals for model: {model.__name__}")
        
@csrf_exempt
def gemini_api(request):
    """
    View to handle Gemini API requests using comprehensive database exports
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            # Configure the Gemini API
            api_key = "AIzaSyCU0QEQYbgD5k44SC5D5J_A1RYVa_CQQ1M"
            genai.configure(api_key=api_key)
            
            # Create context about the Books4Geeks application
            system_prompt = "You are an AI assistant for the Books4Geeks application, a Django web app for managing books, authors, publishers, and categories. Keep responses helpful, concise, and focused on the application's features."
            
            # Load database summary
            data_dir = os.path.join(settings.BASE_DIR, 'ai_data')
            
            try:
                with open(os.path.join(data_dir, 'database_summary.txt'), 'r') as f:
                    db_summary = f.read()
                    system_prompt += f"\n\nDatabase Information:\n{db_summary}"
            except FileNotFoundError:
                system_prompt += "\n\nDatabase summary not available."
            
            # Determine which model data to include based on query
            relevant_models = []
            
            # Simple keyword matching for model identification
            model_keywords = {
                'publishers': ['publisher', 'publishers', 'publication', 'pubname'],
                'authors': ['author', 'authors', 'writer', 'writers'],
                'categories': ['category', 'categories', 'genre', 'genres'],
                'books': ['book', 'books', 'title', 'description'],
                'customers': ['customer', 'customers', 'client', 'clients'],
                'bills': ['bill', 'bills', 'invoice', 'invoices', 'sale', 'sales'],
                'bookauthors': ['bookauthor', 'book author', 'book writer'],
                'bookcategories': ['bookcategory', 'book category', 'book genre'],
                'bookshelves': ['bookshelf', 'bookshelves', 'shelf', 'shelves'],
                'imports': ['import', 'imports', 'inventory'],
                'billdetails': ['billdetail', 'bill details', 'invoice details']
            }
            
            # Find relevant models based on keywords
            for model, keywords in model_keywords.items():
                if any(keyword in user_message.lower() for keyword in keywords):
                    relevant_models.append(model)
            
            # Always include basic models if nothing specific is found
            if not relevant_models:
                relevant_models = ['books', 'authors', 'publishers', 'categories']
            
            # Add sample data from relevant models
            for model in relevant_models:
                try:
                    model_file = os.path.join(data_dir, f"{model}.json")
                    if os.path.exists(model_file):
                        with open(model_file, 'r') as f:
                            model_data = json.load(f)
                            
                            # Only include a sample (first 3 records)
                            sample_data = model_data[:3] if len(model_data) > 3 else model_data
                            
                            system_prompt += f"\n\n{model.capitalize()} data sample:\n"
                            system_prompt += json.dumps(sample_data, indent=2)
                            
                            if len(model_data) > 3:
                                system_prompt += f"\n...and {len(model_data) - 3} more records."
                except Exception as e:
                    pass  # Skip if we can't load this model data
            
            # Access the model and configure it
            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                system_instruction=system_prompt,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 1024,
                }
            )
            
            # Generate content
            response = model.generate_content(user_message)
            
            # Check if the response has text
            if hasattr(response, 'text'):
                return JsonResponse({'response': response.text})
            else:
                return JsonResponse({
                    'response': 'Sorry, I could not generate a response at this time.',
                    'error': 'Invalid response structure'
                })
                
        except Exception as e:
            return JsonResponse({
                'response': 'Sorry, an error occurred while processing your request.',
                'error': str(e)
            })
    
    return JsonResponse({'error': 'Only POST requests are allowed'})

# Role and Permission Views
@login_required
def role_list(request):
    """
    View to display all roles (groups) and their permissions
    """
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType
    
    groups = Group.objects.all()
    content_types = ContentType.objects.filter(app_label='B4G')
    permissions = Permission.objects.filter(content_type__app_label='B4G')
    
    # Group permissions by model
    permissions_by_model = {}
    for ct in content_types:
        model_perms = permissions.filter(content_type=ct)
        if model_perms.exists():
            permissions_by_model[ct.model] = model_perms
    
    template = 'role/list.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'role/ajax_list.html'
        
    return render(request, template, {
        'groups': groups,
        'permissions_by_model': permissions_by_model
    })

@login_required
def role_create(request):
    """
    View to create a new role (group) with permissions
    """
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType
    
    if request.method == 'POST':
        name = request.POST.get('name')
        permission_ids = request.POST.getlist('permissions[]') or []
        
        # Create the group
        group = Group.objects.create(name=name)
        
        # Add permissions to the group
        for perm_id in permission_ids:
            permission = get_object_or_404(Permission, pk=perm_id)
            group.permissions.add(permission)
        
        messages.success(request, 'Role created successfully!')
        return redirect('role_list')
    
    # Get all relevant permissions
    content_types = ContentType.objects.filter(Q(app_label='B4G') | Q(app_label='auth'))
    permissions = Permission.objects.filter(content_type__in=content_types)
    
    # Group permissions by model
    permissions_by_model = {}
    for ct in content_types:
        model_perms = permissions.filter(content_type=ct)
        if model_perms.exists():
            permissions_by_model[f"{ct.app_label}.{ct.model}"] = model_perms
    
    template = 'role/create.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'role/ajax_create.html'
        
    return render(request, template, {
        'permissions': permissions,
        'permissions_by_model': permissions_by_model
    })

@login_required
def role_edit(request, pk):
    """
    View to edit a role (group) and its permissions
    """
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType
    
    group = get_object_or_404(Group, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        permission_ids = request.POST.getlist('permissions[]') or []
        
        # Update the group
        group.name = name
        group.save()
        
        # Clear existing permissions
        group.permissions.clear()
        
        # Add new permissions
        for perm_id in permission_ids:
            permission = get_object_or_404(Permission, pk=perm_id)
            group.permissions.add(permission)
        
        messages.success(request, 'Role updated successfully!')
        return redirect('role_list')
    
    # Get all relevant permissions
    content_types = ContentType.objects.filter(Q(app_label='B4G') | Q(app_label='auth'))
    permissions = Permission.objects.filter(content_type__in=content_types)
    
    # Group permissions by model
    permissions_by_model = {}
    for ct in content_types:
        model_perms = permissions.filter(content_type=ct)
        if model_perms.exists():
            permissions_by_model[f"{ct.app_label}.{ct.model}"] = model_perms
    
    # Get the group's current permissions
    group_permissions = [p.id for p in group.permissions.all()]
    
    template = 'role/edit.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'role/ajax_edit.html'
        
    return render(request, template, {
        'group': group,
        'permissions': permissions,
        'permissions_by_model': permissions_by_model,
        'group_permissions': group_permissions
    })

@login_required
def role_delete(request, pk):
    """
    View to delete a role (group)
    """
    from django.contrib.auth.models import Group
    
    group = get_object_or_404(Group, pk=pk)
    group.delete()
    
    messages.success(request, 'Role deleted successfully!')
    return redirect('role_list')

@login_required
def assign_user_roles(request, user_id=None):
    """
    View to assign roles to users
    """
    from django.contrib.auth.models import Group
    
    if user_id:
        user = get_object_or_404(User, pk=user_id)
    else:
        user = None
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        group_ids = request.POST.getlist('groups[]') or []
        
        user = get_object_or_404(User, pk=user_id)
        
        # Clear existing groups
        user.groups.clear()
        
        # Add new groups
        for group_id in group_ids:
            group = get_object_or_404(Group, pk=group_id)
            user.groups.add(group)
        
        messages.success(request, 'User roles updated successfully!')
        return redirect('assign_user_roles')
    
    users = User.objects.all()
    groups = Group.objects.all()
    
    # If a specific user is selected, get their current groups
    user_groups = []
    if user:
        user_groups = [g.id for g in user.groups.all()]
    
    template = 'role/assign_user.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'role/ajax_assign_user.html'
        
    return render(request, template, {
        'users': users,
        'groups': groups,
        'selected_user': user,
        'user_groups': user_groups
    })

def lookup_barcode(request, barcode_number):
    """
    Simplified endpoint to look up a book by barcode number.
    Does not require login for faster lookup during scanning.
    """
    try:
        book = Books.objects.get(barcode_number=barcode_number)
        
        # Get author and category info
        authors = [ba.id_author.authorname for ba in Bookauthors.objects.filter(id_book=book)]
        categories = [bc.id_cat.catname for bc in Bookcategories.objects.filter(id_book=book)]
        
        # Format response
        response = {
            'success': True,
            'book': {
                'id': book.id,
                'description': book.description,
                'price': book.price,
                'publisher': book.id_pub.pubname if book.id_pub else None,
                'authors': authors,
                'categories': categories,
            }
        }
        
        return JsonResponse(response)
    except Books.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Book not found with barcode: {barcode_number}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
