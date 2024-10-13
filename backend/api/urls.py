from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("search/", views.SearchView.as_view(), name="search"),
    path("analysis/", views.AnalysisView.as_view(), name="analysis"),
    path("indianEconomy/", views.IndianEconomy.as_view(), name="indianEconomy"),
    # path("generalgraphs/", views.GeneralGraphsView.as_view(), name="generalgraphs"),
]