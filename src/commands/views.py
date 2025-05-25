from commands.models import Commands
import django_filters.rest_framework

from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView, ListAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from .serializers import CSVUploadSerializer

from .models import Vendor, OS, Category, Commands
from .serializers import *
from .filters import CommandFilter
from .parsing.csv_parsing import ParseCsv
import chardet


class CommandPagination(PageNumberPagination):
    page_size = 10  # Default number of items per page
    page_size_query_param = 'page_size'  # Allows client to override page_size (e.g., ?page_size=20)
    max_page_size = 100  # Maximum page size allowed to prevent abuse
#:


# CRUD Admin
class AdminVendorViewSet(ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorFullSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
#:


# Vendors

# Create
class VendorCreateAPIView(CreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorFullSerializer
    permission_classes = [IsAuthenticated]

    # Override perform_create to automatically set created_by
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
#:

# Read
class UserVendorListSet(ListAPIView):
    serializer_class = VendorFullSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Vendor.objects.filter(created_by=user)
#:

class VendorListSet(ListAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorBasicSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
#:

# Delete
class UserVendorDelete(DestroyAPIView):
    serializer_class = VendorFullSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Vendor.objects.filter(created_by=user)
#:


# OSes

# CRUD Admin
class AdminOSViewSet(ModelViewSet):
    queryset = OS.objects.all()
    serializer_class = OSFullSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
#:

# Create
class OSCreateAPIView(CreateAPIView):
    queryset = OS.objects.all()
    serializer_class = OSFullSerializer
    permission_classes = [IsAuthenticated]

    # Override perform_create to automatically set created_by
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
#:

# Read
class UserOSListSet(ListAPIView):
    serializer_class = OSFullSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = OS.objects.filter(created_by=user)
        # Add filtering by vendor_id
        vendor_id = self.request.query_params.get('vendor_id', None)
        if vendor_id is not None:
            queryset = queryset.filter(vendor=vendor_id)
        return queryset
#:

class OSListSet(ListAPIView):
    queryset = OS.objects.all()
    serializer_class = OSBasicSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def get_queryset(self):
        queryset = OS.objects.all()
        # Add filtering by vendor_id
        vendor_id = self.request.query_params.get('vendor_id', None)
        if vendor_id is not None:
            queryset = queryset.filter(vendor=vendor_id)
        return queryset
#:

# Delete
class UserOSDelete(DestroyAPIView):
    serializer_class = OSFullSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return OS.objects.filter(created_by=user)
#:


# Categories

# CRUD Admin
class AdminCategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryFullSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
#:

# Create
class CategoryCreateAPIView(CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryFullSerializer
    permission_classes = [IsAuthenticated]

    # Override perform_create to automatically set created_by
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
#:

# Read
class UserCategoryListSet(ListAPIView):
    serializer_class = CategoryFullSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Category.objects.filter(created_by=user)
        # Add filtering by vendor_id
        vendor_id = self.request.query_params.get('vendor_id', None)
        if vendor_id is not None:
            queryset = queryset.filter(vendor=vendor_id)
        return queryset
#:

class CategoryListSet(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryBasicSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def get_queryset(self):
        queryset = Category.objects.all()
        # Add filtering by vendor_id
        vendor_id = self.request.query_params.get('vendor_id', None)
        if vendor_id is not None:
            queryset = queryset.filter(vendor=vendor_id)
        return queryset
#:

class CategoryTreeListSet(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryTreeSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def get_queryset(self):
        queryset = Category.objects.filter(parent__isnull=True) # Start with root categories for tree
        # Add filtering by vendor_id
        vendor_id = self.request.query_params.get('vendor_id', None)
        if vendor_id is not None:
            queryset = queryset.filter(vendor=vendor_id)
        return queryset
#:

# Delete
class UserCategoryDelete(DestroyAPIView):
    serializer_class = CategoryFullSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Category.objects.filter(created_by=user)
#:


# Commands

# CRUD Admin
class AdminCommandViewSet(ModelViewSet):
    queryset = Commands.objects.all()
    serializer_class = CommandFullSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
#:

# Create
class CommandCreateAPIView(CreateAPIView):
    queryset = Commands.objects.all()
    serializer_class = CommandFullSerializer
    permission_classes = [IsAuthenticated]

    # Override perform_create to automatically set created_by
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
#:

# Read
class UserCommandListSet(ListAPIView):
    serializer_class = CommandFullSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CommandPagination

    def get_queryset(self):
        user = self.request.user
        return Commands.objects.filter(created_by=user).select_related('vendor', 'os', 'category')
#:

class CommandListSet(ListAPIView):
    queryset = Commands.objects.all().select_related('vendor', 'os', 'category')
    serializer_class = CommandBasicSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    pagination_class = CommandPagination
#:

# Delete
class UserCommandDelete(DestroyAPIView):
    serializer_class = CommandFullSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Commands.objects.filter(created_by=user)
#:

# Filtered List
class CommandFilteredListView(ListAPIView):
    queryset = Commands.objects.all().select_related('vendor', 'os', 'category')
    serializer_class = CommandBasicSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = CommandFilter # Point to filter class
    permission_classes = [AllowAny]
    authentication_classes = []
    pagination_class = CommandPagination
#:


# --- CSV Upload View ---
class CommandCSVUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CSVUploadSerializer(data=request.data)

        if serializer.is_valid():
            csv_file = serializer.validated_data.get('csv_file')
            vendor_obj = serializer.validated_data.get('vendor') # Already a Vendor instance
            main_category_obj = serializer.validated_data.get('main_category') # Now an optional Category instance, or None

            try:
                raw_file_content = csv_file.read()

                detection_result = chardet.detect(raw_file_content)
                detected_encoding = detection_result['encoding']

                try:
                    decoded_file = raw_file_content.decode(detected_encoding)
                except (UnicodeDecodeError, TypeError):
                    print(f"Failed to decode with {detected_encoding}. Attempting UTF-8 fallback.")
                    decoded_file = raw_file_content.decode('utf-8', errors='replace')
                
                parsed_data = ParseCsv(
                    vendor_name=vendor_obj.name,
                    csv_file_content=decoded_file,
                    main_category=main_category_obj.name if main_category_obj else None
                )

                categories_created_count = 0
                commands_created_count = 0
                total_commands_processed = len(parsed_data.get('commands', []))
                total_categories_processed = len(parsed_data.get('categories', []))

                with transaction.atomic():
                    csv_parsed_categories_parent = main_category_obj

                    # Process Categories found in CSV
                    for cat_info in parsed_data.get('categories', []):
                        category_name = cat_info['name']
                        
                        category_obj, created = Category.objects.get_or_create(
                            name__iexact=category_name, # <-- ADDED __iexact here
                            parent=csv_parsed_categories_parent,
                            vendor=vendor_obj,
                            defaults={
                                'name': category_name, # Ensure original case name is saved if created
                                'created_by': request.user if request.user.is_authenticated else None
                            }
                        )
                        if created:
                            categories_created_count += 1

                    # Process Commands
                    for cmd_info in parsed_data.get('commands', []):
                        command_name = cmd_info['command']
                        description = cmd_info['description']
                        example = cmd_info['example']
                        csv_category_name = cmd_info['category']

                        final_command_category_obj = None

                        if csv_category_name:
                            try:
                                final_command_category_obj = Category.objects.get(
                                    name__iexact=csv_category_name,
                                    parent=csv_parsed_categories_parent,
                                    vendor=vendor_obj
                                )
                            except Category.DoesNotExist:
                                final_command_category_obj, _ = Category.objects.get_or_create(
                                    name__iexact=csv_category_name, # <-- ADDED __iexact here
                                    parent=csv_parsed_categories_parent,
                                    vendor=vendor_obj,
                                    defaults={
                                        'name': csv_category_name, # Ensure original case name is saved if created
                                        'created_by': request.user if request.user.is_authenticated else None
                                    }
                                )
                                if _: categories_created_count += 1
                        elif csv_parsed_categories_parent:
                            final_command_category_obj = csv_parsed_categories_parent

                        os_obj, _ = OS.objects.get_or_create(
                            name='N/A',
                            vendor=vendor_obj,
                            defaults={'created_by': request.user if request.user.is_authenticated else None}
                        )

                        existing_command = Commands.objects.filter(
                            command__iexact=command_name,
                            vendor=vendor_obj
                        ).first()

                        if existing_command:
                            print(f"Skipping duplicate command: '{command_name}' for vendor '{vendor_obj.name}'")
                            continue

                        command_obj, created = Commands.objects.get_or_create(
                            command=command_name,
                            vendor=vendor_obj,
                            category=final_command_category_obj,
                            os=os_obj,
                            defaults={
                                'description': description,
                                'example': example,
                                'created_by': request.user if request.user.is_authenticated else None
                            }
                        )
                        if created:
                            commands_created_count += 1

                return Response(
                    {
                        'message': 'CSV file uploaded and commands imported successfully!',
                        'data': {
                            'vendor_name': vendor_obj.name,
                            'main_category_name': main_category_obj.name if main_category_obj else 'N/A',
                            'categories_created': categories_created_count,
                            'commands_created': commands_created_count,
                            'total_commands_processed': total_commands_processed,
                            'total_categories_processed': total_categories_processed,
                        }
                    },
                    status=status.HTTP_200_OK
                )

            except Exception as e:
                import traceback
                print(f"\n--- DEBUG: Exception during processing ---")
                print(f"Error type: {type(e)}")
                print(f"Error message: {e}")
                print(f"Traceback:\n{traceback.format_exc()}")
                print("------------------------------------------\n")
                return Response(
                    {'error': f'An error occurred during CSV processing and import: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#:
