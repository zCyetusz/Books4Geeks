from B4G.forms import LoginForm, RegistrationForm, UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from .models import *
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
import os
from django.contrib.auth import views as auth_views

# Create your views here.

# Authentication
def register(request):
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
        Publishers.objects.create(pubname=pubname)
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
        Categories.objects.create(catname=catname)
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
        Authors.objects.create(authorname=authorname)
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
    return render(request, 'book/list.html', {'books': books})

@login_required
def book_create(request):
    if request.method == 'POST':
        id_pub = get_object_or_404(Publishers, pk=request.POST.get('id_pub'))
        publishdate = request.POST.get('publishdate')
        price = request.POST.get('price')
        description = request.POST.get('description')
        
        book = Books.objects.create(
            id_pub=id_pub,
            publishdate=publishdate,
            price=price,
            description=description
        )
        
        # Generate barcode
        barcode_number = f"BK{book.id:06d}"
        ean = barcode.get('ean13', barcode_number, writer=ImageWriter())
        buffer = BytesIO()
        ean.write(buffer)
        
        # Save barcode image
        filename = f'barcode_{book.id}.png'
        book.barcode.save(filename, File(buffer), save=True)
        
        messages.success(request, 'Book created successfully!')
        return redirect('book_list')
    
    publishers = Publishers.objects.all()
    return render(request, 'book/create.html', {'publishers': publishers})

@login_required
def book_edit(request, pk):
    book = get_object_or_404(Books, pk=pk)
    if request.method == 'POST':
        book.id_pub = get_object_or_404(Publishers, pk=request.POST.get('id_pub'))
        book.publishdate = request.POST.get('publishdate')
        book.price = request.POST.get('price')
        book.description = request.POST.get('description')
        book.save()
        messages.success(request, 'Book updated successfully!')
        return redirect('book_list')
    
    publishers = Publishers.objects.all()
    return render(request, 'book/edit.html', {'book': book, 'publishers': publishers})

@login_required
def book_delete(request, pk):
    book = get_object_or_404(Books, pk=pk)
    book.delete()
    messages.success(request, 'Book deleted successfully!')
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
    bills = Bills.objects.all()
    return render(request, 'bill/list.html', {'bills': bills})

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
        
        for book_id, quantity in zip(book_ids, quantities):
            book = get_object_or_404(Books, pk=book_id)
            total = float(book.price) * float(quantity)
            
            Billdetails.objects.create(
                id_book=book,
                total=total
            )
            
            # Update book quantity
            bookshelf = get_object_or_404(Bookshelves, id_book=book)
            bookshelf.quantity = int(bookshelf.quantity) - int(quantity)
            bookshelf.save()
        
        messages.success(request, 'Bill created successfully!')
        return redirect('bill_list')
    
    customers = Customers.objects.all()
    books = Books.objects.all()
    return render(request, 'bill/create.html', {'customers': customers, 'books': books})

# Area Views
@login_required
def area_list(request):
    areas = Areas.objects.all()
    return render(request, 'area/list.html', {'areas': areas})

@login_required
def area_create(request):
    if request.method == 'POST':
        areaname = request.POST.get('areaname')
        Areas.objects.create(areaname=areaname)
        messages.success(request, 'Area created successfully!')
        return redirect('area_list')
    return render(request, 'area/create.html')

@login_required
def area_edit(request, pk):
    area = get_object_or_404(Areas, pk=pk)
    if request.method == 'POST':
        area.areaname = request.POST.get('areaname')
        area.save()
        messages.success(request, 'Area updated successfully!')
        return redirect('area_list')
    return render(request, 'area/edit.html', {'area': area})

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
    return render(request, 'shelf/list.html', {'shelves': shelves})

@login_required
def shelf_create(request):
    if request.method == 'POST':
        shelfname = request.POST.get('shelfname')
        id_area = get_object_or_404(Areas, pk=request.POST.get('id_area'))
        Shelves.objects.create(shelfname=shelfname, id_area=id_area)
        messages.success(request, 'Shelf created successfully!')
        return redirect('shelf_list')
    
    areas = Areas.objects.all()
    return render(request, 'shelf/create.html', {'areas': areas})

@login_required
def shelf_edit(request, pk):
    shelf = get_object_or_404(Shelves, pk=pk)
    if request.method == 'POST':
        shelf.shelfname = request.POST.get('shelfname')
        shelf.id_area = get_object_or_404(Areas, pk=request.POST.get('id_area'))
        shelf.save()
        messages.success(request, 'Shelf updated successfully!')
        return redirect('shelf_list')
    
    areas = Areas.objects.all()
    return render(request, 'shelf/edit.html', {'shelf': shelf, 'areas': areas})

@login_required
def shelf_delete(request, pk):
    shelf = get_object_or_404(Shelves, pk=pk)
    shelf.delete()
    messages.success(request, 'Shelf deleted successfully!')
    return redirect('shelf_list')

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

# Reservation Views
@login_required
def reservation_list(request):
    reservations = Reservations.objects.all()
    return render(request, 'reservation/list.html', {'reservations': reservations})

@login_required
def reservation_create(request):
    if request.method == 'POST':
        reservedate = request.POST.get('reservedate')
        pickupdate = request.POST.get('pickupdate')
        status = request.POST.get('status')
        
        Reservations.objects.create(
            reservedate=reservedate,
            pickupdate=pickupdate,
            status=status
        )
        
        messages.success(request, 'Reservation created successfully!')
        return redirect('reservation_list')
    
    return render(request, 'reservation/create.html')

@login_required
def reservation_edit(request, pk):
    reservation = get_object_or_404(Reservations, pk=pk)
    if request.method == 'POST':
        reservation.reservedate = request.POST.get('reservedate')
        reservation.pickupdate = request.POST.get('pickupdate')
        reservation.status = request.POST.get('status')
        reservation.save()
        
        messages.success(request, 'Reservation updated successfully!')
        return redirect('reservation_list')
    
    return render(request, 'reservation/edit.html', {'reservation': reservation})

@login_required
def reservation_delete(request, pk):
    reservation = get_object_or_404(Reservations, pk=pk)
    reservation.delete()
    messages.success(request, 'Reservation deleted successfully!')
    return redirect('reservation_list')

# API Views
@login_required
def get_book_by_barcode(request, barcode_number):
    try:
        book = Books.objects.get(barcode_number=barcode_number)
        data = {
            'id': book.id,
            'description': book.description,
            'price': book.price,
        }
        return JsonResponse(data)
    except Books.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=404)
