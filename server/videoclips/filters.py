from django_filters.rest_framework import FilterSet, CharFilter, DateFilter

from .models import Videoclip


class VideoclipFilter(FilterSet):
    title = CharFilter(lookup_expr='icontains', field_name='title')
    description = CharFilter(lookup_expr='icontains', field_name='description')
    categories__name = CharFilter(
        lookup_expr='icontains', field_name='categories__name')
    date_from = DateFilter(lookup_expr='date__gte', field_name='create_date')
    date_to = DateFilter(lookup_expr='date__lte', field_name='create_date')

    class Meta:
        model = Videoclip
        fields = ['title', 'description',
                  'categories__name', 'date_from', 'date_to']
