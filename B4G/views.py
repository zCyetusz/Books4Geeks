from B4G.forms import LoginForm, RegistrationForm, UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count, Sum
from datetime import datetime, timedelta
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
from .smart_inventory import SmartInventoryManager, get_smart_inventory_alerts, get_book_restock_recommendation, get_inventory_dashboard_data
from .ai_image_recognition import process_book_cover_image, count_books_in_shelf, assess_book_damage, image_recognition
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
import tempfile
import uuid

# Create your views here.

# Authentication
def register(request):
  if request.method == 'POST':
    form = RegistrationForm(request.POST)
    if form.is_valid():
      try:
        user = form.save()
        messages.success(request, f'Account created successfully for {user.username}! You can now log in.')
        return redirect('/accounts/login/')
      except Exception as e:
        messages.error(request, f'Error creating account: {str(e)}')
    else:
      messages.error(request, 'Registration failed! Please check the form for errors.')
  else:
    form = RegistrationForm()
  
  context = {'form': form}
  return render(request, 'accounts/register.html', context)
  
def register_v1(request):
  if request.method == 'POST':
    form = RegistrationForm(request.POST)
    if form.is_valid():
      try:
        user = form.save()
        messages.success(request, f'Account created successfully for {user.username}! You can now log in.')
        return redirect('/accounts/login/')
      except Exception as e:
        messages.error(request, f'Error creating account: {str(e)}')
    else:
      messages.error(request, 'Registration failed! Please check the form for errors.')
  else:
    form = RegistrationForm()
  
  context = {'form': form}
  return render(request, 'pages/examples/register.html', context)

def register_v2(request):
  if request.method == 'POST':
    form = RegistrationForm(request.POST)
    if form.is_valid():
      try:
        user = form.save()
        messages.success(request, f'Account created successfully for {user.username}! You can now log in.')
        return redirect('/accounts/login/')
      except Exception as e:
        messages.error(request, f'Error creating account: {str(e)}')
    else:
      messages.error(request, 'Registration failed! Please check the form for errors.')
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
    from django.db.models import Sum, Count, Avg
    from decimal import Decimal
    from datetime import datetime, timedelta
    
    # Get current date and calculate date ranges
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Calculate key statistics
    # 1. Total Books in System
    total_books = Books.objects.count()
    
    # 2. Total Inventory from Bookshelves
    total_inventory = Bookshelves.objects.aggregate(
        total_qty=Sum('quantity')
    )['total_qty'] or 0
    
    # 3. Total Sales (from Bills)
    total_sales = Bills.objects.aggregate(
        total_amount=Sum('totalbill')
    )['total_amount'] or 0
    
    # 4. Total Customers
    total_customers = Customers.objects.count()
    
    # 5. Monthly Statistics
    monthly_bills = Bills.objects.filter(
        date__gte=thirty_days_ago
    ).count()
    
    monthly_revenue = Bills.objects.filter(
        date__gte=thirty_days_ago
    ).aggregate(
        revenue=Sum('totalbill')
    )['revenue'] or 0
    
    # 6. Recent Bills (Last 5)
    recent_bills = Bills.objects.select_related('id_cus').order_by('-date')[:5]
      # 7. Low Stock Books (quantity < 10)
    low_stock_books = Bookshelves.objects.select_related('id_book').exclude(
        quantity__isnull=True
    ).exclude(
        quantity=''
    ).order_by('quantity')[:5]
    
    # Filter low stock in Python since quantity is stored as string
    low_stock_filtered = []
    for item in low_stock_books:
        try:
            qty = int(item.quantity) if item.quantity else 0
            if qty < 10:
                low_stock_filtered.append(item)
        except (ValueError, TypeError):
            continue
    low_stock_books = low_stock_filtered[:5]
    
    # 8. Popular Books (most sold - from BillDetails)
    popular_books = Billdetails.objects.select_related('id_book').values(
        'id_book__bookname', 'id_book__id'
    ).annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]
    
    # 9. Recent Imports
    recent_imports = Imports.objects.select_related('id_book', 'id_pub').order_by('-lastmodified')[:5]
    
    # 10. Smart Inventory Dashboard Data
    try:
        inventory_dashboard_data = get_inventory_dashboard_data()
    except Exception as e:
        inventory_dashboard_data = {
            'critical_count': 0,
            'high_count': 0,
            'total_alerts': 0,
            'top_urgent_books': []
        }
    
    context = {
        'parent': 'dashboard',
        'segment': 'dashboardv1',
        # Key Statistics
        'total_books': total_books,
        'total_inventory': total_inventory,
        'total_sales': float(total_sales) if total_sales else 0,
        'total_customers': total_customers,
        'monthly_bills': monthly_bills,
        'monthly_revenue': float(monthly_revenue) if monthly_revenue else 0,
        # Data for widgets
        'recent_bills': recent_bills,
        'low_stock_books': low_stock_books,
        'popular_books': popular_books,
        'recent_imports': recent_imports,
        # Smart Inventory Data
        'inventory_alerts': inventory_dashboard_data
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
    imports = Imports.objects.all().select_related('id_book', 'id_pub')
    
    # Calculate statistics
    total_quantity = sum(imp.quantity for imp in imports)
    total_amount = sum(imp.total for imp in imports)
    avg_price = total_amount / len(imports) if imports else 0
    
    context = {
        'imports': imports,
        'total_quantity': total_quantity,
        'total_amount': total_amount,
        'avg_price': avg_price
    }
    return render(request, 'import/list.html', context)

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

@login_required
def import_edit(request, pk):
    import_record = get_object_or_404(Imports, pk=pk)
    if request.method == 'POST':
        old_quantity = import_record.quantity
        
        import_record.id_book = get_object_or_404(Books, pk=request.POST.get('id_book'))
        import_record.id_pub = get_object_or_404(Publishers, pk=request.POST.get('id_pub'))
        import_record.quantity = int(request.POST.get('quantity'))
        import_record.impprice = float(request.POST.get('impprice'))
        import_record.total = import_record.quantity * import_record.impprice
        import_record.save()
        
        # Update bookshelf quantity
        bookshelf = Bookshelves.objects.get_or_create(
            id_book=import_record.id_book,
            defaults={'quantity': 0}
        )[0]
        bookshelf.quantity = int(bookshelf.quantity) - int(old_quantity) + import_record.quantity
        bookshelf.save()
        
        messages.success(request, 'Import record updated successfully!')
        return redirect('import_list')
    
    books = Books.objects.all()
    publishers = Publishers.objects.all()
    return render(request, 'import/edit.html', {
        'import': import_record,
        'books': books,
        'publishers': publishers
    })

@login_required
def import_delete(request, pk):
    import_record = get_object_or_404(Imports, pk=pk)
    
    # Update bookshelf quantity
    try:
        bookshelf = Bookshelves.objects.get(id_book=import_record.id_book)
        bookshelf.quantity = max(0, int(bookshelf.quantity) - import_record.quantity)
        bookshelf.save()
    except Bookshelves.DoesNotExist:
        pass
    
    import_record.delete()
    messages.success(request, 'Import record deleted successfully!')
    return redirect('import_list')

@login_required
def import_detail(request, pk):
    import_record = get_object_or_404(Imports, pk=pk)
    return render(request, 'import/detail.html', {'import': import_record})

# Bill Views
@login_required
def bill_list(request):
    from django.core.paginator import Paginator
    
    # Get all bills with related customer data and prefetch related bill details
    bills_queryset = Bills.objects.select_related('id_cus').prefetch_related(
        'billdetails_set__id_book'
    ).order_by('-id')  # Order by newest first
    
    # Set up pagination - 20 bills per page
    paginator = Paginator(bills_queryset, 20)
    page_number = request.GET.get('page', 1)
    
    try:
        bills_page = paginator.get_page(page_number)
    except:
        bills_page = paginator.get_page(1)
    
    # Add bill details to each bill for template display
    for bill in bills_page:
        bill.details = bill.billdetails_set.all()
    
    template = 'bill/list.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'bill/ajax_list.html'
        
    context = {
        'bills': bills_page,
        'page_obj': bills_page,
        'is_paginated': bills_page.has_other_pages(),
        'paginator': paginator
    }
        
    return render(request, template, context)

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
                            'categories': categories,                            'scanned_by': 'manual'                        })
                    
                    request.session['scanned_books'] = scanned_books
                    messages.success(request, f"Added book: {book.description}")
                    
                    # Return JSON response for AJAX requests
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'message': f'Added book: {book.description}',                            'book': {
                                'id': book.id,
                                'description': book.description,
                                'price': str(book.price),
                                'quantity': 1,
                                'publisher': book.id_pub.pubname if book.id_pub else None,
                                'authors': authors,
                                'categories': categories,
                                'scanned_by': 'camera'
                            }
                        })
                    
                except Books.DoesNotExist:
                    messages.error(request, f"Book with barcode {barcode_number} not found")
                    # Return JSON response for AJAX requests
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'error': f'Book not found with barcode: {barcode_number}'
                        })
        
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
    if (desktop_scanned_books):
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
                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)            # Display the frame (with error handling for Windows/virtual environments)
            try:
                cv2.imshow("Books4Geeks Barcode Scanner", frame)
                
                # Break if 'c' is pressed or window is closed
                key = cv2.waitKey(1) & 0xFF
                if key == ord('c') or key == 27:  # 'c' or ESC key
                    break
                
                # Check if window was closed
                try:
                    if cv2.getWindowProperty("Books4Geeks Barcode Scanner", cv2.WND_PROP_VISIBLE) < 1:
                        break
                except cv2.error:
                    # Window property check failed, continue without it
                    pass
                    
            except cv2.error as cv_error:
                # GUI display not available (common in Windows/virtual environments)
                print(f"OpenCV GUI Error: {cv_error}")
                print("GUI display not available. Running in headless mode.")
                print("Scanner will process 30 frames and then stop.")
                
                # Process a limited number of frames without display
                import time
                time.sleep(0.1)  # Small delay to simulate real-time scanning
                
                # Counter to limit frames in headless mode
                if not hasattr(scan_barcode_desktop, 'headless_frame_count'):
                    scan_barcode_desktop.headless_frame_count = 0
                scan_barcode_desktop.headless_frame_count += 1
                
                # Stop after 30 frames in headless mode
                if scan_barcode_desktop.headless_frame_count >= 30:
                    print("Headless mode: Processed 30 frames, stopping scanner.")
                    break
          # Clean up
        cap.release()
        try:
            cv2.destroyAllWindows()
        except cv2.error:
            # Error destroying windows (common in headless mode)
            pass
        
        # Reset headless frame counter for next use
        if hasattr(scan_barcode_desktop, 'headless_frame_count'):
            delattr(scan_barcode_desktop, 'headless_frame_count')
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
    # Include both B4G and auth app permissions for comprehensive role management
    content_types = ContentType.objects.filter(Q(app_label='B4G') | Q(app_label='auth'))
    permissions = Permission.objects.filter(content_type__in=content_types)
    
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
        
        # Validate role name
        if not name or not name.strip():
            messages.error(request, 'Role name is required!')
            return redirect('role_create')
        
        # Check if role name already exists
        if Group.objects.filter(name=name.strip()).exists():
            messages.error(request, 'A role with this name already exists!')
            return redirect('role_create')
        
        try:
            # Create the group
            group = Group.objects.create(name=name.strip())
            
            # Add permissions to the group
            for perm_id in permission_ids:
                try:
                    permission = Permission.objects.get(pk=perm_id)
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    continue
            
            messages.success(request, f'Role "{group.name}" created successfully with {group.permissions.count()} permissions!')
            return redirect('role_list')
        except Exception as e:
            messages.error(request, f'Error creating role: {str(e)}')
            return redirect('role_create')
    
    # Get all relevant permissions
    content_types = ContentType.objects.filter(Q(app_label='B4G') | Q(app_label='auth'))
    permissions = Permission.objects.filter(content_type__in=content_types)
    
    # Group permissions by model
    permissions_by_model = {}
    for ct in content_types:
        model_perms = permissions.filter(content_type=ct)
        if model_perms.exists():
            permissions_by_model[ct.model] = model_perms
    
    template = 'role/create.html'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'role/ajax_create.html'
        
    return render(request, template, {
        'permissions': permissions,
        'permissions_by_model': permissions_by_model
    })
    
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
        
        # Validate role name
        if not name or not name.strip():
            messages.error(request, 'Role name is required!')
            return redirect('role_edit', pk=pk)
        
        # Check if role name already exists (excluding current role)
        if Group.objects.filter(name=name.strip()).exclude(pk=pk).exists():
            messages.error(request, 'A role with this name already exists!')
            return redirect('role_edit', pk=pk)
        
        try:
            # Update the group
            group.name = name.strip()
            group.save()
            
            # Clear existing permissions
            group.permissions.clear()
            
            # Add new permissions
            for perm_id in permission_ids:
                try:
                    permission = Permission.objects.get(pk=perm_id)
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    continue
            
            messages.success(request, f'Role "{group.name}" updated successfully with {group.permissions.count()} permissions!')
            return redirect('role_list')
        except Exception as e:
            messages.error(request, f'Error updating role: {str(e)}')
            return redirect('role_edit', pk=pk)
    
    # Get all relevant permissions
    content_types = ContentType.objects.filter(Q(app_label='B4G') | Q(app_label='auth'))
    permissions = Permission.objects.filter(content_type__in=content_types)
    
    # Group permissions by model
    permissions_by_model = {}
    for ct in content_types:
        model_perms = permissions.filter(content_type=ct)
        if model_perms.exists():
            permissions_by_model[ct.model] = model_perms
    
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
    
    # Check if any users are assigned to this role
    users_count = group.user_set.count()
    if users_count > 0:
        messages.warning(request, f'Cannot delete role "{group.name}" because {users_count} user(s) are assigned to it. Please remove users from this role first.')
        return redirect('role_list')
    
    group_name = group.name
    try:
        group.delete()
        messages.success(request, f'Role "{group_name}" deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting role: {str(e)}')
    
    return redirect('role_list')

@login_required
def assign_user_roles(request, user_id=None):
    """
    View to assign roles to users
    """
    from django.contrib.auth.models import Group
    from django.http import JsonResponse
    
    # Handle AJAX requests for user data
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.GET.get('ajax_user_id'):
        ajax_user_id = request.GET.get('ajax_user_id')
        ajax_user = get_object_or_404(User, pk=ajax_user_id)
        user_groups = [g.id for g in ajax_user.groups.all()]
        return JsonResponse({
            'success': True,
            'user': {
                'id': ajax_user.id,
                'username': ajax_user.username,
                'email': ajax_user.email,
                'full_name': ajax_user.get_full_name(),
                'is_active': ajax_user.is_active,
            },
            'user_groups': user_groups
        })
    
    # Set user if provided via URL parameter
    if user_id:
        user = get_object_or_404(User, pk=user_id)
    else:
        user = None
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        group_ids = request.POST.getlist('groups[]') or []
        
        if not user_id:
            messages.error(request, 'Please select a user!')
            return redirect('assign_user_roles')
        
        user = get_object_or_404(User, pk=user_id)
        
        try:
            # Clear existing groups
            user.groups.clear()
            
            # Add new groups
            for group_id in group_ids:
                try:
                    group = Group.objects.get(pk=group_id)
                    user.groups.add(group)
                except Group.DoesNotExist:
                    continue
            
            role_count = user.groups.count()
            if role_count > 0:
                messages.success(request, f'User "{user.get_full_name() or user.username}" roles updated successfully! Assigned {role_count} role(s).')
            else:
                messages.success(request, f'All roles removed from user "{user.get_full_name() or user.username}".')
            
            return redirect('assign_user_roles', user_id=user.id)
        except Exception as e:
            messages.error(request, f'Error updating user roles: {str(e)}')
            return redirect('assign_user_roles')
    
    users = User.objects.all().order_by('username')
    groups = Group.objects.all().order_by('name')
    
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

# Advanced Reports and Analytics Views
@login_required
def reports(request):
    from django.db.models import Sum, Count, Avg, F
    from django.http import HttpResponse, JsonResponse
    from datetime import datetime, timedelta
    import json
    import csv
    
    # Get filter parameters
    start_date = request.GET.get('start_date') or request.POST.get('start_date')
    end_date = request.GET.get('end_date') or request.POST.get('end_date')
    report_type = request.GET.get('report_type') or request.POST.get('report_type', 'sales')
    export_type = request.GET.get('export')
    format_type = request.GET.get('format', 'html')
    
    # Default date range (last 30 days)
    if not start_date:
        start_date = (timezone.now() - timedelta(days=30)).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Calculate summary statistics
    total_revenue = Bills.objects.filter(
        date__range=[start_date, end_date]
    ).aggregate(total=Sum('totalbill'))['total'] or 0
    
    total_bills = Bills.objects.filter(
        date__range=[start_date, end_date]
    ).count()
    
    monthly_revenue = Bills.objects.filter(
        date__gte=timezone.now().date() - timedelta(days=30)
    ).aggregate(total=Sum('totalbill'))['total'] or 0
    
    monthly_bills = Bills.objects.filter(
        date__gte=timezone.now().date() - timedelta(days=30)
    ).count()
    
    total_imports = Imports.objects.filter(
        lastmodified__range=[start_date, end_date]
    ).count()
    
    total_import_value = Imports.objects.filter(
        lastmodified__range=[start_date, end_date]
    ).aggregate(total=Sum('total'))['total'] or 0
    
    avg_bill_amount = Bills.objects.filter(
        date__range=[start_date, end_date]
    ).aggregate(avg=Avg('totalbill'))['avg'] or 0
    
    # Top selling books
    top_books = Billdetails.objects.filter(
        id_bill__date__range=[start_date, end_date]
    ).values(
        'id_book__bookname'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('price'))
    ).order_by('-total_sold')[:10]
    
    # Top customers
    top_customers = Bills.objects.filter(
        date__range=[start_date, end_date]
    ).values(
        'id_cus__cusname'
    ).annotate(
        bill_count=Count('id'),
        total_spent=Sum('totalbill')
    ).order_by('-total_spent')[:10]
    
    # Monthly revenue data for chart (last 12 months)
    month_labels = []
    revenue_data = []
    for i in range(11, -1, -1):
        month_start = (timezone.now().replace(day=1) - timedelta(days=32*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        month_revenue = Bills.objects.filter(
            date__range=[month_start, month_end]
        ).aggregate(total=Sum('totalbill'))['total'] or 0
        
        month_labels.append(month_start.strftime('%b %Y'))
        revenue_data.append(float(month_revenue))
    
    # Category data for pie chart
    category_labels = []
    category_data = []
    categories = Categories.objects.all()[:6]  # Top 6 categories
    
    for category in categories:
        # Get books in this category
        book_ids = Bookcategories.objects.filter(id_cat=category).values_list('id_book', flat=True)
        
        # Calculate sales for these books
        category_sales = Billdetails.objects.filter(
            id_book__in=book_ids,
            id_bill__date__range=[start_date, end_date]
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        category_labels.append(category.catname or 'Unknown')
        category_data.append(category_sales)
    
    # Handle export requests
    if export_type and format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        
        if export_type == 'top_books':
            response['Content-Disposition'] = 'attachment; filename="top_books.csv"'
            writer = csv.writer(response)
            writer.writerow(['Rank', 'Book Name', 'Total Sold', 'Total Revenue'])
            for i, book in enumerate(top_books, 1):
                writer.writerow([
                    i,
                    book['id_book__bookname'],
                    book['total_sold'],
                    f"${book['total_revenue']:.2f}"
                ])
            return response
            
        elif export_type == 'top_customers':
            response['Content-Disposition'] = 'attachment; filename="top_customers.csv"'
            writer = csv.writer(response)
            writer.writerow(['Rank', 'Customer Name', 'Bill Count', 'Total Spent'])
            for i, customer in enumerate(top_customers, 1):
                writer.writerow([
                    i,
                    customer['id_cus__cusname'],
                    customer['bill_count'],
                    f"${customer['total_spent']:.2f}"
                ])
            return response
    
    context = {
        'parent': 'reports',
        'segment': 'reports',
        # Summary data
        'total_revenue': float(total_revenue),
        'total_bills': total_bills,
        'monthly_revenue': float(monthly_revenue),
        'monthly_bills': monthly_bills,
        'total_imports': total_imports,
        'total_import_value': float(total_import_value),
        'avg_bill_amount': float(avg_bill_amount),
        # Chart data
        'month_labels': json.dumps(month_labels),
        'revenue_data': json.dumps(revenue_data),
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
        # Table data
        'top_books': top_books,
        'top_customers': top_customers,
        # Filter values
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'report_type': report_type,
    }
    
    return render(request, 'pages/reports.html', context)

@login_required
def advanced_search(request):
    """
    Advanced search view with multiple filter options and search types
    """
    from django.db.models import Q, Sum, Count, Avg
    from django.http import HttpResponse, JsonResponse
    from datetime import datetime, timedelta
    import json
    import csv
    
    # Initialize search parameters
    query = request.GET.get('query', '')
    search_type = request.GET.get('search_type', 'all')
    category_id = request.GET.get('category')
    author_id = request.GET.get('author')
    publisher_id = request.GET.get('publisher')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    sort_by = request.GET.get('sort_by', 'relevance')
    export_format = request.GET.get('export')
    
    # Initialize result containers
    books_results = []
    authors_results = []
    categories_results = []
    publishers_results = []
    customers_results = []
    total_results = 0
    
    # Build search filters
    search_filters = Q()
    
    if query:
        # Create search filters based on query
        book_filters = Q(bookname__icontains=query) | Q(description__icontains=query) | Q(barcode_number__icontains=query)
        author_filters = Q(authorname__icontains=query) | Q(description__icontains=query)
        category_filters = Q(catname__icontains=query) | Q(description__icontains=query)
        publisher_filters = Q(pubname__icontains=query) | Q(description__icontains=query)
        customer_filters = Q(cusname__icontains=query) | Q(phone__icontains=query)
        
        # Search Books
        if search_type in ['all', 'books']:
            books_query = Books.objects.filter(book_filters)
            
            # Apply additional filters
            if category_id:
                book_category_ids = Bookcategories.objects.filter(id_cat=category_id).values_list('id_book', flat=True)
                books_query = books_query.filter(id__in=book_category_ids)
            
            if author_id:
                book_author_ids = Bookauthors.objects.filter(id_author=author_id).values_list('id_book', flat=True)
                books_query = books_query.filter(id__in=book_author_ids)
            
            if publisher_id:
                books_query = books_query.filter(id_pub=publisher_id)
            
            if price_min:
                try:
                    books_query = books_query.filter(price__gte=float(price_min))
                except (ValueError, TypeError):
                    pass
            
            if price_max:
                try:
                    books_query = books_query.filter(price__lte=float(price_max))
                except (ValueError, TypeError):
                    pass
            
            if date_from:
                try:
                    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                    books_query = books_query.filter(publishdate__gte=date_from_obj)
                except ValueError:
                    pass
            
            if date_to:
                try:
                    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                    books_query = books_query.filter(publishdate__lte=date_to_obj)
                except ValueError:
                    pass
            
            # Add related data to books
            for book in books_query.select_related('id_pub')[:50]:  # Limit results
                # Get authors
                book_authors = Bookauthors.objects.filter(id_book=book).select_related('id_author')
                authors_list = [ba.id_author.authorname for ba in book_authors if ba.id_author.authorname]
                
                # Get categories
                book_categories = Bookcategories.objects.filter(id_book=book).select_related('id_cat')
                categories_list = [bc.id_cat.catname for bc in book_categories if bc.id_cat.catname]
                
                # Get sales data
                total_sold = Billdetails.objects.filter(id_book=book).aggregate(
                    total=Sum('quantity')
                )['total'] or 0
                
                books_results.append({
                    'id': book.id,
                    'title': book.bookname or 'Unknown Title',
                    'description': book.description or '',
                    'price': book.price or 0,
                    'publisher': book.id_pub.pubname if book.id_pub else 'Unknown Publisher',
                    'publish_date': book.publishdate,
                    'authors': authors_list,
                    'categories': categories_list,
                    'barcode': book.barcode_number,
                    'total_sold': total_sold,
                    'type': 'book'
                })
        
        # Search Authors
        if search_type in ['all', 'authors']:
            authors_query = Authors.objects.filter(author_filters)
            
            for author in authors_query[:20]:  # Limit results
                # Get books by this author
                author_books = Bookauthors.objects.filter(id_author=author).count()
                
                authors_results.append({
                    'id': author.id,
                    'name': author.authorname or 'Unknown Author',
                    'description': author.description or '',
                    'books_count': author_books,
                    'last_modified': author.lastmodified,
                    'type': 'author'
                })
        
        # Search Categories
        if search_type in ['all', 'categories']:
            categories_query = Categories.objects.filter(category_filters)
            
            for category in categories_query[:20]:  # Limit results
                # Get books in this category
                category_books = Bookcategories.objects.filter(id_cat=category).count()
                
                categories_results.append({
                    'id': category.id,
                    'name': category.catname or 'Unknown Category',
                    'description': category.description or '',
                    'books_count': category_books,
                    'last_modified': category.lastmodified,
                    'type': 'category'
                })
        
        # Search Publishers
        if search_type in ['all', 'publishers']:
            publishers_query = Publishers.objects.filter(publisher_filters)
            
            for publisher in publishers_query[:20]:  # Limit results
                # Get books by this publisher
                publisher_books = Books.objects.filter(id_pub=publisher).count()
                
                publishers_results.append({
                    'id': publisher.id,
                    'name': publisher.pubname or 'Unknown Publisher',
                    'description': publisher.description or '',
                    'books_count': publisher_books,
                    'last_modified': publisher.lastmodified,
                    'type': 'publisher'
                })
        
        # Search Customers (if admin/employee)
        if search_type in ['all', 'customers'] and request.user.is_staff:
            customers_query = Customers.objects.filter(customer_filters)
            
            for customer in customers_query[:20]:  # Limit results                # Get customer purchase history
                customer_bills = Bills.objects.filter(id_cus=customer).count()
                total_spent = Bills.objects.filter(id_cus=customer).aggregate(
                    total=Sum('totalbill')
                )['total'] or 0
                
                customers_results.append({
                    'id': customer.id,
                    'name': customer.cusname or 'Unknown Customer',
                    'phone': customer.phone or '',
                    'gender': customer.gender or '',
                    'bills_count': customer_bills,
                    'total_spent': total_spent,
                    'type': 'customer'
                })
    
    # Calculate total results
    total_results = len(books_results) + len(authors_results) + len(categories_results) + len(publishers_results) + len(customers_results)
    
    # Sort results
    if sort_by == 'name':
        books_results.sort(key=lambda x: x['title'].lower())
        authors_results.sort(key=lambda x: x['name'].lower())
        categories_results.sort(key=lambda x: x['name'].lower())
        publishers_results.sort(key=lambda x: x['name'].lower())
        customers_results.sort(key=lambda x: x['name'].lower())
    elif sort_by == 'date':
        books_results.sort(key=lambda x: x['publish_date'] or datetime.min.date(), reverse=True)
        authors_results.sort(key=lambda x: x['last_modified'] or datetime.min, reverse=True)
        categories_results.sort(key=lambda x: x['last_modified'] or datetime.min, reverse=True)
        publishers_results.sort(key=lambda x: x['last_modified'] or datetime.min, reverse=True)
    elif sort_by == 'popularity':
        books_results.sort(key=lambda x: x['total_sold'], reverse=True)
        authors_results.sort(key=lambda x: x['books_count'], reverse=True)
        categories_results.sort(key=lambda x: x['books_count'], reverse=True)
        publishers_results.sort(key=lambda x: x['books_count'], reverse=True)
    
    # Handle export requests
    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="search_results_{search_type}.csv"'
        writer = csv.writer(response)
        
        if search_type in ['all', 'books'] and books_results:
            writer.writerow(['Type', 'Title', 'Authors', 'Publisher', 'Price', 'Categories', 'Total Sold'])
            for book in books_results:
                writer.writerow([
                    'Book',
                    book['title'],
                    ', '.join(book['authors']),
                    book['publisher'],
                    book['price'],
                    ', '.join(book['categories']),
                    book['total_sold']
                ])
        
        if search_type in ['all', 'authors'] and authors_results:
            writer.writerow(['Type', 'Name', 'Description', 'Books Count'])
            for author in authors_results:
                writer.writerow([
                    'Author',
                    author['name'],
                    author['description'],
                    author['books_count']
                ])
        
        return response
    
    # Prepare form data for filters
    all_categories = Categories.objects.all().order_by('catname')
    all_authors = Authors.objects.all().order_by('authorname')
    all_publishers = Publishers.objects.all().order_by('pubname')
    
    # Create search statistics
    search_stats = {
        'total_results': total_results,
        'books_count': len(books_results),
        'authors_count': len(authors_results),
        'categories_count': len(categories_results),
        'publishers_count': len(publishers_results),
        'customers_count': len(customers_results),
        'search_time': '0.05',  # Mock search time
    }
    
    context = {
        'parent': 'search',
        'segment': 'advanced_search',
        
        # Search parameters
        'query': query,
        'search_type': search_type,
        'category_id': int(category_id) if category_id else None,
        'author_id': int(author_id) if author_id else None,
        'publisher_id': int(publisher_id) if publisher_id else None,
        'price_min': price_min,
        'price_max': price_max,
        'date_from': date_from,
        'date_to': date_to,
        'sort_by': sort_by,
        
        # Search results
        'books_results': books_results,
        'authors_results': authors_results,
        'categories_results': categories_results,
        'publishers_results': publishers_results,
        'customers_results': customers_results,
        'search_stats': search_stats,
        
        # Form data
        'all_categories': all_categories,
        'all_authors': all_authors,
        'all_publishers': all_publishers,
        
        # UI flags
        'has_results': total_results > 0,
        'show_customers': request.user.is_staff,
    }
    
    return render(request, 'pages/advanced_search.html', context)

@login_required
def get_ai_recommendations(request):
    """
    AI-powered book recommendations using Gemini API
    """
    from django.http import JsonResponse
    import json
    
    book_id = request.GET.get('book_id')
    user_interests = request.GET.get('interests', '')
    recommendation_type = request.GET.get('type', 'similar')  # similar, related, trending
    
    try:
        # Get book details if book_id is provided
        book_context = ""
        if (book_id):
            try:
                book = Books.objects.get(id=book_id)
                # Get book authors and categories
                authors = Bookauthors.objects.filter(id_book=book).select_related('id_author')
                categories = Bookcategories.objects.filter(id_book=book).select_related('id_cat')
                
                author_names = [ba.id_author.authorname for ba in authors if ba.id_author.authorname]
                category_names = [bc.id_cat.catname for bc in categories if bc.id_cat.catname]
                
                book_context = f"""
                Book: {book.bookname or 'Unknown'}
                Description: {book.description or 'No description'}
                Authors: {', '.join(author_names)}
                Categories: {', '.join(category_names)}
                Publisher: {book.id_pub.pubname if book.id_pub else 'Unknown'}
                """
            except Books.DoesNotExist:
                book_context = "Book not found."
        
        # Prepare AI prompt based on recommendation type
        if recommendation_type == 'similar':
            prompt = f"""
            Based on this book information:
            {book_context}
            
            User interests: {user_interests}
            
            Please recommend 5 similar books that would appeal to someone who liked this book. 
            Consider the genre, themes, writing style, and target audience.
            
            Format your response as a JSON array with the following structure:
            [
                {{
                    "title": "Book Title",
                    "author": "Author Name",
                    "reason": "Brief explanation why this book is recommended",
                    "genre": "Genre",
                    "rating": "Estimated rating out of 5"
                }}
            ]
            
            Only return the JSON array, no additional text.
            """
        elif recommendation_type == 'trending':
            prompt = f"""
            Based on current trends in literature and these user interests: {user_interests}
            
            Please recommend 5 trending/popular books that are currently popular among readers.
            Consider recent publications, award winners, and books gaining attention.
            
            Format your response as a JSON array with the following structure:
            [
                {{
                    "title": "Book Title",
                    "author": "Author Name",
                    "reason": "Why this book is trending",
                    "genre": "Genre",
                    "rating": "Estimated rating out of 5"
                }}
            ]
            
            Only return the JSON array, no additional text.
            """
        else:  # related
            prompt = f"""
            Based on this book:
            {book_context}
            
            And user interests: {user_interests}
            
            Please recommend 5 books that are thematically related or would be good follow-up reads.
            Consider books that explore similar themes, historical periods, or philosophical questions.
            
            Format your response as a JSON array with the following structure:
            [
                {{
                    "title": "Book Title",
                    "author": "Author Name", 
                    "reason": "How this relates to the original book",
                    "genre": "Genre",
                    "rating": "Estimated rating out of 5"
                }}
            ]
            
            Only return the JSON array, no additional text.
            """
        
        # Configure Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        
        # Generate recommendations
        response = model.generate_content(prompt)
        ai_response = response.text.strip()
        
        # Try to parse the JSON response
        try:
            # Clean up the response to extract JSON
            if ai_response.startswith('```json'):
                ai_response = ai_response.replace('```json', '').replace('```', '').strip()
            elif ai_response.startswith('```'):
                ai_response = ai_response.replace('```', '').strip()
                
            recommendations = json.loads(ai_response)
            
            return JsonResponse({
                'success': True,
                'recommendations': recommendations,
                'type': recommendation_type,
                'book_context': book_context if book_id else None
            })
            
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw response
            return JsonResponse({
                'success': False,
                'error': 'Failed to parse AI response',
                'raw_response': ai_response
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# Smart Inventory Views
@login_required
def inventory_alerts(request):
    """Display smart inventory alerts dashboard"""
    try:
        manager = SmartInventoryManager()
        
        # Get filter parameters
        urgency_filter = request.GET.get('urgency', 'all')
        publisher_filter = request.GET.get('publisher', 'all')
        
        # Get all recommendations
        all_recommendations = manager.smart_restock_alert()
        
        # Apply filters
        filtered_recommendations = all_recommendations
        
        if urgency_filter != 'all':
            filtered_recommendations = [
                r for r in filtered_recommendations 
                if r['urgency_level'].lower() == urgency_filter.lower()
            ]
        
        if publisher_filter != 'all':
            filtered_recommendations = [
                r for r in filtered_recommendations 
                if r['publisher_name'] == publisher_filter
            ]
        
        # Get unique publishers for filter dropdown
        publishers = list(set(r['publisher_name'] for r in all_recommendations))
        publishers.sort()
        
        # Generate summary stats
        summary_stats = {
            'total_alerts': len(all_recommendations),
            'critical_count': len([r for r in all_recommendations if r['urgency_level'] == 'CRITICAL']),
            'high_count': len([r for r in all_recommendations if r['urgency_level'] == 'HIGH']),
            'medium_count': len([r for r in all_recommendations if r['urgency_level'] == 'MEDIUM']),
            'low_count': len([r for r in all_recommendations if r['urgency_level'] == 'LOW']),
            'total_suggested_qty': sum(r['suggested_order_qty'] for r in all_recommendations)
        }
        
        context = {
            'parent': 'inventory',
            'segment': 'alerts',
            'recommendations': filtered_recommendations,
            'summary_stats': summary_stats,
            'publishers': publishers,
            'current_urgency_filter': urgency_filter,
            'current_publisher_filter': publisher_filter,
            'urgency_levels': ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        }
        
        return render(request, 'inventory/alerts.html', context)
        
    except Exception as e:
        messages.error(request, f'Error generating inventory alerts: {str(e)}')
        return render(request, 'inventory/alerts.html', {
            'parent': 'inventory',
            'segment': 'alerts',
            'recommendations': [],
            'summary_stats': {},
            'publishers': [],
            'error': str(e)
        })

@login_required
def inventory_analytics(request):
    """Display inventory analytics and patterns"""
    try:
        manager = SmartInventoryManager()
        
        # Get book ID from request (if analyzing specific book)
        book_id = request.GET.get('book_id')
        
        if book_id:
            try:
                book = Books.objects.get(id=book_id)
                
                # Analyze specific book
                velocity_data = manager.calculate_sales_velocity(book_id)
                seasonal_data = manager.analyze_seasonal_patterns(book_id)
                lead_time_data = manager.calculate_supplier_lead_time(book.id_pub.id)
                recommendation = get_book_restock_recommendation(book_id)
                
                context = {
                    'parent': 'inventory',
                    'segment': 'analytics',
                    'book': book,
                    'velocity_data': velocity_data,
                    'seasonal_data': seasonal_data,
                    'lead_time_data': lead_time_data,
                    'recommendation': recommendation,
                    'analyzing_specific_book': True
                }
                
            except Books.DoesNotExist:
                messages.error(request, 'Book not found')
                return redirect('inventory_analytics')
        else:
            # General analytics overview
            report = manager.generate_inventory_report()
            
            # Get top performing books by velocity
            recent_books = Billdetails.objects.filter(
                id_bill__date__gte=timezone.now().date() - timedelta(days=30)
            ).values('id_book').annotate(
                total_sold=Sum('quantity')
            ).order_by('-total_sold')[:10]
            
            top_books_data = []
            for book_data in recent_books:
                try:
                    book = Books.objects.get(id=book_data['id_book'])
                    velocity = manager.calculate_sales_velocity(book.id)
                    top_books_data.append({
                        'book': book,
                        'total_sold': book_data['total_sold'],
                        'velocity_data': velocity
                    })
                except Books.DoesNotExist:
                    continue
            
            context = {
                'parent': 'inventory',
                'segment': 'analytics',
                'report': report,
                'top_books_data': top_books_data,
                'analyzing_specific_book': False
            }
        
        return render(request, 'inventory/analytics.html', context)
        
    except Exception as e:
        messages.error(request, f'Error generating analytics: {str(e)}')
        return render(request, 'inventory/analytics.html', {
            'parent': 'inventory',
            'segment': 'analytics',
            'error': str(e)
        })

@login_required
def book_velocity_analysis(request, book_id):
    """AJAX endpoint for book velocity analysis"""
    try:
        manager = SmartInventoryManager()
        book = Books.objects.get(id=book_id)
        
        # Get different time periods
        velocity_7d = manager.calculate_sales_velocity(book_id, days=7)
        velocity_30d = manager.calculate_sales_velocity(book_id, days=30)
        velocity_90d = manager.calculate_sales_velocity(book_id, days=90)
        
        seasonal_data = manager.analyze_seasonal_patterns(book_id)
        recommendation = get_book_restock_recommendation(book_id)
        
        data = {
            'book_id': book_id,
            'book_name': book.bookname or f"Book {book_id}",
            'velocity_analysis': {
                '7_days': velocity_7d,
                '30_days': velocity_30d,
                '90_days': velocity_90d
            },
            'seasonal_analysis': seasonal_data,
            'recommendation': recommendation,
            'success': True
        }
        
        return JsonResponse(data)
        
    except Books.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Book not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def generate_purchase_order(request):
    """Generate purchase order based on inventory alerts"""
    if request.method == 'POST':
        try:
            # Get selected book IDs from form
            selected_books = request.POST.getlist('selected_books')
            
            if not selected_books:
                messages.warning(request, 'Please select at least one book for purchase order.')
                return redirect('inventory_alerts')
            
            manager = SmartInventoryManager()
            recommendations = manager.smart_restock_alert()
            
            # Filter recommendations for selected books
            selected_recommendations = [
                r for r in recommendations 
                if str(r['book_id']) in selected_books
            ]
            
            # Group by publisher for organized purchase orders
            purchase_orders = manager._group_alerts_by_publisher(selected_recommendations)
            
            context = {
                'parent': 'inventory',
                'segment': 'purchase_order',
                'purchase_orders': purchase_orders,
                'total_items': len(selected_recommendations),
                'total_quantity': sum(r['suggested_order_qty'] for r in selected_recommendations),
                'generated_date': timezone.now().date()
            }
            
            return render(request, 'inventory/purchase_order.html', context)
            
        except Exception as e:
            messages.error(request, f'Error generating purchase order: {str(e)}')
            return redirect('inventory_alerts')
    
    return redirect('inventory_alerts')

@login_required
def inventory_api_alerts(request):
    """API endpoint for getting inventory alerts (for AJAX)"""
    try:
        manager = SmartInventoryManager()
        recommendations = manager.smart_restock_alert()
        
        # Limit to top 20 most urgent
        top_recommendations = recommendations[:20]
        
        return JsonResponse({
            'success': True,
            'alerts': top_recommendations,
            'total_count': len(recommendations),
            'critical_count': len([r for r in recommendations if r['urgency_level'] == 'CRITICAL']),
            'high_count': len([r for r in recommendations if r['urgency_level'] == 'HIGH'])
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# ============================
# AI IMAGE RECOGNITION VIEWS
# ============================

@login_required
def ai_image_recognition_dashboard(request):
    """Main dashboard for AI Image Recognition features"""
    try:
        # Get recent AI analyses
        recent_analyses = Books.objects.filter(
            last_ai_analysis__isnull=False
        ).order_by('-last_ai_analysis')[:10]
        
        # Get damage statistics
        damage_stats = Books.objects.filter(
            damage_status__isnull=False
        ).values('damage_status').annotate(count=Count('id'))
        
        # Get AI confidence statistics
        high_confidence = Books.objects.filter(ai_confidence_score__gte=0.8).count()
        medium_confidence = Books.objects.filter(
            ai_confidence_score__gte=0.5, 
            ai_confidence_score__lt=0.8
        ).count()
        low_confidence = Books.objects.filter(ai_confidence_score__lt=0.5).count()
        
        context = {
            'parent': 'ai_recognition',
            'segment': 'dashboard',
            'recent_analyses': recent_analyses,
            'damage_stats': damage_stats,
            'confidence_stats': {
                'high': high_confidence,
                'medium': medium_confidence,
                'low': low_confidence
            },
            'total_analyzed': Books.objects.filter(last_ai_analysis__isnull=False).count()
        }
        
        return render(request, 'ai_recognition/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading AI dashboard: {str(e)}')
        return redirect('index')

@login_required
@require_http_methods(["GET", "POST"])
def book_cover_analyzer(request):
    """Book cover analysis interface"""
    if request.method == 'POST':
        try:
            if 'cover_image' not in request.FILES:
                return JsonResponse({'success': False, 'error': 'No image provided'})
            
            uploaded_file = request.FILES['cover_image']
            
            # Save uploaded file temporarily
            temp_filename = f"temp_cover_{uuid.uuid4()}.{uploaded_file.name.split('.')[-1]}"
            temp_path = default_storage.save(f"temp/{temp_filename}", uploaded_file)
            
            try:
                # Process the image
                full_path = default_storage.path(temp_path)
                result = process_book_cover_image(full_path)
                
                # If processing successful, save to book if book_id provided
                if result['success'] and request.POST.get('book_id'):
                    book_id = request.POST.get('book_id')
                    book = get_object_or_404(Books, id=book_id)
                    
                    # Update book with AI analysis
                    book.cover_image = uploaded_file
                    book.ai_extracted_title = result['book_info']['title']
                    book.ai_extracted_authors = json.dumps(result['book_info']['authors'])
                    book.ai_suggested_category = result['suggested_category']
                    book.ai_confidence_score = result['book_info']['confidence']
                    book.damage_status = result['damage_assessment']['severity']
                    book.damage_details = json.dumps(result['damage_assessment'])
                    book.last_ai_analysis = django_timezone.now()
                    book.save()
                    
                    result['book_updated'] = True
                
                return JsonResponse(result)
                
            finally:
                # Clean up temporary file
                if default_storage.exists(temp_path):
                    default_storage.delete(temp_path)
                    
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    else:
        # GET request - show the interface
        context = {
            'parent': 'ai_recognition',
            'segment': 'cover_analyzer',
            'books': Books.objects.all()[:100]  # For selection dropdown
        }
        
        return render(request, 'ai_recognition/cover_analyzer.html', context)

@login_required
@require_http_methods(["GET", "POST"])
def inventory_counter(request):
    """Inventory counting through image recognition"""
    if request.method == 'POST':
        try:
            if 'shelf_image' not in request.FILES:
                return JsonResponse({'success': False, 'error': 'No image provided'})
            
            uploaded_file = request.FILES['shelf_image']
            
            # Save uploaded file temporarily
            temp_filename = f"temp_shelf_{uuid.uuid4()}.{uploaded_file.name.split('.')[-1]}"
            temp_path = default_storage.save(f"temp/{temp_filename}", uploaded_file)
            
            try:
                # Count books in the image
                full_path = default_storage.path(temp_path)
                result = count_books_in_shelf(full_path)
                
                # Add shelf information if provided
                if request.POST.get('shelf_id'):
                    shelf_id = request.POST.get('shelf_id')
                    shelf = get_object_or_404(Shelves, id=shelf_id)
                    result['shelf_name'] = shelf.shelfname
                    result['area_name'] = shelf.id_area.areaname if shelf.id_area else 'Unknown'
                
                return JsonResponse(result)
                
            finally:
                # Clean up temporary file
                if default_storage.exists(temp_path):
                    default_storage.delete(temp_path)
                    
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    else:
        # GET request - show the interface
        context = {
            'parent': 'ai_recognition',
            'segment': 'inventory_counter',
            'shelves': Shelves.objects.all()  # For selection dropdown
        }
        
        return render(request, 'ai_recognition/inventory_counter.html', context)

@login_required
@require_http_methods(["GET", "POST"])
def damage_assessor(request):
    """Book damage assessment interface"""
    if request.method == 'POST':
        try:
            if 'book_image' not in request.FILES:
                return JsonResponse({'success': False, 'error': 'No image provided'})
            
            uploaded_file = request.FILES['book_image']
            
            # Save uploaded file temporarily
            temp_filename = f"temp_damage_{uuid.uuid4()}.{uploaded_file.name.split('.')[-1]}"
            temp_path = default_storage.save(f"temp/{temp_filename}", uploaded_file)
            
            try:
                # Assess damage
                full_path = default_storage.path(temp_path)
                result = assess_book_damage(full_path)
                
                # Update book record if book_id provided
                if result['success'] and request.POST.get('book_id'):
                    book_id = request.POST.get('book_id')
                    book = get_object_or_404(Books, id=book_id)
                    
                    damage_info = result['damage_assessment']
                    book.damage_status = damage_info['severity']
                    book.damage_details = json.dumps(damage_info)
                    book.last_ai_analysis = django_timezone.now()
                    book.save()
                    
                    result['book_updated'] = True
                
                return JsonResponse(result)
                
            finally:
                # Clean up temporary file
                if default_storage.exists(temp_path):
                    default_storage.delete(temp_path)
                    
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    else:
        # GET request - show the interface
        context = {
            'parent': 'ai_recognition',
            'segment': 'damage_assessor',
            'books': Books.objects.all()[:100]  # For selection dropdown
        }
        
        return render(request, 'ai_recognition/damage_assessor.html', context)

@login_required
def auto_categorizer(request):
    """Auto-categorization management interface"""
    try:
        # Get books that need categorization (no category assigned)
        uncategorized_books = Books.objects.filter(
            Q(ai_suggested_category__isnull=True) | Q(ai_suggested_category='')
        ).filter(cover_image__isnull=False)[:50]
        
        # Get recently categorized books
        recently_categorized = Books.objects.filter(
            ai_suggested_category__isnull=False
        ).exclude(ai_suggested_category='').order_by('-last_ai_analysis')[:20]
        
        # Get category statistics
        category_stats = Books.objects.filter(
            ai_suggested_category__isnull=False
        ).exclude(ai_suggested_category='').values(
            'ai_suggested_category'
        ).annotate(count=Count('id')).order_by('-count')
        
        context = {
            'parent': 'ai_recognition',
            'segment': 'auto_categorizer',
            'uncategorized_books': uncategorized_books,
            'recently_categorized': recently_categorized,
            'category_stats': category_stats,
            'available_categories': Categories.objects.all()
        }
        
        return render(request, 'ai_recognition/auto_categorizer.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading categorizer: {str(e)}')
        return redirect('ai_image_recognition_dashboard')

@csrf_exempt
@login_required
def batch_categorize_books(request):
    """Batch categorize books using AI"""
    if request.method == 'POST':
        try:
            book_ids = request.POST.getlist('book_ids')
            
            if not book_ids:
                return JsonResponse({'success': False, 'error': 'No books selected'})
            
            results = []
            
            for book_id in book_ids:
                try:
                    book = get_object_or_404(Books, id=book_id)
                    
                    if not book.cover_image:
                        results.append({
                            'book_id': book_id,
                            'success': False,
                            'error': 'No cover image'
                        })
                        continue
                    
                    # Process the cover image
                    image_path = book.cover_image.path
                    result = process_book_cover_image(image_path)
                    
                    if result['success']:
                        # Update book with AI analysis
                        book.ai_extracted_title = result['book_info']['title']
                        book.ai_extracted_authors = json.dumps(result['book_info']['authors'])
                        book.ai_suggested_category = result['suggested_category']
                        book.ai_confidence_score = result['book_info']['confidence']
                        book.damage_status = result['damage_assessment']['severity']
                        book.damage_details = json.dumps(result['damage_assessment'])
                        book.last_ai_analysis = django_timezone.now()
                        book.save()
                        
                        results.append({
                            'book_id': book_id,
                            'success': True,
                            'category': result['suggested_category'],
                            'confidence': result['book_info']['confidence']
                        })
                    else:
                        results.append({
                            'book_id': book_id,
                            'success': False,
                            'error': result.get('error', 'Analysis failed')
                        })
                        
                except Exception as e:
                    results.append({
                        'book_id': book_id,
                        'success': False,
                        'error': str(e)
                    })
            
            successful_count = len([r for r in results if r['success']])
            
            return JsonResponse({
                'success': True,
                'results': results,
                'processed_count': len(results),
                'successful_count': successful_count
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def ai_analysis_report(request):
    """Generate comprehensive AI analysis report"""
    try:
        # Get analysis statistics
        total_books = Books.objects.count()
        analyzed_books = Books.objects.filter(last_ai_analysis__isnull=False).count()
        
        # Damage statistics
        damage_breakdown = Books.objects.values('damage_status').annotate(
            count=Count('id')
        ).order_by('damage_status')
        
        # Category accuracy (books with both AI and manual categories)
        category_comparison = Books.objects.filter(
            ai_suggested_category__isnull=False
        ).exclude(ai_suggested_category='')
        
        # Recent analysis trends (last 30 days)
        thirty_days_ago = django_timezone.now() - timedelta(days=30)
        recent_analyses = Books.objects.filter(
            last_ai_analysis__gte=thirty_days_ago
        ).extra(
            select={'day': 'date(last_ai_analysis)'}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        # Top AI-suggested categories
        top_categories = Books.objects.filter(
            ai_suggested_category__isnull=False
        ).exclude(ai_suggested_category='').values(
            'ai_suggested_category'
        ).annotate(count=Count('id')).order_by('-count')[:10]
        
        context = {
            'parent': 'ai_recognition',
            'segment': 'analysis_report',
            'total_books': total_books,
            'analyzed_books': analyzed_books,
            'analysis_percentage': round((analyzed_books / total_books * 100), 2) if total_books > 0 else 0,
            'damage_breakdown': damage_breakdown,
            'category_comparison': category_comparison,
            'recent_analyses': recent_analyses,
            'top_categories': top_categories,
            'report_generated': django_timezone.now()
        }
        
        return render(request, 'ai_recognition/analysis_report.html', context)
        
    except Exception as e:
        messages.error(request, f'Error generating report: {str(e)}')
        return redirect('ai_image_recognition_dashboard')

@csrf_exempt
@login_required
def api_book_cover_analysis(request, book_id):
    """API endpoint for book cover analysis"""
    if request.method == 'POST':
        try:
            book = get_object_or_404(Books, id=book_id)
            
            if not book.cover_image:
                return JsonResponse({
                    'success': False,
                    'error': 'No cover image available for this book'
                })
            
            # Process the cover image
            result = process_book_cover_image(book.cover_image.path)
            
            if result['success']:
                # Update book with AI analysis
                book.ai_extracted_title = result['book_info']['title']
                book.ai_extracted_authors = json.dumps(result['book_info']['authors'])
                book.ai_suggested_category = result['suggested_category']
                book.ai_confidence_score = result['book_info']['confidence']
                book.damage_status = result['damage_assessment']['severity']
                book.damage_details = json.dumps(result['damage_assessment'])
                book.last_ai_analysis = django_timezone.now()
                book.save()
            
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
