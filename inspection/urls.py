from django.conf.urls import url, include, handler404

from django.urls import path, re_path
from rest_framework import routers
from inspection.views import (MyTokenObtainPairView, PortView, UserViewSet, error_page,
                              UserCreateAPIView, UserIsRefusedViewSet, DepartementView, VesselView, LoadingView,
                              InspectionView, HourlyCheckView, ProductCategoryView, ProductFamilyView, ProductView,
                              OriginView, ClientView, ClientLoadingDetailView, HaltView, InspectionStat,
                              HaltEventView, InspectionTestView, IncidentEventView,
                              IncidentDetailsView, MonthlyQuantityView, IncidentSpecView, RequirementView, PortstatsView)

from inspection.CustomViews.m_views import (
    HourlyCheckByInspecRefView, UserDisableViewSet,
    EventsCountView,
    MonthlyEventsViewSet, ProductListView, QuantitiesStatView)
from inspection.CustomViews.a_views import IntermediateDraughtSurveyView, ProductCreateView, CLientLinkView, ProductTypeView, IncidentTestView, FileView, EditProductView, ProductCustomizedView, ChartPieIncidentView, AllTimeChartView
from rest_framework_simplejwt.views import TokenRefreshView


handler404 = error_page

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'departement', DepartementView)
router.register(r'vessel', VesselView)
router.register(r'loading', LoadingView)
router.register(r'inspection', InspectionView)
router.register(r'productcategory', ProductCategoryView)
router.register(r'productfamily', ProductFamilyView)
router.register(r'productype', ProductTypeView)
router.register(r'product', ProductView)
router.register(r'origin', OriginView)
router.register(r'port', PortView)
router.register(r'client', ClientView)
router.register(r'clientdetail', ClientLoadingDetailView)
router.register(r'halt', HaltView)
router.register(r'haltevent', HaltEventView)
router.register(r'incident', IncidentEventView)
router.register(r'incidentdetails', IncidentDetailsView)
router.register(r'incidentspec', IncidentSpecView)
router.register(r'list/inspection', InspectionTestView)
router.register(r'file', FileView)

urlpatterns = [
    url(r'^', include(router.urls)),
    path("users/<int:pk>/is_refused/", UserIsRefusedViewSet.as_view()),
    path("users/<int:pk>/is_active/", UserDisableViewSet.as_view()),
    path("user/create/", UserCreateAPIView.as_view()),
    url(r'^auth/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("requirement/", RequirementView.as_view()),
    path("inspections/stat", InspectionStat.as_view()),
    path("ports/stat", PortstatsView.as_view()),
    path("qte/stat", MonthlyQuantityView.as_view()),
    path("hourly/<int:pk>", HourlyCheckByInspecRefView.as_view(),
         name='Hourly Check List by Inspection Ref'),
    path("createproduct/", ProductCreateView.as_view()),
    path("clientinsert/", CLientLinkView.as_view()),
    path("list/incident/", IncidentTestView.as_view()),
    path("editproduct/", EditProductView.as_view()),
    path("productree/", ProductCustomizedView.as_view()),
    path("events/monthly/count", MonthlyEventsViewSet.as_view()),
    path("hourlycheck/", HourlyCheckView.as_view()),
    path("inter/", IntermediateDraughtSurveyView.as_view()),
    path("incidentpiechart/", ChartPieIncidentView.as_view()),
    path("incidentchart/", AllTimeChartView.as_view()),
    path("products/", ProductListView.as_view()),
    path("quantity/statistic", QuantitiesStatView.as_view()),
    path("inpection/events/counts", EventsCountView.as_view()),
    # url(r'^export/xls/', export_users_xls, name='export_users_xls')
]
