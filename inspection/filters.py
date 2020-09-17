import django_filters
from django_filters import FilterSet, BooleanFilter, Filter, CharFilter
from .models import User, Inspection
from django_filters.fields import Lookup
from django.db.models import Q


class UserFilterSet(FilterSet):
    is_refused = BooleanFilter('profile__is_refused')
    first_name = CharFilter(method='first_name_filter')
    last_name = CharFilter(method='last_name_filter')
    email = CharFilter(method='email_filter')
    company = CharFilter('profile__company_name')

    class Meta:
        model = User
        fields = ['is_refused', 'is_active', 'is_staff',
                  'first_name', 'last_name', 'email', 'company']

    def first_name_filter(self, queryset, name, value):
        return queryset.filter(first_name__icontains=value)

    def last_name_filter(self, queryset, name, value):
        return queryset.filter(last_name__icontains=value)

    def email_filter(self, queryset, name, value):
        return queryset.filter(email__icontains=value)

    def company_filter(self, queryset, name, value):
        return queryset.filter(profile__company_name__icontains=value)
