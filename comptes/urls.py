from django.urls import path
from comptes.views import account_view
from comptes.views.account_view import SignUpView , CustomLoginView, CustomLogoutView
from comptes.views.contact_view import ContactUsView
from comptes.views.dashboard_view import DashboardView,GenerateView
from comptes.views.privacy_policy_view import PrivacyPolicyView, TermsOfServiceView

app_name = 'comptes'

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("settings/", account_view.AccountSettingsView.as_view(), name="account_settings"),
    path("update-profile/", account_view.UpdateProfileView.as_view(), name="update_profile"),
    path("update-account/", account_view.UpdateProfileView.as_view(), name="update_account"),
    path("update-contact/", account_view.UpdateProfileView.as_view(), name="update_contact"),
    path("upgrade/", account_view.UpgradePlanView.as_view(), name="upgrade"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path('generate/', GenerateView.as_view(), name='generate'),
    path('contact/', ContactUsView.as_view(), name='contact'),
    path("privacy-policy/", PrivacyPolicyView.as_view(), name="privacy_policy"),
    path("terms-of-service/", TermsOfServiceView.as_view(), name="terms_of_service"),

]
