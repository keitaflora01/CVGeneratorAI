# mon_app/views.py
from django.urls import reverse
from django.views.generic import TemplateView

class DashboardView(TemplateView):
    template_name = "user/dashboard.html"   

    def get_success_url(self):
        return reverse("dashboard") 

class GenerateView(TemplateView):
    template_name = "user/generate.html"