from django.urls import path
from B4G import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Pages
    path('', views.index),
    path('dashboard/', views.index, name='dashboard'),  # Add missing dashboard URL
    path('dashboard-v2/', views.index2, name='dashboardv2'),
    path('dashboard-v3/', views.index3, name='dashboardv3'),

    # API endpoints
    path('api/gemini/', views.gemini_api, name='gemini_api'),
    path('api/get_book_by_barcode/<str:barcode_number>/', views.get_book_by_barcode, name='get_book_by_barcode'),
    path('api/process_barcode/', views.process_barcode, name='process_barcode'),
    path('api/create_bill_from_scanned/', views.create_bill_from_scanned, name='create_bill_from_scanned'),
    path('api/lookup_barcode/<str:barcode_number>/', views.lookup_barcode, name='lookup_barcode'),

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
    path('bills/test-barcode-scan/', views.test_barcode_scan, name='test_barcode_scan'),
    path('bills/start-camera/', views.start_camera, name='start_camera'),
    path('bills/stop-camera/', views.stop_camera, name='stop_camera'),
    path('bills/video-feed/', views.video_feed, name='video_feed'),
    path('bills/scan-barcode-desktop/', views.scan_barcode_desktop, name='bill_scan_barcode_desktop'),
    
    # Customers
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/edit/<int:pk>/', views.customer_edit, name='customer_edit'),
    path('customers/delete/<int:pk>/', views.customer_delete, name='customer_delete'),
    
    # Employees
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/edit/<int:pk>/', views.employee_edit, name='employee_edit'),
    path('employees/delete/<int:pk>/', views.employee_delete, name='employee_delete'),
    
    # Imports
    path('imports/', views.import_list, name='import_list'),
    path('imports/create/', views.import_create, name='import_create'),
    path('imports/edit/<int:pk>/', views.import_edit, name='import_edit'),
    path('imports/delete/<int:pk>/', views.import_delete, name='import_delete'),
    path('imports/detail/<int:pk>/', views.import_detail, name='import_detail'),
    
    # Reservations
    path('reservations/', views.reservation_list, name='reservation_list'),
    path('reservations/create/', views.reservation_create, name='reservation_create'),
    path('reservations/edit/<int:pk>/', views.reservation_edit, name='reservation_edit'),
    path('reservations/delete/<int:pk>/', views.reservation_delete, name='reservation_delete'),
    path('reservations/customer/<int:customer_id>/', views.customer_reservations, name='customer_reservations'),
    
    # Roles and Permissions
    path('roles/', views.role_list, name='role_list'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/edit/<int:pk>/', views.role_edit, name='role_edit'),
    path('roles/delete/<int:pk>/', views.role_delete, name='role_delete'),
    path('roles/assign/', views.assign_user_roles, name='assign_user_roles'),
    path('roles/assign/<int:user_id>/', views.assign_user_roles, name='assign_user_roles_to_user'),
    
    # Reports and Analytics
    path('reports/', views.reports, name='reports'),
    
    # Smart Inventory Management
    path('inventory/alerts/', views.inventory_alerts, name='inventory_alerts'),
    path('inventory/analytics/', views.inventory_analytics, name='inventory_analytics'),
    path('inventory/purchase-order/', views.generate_purchase_order, name='generate_purchase_order'),
    path('api/inventory/alerts/', views.inventory_api_alerts, name='inventory_api_alerts'),
    path('api/book-velocity/<int:book_id>/', views.book_velocity_analysis, name='book_velocity_analysis'),
    
    # Advanced Search
    path('search/advanced/', views.advanced_search, name='advanced_search'),
    
    # AI Recommendations
    path('api/ai-recommendations/', views.get_ai_recommendations, name='ai_recommendations'),
    
    # AI Image Recognition URLs
    path('ai-recognition/', views.ai_image_recognition_dashboard, name='ai_image_recognition_dashboard'),
    path('ai-recognition/cover-analyzer/', views.book_cover_analyzer, name='book_cover_analyzer'),
    path('ai-recognition/inventory-counter/', views.inventory_counter, name='inventory_counter'),
    path('ai-recognition/damage-assessor/', views.damage_assessor, name='damage_assessor'),
    path('ai-recognition/auto-categorizer/', views.auto_categorizer, name='auto_categorizer'),
    path('ai-recognition/batch-categorize/', views.batch_categorize_books, name='batch_categorize_books'),
    path('ai-recognition/analysis-report/', views.ai_analysis_report, name='ai_analysis_report'),
    path('api/ai-analysis/<int:book_id>/', views.api_book_cover_analysis, name='api_book_cover_analysis'),
    
    # Smart Inventory URLs (keeping existing for reference)
]