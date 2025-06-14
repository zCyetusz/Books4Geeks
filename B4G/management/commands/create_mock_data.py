"""
Management command to create mock data for all database tables
Usage: python manage.py create_mock_data [--count N]
"""

import os
import random
import json
import string
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.conf import settings
from django.core.files.base import ContentFile
from B4G.models import (
    UserProfile, Publishers, Categories, Authors, Books, Bookauthors, 
    Bookcategories, Imports, Customers, Bills, Billdetails, Areas, 
    Shelves, Bookshelves, Employees, Reservations, ReservationItems
)

class MockDataGenerator:
    """Simple mock data generator without external dependencies"""
    
    def __init__(self):
        self.first_names = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'James', 'Emma',
            'Robert', 'Olivia', 'William', 'Ava', 'Richard', 'Isabella', 'Joseph',
            'Sophia', 'Thomas', 'Charlotte', 'Christopher', 'Mia', 'Charles', 'Amelia'
        ]
        
        self.last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
            'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin'
        ]
        
        self.companies = [
            'Tech Solutions', 'Global Systems', 'Innovation Corp', 'Future Dynamics',
            'Digital Works', 'Creative Studio', 'Professional Services', 'Advanced Tech',
            'Modern Solutions', 'Strategic Partners', 'Elite Group', 'Premier Systems'
        ]
        
        self.domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'example.com', 'test.org']
        
        self.words = [
            'amazing', 'brilliant', 'creative', 'dynamic', 'elegant', 'fantastic',
            'gorgeous', 'incredible', 'magnificent', 'outstanding', 'remarkable',
            'spectacular', 'wonderful', 'adventure', 'mystery', 'science', 'history',
            'technology', 'education', 'business', 'health', 'travel', 'cooking'
        ]
        
        self.streets = [
            'Main St', 'Oak Ave', 'Pine Rd', 'Elm Dr', 'Maple Ln', 'Cedar Way',
            'First St', 'Second Ave', 'Park Blvd', 'Church Rd', 'School St', 'Mill Ave'
        ]
    
    def name(self):
        return f"{random.choice(self.first_names)} {random.choice(self.last_names)}"
    
    def first_name(self):
        return random.choice(self.first_names)
    
    def last_name(self):
        return random.choice(self.last_names)
    
    def user_name(self):
        return f"{random.choice(self.first_names).lower()}{random.choice(self.last_names).lower()}"
    
    def email(self):
        username = f"{random.choice(self.first_names).lower()}{random.randint(1, 999)}"
        domain = random.choice(self.domains)
        return f"{username}@{domain}"
    
    def company(self):
        return random.choice(self.companies)
    
    def phone_number(self):
        return f"+1-{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    
    def address(self):
        num = random.randint(100, 9999)
        street = random.choice(self.streets)
        return f"{num} {street}"
    
    def text(self, max_nb_chars=200):
        words = random.sample(self.words, random.randint(5, 15))
        text = ' '.join(words).capitalize() + '.'
        return text[:max_nb_chars]
    
    def catch_phrase(self):
        adj = random.choice(self.words)
        noun = random.choice(['adventure', 'journey', 'story', 'tale', 'mystery', 'guide'])
        return f"The {adj.title()} {noun.title()}"
    
    def word(self):
        return random.choice(self.words)
    
    def ean13(self):
        """Generate a fake EAN13 barcode"""
        return ''.join([str(random.randint(0, 9)) for _ in range(13)])
    
    def date_between(self, start_date, end_date):
        """Generate random date between two dates"""
        if isinstance(start_date, str):
            if start_date == '-10y':
                start_date = datetime.now() - timedelta(days=3650)
            elif start_date == '-5y':
                start_date = datetime.now() - timedelta(days=1825)
            elif start_date == '-2y':
                start_date = datetime.now() - timedelta(days=730)
            elif start_date == '-1y':
                start_date = datetime.now() - timedelta(days=365)
            elif start_date == '-6m':
                start_date = datetime.now() - timedelta(days=180)
            elif start_date == '-30d':
                start_date = datetime.now() - timedelta(days=30)
        
        if isinstance(end_date, str):
            if end_date == 'today' or end_date == 'now':
                end_date = datetime.now()
        
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randint(0, days_between)
        return start_date + timedelta(days=random_days)
    
    def date_time_between(self, start_date, end_date, tzinfo=None):
        """Generate random datetime between two dates"""
        date = self.date_between(start_date, end_date)
        dt = datetime.combine(date, datetime.min.time())
        dt = dt.replace(hour=random.randint(0, 23), minute=random.randint(0, 59))
        if tzinfo:
            dt = dt.replace(tzinfo=tzinfo)
        return dt

fake = MockDataGenerator()

class Command(BaseCommand):
    help = 'Create mock data for all database tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of records to create for each model (default: 50)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data'
        )

    def handle(self, *args, **options):
        count = options['count']
        clear_data = options['clear']

        self.stdout.write(
            self.style.SUCCESS(f'Creating mock data with {count} records per model...')
        )

        if clear_data:
            self.clear_existing_data()

        # Create data in order (respecting foreign key dependencies)
        self.create_groups()
        self.create_users_and_profiles(count)
        self.create_publishers(count)
        self.create_categories(count)
        self.create_authors(count)
        self.create_books(count)
        self.create_book_relationships(count)
        self.create_customers(count)
        self.create_areas_and_shelves(count // 5)  # Fewer areas and shelves
        self.create_imports(count)
        self.create_bills_and_details(count // 2)  # Fewer bills
        self.create_bookshelves(count)
        self.create_employees(count // 10)  # Fewer employees
        self.create_reservations(count // 3)  # Fewer reservations

        self.stdout.write(
            self.style.SUCCESS('Successfully created all mock data!')
        )

    def clear_existing_data(self):
        """Clear existing data from all tables"""
        self.stdout.write('Clearing existing data...')
        
        # Clear in reverse order to respect foreign key constraints
        ReservationItems.objects.all().delete()
        Reservations.objects.all().delete()
        Employees.objects.all().delete()
        Bookshelves.objects.all().delete()
        Shelves.objects.all().delete()
        Areas.objects.all().delete()
        Billdetails.objects.all().delete()
        Bills.objects.all().delete()
        Customers.objects.all().delete()
        Imports.objects.all().delete()
        Bookcategories.objects.all().delete()
        Bookauthors.objects.all().delete()
        Books.objects.all().delete()
        Authors.objects.all().delete()
        Categories.objects.all().delete()
        Publishers.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()  # Keep superuser
        
        self.stdout.write(self.style.WARNING('Existing data cleared.'))

    def create_groups(self):
        """Create user groups/roles"""
        roles = ['Admin', 'Manager', 'Librarian', 'Staff', 'Volunteer']
        for role in roles:
            group, created = Group.objects.get_or_create(name=role)
            if created:
                self.stdout.write(f'Created group: {role}')

    def create_users_and_profiles(self, count):
        """Create users and their profiles"""
        self.stdout.write('Creating users and profiles...')
        
        groups = list(Group.objects.all())
        
        for i in range(count):
            # Create user
            username = fake.user_name() + str(i)
            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password='password123'
            )
            
            # Create profile
            primary_role = random.choice(groups) if groups else None
            UserProfile.objects.create(
                user=user,
                password='hashed_password_' + str(i),
                primary_role=primary_role
            )

        self.stdout.write(f'Created {count} users and profiles')

    def create_publishers(self, count):
        """Create publishers"""
        self.stdout.write('Creating publishers...')
        
        publisher_names = [
            'Penguin Random House', 'HarperCollins', 'Macmillan', 'Simon & Schuster',
            'Hachette', 'Scholastic', 'Pearson', 'Oxford University Press',
            'Cambridge University Press', 'Wiley', 'McGraw-Hill', 'Cengage Learning'
        ]
        
        for i in range(count):
            if i < len(publisher_names):
                name = publisher_names[i]
            else:
                name = fake.company() + ' Publishers'
                
            Publishers.objects.create(
                pubname=name,
                description=fake.text(max_nb_chars=200),
                lastmodified=fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.get_current_timezone())
            )

        self.stdout.write(f'Created {count} publishers')

    def create_categories(self, count):
        """Create book categories"""
        self.stdout.write('Creating categories...')
        
        categories = [
            'Fiction', 'Non-Fiction', 'Science Fiction', 'Fantasy', 'Mystery',
            'Romance', 'Thriller', 'Horror', 'Biography', 'History',
            'Science', 'Technology', 'Business', 'Self-Help', 'Health',
            'Cooking', 'Travel', 'Art', 'Music', 'Sports', 'Education',
            'Children', 'Young Adult', 'Poetry', 'Drama', 'Philosophy',
            'Religion', 'Politics', 'Economics', 'Psychology'
        ]
        
        for i in range(count):
            if i < len(categories):
                name = categories[i]
            else:
                name = fake.word().title() + ' Category'
                
            Categories.objects.create(
                catname=name,
                description=fake.text(max_nb_chars=200),
                lastmodified=fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.get_current_timezone())
            )

        self.stdout.write(f'Created {count} categories')

    def create_authors(self, count):
        """Create authors"""
        self.stdout.write('Creating authors...')
        
        famous_authors = [
            'Stephen King', 'J.K. Rowling', 'George R.R. Martin', 'Agatha Christie',
            'Mark Twain', 'Ernest Hemingway', 'Maya Angelou', 'Toni Morrison',
            'Harper Lee', 'F. Scott Fitzgerald', 'Jane Austen', 'Charles Dickens'
        ]
        
        for i in range(count):
            if i < len(famous_authors):
                name = famous_authors[i]
            else:
                name = fake.name()
                
            Authors.objects.create(
                authorname=name,
                description=fake.text(max_nb_chars=300),
                lastmodified=fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.get_current_timezone())
            )

        self.stdout.write(f'Created {count} authors')

    def create_books(self, count):
        """Create books with AI fields"""
        self.stdout.write('Creating books...')
        
        publishers = list(Publishers.objects.all())
        damage_statuses = ['none', 'minor', 'moderate', 'severe']
        
        book_titles = [
            'The Great Adventure', 'Mystery of the Lost City', 'Digital Revolution',
            'Cooking Masterclass', 'History of Tomorrow', 'Art of Living',
            'Space Exploration', 'Modern Psychology', 'Economics Today',
            'Science Wonders', 'Fantasy Realms', 'Detective Stories'
        ]
        
        for i in range(count):
            publisher = random.choice(publishers) if publishers else None
            
            if i < len(book_titles):
                book_name = book_titles[i]
            else:
                book_name = fake.catch_phrase()
            
            # Generate AI analysis data
            ai_authors = json.dumps([fake.name() for _ in range(random.randint(1, 3))])
            ai_categories = ['Fiction', 'Science', 'History', 'Technology', 'Art']
            
            damage_details = json.dumps({
                'condition': random.choice(['excellent', 'good', 'fair', 'poor']),
                'issues': random.sample(['worn_cover', 'torn_pages', 'stains', 'bent_corners'], 
                                      random.randint(0, 2)),
                'assessment_date': fake.date().isoformat()
            })
            
            Books.objects.create(
                id_pub=publisher,
                bookname=book_name,
                publishdate=fake.date_between(start_date='-10y', end_date='today'),
                price=str(random.randint(10, 100)),
                description=fake.text(max_nb_chars=200),
                lastmodified=fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone()),
                barcode_number=fake.ean13(),
                
                # AI Image Recognition Fields
                ai_extracted_title=book_name + ' (AI Extracted)',
                ai_extracted_authors=ai_authors,
                ai_suggested_category=random.choice(ai_categories),
                ai_confidence_score=round(random.uniform(0.7, 0.99), 2),
                damage_status=random.choice(damage_statuses),
                damage_details=damage_details,
                last_ai_analysis=fake.date_time_between(start_date='-30d', end_date='now', tzinfo=timezone.get_current_timezone())
            )

        self.stdout.write(f'Created {count} books')

    def create_book_relationships(self, count):
        """Create book-author and book-category relationships"""
        self.stdout.write('Creating book relationships...')
        
        books = list(Books.objects.all())
        authors = list(Authors.objects.all())
        categories = list(Categories.objects.all())
        
        # Create book-author relationships
        for book in books[:count]:
            # Each book can have 1-3 authors
            book_authors = random.sample(authors, min(random.randint(1, 3), len(authors)))
            for author in book_authors:
                Bookauthors.objects.get_or_create(
                    id_book=book,
                    id_author=author,
                    defaults={'lastmodified': fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone())}
                )
        
        # Create book-category relationships
        for book in books[:count]:
            # Each book can have 1-2 categories
            book_categories = random.sample(categories, min(random.randint(1, 2), len(categories)))
            for category in book_categories:
                Bookcategories.objects.get_or_create(
                    id_book=book,
                    id_cat=category,
                    defaults={'lastmodified': fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone())}
                )

        self.stdout.write(f'Created book relationships')

    def create_customers(self, count):
        """Create customers"""
        self.stdout.write('Creating customers...')
        
        for i in range(count):
            Customers.objects.create(
                cusname=fake.name(),
                gender=random.choice(['Male', 'Female', 'Other']),
                phone=fake.phone_number(),
                lastmodified=fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone())
            )

        self.stdout.write(f'Created {count} customers')

    def create_areas_and_shelves(self, count):
        """Create areas and shelves"""
        self.stdout.write('Creating areas and shelves...')
        
        area_names = [
            'Fiction Section', 'Non-Fiction Section', 'Children\'s Area',
            'Reference Section', 'Periodicals', 'Study Area', 'New Arrivals',
            'Rare Books', 'Local Authors', 'International Collection'
        ]
        
        # Create areas
        areas = []
        for i in range(count):
            if i < len(area_names):
                name = area_names[i]
            else:
                name = f'Section {i+1}'
                
            area = Areas.objects.create(
                areaname=name,
                description=fake.text(max_nb_chars=150),
                lastmodified=fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone())
            )
            areas.append(area)
        
        # Create shelves for each area
        shelf_names = ['A', 'B', 'C', 'D', 'E', 'F']
        for area in areas:
            num_shelves = random.randint(3, 6)
            for i in range(num_shelves):
                shelf_name = f'{area.areaname} - Shelf {shelf_names[i % len(shelf_names)]}{i+1}'
                Shelves.objects.create(
                    shelfname=shelf_name,
                    id_area=area,
                    lastmodified=fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone())
                )

        self.stdout.write(f'Created {count} areas and their shelves')

    def create_imports(self, count):
        """Create import records"""
        self.stdout.write('Creating imports...')
        
        books = list(Books.objects.all())
        publishers = list(Publishers.objects.all())
        
        for i in range(count):
            book = random.choice(books) if books else None
            publisher = random.choice(publishers) if publishers else None
            quantity = random.randint(5, 100)
            import_price = random.randint(5, 50)
            
            Imports.objects.create(
                id_book=book,
                id_pub=publisher,
                quantity=quantity,
                impprice=str(import_price),
                total=str(quantity * import_price),
                lastmodified=fake.date_time_between(start_date='-6m', end_date='now', tzinfo=timezone.get_current_timezone())
            )

        self.stdout.write(f'Created {count} imports')

    def create_bills_and_details(self, count):
        """Create bills and bill details"""
        self.stdout.write('Creating bills and details...')
        
        customers = list(Customers.objects.all())
        books = list(Books.objects.all())
        
        for i in range(count):
            customer = random.choice(customers) if customers else None
            
            # Create bill
            bill = Bills.objects.create(
                id_cus=customer,
                totalbill=str(random.randint(20, 500)),
                date=fake.date_time_between(start_date='-6m', end_date='now', tzinfo=timezone.get_current_timezone()),
                lastmodified=fake.date_time_between(start_date='-6m', end_date='now', tzinfo=timezone.get_current_timezone())
            )
            
            # Create 1-5 bill details for each bill
            num_items = random.randint(1, 5)
            total_bill = 0
            
            for j in range(num_items):
                book = random.choice(books) if books else None
                quantity = random.randint(1, 3)
                price = Decimal(str(random.randint(10, 100)))
                item_total = quantity * price
                total_bill += item_total
                
                Billdetails.objects.create(
                    id_book=book,
                    id_bill=bill,
                    quantity=quantity,
                    price=price,
                    total=str(item_total),
                    lastmodified=fake.date_time_between(start_date='-6m', end_date='now', tzinfo=timezone.get_current_timezone())
                )
            
            # Update bill total
            bill.totalbill = str(total_bill)
            bill.save()

        self.stdout.write(f'Created {count} bills with details')

    def create_bookshelves(self, count):
        """Create bookshelf assignments"""
        self.stdout.write('Creating bookshelf assignments...')
        
        books = list(Books.objects.all())
        shelves = list(Shelves.objects.all())
        
        for i in range(count):
            book = random.choice(books) if books else None
            shelf = random.choice(shelves) if shelves else None
            
            if book and shelf:
                Bookshelves.objects.get_or_create(
                    id_book=book,
                    id_shelf=shelf,
                    defaults={
                        'quantity': str(random.randint(1, 20)),
                        'lastmodified': fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone())
                    }
                )

        self.stdout.write(f'Created bookshelf assignments')

    def create_employees(self, count):
        """Create employees"""
        self.stdout.write('Creating employees...')
        
        user_profiles = list(UserProfile.objects.all())
        roles = ['Manager', 'Librarian', 'Assistant', 'Clerk', 'Security']
        
        for i in range(min(count, len(user_profiles))):
            user_profile = user_profiles[i]
            
            Employees.objects.create(
                id_user=user_profile,
                empname=user_profile.user.get_full_name() or fake.name(),
                role=random.choice(roles),
                phone=fake.phone_number(),
                gender=random.choice(['Male', 'Female', 'Other']),
                address=fake.address(),
                hiredate=fake.date_between(start_date='-5y', end_date='today'),
                lastmodified=fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone())
            )

        self.stdout.write(f'Created {count} employees')

    def create_reservations(self, count):
        """Create reservations and reservation items"""
        self.stdout.write('Creating reservations...')
        
        customers = list(Customers.objects.all())
        books = list(Books.objects.all())
        statuses = ['Pending', 'Ready', 'Picked Up', 'Cancelled', 'Expired']
        
        for i in range(count):
            customer = random.choice(customers) if customers else None
            reserve_date = fake.date_time_between(start_date='-30d', end_date='now', tzinfo=timezone.get_current_timezone())
            pickup_date = reserve_date + timedelta(days=random.randint(1, 7))
            
            reservation = Reservations.objects.create(
                id_cus=customer,
                reservedate=reserve_date,
                pickupdate=pickup_date,
                status=random.choice(statuses),
                lastmodified=fake.date_time_between(start_date='-30d', end_date='now', tzinfo=timezone.get_current_timezone())
            )
            
            # Create 1-3 reservation items for each reservation
            num_items = random.randint(1, 3)
            reserved_books = random.sample(books, min(num_items, len(books)))
            
            for book in reserved_books:
                ReservationItems.objects.create(
                    id_reservation=reservation,
                    id_book=book,
                    lastmodified=fake.date_time_between(start_date='-30d', end_date='now', tzinfo=timezone.get_current_timezone())
                )

        self.stdout.write(f'Created {count} reservations with items')
