import django_filters
from .models import Commands, Vendor, Platform, Tag

class CommandFilter(django_filters.FilterSet):
    # For text-based search on command and description
    # icontains means case-insensitive containment
    search = django_filters.CharFilter(field_name='command', lookup_expr='icontains', label='Search Command')
    
    
    vendor__name = django_filters.CharFilter(lookup_expr='iexact', label='Vendor Name') # iexact for exact match
    platform__name = django_filters.CharFilter(lookup_expr='iexact', label='Platform Name')
    tag__name = django_filters.CharFilter(lookup_expr='iexact', label='Tag Name')

    # Filtering by version
    version = django_filters.CharFilter(lookup_expr='icontains', label='Version')

    class Meta:
        model = Commands
        fields = ['command', 'description', 'vendor__name', 'platform__name', 'tag__name', 'version']
    #:
#:
