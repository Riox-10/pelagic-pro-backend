from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health_check, name="health-check"),

    path("products/", views.products_list, name="products-list"),
    path("products/create/", views.create_product, name="create-product"),
    path(
        "products/<int:product_id>/delete/",
        views.delete_product,
        name="delete-product",
    ),

    path("certificates/", views.certificates_list, name="certificates-list"),
    path(
        "certificates/create/",
        views.create_certificate,
        name="create-certificate",
    ),
    path(
        "certificates/<int:certificate_id>/delete/",
        views.delete_certificate,
        name="delete-certificate",
    ),

    path("gallery-images/", views.gallery_images_list, name="gallery-images-list"),
    path(
        "gallery-images/create/",
        views.gallery_image_create,
        name="gallery-image-create",
    ),
    path(
        "gallery-images/<int:pk>/delete/",
        views.gallery_image_delete,
        name="gallery-image-delete",
    ),

    path("contact/", views.create_contact_message, name="contact-message"),
    path(
        "contact-messages/",
        views.contact_messages_list,
        name="contact-messages-list",
    ),

    path("auth/login/", views.admin_login, name="admin-login"),
    path("auth/me/", views.admin_me, name="admin-me"),
    path("auth/logout/", views.admin_logout, name="admin-logout"),
]