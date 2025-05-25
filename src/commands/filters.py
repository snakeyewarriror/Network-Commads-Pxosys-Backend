import django_filters
from .models import Commands, Vendor, OS, Category

class CommandFilter(django_filters.FilterSet):
    # For text-based search on command and description
    # icontains means case-insensitive containment
    search = django_filters.CharFilter(field_name='command', lookup_expr='icontains', label='Search Command')
    
    
    vendor__name = django_filters.CharFilter(lookup_expr='iexact', label='Vendor Name') # iexact for exact match
    os__name = django_filters.CharFilter(lookup_expr='iexact', label='OS Name')
    category__name = django_filters.CharFilter(lookup_expr='iexact', label='Category Name')

    # Filtering by version
    version = django_filters.CharFilter(lookup_expr='icontains', label='Version')

    class Meta:
        model = Commands
        fields = ['command', 'description', 'vendor__name', 'os__name', 'category__name', 'version']
    #:
#:
