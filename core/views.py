from django.contrib.auth import authenticate
from django.conf import settings
from django.core.mail import EmailMessage

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    Product,
    Certificate,
    ContactMessage,
    GalleryImage,
    CompanyFact,
    CompanyImage,
    CatalogueFile,
)

from .serializers import (
    ContactMessageSerializer,
    ProductSerializer,
    CertificateSerializer,
    GalleryImageSerializer,
    CompanyFactSerializer,
    CompanyImageSerializer,
    CatalogueFileSerializer,
)


def is_admin_user(request):
    return request.user.is_authenticated and request.user.is_staff


def parse_boolean(value, default=True):
    if isinstance(value, bool):
        return value

    if value is None:
        return default

    return str(value).lower() in ["true", "1", "yes", "on"]


@api_view(["GET"])
def health_check(request):
    return Response({
        "status": "ok",
        "message": "Django backend is working successfully."
    })


@api_view(["GET"])
def products_list(request):
    products = Product.objects.filter(is_active=True).order_by("-created_at")
    serializer = ProductSerializer(
        products,
        many=True,
        context={"request": request},
    )
    return Response(serializer.data)


@api_view(["GET"])
def certificates_list(request):
    certificates = Certificate.objects.all().order_by("-created_at")
    serializer = CertificateSerializer(
        certificates,
        many=True,
        context={"request": request},
    )
    return Response(serializer.data)


@api_view(["GET"])
def gallery_images_list(request):
    gallery_images = GalleryImage.objects.filter(is_active=True).order_by(
        "-created_at"
    )
    serializer = GalleryImageSerializer(
        gallery_images,
        many=True,
        context={"request": request},
    )
    return Response(serializer.data)


# =========================
# Catalogue PDF
# =========================

@api_view(["GET"])
def latest_catalogue_file(request):
    catalogue = CatalogueFile.objects.filter(is_active=True).order_by(
        "-created_at"
    ).first()

    if not catalogue:
        return Response(
            {
                "message": "Aucun catalogue disponible.",
                "data": None,
            },
            status=status.HTTP_200_OK,
        )

    serializer = CatalogueFileSerializer(
        catalogue,
        context={"request": request},
    )

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def catalogue_files_list(request):
    if not is_admin_user(request):
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    catalogues = CatalogueFile.objects.all().order_by("-created_at")
    serializer = CatalogueFileSerializer(
        catalogues,
        many=True,
        context={"request": request},
    )

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def catalogue_file_create(request):
    if not is_admin_user(request):
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    title = request.data.get("title", "Catalogue PELAGIC PRO")
    is_active = parse_boolean(request.data.get("is_active"), True)
    file = request.FILES.get("file")

    if not file:
        return Response(
            {"message": "Le fichier PDF du catalogue est obligatoire."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not file.name.lower().endswith(".pdf"):
        return Response(
            {"message": "Le catalogue doit être un fichier PDF."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if is_active:
        CatalogueFile.objects.update(is_active=False)

    catalogue = CatalogueFile.objects.create(
        title=title or "Catalogue PELAGIC PRO",
        file=file,
        is_active=is_active,
    )

    serializer = CatalogueFileSerializer(
        catalogue,
        context={"request": request},
    )

    return Response(
        {
            "message": "Catalogue ajouté avec succès.",
            "data": serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def catalogue_file_update(request, pk):
    if not is_admin_user(request):
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        catalogue = CatalogueFile.objects.get(pk=pk)
    except CatalogueFile.DoesNotExist:
        return Response(
            {"message": "Catalogue introuvable."},
            status=status.HTTP_404_NOT_FOUND,
        )

    title = request.data.get("title", catalogue.title)
    is_active = request.data.get("is_active", catalogue.is_active)
    file = request.FILES.get("file")

    catalogue.title = title or "Catalogue PELAGIC PRO"

    parsed_is_active = parse_boolean(is_active, catalogue.is_active)

    if parsed_is_active:
        CatalogueFile.objects.exclude(pk=catalogue.pk).update(is_active=False)

    catalogue.is_active = parsed_is_active

    if file:
        if not file.name.lower().endswith(".pdf"):
            return Response(
                {"message": "Le catalogue doit être un fichier PDF."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        catalogue.file = file

    catalogue.save()

    serializer = CatalogueFileSerializer(
        catalogue,
        context={"request": request},
    )

    return Response(
        {
            "message": "Catalogue modifié avec succès.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def catalogue_file_delete(request, pk):
    if not is_admin_user(request):
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        catalogue = CatalogueFile.objects.get(pk=pk)
    except CatalogueFile.DoesNotExist:
        return Response(
            {"message": "Catalogue introuvable."},
            status=status.HTTP_404_NOT_FOUND,
        )

    catalogue.delete()

    return Response({
        "message": "Catalogue supprimé avec succès."
    })


# =========================
# Contact
# =========================

@api_view(["POST"])
def create_contact_message(request):
    serializer = ContactMessageSerializer(data=request.data)

    if serializer.is_valid():
        contact_message = serializer.save()
        email_sent = False

        try:
            email_subject = f"Nouveau message contact - {contact_message.subject}"

            email_body = f"""
Nouveau message reçu depuis le site web PELAGIC PRO.

Nom complet :
{contact_message.full_name}

Email :
{contact_message.email}

Téléphone :
{contact_message.phone or "Non renseigné"}

Sujet :
{contact_message.subject}

Message :
{contact_message.message}

Date :
{contact_message.created_at}
"""

            email = EmailMessage(
                subject=email_subject,
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.COMPANY_CONTACT_EMAIL],
                reply_to=[contact_message.email],
            )

            email.send(fail_silently=False)
            email_sent = True

        except Exception as error:
            print(f"Erreur envoi email contact: {error}")

        return Response(
            {
                "message": "Message envoyé avec succès.",
                "email_sent": email_sent,
                "data": ContactMessageSerializer(contact_message).data,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(
        {
            "message": "Erreur dans les données envoyées.",
            "errors": serializer.errors,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def contact_messages_list(request):
    if not is_admin_user(request):
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    messages = ContactMessage.objects.all().order_by("-created_at")
    serializer = ContactMessageSerializer(messages, many=True)
    return Response(serializer.data)


# =========================
# Admin auth
# =========================

@api_view(["POST"])
def admin_login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {"message": "Nom d'utilisateur ou mot de passe incorrect."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.is_staff:
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    token, created = Token.objects.get_or_create(user=user)

    return Response({
        "message": "Connexion réussie.",
        "token": token.key,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
        },
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_me(request):
    user = request.user

    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def admin_logout(request):
    try:
        request.user.auth_token.delete()
    except Exception:
        pass

    return Response({
        "message": "Déconnexion réussie."
    })


# =========================
# Products
# =========================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_product(request):
    if not is_admin_user(request):
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    name = request.data.get("name", "")
    brand = request.data.get("brand", "")
    category = request.data.get("category", "")
    weight = request.data.get("weight", "")
    packaging = request.data.get("packaging", "")
    description = request.data.get("description", "")
    is_active = request.data.get("is_active", "true")
    image = request.FILES.get("image")

    if not name or not brand or not category:
        return Response(
            {"message": "Name, brand et category sont obligatoires."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    product = Product.objects.create(
        name=name,
        brand=brand,
        category=category,
        weight=weight,
        packaging=packaging,
        description=description,
        image=image,
        is_active=parse_boolean(is_active, True),
    )

    serializer = ProductSerializer(
        product,
        context={"request": request},
    )

    return Response(
        {
            "message": "Produit ajouté avec succès.",
            "data": serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_product(request, product_id):
    if not is_admin_user(request):
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {"message": "Produit introuvable."},
            status=status.HTTP_404_NOT_FOUND,
        )

    name = request.data.get("name", product.name)
    brand = request.data.get("brand", product.brand)
    category = request.data.get("category", product.category)
    weight = request.data.get("weight", product.weight)
    packaging = request.data.get("packaging", product.packaging)
    description = request.data.get("description", product.description)
    is_active = request.data.get("is_active", product.is_active)
    image = request.FILES.get("image")

    if not name or not brand or not category:
        return Response(
            {"message": "Name, brand et category sont obligatoires."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    product.name = name
    product.brand = brand
    product.category = category
    product.weight = weight
    product.packaging = packaging
    product.description = description

    if image:
        product.image = image

    product.is_active = parse_boolean(is_active, product.is_active)
    product.save()

    serializer = ProductSerializer(
        product,
        context={"request": request},
    )

    return Response(
        {
            "message": "Produit modifié avec succès.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_product(request, product_id):
    if not is_admin_user(request):
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {"message": "Produit introuvable."},
            status=status.HTTP_404_NOT_FOUND,
        )

    product.delete()

    return Response({
        "message": "Produit supprimé avec succès."
    })


# =========================
# Certificates
# =========================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_certificate(request):
    if not is_admin_user(request):
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    name = request.data.get("name", "")
    alt = request.data.get("alt", "")
    image = request.FILES.get("image")

    if not name:
        return Response(
            {"message": "Le nom du certificat est obligatoire."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    certificate = Certificate.objects.create(
        name=name,
        alt=alt,
        image=image,
    )

    serializer = CertificateSerializer(
        certificate,
        context={"request": request},
    )

    return Response(
        {
            "message": "Certificat ajouté avec succès.",
            "data": serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_certificate(request, certificate_id):
    if not is_admin_user(request):
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        certificate = Certificate.objects.get(id=certificate_id)
    except Certificate.DoesNotExist:
        return Response(
            {"message": "Certificat introuvable."},
            status=status.HTTP_404_NOT_FOUND,
        )

    name = request.data.get("name", certificate.name)
    alt = request.data.get("alt", certificate.alt)
    image = request.FILES.get("image")

    if not name:
        return Response(
            {"message": "Le nom du certificat est obligatoire."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    certificate.name = name
    certificate.alt = alt

    if image:
        certificate.image = image

    certificate.save()

    serializer = CertificateSerializer(
        certificate,
        context={"request": request},
    )

    return Response(
        {
            "message": "Certificat modifié avec succès.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_certificate(request, certificate_id):
    if not is_admin_user(request):
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        certificate = Certificate.objects.get(id=certificate_id)
    except Certificate.DoesNotExist:
        return Response(
            {"message": "Certificat introuvable."},
            status=status.HTTP_404_NOT_FOUND,
        )

    certificate.delete()

    return Response({
        "message": "Certificat supprimé avec succès."
    })


# =========================
# Gallery
# =========================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def gallery_image_create(request):
    if not is_admin_user(request):
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    title = request.data.get("title", "")
    description = request.data.get("description", "")
    is_active = request.data.get("is_active", "true")
    image = request.FILES.get("image")

    if not title:
        return Response(
            {"message": "Le titre de l'image est obligatoire."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not image:
        return Response(
            {"message": "L'image est obligatoire."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    gallery_image = GalleryImage.objects.create(
        title=title,
        description=description,
        image=image,
        is_active=parse_boolean(is_active, True),
    )

    serializer = GalleryImageSerializer(
        gallery_image,
        context={"request": request},
    )

    return Response(
        {
            "message": "Image ajoutée avec succès.",
            "data": serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def gallery_image_delete(request, pk):
    if not is_admin_user(request):
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        gallery_image = GalleryImage.objects.get(pk=pk)
    except GalleryImage.DoesNotExist:
        return Response(
            {"message": "Image introuvable."},
            status=status.HTTP_404_NOT_FOUND,
        )

    gallery_image.delete()

    return Response({
        "message": "Image supprimée avec succès."
    })


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def gallery_image_update(request, pk):
    if not is_admin_user(request):
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        gallery_image = GalleryImage.objects.get(pk=pk)
    except GalleryImage.DoesNotExist:
        return Response(
            {"message": "Image introuvable."},
            status=status.HTTP_404_NOT_FOUND,
        )

    title = request.data.get("title", gallery_image.title)
    description = request.data.get("description", gallery_image.description)
    is_active = request.data.get("is_active", gallery_image.is_active)
    image = request.FILES.get("image")

    if not title:
        return Response(
            {"message": "Le titre de l'image est obligatoire."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    gallery_image.title = title
    gallery_image.description = description

    if image:
        gallery_image.image = image

    gallery_image.is_active = parse_boolean(is_active, gallery_image.is_active)
    gallery_image.save()

    serializer = GalleryImageSerializer(
        gallery_image,
        context={"request": request},
    )

    return Response(
        {
            "message": "Image modifiée avec succès.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# =========================
# Company facts
# =========================

@api_view(["GET"])
def company_facts_list(request):
    company_facts = CompanyFact.objects.filter(is_active=True).order_by(
        "order",
        "-created_at",
    )
    serializer = CompanyFactSerializer(company_facts, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def company_fact_create(request):
    if not is_admin_user(request):
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    label = request.data.get("label", "")
    value = request.data.get("value", "")
    description = request.data.get("description", "")
    order = request.data.get("order", 0)
    is_active = request.data.get("is_active", "true")

    if not label or not value:
        return Response(
            {"message": "Le titre et la valeur sont obligatoires."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    company_fact = CompanyFact.objects.create(
        label=label,
        value=value,
        description=description,
        order=order or 0,
        is_active=parse_boolean(is_active, True),
    )

    serializer = CompanyFactSerializer(company_fact)

    return Response(
        {
            "message": "Information ajoutée avec succès.",
            "data": serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def company_fact_update(request, pk):
    if not is_admin_user(request):
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        company_fact = CompanyFact.objects.get(pk=pk)
    except CompanyFact.DoesNotExist:
        return Response(
            {"message": "Information introuvable."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = CompanyFactSerializer(
        company_fact,
        data=request.data,
        partial=True,
    )

    if serializer.is_valid():
        updated_company_fact = serializer.save()
        return Response(
            {
                "message": "Information modifiée avec succès.",
                "data": CompanyFactSerializer(updated_company_fact).data,
            },
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def company_fact_delete(request, pk):
    if not is_admin_user(request):
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        company_fact = CompanyFact.objects.get(pk=pk)
    except CompanyFact.DoesNotExist:
        return Response(
            {"message": "Information introuvable."},
            status=status.HTTP_404_NOT_FOUND,
        )

    company_fact.delete()

    return Response({
        "message": "Information supprimée avec succès."
    })


# =========================
# Company images
# =========================

@api_view(["GET"])
def company_images_list(request):
    company_images = CompanyImage.objects.filter(is_active=True).order_by(
        "order",
        "-created_at",
    )
    serializer = CompanyImageSerializer(
        company_images,
        many=True,
        context={"request": request},
    )
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def company_image_create(request):
    if not is_admin_user(request):
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    title = request.data.get("title", "")
    alt = request.data.get("alt", "")
    order = request.data.get("order", 0)
    is_active = request.data.get("is_active", "true")
    image = request.FILES.get("image")

    if not title:
        return Response(
            {"message": "Le titre de l'image est obligatoire."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not image:
        return Response(
            {"message": "L'image est obligatoire."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    company_image = CompanyImage.objects.create(
        title=title,
        alt=alt,
        order=order or 0,
        image=image,
        is_active=parse_boolean(is_active, True),
    )

    serializer = CompanyImageSerializer(
        company_image,
        context={"request": request},
    )

    return Response(
        {
            "message": "Image ajoutée avec succès.",
            "data": serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def company_image_update(request, pk):
    if not is_admin_user(request):
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        company_image = CompanyImage.objects.get(pk=pk)
    except CompanyImage.DoesNotExist:
        return Response(
            {"message": "Image introuvable."},
            status=status.HTTP_404_NOT_FOUND,
        )

    title = request.data.get("title", company_image.title)
    alt = request.data.get("alt", company_image.alt)
    order = request.data.get("order", company_image.order)
    is_active = request.data.get("is_active", company_image.is_active)
    image = request.FILES.get("image")

    if not title:
        return Response(
            {"message": "Le titre de l'image est obligatoire."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    company_image.title = title
    company_image.alt = alt
    company_image.order = order or 0

    if image:
        company_image.image = image

    company_image.is_active = parse_boolean(is_active, company_image.is_active)
    company_image.save()

    serializer = CompanyImageSerializer(
        company_image,
        context={"request": request},
    )

    return Response(
        {
            "message": "Image modifiée avec succès.",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def company_image_delete(request, pk):
    if not is_admin_user(request):
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        company_image = CompanyImage.objects.get(pk=pk)
    except CompanyImage.DoesNotExist:
        return Response(
            {"message": "Image introuvable."},
            status=status.HTTP_404_NOT_FOUND,
        )

    company_image.delete()

    return Response({
        "message": "Image supprimée avec succès."
    })