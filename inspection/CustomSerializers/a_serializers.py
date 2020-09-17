from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from inspection.models import (User, UserProfile, Departement, Docks,
                               Vessel, Loading, Inspection,
                               HourlyCheck, ProductType, ProductCategory,
                               ProductFamily, Product, Origin,
                               Client, ClientLoadingDetails,
                               Halt, HaltEvent, IncidentEvent,
                               IncidentSpecs, IncidentDetails, Port, IntermediateDraughtSurvey, Files)

import json
import ntpath
import os


class ProductTypeCustomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ('name',)


class ProductFamilyCustomSerializer(serializers.ModelSerializer):
    productype = serializers.SerializerMethodField('get_type')

    def get_type(self, productf):
        queryset = ProductType.objects.get(id=productf.product_type_ref.id)
        serializer = ProductTypeCustomSerializer(queryset, many=False)
        return serializer.data

    class Meta:
        model = ProductFamily
        fields = ('name', 'productype')


class ProductCategoryCustomSerializer(serializers.ModelSerializer):
    productfamily = serializers.SerializerMethodField('get_family')

    def get_family(self, productc):
        queryset = ProductFamily.objects.get(id=productc.product_family_ref.id)
        serializer = ProductFamilyCustomSerializer(queryset, many=False)
        return serializer.data

    class Meta:
        model = ProductCategory
        fields = ('name', 'productfamily')


class ProductCustomSerializer(serializers.ModelSerializer):
    productcategory = serializers.SerializerMethodField('get_category')

    def get_category(self, product):
        queryset = ProductCategory.objects.get(
            id=product.product_category_ref.id)
        serializer = ProductCategoryCustomSerializer(queryset, many=False)
        return serializer.data

    class Meta:
        model = Product
        fields = ('id', 'name', 'productcategory')


class IntermediateDraughtSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = IntermediateDraughtSurvey
        fields = '__all__'


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = '__all__'


class HaltEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = HaltEvent
        fields = '__all__'


class HaltSerializer(serializers.ModelSerializer):
    halt_event = serializers.SerializerMethodField('get_event')

    def get_event(self, halt):
        queryset = HaltEvent.objects.get(id=halt.halt_event_ref.id)
        serializer = HaltEventSerializer(queryset, many=False)
        return serializer.data['name']

    class Meta:
        model = Halt
        fields = ('id', 'halt_event', 'possible_cause')


class IncidentEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentEvent
        fields = '__all__'


class IncidentSpecSerializer(serializers.ModelSerializer):
    incident_event = serializers.SerializerMethodField('get_event')

    def get_event(self, incidentspec):
        queryset = IncidentEvent.objects.get(
            id=incidentspec.incident_event_ref.id)
        serializer = IncidentEventSerializer(queryset, many=False)
        return serializer.data['name']

    class Meta:
        model = IncidentSpecs
        fields = ('id',
                  'incident_event',
                  'qte_by_kgs',
                  'temperature',
                  'possible_cause',
                  'humidity_rate'
                  )


class FileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_name')

    def get_name(self, queryset):
        return os.path.basename(str(queryset.file))

    class Meta:
        model = Files
        fields = '__all__'

# Product Listing


class ProductTreeFamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFamily
        fields = ('id', 'name')


class ProductTreeTypeSerializer(serializers.ModelSerializer):
    productfamily = serializers.SerializerMethodField('get_family')

    def get_family(self, queryset):
        queryset = ProductFamily.objects.all()
        serializer = ProductTreeFamilySerializer(queryset)
        return serializer.data

    class Meta:
        model = ProductType
        fields = ('name', 'productfamily')

# Product Listing

# Charts Serializers


class ChartIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentDetails
        # exclude = ('description',)
        fields = '__all__'
