from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token
from .views import AsyncView

urlpatterns = [
    path("search/", views.SearchView.as_view(), name="search"),
    path("analysis/", views.AnalysisView.as_view(), name="analysis"),
    # path("generalgraphs/", views.GeneralGraphsView.as_view(), name="generalgraphs"),
]