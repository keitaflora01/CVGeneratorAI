from django.views.generic import TemplateView
from django.utils.translation import gettext as _
from django.contrib import messages
import traceback

from comptes.models import SystemSetting


class PrivacyPolicyView(TemplateView):
    template_name = 'setting/privacy_policy.html'

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)

            # Récupère les paramètres globaux
            parametre = SystemSetting.objects.first()

            context.update({
                "page_title": _("Politique de confidentialité"),
                "privacy": parametre.privacy_policy if parametre else "",
                "contact_email": parametre.contact_email if parametre else "",
                "contact_phone": parametre.contact_phone if parametre else "",
                "contact_address": parametre.contact_address if parametre else "",
            })
            return context

        except Exception as e:
            messages.error(self.request, _("Une erreur s'est produite lors du chargement de la politique de confidentialité."))
            print("Erreur PrivacyPolicyView:", e)
            print(traceback.format_exc())
            return {"page_title": _("Politique de confidentialité"), "privacy": ""}


class TermsOfServiceView(TemplateView):
    template_name = 'setting/terms_of_service.html'

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            parametre = SystemSetting.objects.first()
            context.update({
                "page_title": _("Conditions d'utilisation"),
                "terms": parametre.terms_of_service if parametre else "",
            })
            return context

        except Exception as e:
            messages.error(self.request, _("Une erreur s'est produite lors du chargement des conditions d'utilisation."))
            print("Erreur TermsOfServiceView:", e)
            print(traceback.format_exc())
            return {"page_title": _("Conditions d'utilisation"), "terms": ""}

