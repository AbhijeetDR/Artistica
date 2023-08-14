import django_filters
from .models import *
from django import forms
class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        exclude = ('image', 'description')
