from django.contrib.auth import authenticate

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Product, Certificate, ContactMessage, GalleryImage, CompanyFact
from .serializers import (
    ContactMessageSerializer,
    ProductSerializer,
    CertificateSerializer,
    GalleryImageSerializer,
    CompanyFactSerializer,
)


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


@api_view(["POST"])
def create_contact_message(request):
    serializer = ContactMessageSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "message": "Message envoyé avec succès.",
                "data": serializer.data,
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
    if not request.user.is_staff:
        return Response(
            {"message": "Accès refusé. Compte admin requis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    messages = ContactMessage.objects.all().order_by("-created_at")
    serializer = ContactMessageSerializer(messages, many=True)
    return Response(serializer.data)


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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_product(request):
    if not request.user.is_staff:
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
        is_active=str(is_active).lower() in ["true", "1", "yes", "on"],
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


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_product(request, product_id):
    if not request.user.is_staff:
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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_certificate(request):
    if not request.user.is_staff:
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


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_certificate(request, certificate_id):
    if not request.user.is_staff:
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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def gallery_image_create(request):
    if not request.user.is_staff:
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
        is_active=str(is_active).lower() in ["true", "1", "yes", "on"],
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
    if not request.user.is_staff:
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
    
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def gallery_image_update(request, pk):
    if not request.user.is_staff:
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

    if isinstance(is_active, bool):
        gallery_image.is_active = is_active
    else:
        gallery_image.is_active = str(is_active).lower() in [
            "true",
            "1",
            "yes",
            "on",
        ]

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
    if not request.user.is_staff:
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
        is_active=str(is_active).lower() in ["true", "1", "yes", "on"],
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
    if not request.user.is_staff:
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
    if not request.user.is_staff:
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

    return Response({
        "message": "Image supprimée avec succès."
    })