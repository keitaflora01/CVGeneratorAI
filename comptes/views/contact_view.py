from django.views.generic import TemplateView


class ContactUsView(TemplateView):
    template_name = "accound/contact_us.html"