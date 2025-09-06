from django.urls import path
from comptes.views.account_view import SignUpView , CustomLoginView, CustomLogoutView
from comptes.views.dashboard_view import DashboardView,GenerateView

app_name = 'comptes'

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path('generate/', GenerateView.as_view(), name='generate'),
]
