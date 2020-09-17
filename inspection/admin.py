from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from inspection.models import User, UserProfile, Departement, Vessel, Loading, Inspection, HourlyCheck, ProductCategory, ProductFamily, Product, Origin, Client, ClientLoadingDetails, Halt, HaltEvent, IncidentEvent, IncidentSpecs, IncidentDetails, Port, Docks, ProductType, Files


class LoadingAdmin(admin.ModelAdmin):
    list_display = ('id', 'loading_port')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(Departement)
admin.site.register(Vessel)
admin.site.register(Loading, LoadingAdmin)
admin.site.register(Inspection)
admin.site.register(HourlyCheck)
admin.site.register(ProductCategory)
admin.site.register(ProductFamily)
admin.site.register(ProductType)
admin.site.register(Product, ProductAdmin)
admin.site.register(Origin, ProductAdmin)
admin.site.register(Client, ProductAdmin)
admin.site.register(ClientLoadingDetails)
admin.site.register(Halt)
admin.site.register(HaltEvent)
admin.site.register(IncidentEvent)
admin.site.register(IncidentSpecs)
admin.site.register(IncidentDetails)
admin.site.register(Port)
admin.site.register(Docks)
admin.site.register(Files)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('id', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    inlines = (UserProfileInline, )
