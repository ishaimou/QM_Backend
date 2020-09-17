from rest_framework.parsers import FileUploadParser
from django.views.generic.edit import UpdateView
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import django_filters
import datetime
from django.db.models import Count, Sum
from django.core import serializers
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
import os
from django.http import HttpResponse
from twilio.rest import Client as TwilioClient
from django.db.models import Q
# Models imports
import requests
import csv
from inspection.models import (User, Halt,
                               UserProfile, Departement, Vessel,
                               Loading, Inspection, HourlyCheck, ProductType,
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

from inspection.CustomSerializers.a_serializers import IntermediateDraughtSurveySerializer, ProductTypeSerializer, HaltSerializer, FileSerializer, ProductTreeTypeSerializer, ProductTreeFamilySerializer, ChartIncidentSerializer
from inspection.views import file_create
# Permissions Import
from inspection.permissions import IsLoggedInUserOrAdmin, IsAdminUser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django.core.exceptions import ObjectDoesNotExist

import json
import xlwt
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.http import JsonResponse


class IntermediateDraughtSurveyView(generics.ListAPIView):
    queryset = IntermediateDraughtSurvey.objects.all()
    serializer_class = IntermediateDraughtSurveySerializer
    permission_classes = (AllowAny,)
    filterset_fields = ['loading_ref']

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if (
            'loading_ref' in request.data
            and 'start_inter_draugth_surv' in request.data
            and 'end_inter_draugth_surv' in request.data
        ):
            loading_inst = Loading.objects.get(id=request.data['loading_ref'])
            Survey = IntermediateDraughtSurvey.objects.create(
                loading_ref=loading_inst, start_inter_draugth_surv=request.data['start_inter_draugth_surv'], end_inter_draugth_surv=request.data['end_inter_draugth_surv'])
            survey_ref = Survey.id
            try:
                inspection_ref = Inspection.objects.get(
                    loading_ref=loading_inst).id
            except:
                print("taG")
        data = request.data.copy()
        data.update({"survey_ref": str(survey_ref)})
        data.update({"inspection_ref": str(inspection_ref)})
        if request.FILES:
            files = request.FILES.copy()
            file_create(data, files)
        return Response(data={"Survey Created"}, status=status.HTTP_201_CREATED)


class CLientLinkView(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            loading_instance = Loading.objects.get(
                id=request.data['loading_id'])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "Loading Choosen Does not exist"})
        try:
            client_instance = Client.objects.get(id=request.data['client_id'])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "Client Choosen Does not exist"})
        if ClientLoadingDetails.objects.filter(loading_ref=loading_instance.id, client_ref=client_instance.id).count() == 0:
            ClientLoadingDetails.objects.create(
                loading_ref=loading_instance, client_ref=client_instance)
            inspection_ref = Inspection.objects.get(
                loading_ref=loading_instance.id).id
            data = request.data.copy()
            data.update({"inspection_ref": str(inspection_ref)})
            if request.FILES:
                files = request.FILES.copy()
                file_create(data, files)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "ClientLoadingDetails Table already exists"})
        return Response(status=status.HTTP_201_CREATED, data={"msg": "Client Created Successfully"})


class ProductCreateView(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        origin_checker = False
        try:
            loading_instance = Loading.objects.get(
                id=int(request.data['loading_id']))
            if 'origin' in request.data and str(request.data['origin']).isdigit():
                origin_instance = Origin.objects.get(id=request.data['origin'])
                origin_checker = True
            if 'quantity' not in request.data:
                quantity = 0
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "Loading Choosen Does not exist"})
        product_instance = Product.objects.get(id=request.data['Name'])
        if ClientLoadingDetails.objects.filter(loading_ref=request.data['loading_id'], product_ref=product_instance.id).count() == 0:
            if origin_checker:
                ClientLoadingDetails.objects.create(
                    loading_ref=loading_instance, product_ref=product_instance, origin_ref=origin_instance, quantity=quantity)
            else:
                ClientLoadingDetails.objects.create(
                    loading_ref=loading_instance, product_ref=product_instance, quantity=quantity)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "Product Already Exists"})
        data = request.data.copy()
        inspection_inst = Inspection.objects.get(
            loading_ref=loading_instance)
        data.update({"product_ref": str(product_instance.id)})
        data.update({"inspection_ref": str(inspection_inst.id)})
        if request.FILES:
            files = request.FILES.copy()
            file_create(data, files)
        # else:
        #     return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "ClientLoadingDetails Table already created"})
        return Response(status=status.HTTP_201_CREATED, data={"msg": "Product Created Successfully"})


class EditProductView(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    def patch(self, request):
        try:
            loading_instance = Loading.objects.get(
                id=request.data['loading_id'])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "Loading Choosen Does not exist"})
        try:
            product_instance = Product.objects.get(
                id=request.data['product_id'])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "Category Choosen Does not Exist"})
        try:
            instance = ClientLoadingDetails.objects.get(
                loading_ref=loading_instance, product_ref=product_instance)
            if "origin_id" in request.data and str(request.data['origin_id']).isdigit():
                origin_instance = Origin.objects.get(
                    id=request.data['origin_id'])
                instance.origin_ref = origin_instance
                instance.save()
                return Response(status=status.HTTP_201_CREATED, data={"msg": "Product Updated Successfully"})
            if "product_status" in request.data:
                if request.data["product_status"] == "LOADED":
                    instance.loaded = True
                    if 'qte' in request.data:
                        instance.quantity = request.data['qte']
                elif request.data["product_status"] == "NOTLOADED":
                    instance.loaded = False
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "Wrong Status"})
                instance.save()
                return Response(status=status.HTTP_201_CREATED, data={"msg": "Product Status Updated Successfully"})
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "Table Choosen Does not exist"})


class ProductTypeView(viewsets.ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    permission_classes = (AllowAny,)


class IncidentTestView(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    def send_sms(self, vessel, dock, incident_type, incident_details=None):
        account_sid = 'ACa49d66d3b30c863b679c3b9dbc67f0a8'
        auth_token = '68171d5f729f23cfe260efe5d118d36a'
        client = TwilioClient(account_sid, auth_token)
        if incident_details is None:
            body = "\nStopping ==>\n" + "\nIncident: " + \
                str(incident_type) + "\nVessel: " + \
                str(vessel) + "\nDock: " + str(dock)
        else:
            body = "\nResumed ==>\n" + "Incident: " + str(incident_type) + "\nVessel: " + str(vessel) + "\nDock: " + str(
                dock) + "\nStarted: " + str(incident_details.stopping_hour)[:19] + "\nEnded: " + str(incident_details.resuming_hour)[:19]
        message = client.messages \
                        .create(
                            body=body,
                            from_='+15108783634',
                            to='+212620012669'
                            # to='+212666304577'
                        )

        print(message.sid)

    def post(self, request, *args, **kwargs):
        try:
            inspection_instance = Inspection.objects.get(
                id=request.data['inspection_ref'])
            halt_or_incident = request.data['halt_or_incident']
            stopping_hour = request.data['stopping_hour']
            description = request.data['description'] if "description" in request.data else ""

            if request.data['halt_or_incident'] == 'Halt':
                halt_event_instance = HaltEvent.objects.get(
                    id=request.data['halt_ref'])
                halt_instance = Halt.objects.create(
                    halt_event_ref=halt_event_instance)
                h = str(halt_instance)
                if h.find("Pluie") != -1 or h.find("Mauvais temps") != -1:
                    related = "WEATHER"
                else:
                    related = "HALT"
                inc = IncidentDetails.objects.filter(
                    inspection_ref=inspection_instance,
                    halt_or_incident=halt_or_incident,
                    halt_ref=halt_instance,
                    stopping_hour=stopping_hour,
                    description=description,
                    related=related
                )
                if inc.count() != 0:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "Table Exists"})
                else:
                    incidentdetails_inst = IncidentDetails.objects.create(inspection_ref=inspection_instance, halt_or_incident=halt_or_incident,
                                                                          halt_ref=halt_instance, stopping_hour=stopping_hour, description=description, related=related)
            elif request.data['halt_or_incident'] == 'Incident':
                related = "PRODUCT"
                incident_event_instance = IncidentEvent.objects.get(
                    id=request.data['incident_spec_ref'])
                incident_spec_instance = IncidentSpecs.objects.create(
                    incident_event_ref=incident_event_instance)
                if IncidentDetails.objects.filter(inspection_ref=inspection_instance, halt_or_incident=halt_or_incident,
                                                  incident_spec_ref=incident_spec_instance, stopping_hour=stopping_hour, description=description, related=related).count() != 0:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "Table Exists"})
                else:
                    incidentdetails_inst = IncidentDetails.objects.create(inspection_ref=inspection_instance, halt_or_incident=halt_or_incident,
                                                                          incident_spec_ref=incident_spec_instance, stopping_hour=stopping_hour, description=description, related=related)
            incident_ref = incidentdetails_inst.id
            data = request.data.copy()
            data.update({"incident_ref": str(incident_ref)})
            if request.FILES:
                files = request.FILES.copy()
                file_create(data, files)
            Inspection.objects.filter(id=request.data['inspection_ref']).update(
                inspection_status="ONHOLD")
            try:
                if request.data['halt_or_incident'] == 'Incident':
                    self.send_sms(inspection_instance.vessel_ref.name, inspection_instance.dock.which_dock,
                                  incidentdetails_inst.incident_spec_ref.incident_event_ref.name)
                elif request.data['halt_or_incident'] == 'Halt':
                    self.send_sms(inspection_instance.vessel_ref.name, inspection_instance.dock.which_dock,
                                  incidentdetails_inst.halt_ref.halt_event_ref.name)
            except:
                pass
        except:
            if incidentdetails_inst:
                incidentdetails_inst.delete()
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "Something went wrong"})
        return Response(status=status.HTTP_201_CREATED, data={"msg": "All went well"})

    def patch(self, request):
        try:
            Incident_instance = IncidentDetails.objects.get(
                id=request.data['id'])
            qte_by_kgs = 0 if "qte_by_kgs" not in request.data or request.data[
                'qte_by_kgs'] == 'undefined' else request.data['qte_by_kgs']
            temperature = "" if "temperature" not in request.data or request.data[
                'temperature'] == 'undefined' else request.data['temperature']
            possible_cause = "" if "possible_cause" not in request.data or request.data[
                'possible_cause'] == 'undefined' else request.data['possible_cause']
            humidity_rate = "" if "humidity_rate" not in request.data or request.data[
                'humidity_rate'] == 'undefined' else request.data['humidity_rate']
            description = "" if "description" not in request.data or request.data[
                'description'] == 'undefined' else request.data['description']
            IncidentDetails.objects.filter(id=request.data['id']).update(
                resuming_hour=request.data['resuming_hour'], description=description)
            if Incident_instance.halt_or_incident == 'Halt':
                try:
                    Halt.objects.filter(id=Incident_instance.halt_ref.id).update(
                        possible_cause=possible_cause)
                except:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "Conflict between halt and incident insersion"})
            else:
                try:
                    IncidentSpecs.objects.filter(id=Incident_instance.incident_spec_ref.id).update(
                        qte_by_kgs=qte_by_kgs, temperature=temperature,
                        possible_cause=possible_cause, humidity_rate=humidity_rate)
                except:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "Conflict between incident and halt insersion"})
            Incident_instance.resuming_hour = request.data['resuming_hour']
            Incident_instance.save()
            if len(description) != 0 and len(Incident_instance.description) != 0:
                Incident_instance.description = Incident_instance.description + '_' + description
                Incident_instance.save()
            elif len(Incident_instance.description) == 0:
                Incident_instance.description = description
                Incident_instance.save()
            incident_ref = Incident_instance.id
            data = request.data.copy()
            data.update({"incident_ref": str(data['id'])})
            if request.FILES:
                files = request.FILES.copy()
                file_create(data, files)
            Inspection.objects.filter(id=request.data['inspection_ref']).update(
                inspection_status="INPROGRESS")
            inspection_instance = Inspection.objects.get(
                id=request.data['inspection_ref'])
            try:
                if Incident_instance.halt_or_incident == 'Halt':
                    self.send_sms(inspection_instance.vessel_ref.name, inspection_instance.dock.which_dock,
                                  Incident_instance.halt_ref.halt_event_ref.name, incident_details=Incident_instance)
                else:
                    self.send_sms(inspection_instance.vessel_ref.name, inspection_instance.dock.which_dock,
                                  Incident_instance.incident_spec_ref.incident_event_ref.name, incident_details=Incident_instance)
            except:
                pass
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "Something went wrong"})
        return Response(status=status.HTTP_201_CREATED, data={"msg": "All went well"})


class FileView(viewsets.ModelViewSet):
    queryset = Files.objects.all()
    serializer_class = FileSerializer
    parser_class = (FileUploadParser,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['inspection_ref']
    permission_classes = (AllowAny,)

    def handle_upload_file(self, f, path):
        with open(path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    def perform_create(self, serializer, path):
        serializer.save(file=path)

    def make_path(self, request):
        inspection_pk = "" if "inspection_ref" not in request.data else request.data[
            'inspection_ref']
        if os.path.exists('./uploads/') == False:
            os.mkdir('./uploads/')
        inspection_path = './uploads/' + str(inspection_pk)
        if os.path.exists(inspection_path) == False:
            os.mkdir(inspection_path)
        mini_path = inspection_path + '/'
        time = str(datetime.datetime.now()).translate(
            {ord(i): None for i in '-: '})[:14] + '_'
        path = mini_path + time + str(request.data['file'])
        return path

    def create(self, request, *args, **kwargs):
        if "file" in request.data:
            path = self.make_path(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.handle_upload_file(request.data['file'], path)
        self.perform_create(serializer, path[10:])
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ProductCustomizedView(generics.ListAPIView):
    queryset = Product.objects.all()
    permission_classes = (AllowAny,)

    def get_product(self, product):
        data = []
        for prod in product:
            tempo = {
                'value': prod.id,
                'label': prod.name,
            }
            data.append(tempo)
        return data

    def get_product_category(self, productcategory):
        data = []
        for prod_category in productcategory:
            product = Product.objects.filter(
                product_category_ref=prod_category.id)
            nano_data = self.get_product(product)
            tempo = {
                'value': prod_category.id,
                'label': prod_category.name,
                'children': nano_data
            }
            data.append(tempo)
        return data

    def get_product_family(self, productfamily):
        data = []
        for prod_family in productfamily:
            productcategory = ProductCategory.objects.filter(
                product_family_ref=prod_family.id)
            macro_data = self.get_product_category(productcategory)
            tempo = {
                'value': prod_family.id,
                'label': prod_family.name,
                'children': macro_data
            }
            data.append(tempo)
        return data

    def list(self, request):
        data = []
        productype = ProductType.objects.all()
        for prod_type in productype:
            productfamily = ProductFamily.objects.filter(
                product_type_ref=prod_type.id)
            mini_data = self.get_product_family(productfamily)
            tempo = {
                'value': prod_type.id,
                'label': prod_type.name,
                'children': mini_data
            }
            data.append(tempo)
        return Response(data=data)


class ChartPieIncidentView(generics.ListAPIView):
    permission_classes = (AllowAny,)

    def get_calc_halt(self, queryset_halt):
        sum_halt = datetime.timedelta(0, 0, 0)
        halt_dic = {}
        for q_h in queryset_halt:
            sum_halt += q_h['resuming_hour'] - q_h['stopping_hour']
        halt_dic.update({"total_seconds": sum_halt})
        halt_obj = {}
        halt_count = HaltEvent.objects.all().count()
        i = 0
        while i < halt_count:
            halt_ref = Halt.objects.filter(halt_event_ref=i)
            sum_halt_in = datetime.timedelta(0, 0, 0)
            for h in halt_ref:
                queryset_halt_event = queryset_halt.filter(halt_ref=h)
                sum_halt_indepth = datetime.timedelta(0, 0, 0)
                for x in queryset_halt_event:
                    sum_halt_in += x['resuming_hour'] - x['stopping_hour']
                sum_halt_indepth += sum_halt_in
                if sum_halt_indepth != datetime.timedelta(0, 0, 0):
                    halt_obj.update(
                        {str(HaltEvent.objects.get(id=i)): sum_halt_indepth})
            i += 1
        halt_dic.update(halt_obj)
        return halt_dic

    def get_calc_incident(self, queryset_incident):
        sum_incident = datetime.timedelta(0, 0, 0)
        incident_dic = {}
        for q_i in queryset_incident:
            sum_incident += q_i['resuming_hour'] - q_i['stopping_hour']
        incident_dic.update({"total_seconds": sum_incident})
        incident_obj = {}
        incident_count = IncidentEvent.objects.all().count()
        i = 0
        while i < incident_count:
            incident_spec = IncidentSpecs.objects.filter(incident_event_ref=i)
            sum_inc_in = datetime.timedelta(0, 0, 0)
            for inc in incident_spec:
                queryset_incident_ref = queryset_incident.filter(
                    incident_spec_ref=inc)
                sum_inc_indepth = datetime.timedelta(0, 0, 0)
                for x in queryset_incident_ref:
                    sum_inc_in = x['resuming_hour'] - x['stopping_hour']
                sum_inc_indepth += sum_inc_in
                if sum_inc_indepth != datetime.timedelta(0, 0, 0):
                    incident_obj.update(
                        {str(IncidentEvent.objects.get(id=i)): sum_inc_indepth})
            i += 1
        incident_dic.update(incident_obj)
        return incident_dic

    def query_filter_master(self, definer, start_date=None, end_date=None):
        if definer:
            queryset_halt = IncidentDetails.objects.filter(stopping_hour__range=(start_date, end_date),
                                                           related="HALT").exclude(resuming_hour=None).values('stopping_hour', 'resuming_hour')
            queryset_incident = IncidentDetails.objects.filter(stopping_hour__range=(start_date, end_date),
                                                               related="PRODUCT").exclude(resuming_hour=None).values('stopping_hour', 'resuming_hour')
            queryset_weather = IncidentDetails.objects.filter(stopping_hour__range=(start_date, end_date),
                                                              related="WEATHER").exclude(resuming_hour=None).values('stopping_hour', 'resuming_hour')
        else:
            queryset_halt = IncidentDetails.objects.filter(
                related="HALT").exclude(resuming_hour=None).values('stopping_hour', 'resuming_hour')
            queryset_incident = IncidentDetails.objects.filter(
                related="PRODUCT").exclude(resuming_hour=None).values('stopping_hour', 'resuming_hour')
            queryset_weather = IncidentDetails.objects.filter(
                related="WEATHER").exclude(resuming_hour=None).values('stopping_hour', 'resuming_hour')
        return queryset_halt, queryset_incident, queryset_weather

    def get(self, request):
        definer = False
        if "start_date" in request.GET:
            start_date = request.GET['start_date']
            end_date = request.GET['end_date']
            definer = True
        if definer:
            queryset = IncidentDetails.objects.filter(stopping_hour__range=(
                start_date, end_date)).values('stopping_hour', 'resuming_hour')
        else:
            queryset = IncidentDetails.objects.all().values('stopping_hour', 'resuming_hour')
        data = {}
        if definer:
            queryset_halt, queryset_incident, queryset_weather = self.query_filter_master(
                definer, start_date, end_date)
        else:
            queryset_halt, queryset_incident, queryset_weather = self.query_filter_master(
                definer)
        drill = {}
        sum_weather = datetime.timedelta(0, 0, 0)
        for q_w in queryset_weather:
            sum_weather += q_w['resuming_hour'] - q_w['stopping_hour']
        halt_dic = self.get_calc_halt(queryset_halt)
        incident_dic = self.get_calc_incident(queryset_incident)
        weather_dic = self.get_calc_halt(queryset_weather)
        data.update({"halt": halt_dic})
        data.update({"incident": incident_dic})
        data.update({"weather": weather_dic})
        return Response(data=data)


class AllTimeChartView(generics.ListAPIView):
    permission_classes = (AllowAny,)

    def get_query_custom(self, related):
        data = {}
        if related == "PRODUCT":
            product = IncidentDetails.objects.filter(
                related=related).exclude(resuming_hour=None)
            for prod in product:
                incident = IncidentSpecs.objects.filter(
                    id=prod.incident_spec_ref.id)
                for inci in incident:
                    name = IncidentEvent.objects.get(
                        id=inci.incident_event_ref.id).name
                    if not data.get(name, None):
                        data[name] = []
                    data[name].append({
                        "date": prod.resuming_hour,
                        "duration": prod.resuming_hour - prod.stopping_hour
                    })
            return data
        else:
            halt = IncidentDetails.objects.filter(
                related=related).exclude(resuming_hour=None)
            for hal in halt:
                halty = Halt.objects.filter(id=hal.halt_ref.id)
                for h in halty:
                    name = HaltEvent.objects.get(id=h.halt_event_ref.id).name
                    if not data.get(name, None):
                        data[name] = []
                    data[name].append({
                        "date": hal.resuming_hour,
                        "duration": hal.resuming_hour - hal.stopping_hour
                    })
        return data

    def get(self, request):
        data = {}
        halt_data = self.get_query_custom("HALT")
        incident_data = self.get_query_custom("PRODUCT")
        weather_data = self.get_query_custom("WEATHER")
        data.update({"halt": halt_data})
        data.update({"incident": incident_data})
        data.update({"weather": weather_data})
        return Response(data=data)


# def export_users_xls(request):
#     print(request.GET['pk'])
#     response = HttpResponse(content_type='application/ms-excel')
#     response['Content-Disposition'] = 'attachment; filename="users.xls"'

#     wb = xlwt.Workbook(encoding='utf-8')
#     ws = wb.add_sheet('Users')

#     # Sheet header, first row
#     row_num = 0

#     font_style = xlwt.XFStyle()
#     font_style.font.bold = True

#     columns = ['Inspection', 'First name', 'Last name', 'Email address', ]

#     for col_num in range(len(columns)):
#         ws.write(row_num, col_num, columns[col_num], font_style)

#     # Sheet body, remaining rows
#     font_style = xlwt.XFStyle()

#     rows = User.objects.all().values_list(
#         'username', 'first_name', 'last_name', 'email')
#     for row in rows:
#         row_num += 1
#         for col_num in range(len(row)):
#             ws.write(row_num, col_num, row[col_num], font_style)

#     wb.save(response)
#     return response
