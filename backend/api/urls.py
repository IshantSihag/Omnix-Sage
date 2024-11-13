from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path("search/", views.SearchView.as_view(), name="search"),
    path("analysis/", views.AnalysisView.as_view(), name="analysis"),
    path("indianEconomy/", views.IndianEconomy.as_view(), name="indianEconomy"),
    path("indianIndustry/", views.IndianIndustry.as_view(), name="indianIndustry"),
    # path("generalgraphs/", views.GeneralGraphsView.as_view(), name="generalgraphs"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('user/', views.UserDetailView.as_view(), name='user_detail'),
    path('change-name/', views.ChangeNameView.as_view(), name='change_name'),  # New endpoint for name change
]