from django.views.generic.edit import UpdateView
from rest_framework.decorators import api_view
from rest_framework import viewsets
from .permissions import IsAdminUser
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import django_filters
import datetime
from django.db.models import Count, Sum, Max, Min
from .filters import UserFilterSet  # , InspectionFilterSet
from django.core import serializers
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from inspection.pagination import PageNumberPaginationDataOnly
# Models imports
from inspection.models import (User, Halt,
                               UserProfile, Departement, Vessel,
                               Loading, Inspection, HourlyCheck,
                               ProductCategory, ProductFamily, Product,
                               Origin, Client, ClientLoadingDetails,
                               Halt, HaltEvent, IncidentEvent,
                               IncidentSpecs, IncidentDetails, Docks, Port, IntermediateDraughtSurvey, Files)

# Serialiazers Imports
from inspection.serializers import (UserSerializer, UserRefusedSerializer,
                                    UserCreateSerializer, DepartementSerializer,
                                    VesselSerializer, LoadingSerializer, LoadingFullSerializer, InspectionSerializer,
                                    HourlyCheckSerializer, ProductCategorySerializer,
                                    ProductFamilySerializer, ProductSerializer,
                                    OriginSerializer, ClientSerializer,
                                    ClientLoadingDetailSerializer, HaltCustomSerializer,
                                    HaltEventCustomSerializer, IncidentEventCustomSerializer,
                                    IncidentDetailSerializer, IncidentSpecCustomSerializer,
                                    PortSerializer, MyTokenObtainPairSerializer, InspectionTestSerializer)

from inspection.CustomSerializers.a_serializers import HaltSerializer, IncidentSpecSerializer, FileSerializer

# Permissions Import
from inspection.permissions import IsLoggedInUserOrAdmin, IsAdminUser
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django.core.exceptions import ObjectDoesNotExist
import os
import json
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.http import JsonResponse


class DepartementView(viewsets.ModelViewSet):
    queryset = Departement.objects.all()
    serializer_class = DepartementSerializer
    permission_classes = (AllowAny,)


class VesselView(viewsets.ModelViewSet):
    queryset = Vessel.objects.all()
    serializer_class = VesselSerializer
    permission_classes = (AllowAny,)


class LoadingView(viewsets.ModelViewSet):
    queryset = Loading.objects.all()
    serializer_class = LoadingFullSerializer
    permission_classes = (AllowAny,)


class InspectionView(viewsets.ModelViewSet):
    queryset = Inspection.objects.all()
    serializer_class = InspectionSerializer
    permission_classes = (AllowAny,)


class InspectionTestView(viewsets.ModelViewSet):
    queryset = Inspection.objects.all()
    serializer_class = InspectionTestSerializer
    permission_classes = (AllowAny,)
    # filter_class = InspectionFilterSet
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = [  # 'inspection_status',
        'vessel_ref',
        'loading_ref__loading_port',
        'user_ref',
        'user_ref__profile__company_name',
        'dock__which_dock',
        'foreign_inspector'
    ]
    ordering_fields = ['inspection_date']
    pagination_class = PageNumberPaginationDataOnly

    def list(self, request, *args, **kwargs):
        settler = False
        if 'inspection_status' in request.GET:
            settler = True
            status = Inspection.objects.none()
            if request.GET['inspection_status'].count(',') != 0:
                arguments = request.GET['inspection_status'].split(',')
                for a in arguments:
                    temporary = Inspection.objects.filter(inspection_status=a)
                    status = status | temporary
                queryset = self.filter_queryset(status)
            else:
                queryset = Inspection.objects.filter(
                    inspection_status=request.GET['inspection_status'])
                queryset = self.filter_queryset(queryset)
        else:
            queryset = self.filter_queryset(self.get_queryset())
        if 'date_start' in request.GET:
            start = request.GET['date_start']
            end = request.GET['date_end']
            date_start = datetime.date(
                int(start[:4]), int(start[5:7]), int(start[8:10]))
            date_end = datetime.date(
                int(end[:4]), int(end[5:7]), int(end[8:10]))
            queryset = Inspection.objects.filter(
                inspection_date__range=[date_start, date_end])
            if settler == True:
                if request.GET['inspection_status'].count(',') != 0:
                    status = Inspection.objects.none()
                    for a in arguments:
                        temporary = Inspection.objects.filter(
                            inspection_status=a, inspection_date__range=[date_start, date_end])
                        status = status | temporary
                    queryset = status
                else:
                    queryset = Inspection.objects.filter(
                        inspection_status=request.GET['inspection_status'])
            queryset = self.filter_queryset(queryset)
        elif 'date_start' not in request.GET and 'inspection_status' not in request.GET:
            queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "count": 0,
            "data": serializer.data
        })

    def partial_update(self, request, *args, **kwargs):
        data = request.data.copy()
        kwargs['partial'] = True
        updated_data = self.update(request, *args, **kwargs)
        if 'inspection_status' in request.data:
            if request.data['inspection_status'] == 'CLOSED':
                Surveys = IntermediateDraughtSurvey.objects.filter(
                    loading_ref=request.data['port']['id'])
                Values = Surveys.aggregate(
                    Min('start_inter_draugth_surv'), Max('end_inter_draugth_surv'))
                H_C = HourlyCheck.objects.filter(inspection_ref=Inspection.objects.get(
                    loading_ref=request.data['port']['id']))
                Humidity_values = H_C.aggregate(
                    Min('humidity'), Max('humidity'))
                Temperature_values = H_C.aggregate(
                    Min('temperature'), Max('temperature'))
                if Humidity_values['humidity__min'] == None or Humidity_values['humidity__max'] == None:
                    Humidity = None
                else:
                    Humidity = str(
                        Humidity_values['humidity__min']) + '-' + str(Humidity_values['humidity__max'])
                if Temperature_values['temperature__min'] == None or Temperature_values['temperature__max'] == None:
                    Temperature = None
                else:
                    Temperature = str(
                        Temperature_values['temperature__min']) + '-' + str(Temperature_values['temperature__max'])
                survey_update = Loading.objects.filter(id=request.data['port']['id']).update(
                    initial_draugth_surv=Values['start_inter_draugth_surv__min'], final_draugth_surv=Values['end_inter_draugth_surv__max'], air_temperature=Temperature, humidity_percentage=Humidity)
        return updated_data


def handle_upload_file(f, path):
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def path_maker(inspection_pk, incident_pk, product_pk, hourlycheck_pk, survey_pk, client_pk):
    if os.path.exists('./uploads/') == False:
        os.mkdir('./uploads/')
    inspection_path = './uploads/' + str(inspection_pk)
    if os.path.exists(inspection_path) == False:
        os.mkdir(inspection_path)
    if incident_pk.isdigit():
        path = inspection_path + '/incident/'
        if os.path.exists(path) == False:
            os.mkdir(path)
    elif product_pk.isdigit():
        path = inspection_path + '/product/'
        if os.path.exists(path) == False:
            os.mkdir(path)
        path = path + product_pk + '/'
        if os.path.exists(path) == False:
            os.mkdir(path)
    elif hourlycheck_pk.isdigit():
        path = inspection_path + '/hourlycheck/'
        if os.path.exists(path) == False:
            os.mkdir(path)
    elif survey_pk.isdigit():
        path = inspection_path + '/survey/'
        if os.path.exists(path) == False:
            os.mkdir(path)
    elif client_pk.isdigit():
        path = inspection_path + '/client/'
        if os.path.exists(path) == False:
            os.mkdir(path)
    else:
        path = inspection_path + '/'
    return path


def file_create(data, files):
    inspection_pk = "" if "inspection_ref" not in data else data[
        'inspection_ref']
    try:
        inspection_instance = Inspection.objects.get(id=inspection_pk)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "AYYYWAAAAA.. Tga3d 3la slamtek"})
    incident_pk = "" if "incident_ref" not in data else data[
        'incident_ref']
    product_pk = "" if "product_ref" not in data else data['product_ref']
    hourlycheck_pk = "" if "hourlycheck_ref" not in data else data[
        'hourlycheck_ref']
    survey_pk = "" if "survey_ref" not in data else data['survey_ref']
    client_pk = "" if "client_id" not in data else data['client_id']
    path = path_maker(inspection_pk, incident_pk, product_pk,
                      hourlycheck_pk, survey_pk, client_pk)
    for v in files.getlist('file'):
        try:
            time = str(datetime.datetime.now()).translate(
                {ord(i): None for i in '-: '})[:14] + '_'
            new_path = path + time + str(v)
            handle_upload_file(v, new_path)
            if 'hourlycheck_ref' in data:
                Files.objects.create(
                    file=new_path[10:],
                    inspection_ref=Inspection.objects.get(
                        id=data['inspection_ref']),
                    hourlycheck_ref=HourlyCheck.objects.get(
                        id=data['hourlycheck_ref'])
                )
            elif 'product_ref' in data:
                Files.objects.create(
                    file=new_path[10:],
                    inspection_ref=Inspection.objects.get(
                        id=int(data['inspection_ref'])),
                    product_ref=Product.objects.get(id=data['product_ref'])
                )
            elif 'incident_ref' in data:
                Files.objects.create(
                    file=new_path[10:],
                    inspection_ref=Inspection.objects.get(
                        id=data['inspection_ref']),
                    incident_ref=IncidentDetails.objects.get(
                        id=data['incident_ref'])
                )
            elif 'survey_ref' in data:
                Files.objects.create(
                    file=new_path[10:],
                    inspection_ref=Inspection.objects.get(
                        id=data['inspection_ref']),
                    survey_ref=IntermediateDraughtSurvey.objects.get(
                        id=data['survey_ref'])
                )
            elif 'client_id' in data:
                Files.objects.create(
                    file=new_path[10:],
                    inspection_ref=Inspection.objects.get(
                        id=data['inspection_ref']),
                    client_ref=Client.objects.get(id=data['client_id'])
                )
        except ObjectDoesNotExist:
            return Response(data={"msg": "Info Missing"}, status=status.HTTP_400_BAD_REQUEST)
    return Response(data={"msg": "Uploaded Successfully"}, status=status.HTTP_201_CREATED)


class HourlyCheckView(generics.ListCreateAPIView):
    queryset = HourlyCheck.objects.all()
    serializer_class = HourlyCheckSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['inspection_ref']
    ordering_fields = ['date']
    ordering = ['date']
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if (
            'inspection_ref' in request.data
            and 'temperature' in request.data
            and 'humidity' in request.data
            and 'debit' in request.data
            and 'ambient_temperature' in request.data
            and 'date' in request.data
            and 'origin' in request.data
        ):
            inspection_inst = Inspection.objects.get(
                id=request.data['inspection_ref'])
            origin_inst = Origin.objects.get(id=request.data['origin'])
            hourlycheck = HourlyCheck.objects.create(
                inspection_ref=inspection_inst,
                temperature=request.data['temperature'],
                humidity=request.data['humidity'],
                debit=request.data['debit'],
                ambient_temperature=request.data['ambient_temperature'],
                date=request.data['date'],
                origin=origin_inst
            )
            hourlycheck_ref = hourlycheck.id
        data = request.data.copy()
        data.update({"hourlycheck_ref": str(hourlycheck_ref)})
        if request.FILES:
            files = request.FILES.copy()
            file_create(data, files)
        return Response(data={"Hourly Check Created"}, status=status.HTTP_201_CREATED)


class ProductCategoryView(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = (AllowAny,)


class ProductFamilyView(viewsets.ModelViewSet):
    queryset = ProductFamily.objects.all()
    serializer_class = ProductFamilySerializer
    permission_classes = (AllowAny,)


class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)


class OriginView(viewsets.ModelViewSet):
    queryset = Origin.objects.all()
    serializer_class = OriginSerializer
    permission_classes = (AllowAny,)
    permission_classes = (AllowAny,)


class ClientView(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = (AllowAny,)


class ClientLoadingDetailView(viewsets.ModelViewSet):
    queryset = ClientLoadingDetails.objects.all()
    serializer_class = ClientLoadingDetailSerializer
    permission_classes = (AllowAny,)


class PortView(viewsets.ModelViewSet):
    """
    """
    queryset = Port.objects.all()
    serializer_class = PortSerializer
    permission_classes = (IsLoggedInUserOrAdmin,)


class RequirementView(generics.CreateAPIView):
    permission_classes = (IsLoggedInUserOrAdmin,)

    def post(self, request):
        port_id = request.data["loading_port"]
        dock_number = request.data["which_dock"]
        vessel_pk = request.data["inspection"]["vessel_id"]
        user_pk = request.data["inspection"]["user_id"]
        vessel_breath = request.data["inspection"]["vessel_breathed"]
        vessel_arrive = request.data["inspection"]["vessel_arrived"]
        inspection_date = request.data["inspection_date"]

        try:
            port_instance = Port.objects.get(pk=port_id)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "Port does not exist"})
        try:
            vessel_instance = Vessel.objects.get(pk=vessel_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "Vessel does not exist"})
        try:
            user_instance = User.objects.get(pk=user_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "User does not exist"})

        loading_instance = Loading.objects.create(
            loading_port=port_instance, loading_starting_date=datetime.datetime.now())
        dock_instance = Docks.objects.create(which_dock=dock_number)
        inspection_instance = Inspection.objects.create(
            vessel_breathed=vessel_breath,
            vessel_arrived=vessel_arrive,
            vessel_ref=vessel_instance,
            user_ref=user_instance,
            loading_ref=loading_instance,
            dock=dock_instance,
            inspection_date=inspection_date
        )
        if inspection_instance.pk is not None:
            dock_instance.inspection_id = inspection_instance.pk
            dock_instance.save()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        product_pk = request.data["clientloadingdetails"]["product_id"]
        client_pk = request.data["clientloadingdetails"]["client_id"]
        i = 0
        while i < len(product_pk):
            try:
                product_instance = Product.objects.get(pk=product_pk[i])
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "Product does not exist"})
            try:
                client_instance = Client.objects.get(pk=client_pk[i])
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "Client does not exist"})
            ClientLoadingDetails.objects.create(
                product_ref=product_instance, client_ref=client_instance, loading_ref=loading_instance)
            i += 1
        return Response(status=status.HTTP_201_CREATED, data={"msg": "Requirement were successfully created"})


class HaltView(viewsets.ModelViewSet):
    queryset = Halt.objects.all()
    serializer_class = HaltSerializer
    permission_classes = (AllowAny,)


class HaltEventView(viewsets.ModelViewSet):
    queryset = HaltEvent.objects.all()
    serializer_class = HaltEventCustomSerializer
    permission_classes = (AllowAny,)


class IncidentEventView(viewsets.ModelViewSet):
    queryset = IncidentEvent.objects.all()
    serializer_class = IncidentEventCustomSerializer
    permission_classes = (AllowAny,)


class IncidentDetailsView(viewsets.ModelViewSet):
    queryset = IncidentDetails.objects.all()
    serializer_class = IncidentDetailSerializer
    permission_classes = (AllowAny,)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['inspection_ref__inspection_status',
                        'inspection_ref', 'related']
    ordering_fields = [
        'inspection_ref__inspection_date',
        'stopping_hour',
    ]
    ordering = ['-inspection_ref__inspection_date']

    def list(self, request, *args, **kwargs):
        if 'resuming_hour' in request.GET:
            if request.GET['resuming_hour'] == 'null':
                queryset = self.filter_queryset(
                    self.get_queryset().filter(resuming_hour=None))
            else:
                queryset = self.filter_queryset(self.get_queryset())
        else:
            queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class IncidentSpecView(viewsets.ModelViewSet):
    queryset = IncidentSpecs.objects.all()
    serializer_class = IncidentSpecSerializer
    permission_classes = (AllowAny,)


class UserViewSet(viewsets.ModelViewSet):
    '''
        View Responsible for Viewing All users. Requires Permissions
    '''
    queryset = User.objects.filter(is_staff=False)
    serializer_class = UserSerializer
    http_method_names = ['get', 'patch']
    filter_class = UserFilterSet
    filter_backends = [DjangoFilterBackend]
    # Add this code block

    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [AllowAny]  # [IsLoggedInUserOrAdmin]
        elif self.action == 'list' or self.action == 'destroy':
            permission_classes = [AllowAny]  # [IsAdminUser]
        return [permission() for permission in permission_classes]

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class UserIsRefusedViewSet(generics.UpdateAPIView):
    '''
        View Responsible for confirming a registration of user.
        Admin Only...
        if `is_refuse`d` is false set `is_active` to true else
        leave it as it is.
    '''
    # queryset = User.objects.all()
    # serializer_class = User
    permission_classes = (AllowAny,)

    def patch(self, request, pk):
        user_profile = get_object_or_404(UserProfile, user_id=pk)
        user = get_object_or_404(User, pk=pk)
        serializer = UserRefusedSerializer(
            user_profile, data=request.data, partial=True)
        if request.data['is_refused'] == False:
            user.is_active = True
        else:
            user.delete()
            return JsonResponse(status=status.HTTP_200_OK, data={"msg": "deleted", "id": pk})
        if serializer.is_valid():
            serializer.save()
            user.save()
            return JsonResponse({**serializer.data}, status=status.HTTP_201_CREATED)
        return JsonResponse(status=status.HTTP_400_BAD_REQUEST, data={"msg": "Wrong Param"}, safe=False)


class UserCreateAPIView(generics.CreateAPIView):
    '''
        Viw Responsible for creating a user.
        Permission for any.
    '''
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (AllowAny,)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


# ====================================================


class InspectionStat(generics.ListAPIView):

    queryset = Inspection.objects.all()

    year = datetime.datetime.now().year
    permission_classes = (AllowAny, )

    def add_extra_month(self, object, date_field_by_month):
        months = []
        result = []
        for j in object:
            months.append(j[date_field_by_month])
            result.append(
                {'month': j[date_field_by_month], 'count': j['count']})

        for i in range(1, 13):
            if i not in months:
                result.append({'month': i, 'count': 0})
        return result

    def get_halts(self):
        halts = IncidentDetails.objects.filter(stopping_hour__year=self.year, halt_or_incident='Halt')\
            .values('stopping_hour__month')\
            .annotate(count=Count('pk'))
        return self.add_extra_month(halts, 'stopping_hour__month')

    def get_incident(self):
        incidents = IncidentDetails.objects.filter(stopping_hour__year=self.year, halt_or_incident='Incident')\
            .values('stopping_hour__month')\
            .annotate(count=Count('pk'))

        return self.add_extra_month(incidents, 'stopping_hour__month')

    def list(self, request, *args, **kwargs):
        if request.GET and request.GET['year']:
            self.year = request.GET['year']
        result = []
        inspec = Inspection.objects.filter(inspection_date__year=self.year)\
            .values('inspection_date__month')\
            .annotate(count=Count('pk'))

        result = self.add_extra_month(inspec, 'inspection_date__month')
        return Response(data={'inspections': result, 'incidents': self.get_incident(), 'halts': self.get_halts()})


class PortstatsView(generics.ListAPIView):

    today = datetime.datetime.now()
    permission_classes = (AllowAny, )

    def list(self, request):
        # JSF shall be replaced with query string ?port=some_name
        related = Inspection.objects.select_related('loading_ref', 'dock')\
            .values('loading_ref__loading_port__name', 'dock__id')\
            .annotate(count=Count('dock__id'))

        result = {}
        for inspection in related:
            key = inspection.pop('loading_ref__loading_port__name')
            if key not in result:
                result[key] = []
            result[key].append(inspection)

        return Response(result)
        # loadings = Loading.objects.filter(loading_port=port.id)


class MonthlyQuantityView(generics.ListAPIView):

    today = datetime.datetime.now()
    permission_classes = (AllowAny,)

    def add_extra_month(self, object, date_field_by_month):
        months = []
        result = []
        for j in object:
            months.append(j[date_field_by_month])
            result.append(
                {'month': j[date_field_by_month], 'Quantity': j['Quantity']})

        for i in range(1, 13):
            if i not in months:
                result.append({'month': i, 'Quantity': 0})
        return result

    def list(self, request):
        loads = Loading.objects.filter(loading_starting_date__year=self.today.year)\
            .values("loading_starting_date__month", "loading_port__name")\
            .annotate(Quantity=Sum('Quantity'))

        result = {}
        for inspection in loads:
            key = inspection.pop('loading_port__name')
            if key not in result:
                result[key] = []
            result[key].append(inspection)

        for key, value in result.items():
            result[key] = (self.add_extra_month(
                value, 'loading_starting_date__month'))
        return Response(result)

# Error page handling


@api_view()
def error_page(request):
    return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
