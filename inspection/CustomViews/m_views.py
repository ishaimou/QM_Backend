from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
import datetime
import json
from django.http import HttpResponseNotFound
from django.db.models import Count, Sum
from django.db.models import Q


from inspection.serializers import (HourlyCheckSerializer, UserIsActive,
                                    IncidentDetailSerializer, ProductSerializer, InspectionSerializer)
from inspection.choices import Incident_Choices

from inspection.CustomSerializers.m_serializers import ProductListSerializer

from inspection.models import (HourlyCheck, User, ProductCategory, Inspection,
                               IncidentDetails, ProductFamily, Product, ClientLoadingDetails)


class HourlyCheckByInspecRefView(generics.ListCreateAPIView):

    permission_classes = (AllowAny, )
    serializer_class = HourlyCheckSerializer
    queryset = HourlyCheck.objects.all()

    def list(self, request, pk):
        hourlyCheckRef = HourlyCheck.objects.filter(inspection_ref=pk)
        queryset = self.filter_queryset(hourlyCheckRef)
        pagination = self.paginate_queryset(queryset)
        serialized = self.get_serializer(pagination, many=True)
        if pagination is not None:
            return self.get_paginated_response(serialized.data)
        return Response(serialized.data)

    def create(self, request, pk):
        try:
            inspection = Inspection.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "The referenced inspection does not exist"})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['inspection_ref'] = inspection
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()


def structureTree(items, pop='name'):
    result = {}
    for key in Incident_Choices:
        result[key[0]] = {"count": 0}
    for item in items:
        key = item.pop(pop)
        if key not in result:
            result[key] = {}
        result[key].update(item)
    return result


class MonthlyEventsViewSet(generics.ListAPIView):
    '''
        List all event which happens this month
    '''
    permission_classes = (AllowAny, )
    serializer_class = IncidentDetailSerializer
    queryset = IncidentDetails.objects.all()

    today = datetime.datetime.now()

    def get(self, request):
        Events = IncidentDetails.objects\
            .filter(stopping_hour__year=self.today.year, stopping_hour__month=self.today.month)\
            .values("related").annotate(count=Count("id"))
        result = structureTree(Events, 'related')
        return Response(result)


class UserDisableViewSet(generics.UpdateAPIView):
    '''
        View Responsible for Disable or enable back a user
        Only admins have the rights to do so
    '''
    # Make sure to set permission later on
    permission_classes = (AllowAny, )
    queryset = User.objects.all()
    serializer_class = UserIsActive


class ProductListView(generics.ListAPIView):
    '''
        Retrieve a list of product with category name and family name listed as well
    '''

    permission_classes = (AllowAny, )
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer


# Get tree of product and their families with Quantities

class QuantitiesStatView(generics.ListAPIView):
    permission_classes = (AllowAny, )
    queryset = ClientLoadingDetails.objects.all()
    today = datetime.datetime.now()

    def group_by(self, res, nameToPop):
        result = {}
        for obj in res:
            key = obj.pop(nameToPop)
            if key not in result:
                result[key] = []
            result[key].append(obj)
        result

    def get_product(self, objs):
        res = []
        key = None
        for obj in objs:
            data = {
                'Quantity': obj['Quantity'],
                obj['product_ref__name']: []
            }
            new = {
                Inspection.objects.filter(loading_ref=obj['loading_ref']).values('vessel_ref__name')[0]['vessel_ref__name']: ClientLoadingDetails.objects.filter(loading_ref__loading_starting_date__year=self.today.year,
                                                                                                                                                                 loading_ref__loading_starting_date__month=obj[
                                                                                                                                                                     'loading_ref__loading_starting_date__month'],
                                                                                                                                                                 loading_ref=obj['loading_ref'], product_ref=obj['product_ref']).values().aggregate(Quantity=Sum('quantity'))['Quantity']
            }
            key = obj['product_ref__name']
            data[key] = new
            res.append(data)
        tree = {'Quantity': 0}
        for r in res:
            if key not in tree:
                tree[key] = {}
            tree['Quantity'] = tree['Quantity'] + r['Quantity']
            tree[key].update(r[key])
        return tree

    def get_categories(self, objs, products):
        res = []
        for obj in objs:
            Month = obj['loading_ref__loading_starting_date__month']
            data = {
                'Quantity': obj['Quantity'],
                obj['product_ref__product_category_ref__name']: []
            }
            prod = products.filter(product_ref__product_category_ref=obj['product_ref__product_category_ref'],
                                   loading_ref__loading_starting_date__month=Month)
            # print(prod)
            data[obj['product_ref__product_category_ref__name']].append(
                self.get_product(prod))
            key = obj['product_ref__product_category_ref__name']
            res.append(data)

        return res

    def list(self, request):
        products = ClientLoadingDetails.objects.filter(loading_ref__loading_starting_date__year=self.today.year)\
            .select_related('product_ref')\
            .values('loading_ref__loading_starting_date__month',
                    'product_ref', 'product_ref__name', 'loading_ref',
                    'loading_ref__loading_starting_date__month')\
            .annotate(Quantity=Sum('quantity'))

        categories = products\
            .values('product_ref__product_category_ref__name')\
            .values('loading_ref__loading_starting_date__month',
                    'product_ref__product_category_ref__name',
                    'product_ref__product_category_ref')\
            .annotate(Quantity=Sum('quantity'))

        families = categories.values('loading_ref__loading_starting_date__month',
                                     'product_ref__product_category_ref__product_family_ref',
                                     'product_ref__product_category_ref__product_family_ref__name')\
            .annotate(Quantity=Sum('quantity'))

        # Get all families
        tree = {}
        # bj_families = ProductFamily.objects.all()
        # for family in families:
        #     print(family)

        for family in families:
            print(family)
            month = family['loading_ref__loading_starting_date__month']
            day = datetime.datetime(
                year=2019, month=month, day=1).strftime("%m/%d/%Y")
            data = {
                'Quantity': family['Quantity'],
                day: [],
            }
            res = categories.filter(product_ref__product_category_ref__product_family_ref=family['product_ref__product_category_ref__product_family_ref'],
                                    loading_ref__loading_starting_date__month=month)
            data[day] = self.get_categories(res, products)
            key = family['product_ref__product_category_ref__product_family_ref__name']
            if key not in tree:
                tree[key] = []
            tree[key].append(data)
        return Response(tree)


class EventsCountView(generics.ListAPIView):
    permission_classes = (AllowAny, )
    serializer_class = InspectionSerializer

    def list(self, request):

        INPROGRESS = Inspection.objects.filter(inspection_status='INPROGRESS')\
            .aggregate(INPROGRESS=Count('inspection_status'))
        ONHOLD = Inspection.objects.filter(inspection_status='ONHOLD')\
            .aggregate(ONHOLD=Count('inspection_status'))
        return Response({**INPROGRESS, **ONHOLD})

# Handling 404 Errors in production mode


def error404(request, exception):
    response_data = {}
    response_data['detail'] = 'Not found.'
    return HttpResponseNotFound(json.dumps(response_data), content_type="application/json")
