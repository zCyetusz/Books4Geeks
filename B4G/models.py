# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Create your models here.

class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    #__PROFILE_FIELDS__
    password = models.TextField(max_length=255, null=True, blank=True)
    primary_role = models.ForeignKey('auth.Group', on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='primary_users', verbose_name=_('Primary Role'))
    

    #__PROFILE_FIELDS__END

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name        = _("UserProfile")
        verbose_name_plural = _("UserProfile")

#__MODELS__
class Publishers(models.Model):

    #__Publishers_FIELDS__
    pubname = models.TextField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=255, null=True, blank=True)
    lastmodified = models.DateTimeField(blank=True, null=True, default=timezone.now)

    #__Publishers_FIELDS__END

    class Meta:
        verbose_name        = _("Publishers")
        verbose_name_plural = _("Publishers")


class Categories(models.Model):

    #__Categories_FIELDS__
    catname = models.TextField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=255, null=True, blank=True)
    lastmodified = models.DateTimeField(blank=True, null=True, default=timezone.now)

    #__Categories_FIELDS__END

    class Meta:
        verbose_name        = _("Categories")
        verbose_name_plural = _("Categories")


class Authors(models.Model):

    #__Authors_FIELDS__
    authorname = models.TextField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=255, null=True, blank=True)
    lastmodified = models.DateTimeField(blank=True, null=True, default=timezone.now)

    #__Authors_FIELDS__END

    class Meta:
        verbose_name        = _("Authors")
        verbose_name_plural = _("Authors")


class Books(models.Model):    #__Books_FIELDS__
    id_pub = models.ForeignKey(Publishers, on_delete=models.CASCADE)
    bookname = models.TextField(max_length=255, null=True, blank=True)
    publishdate = models.DateTimeField(blank=True, null=True, default=timezone.now)
    price = models.TextField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=255, null=True, blank=True)
    lastmodified = models.DateTimeField(blank=True, null=True, default=timezone.now)
    barcode = models.ImageField(upload_to='barcodes/', null=True, blank=True)
    barcode_number = models.CharField(max_length=13, null=True, blank=True)
    
    # AI Image Recognition Fields
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True, 
                                  help_text="Book cover image for AI analysis")
    ai_extracted_title = models.TextField(max_length=500, null=True, blank=True,
                                        help_text="Title extracted by AI from cover")
    ai_extracted_authors = models.TextField(max_length=500, null=True, blank=True,
                                          help_text="Authors extracted by AI (JSON format)")
    ai_suggested_category = models.CharField(max_length=100, null=True, blank=True,
                                           help_text="Category suggested by AI analysis")
    ai_confidence_score = models.FloatField(null=True, blank=True,
                                          help_text="AI analysis confidence (0.0-1.0)")
    damage_status = models.CharField(max_length=20, choices=[
        ('none', 'No Damage'),
        ('minor', 'Minor Wear'),
        ('moderate', 'Moderate Damage'),
        ('severe', 'Severe Damage')
    ], default='none', help_text="Book damage assessment")
    damage_details = models.TextField(null=True, blank=True,
                                    help_text="Detailed damage assessment (JSON format)")
    last_ai_analysis = models.DateTimeField(null=True, blank=True,
                                          help_text="When AI analysis was last performed")

    #__Books_FIELDS__END

    class Meta:
        verbose_name        = _("Books")
        verbose_name_plural = _("Books")

    def __str__(self):
        return f"Book {self.id} - {self.description}"


class Bookauthors(models.Model):

    #__Bookauthors_FIELDS__
    id_book = models.ForeignKey(Books, on_delete=models.CASCADE)
    id_author = models.ForeignKey(Authors, on_delete=models.CASCADE)
    lastmodified = models.DateTimeField(blank=True, null=True, default=timezone.now)

    #__Bookauthors_FIELDS__END

    class Meta:
        verbose_name        = _("Bookauthors")
        verbose_name_plural = _("Bookauthors")


class Bookcategories(models.Model):

    #__Bookcategories_FIELDS__
    id_book = models.ForeignKey(Books, on_delete=models.CASCADE)
    id_cat = models.ForeignKey(Categories, on_delete=models.CASCADE)
    lastmodified = models.DateTimeField(blank=True, null=True, default=timezone.now)

    #__Bookcategories_FIELDS__END

    class Meta:
        verbose_name        = _("Bookcategories")
        verbose_name_plural = _("Bookcategories")


class Imports(models.Model):

    #__Imports_FIELDS__
    id_book = models.ForeignKey(Books, on_delete=models.CASCADE)
    id_pub = models.ForeignKey(Publishers, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True, blank=True)
    impprice = models.TextField(max_length=255, null=True, blank=True)
    total = models.TextField(max_length=255, null=True, blank=True)
    lastmodified = models.DateTimeField(blank=True, null=True, default=timezone.now)

    #__Imports_FIELDS__END

    class Meta:
        verbose_name        = _("Imports")
        verbose_name_plural = _("Imports")


class Customers(models.Model):

    #__Customers_FIELDS__
    cusname = models.TextField(max_length=255, null=True, blank=True)
    gender = models.TextField(max_length=255, null=True, blank=True)
    phone = models.TextField(max_length=255, null=True, blank=True)
    lastmodified = models.DateTimeField(blank=True, null=True, default=timezone.now)

    #__Customers_FIELDS__END

    class Meta:
        verbose_name        = _("Customers")
        verbose_name_plural = _("Customers")


class Bills(models.Model):

    #__Bills_FIELDS__
    id_cus = models.ForeignKey(Customers, on_delete=models.CASCADE)
    totalbill = models.TextField(max_length=255, null=True, blank=True)
    date = models.DateTimeField(blank=True, null=True, default=timezone.now)
    lastmodified = models.DateTimeField(blank=True, null=True, default=timezone.now)

    #__Bills_FIELDS__END

    class Meta:
        verbose_name        = _("Bills")
        verbose_name_plural = _("Bills")


class Billdetails(models.Model):

    #__Billdetails_FIELDS__
    id_book = models.ForeignKey(Books, on_delete=models.CASCADE)
    id_bill = models.ForeignKey(Bills, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True, blank=True, default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total = models.TextField(max_length=255, null=True, blank=True)
    lastmodified = models.DateTimeField(blank=True, null=True, default=timezone.now)

    #__Billdetails_FIELDS__END

    class Meta:
        verbose_name        = _("Billdetails")
        verbose_name_plural = _("Billdetails")


class Areas(models.Model):

    #__Areas_FIELDS__
    areaname = models.TextField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=255, null=True, blank=True)
    lastmodified = models.DateTimeField(blank=True, null=True, default=timezone.now)

    #__Areas_FIELDS__END

    class Meta:
        verbose_name        = _("Areas")
        verbose_name_plural = _("Areas")


class Shelves(models.Model):

    #__Shelves_FIELDS__
    shelfname = models.TextField(max_length=255, null=True, blank=True)
    id_area = models.ForeignKey(Areas, on_delete=models.CASCADE)
    lastmodified = models.DateTimeField(blank=True, null=True, default=timezone.now)

    #__Shelves_FIELDS__END

    class Meta:
        verbose_name        = _("Shelves")
        verbose_name_plural = _("Shelves")


class Bookshelves(models.Model):

    #__Bookshelves_FIELDS__
    id_book = models.ForeignKey(Books, on_delete=models.CASCADE)
    id_shelf = models.ForeignKey(Shelves, on_delete=models.CASCADE)
    quantity = models.TextField(max_length=255, null=True, blank=True)
    lastmodified = models.DateTimeField(blank=True, null=True, default=timezone.now)

    #__Bookshelves_FIELDS__END

    class Meta:
        verbose_name        = _("Bookshelves")
        verbose_name_plural = _("Bookshelves")


class Employees(models.Model):

    #__Employees_FIELDS__
    id_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    empname = models.TextField(max_length=255, null=True, blank=True)
    role = models.TextField(max_length=255, null=True, blank=True)
    phone = models.TextField(max_length=255, null=True, blank=True)
    gender = models.TextField(max_length=255, null=True, blank=True)
    address = models.TextField(max_length=255, null=True, blank=True)
    hiredate = models.DateTimeField(blank=True, null=True, default=timezone.now)
    lastmodified = models.DateTimeField(blank=True, null=True, default=timezone.now)

    #__Employees_FIELDS__END

    class Meta:
        verbose_name        = _("Employees")
        verbose_name_plural = _("Employees")


class Reservations(models.Model):

    #__Reservations_FIELDS__
    id_cus = models.ForeignKey(Customers, on_delete=models.CASCADE, verbose_name=_("Customer"))
    reservedate = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("Reservation Date"))
    pickupdate = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("Pickup Date"))
    status = models.TextField(max_length=255, null=True, blank=True, verbose_name=_("Status"))
    lastmodified = models.DateTimeField(blank=True, null=True, default=timezone.now)

    #__Reservations_FIELDS__END

    def __str__(self):
        return f"Reservation #{self.id} - {self.id_cus.cusname}" if self.id_cus else f"Reservation #{self.id}"
    
    class Meta:
        verbose_name = _("Reservation")
        verbose_name_plural = _("Reservations")


class ReservationItems(models.Model):

    #__ReservationItems_FIELDS__
    id_reservation = models.ForeignKey(Reservations, on_delete=models.CASCADE, related_name="items", verbose_name=_("Reservation"))
    id_book = models.ForeignKey(Books, on_delete=models.CASCADE, verbose_name=_("Book"))
    lastmodified = models.DateTimeField(blank=True, null=True, default=timezone.now)

    #__ReservationItems_FIELDS__END

    def __str__(self):
        book_name = self.id_book.description if self.id_book else "Unknown Book"
        return f"{book_name} (Reservation #{self.id_reservation_id})"
    
    class Meta:
        verbose_name = _("Reservation Item")
        verbose_name_plural = _("Reservation Items")