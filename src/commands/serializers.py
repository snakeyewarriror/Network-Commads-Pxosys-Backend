from django.forms import CharField, FileField, ValidationError
from rest_framework.serializers import ModelSerializer, StringRelatedField, SerializerMethodField, Serializer

from rest_framework import serializers

from .models import Vendor, Platform, Tag, Commands


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


# Platform Model Serializers
class OSFullSerializer(ModelSerializer):
    class Meta:
        model = Platform
        fields = '__all__'
        read_only_fields = ['created_by']

    def validate(self, data):
        name = data.get('name')
        vendor = data.get('vendor')
        if not name or not vendor: return data # Let DRF's default validators handle missing fields

        queryset = Platform.objects.filter(name__iexact=name, vendor=vendor)
        if self.instance:
            if queryset.exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError({"name": "An Platform with this name already exists for this vendor."})
        else:
            if queryset.exists():
                raise serializers.ValidationError({"name": "An Platform with this name already exists for this vendor."})
        return data
#:

class OSBasicSerializer(ModelSerializer):
    class Meta:
        model = Platform
        fields = ['id', 'name']
#:


# Tag Model Serializers
class TagFullSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['created_by']

    def validate(self, data):
        name = data.get('name')
        vendor = data.get('vendor')
        parent = data.get('parent')

        if not name or not vendor: return data # Let DRF's default validators handle missing fields

        queryset = Tag.objects.filter(name__iexact=name, vendor=vendor, parent=parent)
        if self.instance:
            if queryset.exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError({"name": "A Tag with this name already exists for this vendor under the specified parent."})
        else:
            if queryset.exists():
                raise serializers.ValidationError({"name": "A Tag with this name already exists for this vendor under the specified parent."})
        return data
#:

class TagBasicSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
#:

class TagTreeSerializer(ModelSerializer):
    children = SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'children']

    def get_children(self, obj):
        # Ensure children are filtered by the same vendor if needed for consistency,
        # though typically the parent is enough to constrain the tree.
        # This serializer is used for read-only tree structure.
        children = obj.subtags.all().order_by('name') # Order children for consistent display
        return TagTreeSerializer(children, many=True).data
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
    platform = StringRelatedField(allow_null=True)
    tag = StringRelatedField(allow_null=True)

    class Meta:
        model = Commands
        fields = ['id', 'command', 'description', 'example', 'version', 'vendor', 'platform', 'tag', 'method']
#:

class CSVUploadSerializer(serializers.Serializer):
    csv_file = serializers.FileField()
    vendor = serializers.PrimaryKeyRelatedField(queryset=Vendor.objects.all())
    main_tag = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        required=False,
        allow_null=True # Allow null for optional tag
    )

    def validate(self, data):
        print(data)
        # Additional validation to ensure main_tag (if provided) belongs to the selected vendor
        vendor = data.get('vendor')
        main_tag = data.get('main_tag')

        if main_tag and vendor:
            if main_tag.vendor != vendor:
                raise serializers.ValidationError({
                    'main_tag': 'The selected main tag does not belong to the selected vendor.'
                })
        return data
    #:
#:
