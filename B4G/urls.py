from django.urls import path
from B4G import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Pages
    path('', views.index),
    path('dashboard-v2/', views.index2, name='dashboardv2'),
    path('dashboard-v3/', views.index3, name='dashboardv3'),

    # API endpoints
    path('api/gemini/', views.gemini_api, name='gemini_api'),
    path('api/get_book_by_barcode/<str:barcode_number>/', views.get_book_by_barcode, name='get_book_by_barcode'),

    # Authentication
    path('accounts/register/', views.register, name='register'),
    path('accounts/login/', views.UserLoginView.as_view(), name='login'),
    path('accounts/logout/', views.user_logout_view, name='logout'),
    path('accounts/password-change/', views.UserPasswordChangeView.as_view(), name='password_change'),
    path('accounts/password-change-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name="password_change_done" ),
    path('accounts/password-reset/', views.UserPasswordResetView.as_view(), name='password_reset'),
    path('accounts/password-reset-confirm/<uidb64>/<token>/', 
        views.UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/password-reset-done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('accounts/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Publishers
    path('publishers/', views.publisher_list, name='publisher_list'),
    path('publishers/create/', views.publisher_create, name='publisher_create'),
    path('publishers/edit/<int:pk>/', views.publisher_edit, name='publisher_edit'),
    path('publishers/delete/<int:pk>/', views.publisher_delete, name='publisher_delete'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/edit/<int:pk>/', views.category_edit, name='category_edit'),
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),
    
    # Authors
    path('authors/', views.author_list, name='author_list'),
    path('authors/create/', views.author_create, name='author_create'),
    path('authors/edit/<int:pk>/', views.author_edit, name='author_edit'),
    path('authors/delete/<int:pk>/', views.author_delete, name='author_delete'),
    
    # Areas
    path('areas/', views.area_list, name='area_list'),
    path('areas/create/', views.area_create, name='area_create'),
    path('areas/edit/<int:pk>/', views.area_edit, name='area_edit'),
    path('areas/delete/<int:pk>/', views.area_delete, name='area_delete'),
    
    # Shelves
    path('shelves/', views.shelf_list, name='shelf_list'),
    path('shelves/create/', views.shelf_create, name='shelf_create'),
    path('shelves/edit/<int:pk>/', views.shelf_edit, name='shelf_edit'),
    path('shelves/delete/<int:pk>/', views.shelf_delete, name='shelf_delete'),
    
    # Books
    path('books/', views.book_list, name='book_list'),
    path('books/create/', views.book_create, name='book_create'),
    path('books/edit/<int:pk>/', views.book_edit, name='book_edit'),
    path('books/delete/<int:pk>/', views.book_delete, name='book_delete'),
    
    # Book Shelf Assignments
    path('bookshelves/', views.bookshelf_list, name='bookshelf_list'),
    path('bookshelves/create/', views.bookshelf_create, name='bookshelf_create'),
    path('bookshelves/edit/<int:pk>/', views.bookshelf_edit, name='bookshelf_edit'),
    path('bookshelves/delete/<int:pk>/', views.bookshelf_delete, name='bookshelf_delete'),
    
    # Bills
    path('bills/', views.bill_list, name='bill_list'),
    path('bills/create/', views.bill_create, name='bill_create'),
    path('bills/edit/<int:pk>/', views.bill_edit, name='bill_edit'),
    path('bills/delete/<int:pk>/', views.bill_delete, name='bill_delete'),
    path('bills/scan-barcode/', views.bill_scan_barcode, name='bill_scan_barcode'),
    
    # Customers
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/edit/<int:pk>/', views.customer_edit, name='customer_edit'),
    path('customers/delete/<int:pk>/', views.customer_delete, name='customer_delete'),
] 