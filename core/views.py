from django.contrib.auth import authenticate

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ContactMessage, Product, Certificate
from .serializers import (
    ContactMessageSerializer,
    ProductSerializer,
    CertificateSerializer,
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