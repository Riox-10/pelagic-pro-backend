# Register your models here.

from django.contrib import admin
from .models import Product, Certificate, ContactMessage, GalleryImage, CompanyFact


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "subject", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("full_name", "email", "subject", "message")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "category", "weight", "packaging", "is_active")
    list_filter = ("brand", "category", "is_active")
    search_fields = ("name", "brand", "category")


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("name", "image", "created_at")
    search_fields = ("name",)

@admin.register(CompanyFact)
class CompanyFactAdmin(admin.ModelAdmin):
    list_display = ("label", "value", "order", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("label", "value", "description")
    ordering = ("order", "-created_at")