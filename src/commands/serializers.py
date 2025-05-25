from django.forms import CharField, FileField, ValidationError
from rest_framework.serializers import ModelSerializer, StringRelatedField, SerializerMethodField, Serializer

from rest_framework import serializers

from .models import Vendor, OS, Category, Commands


# Vendor Model Serializers
class VendorFullSerializer(ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'
        read_only_fields = ['created_by']

    def validate_name(self, value):
        if self.instance:
            if Vendor.objects.filter(name__iexact=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("A vendor with this name already exists.")
        else:
            if Vendor.objects.filter(name__iexact=value).exists():
                raise serializers.ValidationError("A vendor with this name already exists.")
        return value
#:

class VendorBasicSerializer(ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'name']
#:


# OS Model Serializers
class OSFullSerializer(ModelSerializer):
    class Meta:
        model = OS
        fields = '__all__'
        read_only_fields = ['created_by']

    def validate(self, data):
        name = data.get('name')
        vendor = data.get('vendor')
        if not name or not vendor: return data # Let DRF's default validators handle missing fields

        queryset = OS.objects.filter(name__iexact=name, vendor=vendor)
        if self.instance:
            if queryset.exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError({"name": "An OS with this name already exists for this vendor."})
        else:
            if queryset.exists():
                raise serializers.ValidationError({"name": "An OS with this name already exists for this vendor."})
        return data
#:

class OSBasicSerializer(ModelSerializer):
    class Meta:
        model = OS
        fields = ['id', 'name']
#:


# Category Model Serializers
class CategoryFullSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['created_by']

    def validate(self, data):
        name = data.get('name')
        vendor = data.get('vendor')
        parent = data.get('parent')

        if not name or not vendor: return data # Let DRF's default validators handle missing fields

        queryset = Category.objects.filter(name__iexact=name, vendor=vendor, parent=parent)
        if self.instance:
            if queryset.exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError({"name": "A category with this name already exists for this vendor under the specified parent."})
        else:
            if queryset.exists():
                raise serializers.ValidationError({"name": "A category with this name already exists for this vendor under the specified parent."})
        return data
#:

class CategoryBasicSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
#:

class CategoryTreeSerializer(ModelSerializer):
    children = SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'children']

    def get_children(self, obj):
        # Ensure children are filtered by the same vendor if needed for consistency,
        # though typically the parent is enough to constrain the tree.
        # This serializer is used for read-only tree structure.
        children = obj.subcategories.all().order_by('name') # Order children for consistent display
        return CategoryTreeSerializer(children, many=True).data
#:


# Command Model Serializers
class CommandFullSerializer(ModelSerializer):
    class Meta:
        model = Commands
        fields = '__all__'
        read_only_fields = ['created_by']

    def validate(self, data):
        command_name = data.get('command')
        vendor = data.get('vendor')
        if not command_name or not vendor: return data # Let DRF's default validators handle missing fields

        queryset = Commands.objects.filter(command__iexact=command_name, vendor=vendor)
        if self.instance:
            if queryset.exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError({"command": "A command with this name already exists for this vendor."})
        else:
            if queryset.exists():
                raise serializers.ValidationError({"command": "A command with this name already exists for this vendor."})
        return data
#:

class CommandBasicSerializer(ModelSerializer):
    vendor = StringRelatedField()
    os = StringRelatedField(allow_null=True)
    category = StringRelatedField(allow_null=True)

    class Meta:
        model = Commands
        fields = ['id', 'command', 'description', 'example', 'version', 'vendor', 'os', 'category']
#:

class CSVUploadSerializer(serializers.Serializer):
    csv_file = serializers.FileField()
    vendor = serializers.PrimaryKeyRelatedField(queryset=Vendor.objects.all()) # Changed from vendor_name
    main_category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True # Allow null for optional category
    ) # Changed from main_category

    def validate(self, data):
        # Additional validation to ensure main_category (if provided) belongs to the selected vendor
        vendor = data.get('vendor')
        main_category = data.get('main_category')

        if main_category and vendor:
            if main_category.vendor != vendor:
                raise serializers.ValidationError({
                    'main_category': 'The selected main category does not belong to the selected vendor.'
                })
        return data
#:
