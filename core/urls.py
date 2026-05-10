from django.urls import path
from .views import (
    health_check,
    products_list,
    certificates_list,
    create_contact_message,
    contact_messages_list,
    admin_login,
    admin_me,
    admin_logout,
    create_product,
    delete_product,
    create_certificate,
    delete_certificate,
)

urlpatterns = [
    path("health/", health_check, name="health-check"),

    path("products/", products_list, name="products-list"),
    path("products/create/", create_product, name="create-product"),
    path("products/<int:product_id>/delete/", delete_product, name="delete-product"),

    path("certificates/", certificates_list, name="certificates-list"),
    path("certificates/create/", create_certificate, name="create-certificate"),
    path(
        "certificates/<int:certificate_id>/delete/",
        delete_certificate,
        name="delete-certificate",
    ),

    path("contact/", create_contact_message, name="create-contact-message"),
    path("contact-messages/", contact_messages_list, name="contact-messages-list"),

    path("auth/login/", admin_login, name="admin-login"),
    path("auth/me/", admin_me, name="admin-me"),
    path("auth/logout/", admin_logout, name="admin-logout"),
]