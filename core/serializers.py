from rest_framework import serializers
from .models import Product, Certificate, ContactMessage, GalleryImage, CompanyFact, CompanyImage

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "subject",
            "message",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["id", "is_read", "created_at"]


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "brand",
            "category",
            "weight",
            "packaging",
            "description",
            "image",
            "is_active",
            "created_at",
        ]

    def get_image(self, obj):
        request = self.context.get("request")

        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)

        if obj.image:
            return obj.image.url

        return ""


class CertificateSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = [
            "id",
            "name",
            "image",
            "alt",
            "created_at",
        ]

    def get_image(self, obj):
        request = self.context.get("request")

        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)

        if obj.image:
            return obj.image.url

        return ""


class GalleryImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = GalleryImage
        fields = [
            "id",
            "title",
            "image",
            "description",
            "is_active",
            "created_at",
        ]

    def get_image(self, obj):
        request = self.context.get("request")

        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)

        if obj.image:
            return obj.image.url

        return ""


class CompanyFactSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyFact
        fields = [
            "id",
            "label",
            "value",
            "description",
            "order",
            "is_active",
            "created_at",
        ]
class CompanyImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = CompanyImage
        fields = [
            "id",
            "title",
            "image",
            "alt",
            "order",
            "is_active",
            "created_at",
        ]

    def get_image(self, obj):
        request = self.context.get("request")

        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)

        if obj.image:
            return obj.image.url

        return ""