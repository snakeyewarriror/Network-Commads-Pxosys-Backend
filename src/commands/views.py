from commands.models import Commands
import django_filters.rest_framework

from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from .serializers import CSVUploadSerializer

from .models import Vendor, Platform, Tag, Commands
from .serializers import *
from .filters import CommandFilter
from .parsing.csv_parsing import ParseCsv
import chardet


class CommandPagination(PageNumberPagination):
    page_size = 10  # Default number of items per page
    page_size_query_param = 'page_size'  # Allows client to override page_size (e.g., ?page_size=20)
    max_page_size = 100  # Maximum page size allowed
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
    permission_classes = [IsAuthenticated, IsAdminUser]

    # Override perform_create to automatically set created_by
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    #:
#:

# Update
class VendorUpdateAPIView(UpdateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorFullSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    
    def perform_update(self, serializer):
        serializer.save()
    #:
#:

# Read
class UserVendorListSet(ListAPIView):
    serializer_class = VendorFullSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        user = self.request.user
        return Vendor.objects.filter(created_by=user)
    #:
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
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        user = self.request.user
        return Vendor.objects.filter(created_by=user)
    #:
#:


# Platforms

# CRUD Admin
class AdminPlatformViewSet(ModelViewSet):
    queryset = Platform.objects.all()
    serializer_class = PlatformFullSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
#:

# Create
class PlatformCreateAPIView(CreateAPIView):
    queryset = Platform.objects.all()
    serializer_class = PlatformFullSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    # Override perform_create to automatically set created_by
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    #:
#:

# Update
class PlatformUpdateAPIView(UpdateAPIView):
    queryset = Platform.objects.all()
    serializer_class = PlatformFullSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    
    def perform_update(self, serializer):
        serializer.save()
    #:
#:

# Read
class UserPlatformListSet(ListAPIView):
    serializer_class = PlatformFullSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        user = self.request.user
        queryset = Platform.objects.filter(created_by=user)
        
        # Add filtering by vendor_id
        vendor_id = self.request.query_params.get('vendor_id', None)
        
        if vendor_id is not None:
            queryset = queryset.filter(vendor=vendor_id)
        #:
        return queryset
    #:
#:

class PlatformListSet(ListAPIView):
    queryset = Platform.objects.all()
    serializer_class = PlatformBasicSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def get_queryset(self):
        queryset = Platform.objects.all()
        
        # Add filtering by vendor_id
        vendor_id = self.request.query_params.get('vendor_id', None)
        
        if vendor_id is not None:
            queryset = queryset.filter(vendor=vendor_id)
        #:
        
        return queryset
    #:
#:

# Delete
class UserPlatformDelete(DestroyAPIView):
    serializer_class = PlatformFullSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        user = self.request.user
        return Platform.objects.filter(created_by=user)
    #:
#:


# Tags

# CRUD Admin
class AdminTagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagFullSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
#:

# Create
class TagCreateAPIView(CreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagFullSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    # Override perform_create to automatically set created_by
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    #:
#:

# Update
class TagUpdateAPIView(UpdateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagFullSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    
    lookup_field = 'name'
    
    
    def perform_update(self, serializer):
        serializer.save()
    #:
#:

# Read
class UserTagListSet(ListAPIView):
    serializer_class = TagFullSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        user = self.request.user
        queryset = Tag.objects.filter(created_by=user)
        # Add filtering by vendor_id
        vendor_id = self.request.query_params.get('vendor_id', None)
        
        if vendor_id is not None:
            queryset = queryset.filter(vendor=vendor_id)
        #:
        return queryset
    #:
#:

class TagListSet(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagBasicSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def get_queryset(self):
        queryset = Tag.objects.all()
        
        # Add filtering by vendor_id
        vendor_id = self.request.query_params.get('vendor_id', None)
        
        if vendor_id is not None:
            queryset = queryset.filter(vendor=vendor_id)
        #:
        return queryset
    #:
#:

class TagTreeListSet(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagTreeSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def get_queryset(self):
        queryset = Tag.objects.filter(parent__isnull=True) # Start with root tags for tree
        
        vendor_id = self.request.query_params.get('vendor_id', None)
        
        if vendor_id is not None:
            queryset = queryset.filter(vendor=vendor_id)
        #:
        
        return queryset
    #:
#:

# Delete
class UserTagDelete(DestroyAPIView):
    serializer_class = TagFullSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        user = self.request.user
        return Tag.objects.filter(created_by=user)
    #:
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
    permission_classes = [IsAuthenticated, IsAdminUser]

    # Override perform_create to automatically set created_by
    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            method='SINGULAR',
            )
        #:
#:

# Update
class CommandUpdateAPIView(UpdateAPIView):
    queryset = Commands.objects.all()
    serializer_class = CommandFullSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    
    def perform_update(self, serializer):
        serializer.save()
#:

# Checks if the command exists
class CommandExistsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, *args, **kwargs):
        command_name = request.query_params.get('command_name')
        vendor_id = request.query_params.get('vendor_id')

        if not command_name or not vendor_id:
            return Response(
                {'error': 'Both command_name and vendor_id are required query parameters.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        #:

        try:
            vendor_obj = Vendor.objects.get(pk=vendor_id)
        #:
            
        except Vendor.DoesNotExist:
            return Response(
                {'error': 'Vendor not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        #:

        # Use iexact for case-insensitive command name lookup
        command_obj = Commands.objects.filter(
            command__iexact=command_name,
            vendor=vendor_obj
        ).first()

        if command_obj:
            return Response({'exists': True, 'id': command_obj.id}, status=status.HTTP_200_OK)
        #:
        
        else:
            return Response({'exists': False}, status=status.HTTP_200_OK)
        #:
    #:
#:

# Read
class UserCommandListSet(ListAPIView):
    serializer_class = CommandFullSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CommandPagination

    def get_queryset(self):
        user = self.request.user
        return Commands.objects.filter(created_by=user).select_related('vendor', 'platform', 'tag')
    #:
#:

class CommandListSet(ListAPIView):
    queryset = Commands.objects.all().select_related('vendor', 'platform', 'tag')
    serializer_class = CommandBasicSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    pagination_class = CommandPagination
#:

# Delete
class UserCommandDelete(DestroyAPIView):
    serializer_class = CommandFullSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        user = self.request.user
        return Commands.objects.filter(created_by=user)
    #:
#:

# Filtered List
class CommandFilteredListView(ListAPIView):
    queryset = Commands.objects.all().select_related('vendor', 'platform', 'tag')
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
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = CSVUploadSerializer(data=request.data)

        if serializer.is_valid():
            csv_file = serializer.validated_data.get('csv_file')
            vendor_obj = serializer.validated_data.get('vendor')
            main_tag_obj = serializer.validated_data.get('main_tag')
            override_existing = serializer.validated_data.get('override')

            # Lists to store detailed results
            created_commands_details = []
            updated_commands_details = []
            skipped_commands_details = []
            created_tags_details = []

            try:
                raw_file_content = csv_file.read()

                detection_result = chardet.detect(raw_file_content)
                detected_encoding = detection_result['encoding']

                try:
                    decoded_file = raw_file_content.decode(detected_encoding)
                #:
                
                except (UnicodeDecodeError, TypeError):
                    print(f"Failed to decode with {detected_encoding}. Attempting UTF-8 fallback.")
                    decoded_file = raw_file_content.decode('utf-8', errors='replace')
                #:
                
                parsed_data = ParseCsv(
                    vendor_name=vendor_obj.name,
                    csv_file_content=decoded_file,
                    main_tag_name_for_csv_context=main_tag_obj.name if main_tag_obj else None
                )

                total_commands_processed = len(parsed_data.get('commands', []))
                total_tags_processed = len(parsed_data.get('tags', []))

                with transaction.atomic():
                    csv_parsed_tags_parent = main_tag_obj

                    # Handle main_tag_obj being a name from input and needing creation as root
                    if csv_parsed_tags_parent is None and serializer.initial_data.get('main_tag'):
                        main_tag_name_from_input = serializer.initial_data.get('main_tag')
                        
                        csv_parsed_tags_parent, created = Tag.objects.get_or_create(
                            name__iexact=main_tag_name_from_input,
                            vendor=vendor_obj,
                            parent__isnull=True,
                            defaults={
                                'name': main_tag_name_from_input,
                                'created_by': request.user if request.user.is_authenticated else None
                            }
                        )
                        
                        if created:
                            created_tags_details.append({
                                'name': csv_parsed_tags_parent.name,
                                'parent': csv_parsed_tags_parent.parent.name if csv_parsed_tags_parent.parent else None,
                                'status': 'Created (Main Tag)'
                            })
                        #:
                    #:
                    
                    # Process tags found in CSV
                    for cat_info in parsed_data.get('tags', []):
                        tag_name = cat_info['name']
                        
                        if csv_parsed_tags_parent and tag_name.lower() == csv_parsed_tags_parent.name.lower():
                            # This is the main tag itself, not a new child created from CSV
                            tag_obj = csv_parsed_tags_parent
                            created = False
                        #:
                        
                        else:
                            tag_obj, created = Tag.objects.get_or_create(
                                name__iexact=tag_name,
                                vendor=vendor_obj,
                                parent=csv_parsed_tags_parent,
                                defaults={
                                    'name': tag_name,
                                    'created_by': request.user if request.user.is_authenticated else None
                                }
                            )
                        #:
                        
                        if created:
                            created_tags_details.append({
                                'name': tag_obj.name,
                                'parent': tag_obj.parent.name if tag_obj.parent else None,
                                'status': 'Created'
                            })
                        #:


                    # Process Commands
                    for cmd_info in parsed_data.get('commands', []):
                        command_name = cmd_info['command']
                        description = cmd_info['description']
                        example = cmd_info['example']
                        csv_tag_name = cmd_info['tag'] # This is the specific tag for THIS command

                        final_command_tag_obj = None

                        if csv_tag_name:
                            try:
                                final_command_tag_obj = Tag.objects.get(
                                    name__iexact=csv_tag_name,
                                    vendor=vendor_obj,
                                    parent=csv_parsed_tags_parent # Ensure it's under the desired parent
                                )
                            #:
                            
                            except Tag.DoesNotExist:
                                # If it doesn't exist, create it under the 'csv_parsed_tags_parent'
                                final_command_tag_obj, _ = Tag.objects.get_or_create(
                                    name__iexact=csv_tag_name,
                                    vendor=vendor_obj,
                                    parent=csv_parsed_tags_parent, # Assign parent here
                                    defaults={
                                        'name': csv_tag_name,
                                        'created_by': request.user if request.user.is_authenticated else None
                                    }
                                )
                                if _:
                                    created_tags_details.append({
                                        'name': final_command_tag_obj.name,
                                        'parent': final_command_tag_obj.parent.name if final_command_tag_obj.parent else None,
                                        'status': 'Created (from Command Tag)'
                                    })
                            #:
                        #:
                        
                        elif csv_parsed_tags_parent:
                            final_command_tag_obj = csv_parsed_tags_parent
                        #:

                        
                        platform_obj, _ = Platform.objects.get_or_create( 
                            name='N/A',
                            vendor=vendor_obj,
                            defaults={'created_by': request.user if request.user.is_authenticated else None}
                        )

                        lookup_params = {
                            'command__iexact': command_name,
                            'vendor': vendor_obj,
                        }
                        
                        defaults = {
                            'command': command_name,
                            'description': description,
                            'example': example,
                            'tag': final_command_tag_obj,
                            'platform': platform_obj,
                            'created_by': request.user if request.user.is_authenticated else None,
                            'method': 'BULK'
                        }

                        try:
                            
                            command_obj, created = Commands.objects.update_or_create(
                                **lookup_params,
                                defaults=defaults
                            )
                            
                            if created:
                                created_commands_details.append({
                                    'command': command_obj.command,
                                    'description': command_obj.description,
                                    'tag': command_obj.tag.name if command_obj.tag else 'N/A',
                                    'status': 'Created Successfully'
                                })
                            #:
                                
                            elif override_existing: # If the command was note created and a the override bool is true
                                updated_commands_details.append({
                                    'command': command_obj.command,
                                    'description': command_obj.description,
                                    'tag': command_obj.tag.name if command_obj.tag else 'N/A',
                                    'status': 'Updated Successfully'
                                })
                            #:
                                
                            else: # Existed, but update_existing is False, so skip
                                skipped_commands_details.append({
                                    'command': command_name,
                                    'reason': 'Command already exists and update_existing flag is false',
                                    'status': 'Skipped'
                                })
                            #:
                            
                        except Exception as create_error:
                            # Catching any other errors during command creation (e.g., validation)
                            skipped_commands_details.append({
                                'command': command_name,
                                'reason': f'Error during creation/updating: {str(create_error)}',
                                'status': 'Failed'
                            })
                            print(f"Error creating/updating command '{command_name}': {create_error}")
                        #:
                    #:

                return Response(
                    {
                        'message': 'CSV file upload process completed.',
                        'data': {
                            'vendor_name': vendor_obj.name,
                            'main_tag_name': main_tag_obj.name if main_tag_obj else 'N/A',
                            'summary': {
                                'total_commands_in_csv': total_commands_processed,
                                'commands_created': len(created_commands_details),
                                'commands_updated': len(updated_commands_details),
                                'commands_skipped': len(skipped_commands_details),
                                'total_tags_in_csv': total_tags_processed,
                                'tags_created': len(created_tags_details),
                            },
                            'details': {
                                'created_commands': created_commands_details,
                                'updated_commands': updated_commands_details,
                                'skipped_commands': skipped_commands_details,
                                'created_tags': created_tags_details,
                            }
                        }
                    },
                    status=status.HTTP_200_OK
                )
            #:

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
            #:
        #:
        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        #:
    #:
#:
