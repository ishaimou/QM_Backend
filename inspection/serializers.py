from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from inspection.models import (User, UserProfile, Departement, Docks,
                               Vessel, Loading, Inspection,
                               HourlyCheck, ProductCategory, ProductType,
                               ProductFamily, Product, Origin,
                               Client, ClientLoadingDetails,
                               Halt, HaltEvent, IncidentEvent,
                               IncidentSpecs, IncidentDetails, Port)

import json
from .CustomSerializers.a_serializers import ProductCustomSerializer


class UserSecSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name',)


class UserProfileSerializer(serializers.ModelSerializer):
    '''
        View Completer of the User Serializer, As the UserProfile is a one-to-one link with User
    '''
    # photo_url = serializers.SerializerMethodField('get_photo_url')

    class Meta:
        model = UserProfile
        fields = ('photo', 'cin', 'tel', 'is_refused', 'company_name')

    # def get_photo_url(self, obj):
    #     if obj.photo and hasattr(obj.photo, 'url'):
    #         return obj.photo.url
    #     else:
    #         return None


class UserRefusedSerializer(serializers.ModelSerializer):
    '''
        Serializer for confimating registartion of a user
    '''

    class Meta:
        model = UserProfile
        fields = ('is_refused', )


class UserIsActive(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('is_active', )


class UserCreateSerializer(serializers.ModelSerializer):
    '''
        Create user serializer, the serializer responsible for creating a user
    '''
    profile = UserProfileSerializer(required=True)

    class Meta:
        model = User
        fields = ('url', 'email', 'first_name',
                  'last_name', 'password', 'profile')
        extra_kwargs = {'password': {'write_only': True}}

    def get_photo(self, user):
        request = self.context.get('request')
        photo = user.photo.url
        return request.build_absolute_uri(photo)

    def create(self, validate_data):
        profile_data = validate_data.pop('profile')
        password = validate_data.pop('password')
        user = User(**validate_data)
        user.set_password(password)
        user.is_active = False
        profile_data['is_refused'] = True
        user.save()
        UserProfile.objects.create(user=user, **profile_data)
        return user


class UserSerializer(serializers.HyperlinkedModelSerializer):
    '''
        Serializer for users, linked to UserProfile , so fetching UserProfileSerializer is necessary to get all the necessary informations about users
        The Commented def update is yet to be reviewed for it's uses and what it's there
    '''
    profile = UserProfileSerializer(required=True)

    class Meta:
        model = User
        fields = ('id', 'url', 'email', 'first_name', 'last_name', 'is_active', 'is_staff',
                  'last_name', 'password', 'profile')
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, instance, validate_data):
        profile_data = validate_data.pop('profile')
        profile = instance.profile

        instance.email = validate_data.get('email', instance.email)
        instance.save()
        profile.cin = profile_data.get('cin', profile.cin)
        profile.department = profile_data.get('department', profile.department)
        profile.company_name = profile_data.get(
            'company_name', profile.company_name)
        profile.is_refused = profile_data.get('is_refused', profile.is_refused)
        profile.tel = profile_data.get('tel', profile.tel)
        profile.photo = profile_data.get('photo', profile.photo)


class DepartementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departement
        fields = '__all__'


class LoadingFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loading
        fields = '__all__'


class LoadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loading
        fields = ('Quantity', 'loading_port')


class InspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspection
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class VesselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vessel
        fields = ('id', 'name', 'holds_nbr')

# INSPECTION TEST RELATED VIEWS


class UserProfileCustomSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('get_user')

    def get_user(self, userprofile):
        queryset = User.objects.get(id=userprofile.user.id)
        serializer = UserSecSerializer(queryset, many=False)
        return serializer.data

    class Meta:
        model = UserProfile
        fields = ('user', 'company_name')


class DockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Docks
        fields = ('id', 'which_dock')


class VesselCustomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vessel
        fields = ('name', 'holds_nbr')


class PortCustomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Port
        fields = ('name', 'docks')


class ClientCustomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('name', 'destination')


class ClientLoadingDetailSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField('get_client')
    product = serializers.SerializerMethodField('get_product')
    origin = serializers.SerializerMethodField('get_origin')
    # product_status = serializers.BooleanField(source='loaded')
    product_quantity = serializers.CharField(source='quantity')

    def get_client(self, clientl):
        if clientl.client_ref is not None:
            queryset = Client.objects.get(id=clientl.client_ref.id)
            serializer = ClientCustomSerializer(queryset, many=False)
            return serializer.data
        else:
            return None

    def get_product(self, clientl):
        if clientl.product_ref is not None:
            queryset = Product.objects.get(id=clientl.product_ref.id)
            serializer = ProductCustomSerializer(queryset, many=False)
            return serializer.data
        else:
            return None

    def get_origin(self, clientl):
        if clientl.origin_ref is not None:
            queryset = Origin.objects.get(id=clientl.origin_ref.id)
            serializer = OriginSerializer(queryset, many=False)
            return serializer.data
        else:
            return None

    class Meta:
        model = ClientLoadingDetails
        fields = ('loaded', 'client', 'product',
                  'origin', 'product_quantity')


class LoadingCustomSerializer(serializers.ModelSerializer):
    port = serializers.SerializerMethodField('get_port')

    def get_port(self, loading):
        queryset = Port.objects.get(id=loading.loading_port.id)
        serializer = PortCustomSerializer(queryset, many=False)
        return serializer.data

    class Meta:
        model = Loading
        fields = '__all__'

# INSPECTION TEST RELATED VIEWS


class InspectionTestSerializer(serializers.ModelSerializer):
    vessel = serializers.SerializerMethodField('get_vessel')
    port = serializers.SerializerMethodField('get_loading')
    user = serializers.SerializerMethodField('get_user')
    docks = serializers.SerializerMethodField('get_dock')
    clients = serializers.SerializerMethodField('get_client')

    def get_vessel(self, inspection):
        queryset = Vessel.objects.get(id=inspection.vessel_ref.id)
        serializer = VesselCustomSerializer(queryset, many=False)
        return serializer.data

    def get_loading(self, inspection):
        queryset = Loading.objects.get(id=inspection.loading_ref.id)
        serializer = LoadingCustomSerializer(queryset, many=False)
        return serializer.data

    def get_user(self, inspection):
        queryset = UserProfile.objects.get(user=inspection.user_ref.id)
        serializer = UserProfileCustomSerializer(queryset, many=False)
        return serializer.data

    def get_dock(self, inspection):
        queryset = Docks.objects.get(id=inspection.dock.id)
        serializer = DockSerializer(queryset, many=False)
        return serializer.data

    def get_client(self, inspection):
        queryset = ClientLoadingDetails.objects.filter(
            loading_ref=inspection.loading_ref.id)
        serializer = ClientLoadingDetailSerializer(queryset, many=True)
        return serializer.data

    class Meta:
        model = Inspection
        fields = ('id', 'inspection_status', 'vessel_status', 'vessel_arrived', 'vessel_breathed', 'vessel',
                  'port', 'user', 'clients', 'inspection_date', 'inspection_date_end', 'foreign_inspector', 'holds_filled', 'docks')


class HourlyCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = HourlyCheck
        fields = '__all__'


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = '__all__'


class ProductFamilySerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField('get_type')

    class Meta:
        model = ProductFamily
        fields = ('id', 'name', 'product_type_ref', 'type')

    def get_type(self, family):
        queryset = ProductType.objects.get(id=family.product_type_ref.id)
        serializer = ProductTypeSerializer(queryset)
        return serializer.data['name']


class ProductCategorySerializer(serializers.ModelSerializer):
    family = serializers.SerializerMethodField('get_family')

    class Meta:
        model = ProductCategory
        fields = ('id', 'name', 'product_family_ref', 'family')

    def get_family(self, category):
        queryset = ProductFamily.objects.get(id=category.product_family_ref.id)
        serializer = ProductFamilySerializer(queryset)
        return serializer.data['name']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class OriginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Origin
        fields = '__all__'


class PortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Port
        fields = '__all__'

# Custom Serializers for Incident Table


class HaltCustomSerializer(serializers.ModelSerializer):
    halt_event = serializers.SerializerMethodField('get_event')

    def get_event(self, halt):
        queryset = HaltEvent.objects.get(id=halt.halt_event_ref.id)
        serializer = HaltEventCustomSerializer(queryset, many=False)
        return serializer.data['name']

    class Meta:
        model = Halt
        fields = ('halt_event', 'possible_cause')


class HaltEventCustomSerializer(serializers.ModelSerializer):
    class Meta:
        model = HaltEvent
        fields = '__all__'


class UserProfileCustomizedSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('get_user')

    def get_user(self, userprofile):
        queryset = User.objects.get(id=userprofile.user.id)
        serializer = UserSecSerializer(queryset, many=False)
        return serializer.data

    class Meta:
        model = UserProfile
        fields = ('id', 'user')


class PortCustomizedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Port
        fields = ('name',)


class LoadingCustomizedSerializer(serializers.ModelSerializer):
    port = serializers.SerializerMethodField('get_port')

    def get_port(self, loading):
        queryset = Port.objects.get(id=loading.loading_port.id)
        serializer = PortCustomizedSerializer(queryset, many=False)
        return serializer.data

    class Meta:
        model = Loading
        fields = ('port',)


class InspectionIncidentSerializer(serializers.ModelSerializer):
    vessel = serializers.SerializerMethodField('get_vessel')
    port = serializers.SerializerMethodField('get_loading')
    user = serializers.SerializerMethodField('get_user')
    docks = serializers.SerializerMethodField('get_dock')

    def get_vessel(self, inspection):
        queryset = Vessel.objects.get(id=inspection.vessel_ref.id)
        serializer = VesselCustomSerializer(queryset, many=False)
        return serializer.data['name']

    def get_loading(self, inspection):
        queryset = Loading.objects.get(id=inspection.loading_ref.id)
        serializer = LoadingCustomizedSerializer(queryset, many=False)
        return serializer.data['port']

    def get_user(self, inspection):
        queryset = UserProfile.objects.get(user=inspection.user_ref.id)
        serializer = UserProfileCustomizedSerializer(queryset, many=False)
        return serializer.data

    def get_dock(self, inspection):
        queryset = Docks.objects.get(id=inspection.dock.id)
        serializer = DockSerializer(queryset, many=False)
        return serializer.data["which_dock"]

    class Meta:
        model = Inspection
        fields = ('inspection_status', 'vessel',
                  'port', 'user', 'inspection_date', 'docks')


# Custom Serializers for Incident Table

class IncidentDetailSerializer(serializers.ModelSerializer):
    inspection = serializers.SerializerMethodField('get_inspection')
    halt = serializers.SerializerMethodField('get_halt')
    incident = serializers.SerializerMethodField('get_incident')

    def get_inspection(self, insident):
        queryset = Inspection.objects.get(id=insident.inspection_ref.id)
        serializer = InspectionIncidentSerializer(queryset, many=False)
        return serializer.data

    def get_halt(self, insident):
        try:
            queryset = Halt.objects.get(id=insident.halt_ref.id)
            serializer = HaltCustomSerializer(queryset, many=False)
            return serializer.data
        except:
            return None

    def get_incident(self, insident):
        try:
            queryset = IncidentSpecs.objects.get(
                id=insident.incident_spec_ref.id)
            serializer = IncidentSpecCustomSerializer(queryset, many=False)
            return serializer.data
        except:
            return None

    class Meta:
        model = IncidentDetails
        fields = ('id',
                  'inspection',
                  'inspection_ref',
                  'related',
                  'halt_ref',
                  'halt',
                  'incident_spec_ref',
                  'incident',
                  'halt_or_incident',
                  'stopping_hour',
                  'resuming_hour'
                  )


class IncidentSpecCustomSerializer(serializers.ModelSerializer):
    incident_event = serializers.SerializerMethodField('get_event')

    def get_event(self, incidentspec):
        queryset = IncidentEvent.objects.get(
            id=incidentspec.incident_event_ref.id)
        serializer = IncidentEventCustomSerializer(queryset, many=False)
        return serializer.data['name']

    class Meta:
        model = IncidentSpecs
        fields = ('incident_event', 'possible_cause')


class IncidentEventCustomSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentEvent
        fields = '__all__'


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        isProfileExists = UserProfile.objects.filter(user_id=user.id).exists()

        # Add custom claims
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name

        if isProfileExists:
            userProfile = UserProfile.objects.get(user_id=user.id)
            if userProfile.photo and hasattr(userProfile.photo, 'url'):
                token['photo'] = userProfile.photo.url
            else:
                token['photo'] = None
        else:
            token['photo'] = None
        # ...

        return token
