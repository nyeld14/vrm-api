from django.urls import path
from .views import VRMFleetStatusView, VRMSiteDetailView

urlpatterns = [
    path('fleet-status/', VRMFleetStatusView.as_view()),
    path('fleet-status/<int:installation_id>/', VRMSiteDetailView.as_view()),
]
