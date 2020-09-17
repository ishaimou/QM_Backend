from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from django.conf import settings
from .choices import Cargo_State, H_L, Inspection_Choices, Incident_Choices
# Create your models here.


class User(AbstractUser):
    '''
        main user Table/Class
    '''
    username = models.CharField(blank=True, null=True, max_length=50)
    email = models.EmailField(_('email address'), unique=True, max_length=50)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Departement(models.Model):
    '''
        Departement in which each user belongs, to be further Discussed and reviewed and well used
    '''
    name = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    '''
        This one is linked to the User Class/Table with a one-to-one link in order to add fields necessary in our project,
    '''
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE, related_name='profile')
    is_refused = models.BooleanField(_('User refused'), default=True)
    department = models.ManyToManyField(Departement)
    company_name = models.CharField(max_length=150)
    photo = models.ImageField(upload_to='images/', blank=True, null=True)
    cin = models.CharField(blank=True, null=True, max_length=8)
    tel = models.CharField(blank=True, null=True, max_length=24)


class Vessel(models.Model):
    name = models.CharField(max_length=50)
    photo = models.FileField(
        upload_to="vessel/", max_length=255, null=True, blank=True)
    holds_nbr = models.IntegerField(
        _("number of holds in this vessel"), null=True, blank=True)

    def __str__(self):
        return self.name


class Port(models.Model):
    name = models.CharField('Port name', max_length=50)
    docks = models.IntegerField('Number of docks')

    def __str__(self):
        return self.name


class Loading(models.Model):
    loading_port = models.ForeignKey(
        Port, on_delete=models.CASCADE, related_name='port_name')
    nor_tendered_date = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True)
    loading_order_date = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True)
    loading_starting_date = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True)
    loading_end_date = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True)
    cargo_condition = models.CharField(
        choices=Cargo_State, max_length=50, null=True, blank=True)
    air_temperature = models.CharField(max_length=50, null=True, blank=True)
    humidity_percentage = models.CharField(
        max_length=50, null=True, blank=True)
    uld_test_date = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True)
    initial_draugth_surv = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True)
    final_draugth_surv = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True)
    Quantity = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return "Load." + str(self.id) + '.' + self.loading_port.name


class IntermediateDraughtSurvey(models.Model):
    loading_ref = models.ForeignKey(Loading, on_delete=models.CASCADE)
    start_inter_draugth_surv = models.DateTimeField(
        auto_now=False, auto_now_add=False)
    end_inter_draugth_surv = models.DateTimeField(
        auto_now=False, auto_now_add=False)


class Docks(models.Model):
    inspection_id = models.IntegerField('Inspection ID', null=True, blank=True)
    which_dock = models.PositiveIntegerField()

    def __str__(self):
        return str(self.which_dock)


class Inspection(models.Model):
    inspection_status = models.CharField(
        default="INPROGRESS", max_length=50, choices=Inspection_Choices)
    vessel_status = models.CharField(max_length=50, blank=True, null=True)
    vessel_arrived = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True)
    vessel_breathed = models.DateTimeField(auto_now=False, auto_now_add=False)
    vessel_ref = models.ForeignKey(Vessel, on_delete=models.CASCADE)
    # I guess this should be unique
    # It has to be addressed
    loading_ref = models.OneToOneField(Loading, on_delete=models.CASCADE)
    # to check maybe you'll need to use user_profile
    user_ref = models.ForeignKey(User, on_delete=models.CASCADE)
    inspection_date = models.DateTimeField(null=True, blank=True)
    inspection_date_end = models.DateTimeField(null=True, blank=True)
    foreign_inspector = models.BooleanField(default=False)
    holds_filled = models.IntegerField(null=True)
    dock = models.ForeignKey(Docks, on_delete=models.CASCADE)

    def __str__(self):
        return "Ins" + '.' + str(self.inspection_date)[2:4] + '/' + \
            str(self.inspection_date)[5:7] + '/' + \
            str(self.inspection_date)[8:10] + '_' + str(self.id)


class Origin(models.Model):
    name = models.CharField(max_length=50, null=False,
                            blank=False, unique=True)

    def __str__(self):
        return self.name


class HourlyCheck(models.Model):
    temperature = models.DecimalField(max_digits=4, decimal_places=2)
    humidity = models.DecimalField(max_digits=5, decimal_places=2)
    debit = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True)
    ambient_temperature = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True)
    date = models.DateTimeField(auto_now=False, auto_now_add=False)
    inspection_ref = models.ForeignKey(Inspection, on_delete=models.CASCADE)
    origin = models.ForeignKey(Origin, on_delete=models.CASCADE)


class ProductType(models.Model):
    name = models.CharField(max_length=50, blank=False,
                            null=False, unique=True)

    def __str__(self):
        return self.name


class ProductFamily(models.Model):
    name = models.CharField(max_length=50,
                            blank=False, null=False, unique=True)
    product_type_ref = models.ForeignKey(ProductType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    name = models.CharField(
        max_length=50, blank=False, null=False, unique=True)
    product_family_ref = models.ForeignKey(
        ProductFamily, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=50,
                            blank=False, null=False, unique=True)
    product_category_ref = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Client(models.Model):
    destination = models.CharField(
        max_length=50, blank=False, null=False)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ClientLoadingDetails(models.Model):
    bl_figure_mt = models.IntegerField(null=True, blank=True)
    bl_figure_mt_photo = models.FileField(
        upload_to="bl/", max_length=100, null=True, blank=True)
    loaded = models.BooleanField(default=False)
    product_ref = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True, blank=True)
    origin_ref = models.ForeignKey(
        Origin, on_delete=models.CASCADE, null=True, blank=True)
    client_ref = models.ForeignKey(
        Client, on_delete=models.CASCADE, null=True, blank=True)
    loading_ref = models.ForeignKey(
        Loading, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default=0)
    # class Meta:
    #     unique_together = ('product_ref', 'origin_ref',
    #                        'client_ref', 'loading_ref')


class HaltEvent(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Halt(models.Model):
    halt_event_ref = models.ForeignKey(HaltEvent, on_delete=models.CASCADE)
    possible_cause = models.CharField(max_length=200)

    def __str__(self):
        return str(self.id) + '_' + self.halt_event_ref.name


class IncidentEvent(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return self.name


class IncidentSpecs(models.Model):
    qte_by_kgs = models.IntegerField(null=True, blank=True)
    temperature = models.CharField(max_length=50, null=True, blank=True)
    possible_cause = models.CharField(max_length=50, null=True, blank=True)
    humidity_rate = models.CharField(max_length=50, null=True, blank=True)
    photo = models.FileField(upload_to="incident/",
                             max_length=100, null=True, blank=True)
    incident_event_ref = models.ForeignKey(
        IncidentEvent, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id) + '_' + self.incident_event_ref.name


class IncidentDetails(models.Model):
    inspection_ref = models.ForeignKey(Inspection, on_delete=models.CASCADE)
    halt_ref = models.ForeignKey(
        Halt, on_delete=models.CASCADE, null=True, blank=True)
    incident_spec_ref = models.ForeignKey(
        IncidentSpecs, on_delete=models.CASCADE, null=True, blank=True)
    halt_or_incident = models.CharField(choices=H_L, max_length=50)
    stopping_hour = models.DateTimeField(auto_now=False, auto_now_add=False)
    resuming_hour = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True)
    related = models.CharField(choices=Incident_Choices, max_length=50)
    description = models.TextField(null=True, blank=True)


class Files(models.Model):
    file = models.FileField(max_length=256)
    inspection_ref = models.ForeignKey(Inspection, on_delete=models.CASCADE)
    incident_ref = models.ForeignKey(
        IncidentDetails, on_delete=models.CASCADE, null=True, blank=True)
    product_ref = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True, blank=True)
    hourlycheck_ref = models.ForeignKey(
        HourlyCheck, on_delete=models.CASCADE, null=True, blank=True)
    survey_ref = models.ForeignKey(
        IntermediateDraughtSurvey, on_delete=models.CASCADE, null=True, blank=True)
    client_ref = models.ForeignKey(
        Client, on_delete=models.CASCADE, null=True, blank=True)
