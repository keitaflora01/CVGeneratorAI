from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.views import View
from django.http import JsonResponse
from comptes.models import User
import logging
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages

logger = logging.getLogger(__name__)


class SignUpView(View):
    template_name = "accound/pages/signup.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        logger.debug("Données POST reçues : %s", request.POST)
        email = request.POST.get("email")
        full_name = request.POST.get("full_name")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        # Validation
        if not email or not full_name or not password or not password2:
            error = "Tous les champs sont requis."
        elif password != password2:
            error = "Les mots de passe ne correspondent pas."
        elif len(password) < 8:
            error = "Le mot de passe doit contenir au moins 8 caractères."    
        elif User.objects.filter(email=email).exists():
            error = "Cet email est déjà utilisé."
        else:
            # Crée l'utilisateur
            user = User.objects.create_user(
                email=email,
                password=password,
                full_name=full_name
            )
            # Redirection après inscription
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "redirect_url": "/"})
            return redirect("home")

        # Si erreur
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": error})
        return render(request, self.template_name, {"error": error})
# ---------------------------
# Connexion
# ---------------------------
class CustomLoginView(View):
    template_name = "accound/pages/login.html"

    def get(self, request):
        success_message = request.GET.get("success", "")
        return render(request, self.template_name, {"success_message": success_message})

    def post(self, request):
        logger.debug("Données POST reçues : %s", request.POST)
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Authentification avec email
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "redirect_url": "/dashboard/"})
            return redirect("dashboard")
        else:
            error = "Email ou mot de passe incodashboardrrect."
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "error": error})
            return render(request, self.template_name, {"error": error})

class CustomLogoutView(View):
    def post(self, request):
        logger.debug("Déconnexion de l'utilisateur : %s", request.user)
        logout(request)
        
        # Si la requête est AJAX, renvoyer JSON avec redirection vers home
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": True, "redirect_url": "/"})
        
        # Sinon redirection classique vers la page d'accueil
        return redirect("home")

@method_decorator(login_required, name='dispatch')
class AccountSettingsView(View):
    template_name = "accound/pages/account_settings.html"

    def get(self, request):
        return render(request, self.template_name)

@method_decorator(login_required, name='dispatch')
class UpdateProfileView(View):
    def post(self, request):
        user = request.user
        section = request.POST.get("section")

        try:
            if section == "profile":
                user.first_name = request.POST.get("first_name")
                user.last_name = request.POST.get("last_name")
                user.headline = request.POST.get("headline")
                if 'profile_image' in request.FILES:
                    user.profile_image = request.FILES['profile_image']
                user.save()
                messages.success(request, "Profil mis à jour avec succès.")
            
            elif section == "account":
                user.email = request.POST.get("email")
                user.timezone = request.POST.get("timezone")
                user.language = request.POST.get("language")
                user.save()
                messages.success(request, "Informations du compte mises à jour avec succès.")
            
            elif section == "contact":
                user.mobile_phone = request.POST.get("mobile_phone")
                user.country = request.POST.get("country")
                user.state = request.POST.get("state")
                user.city = request.POST.get("city")
                user.save()
                messages.success(request, "Informations de contact mises à jour avec succès.")
            
            else:
                messages.error(request, "Section invalide.")
        
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du profil : {str(e)}")
            messages.error(request, "Une erreur s'est produite lors de la mise à jour.")

        return redirect("comptes:account_settings")


# comptes/views/account_view.py
@method_decorator(login_required, name='dispatch')
class UpgradePlanView(View):
    template_name = "accound/pages/upgrade_plan.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        plan = request.POST.get("plan")
        try:
            if plan in ["Freemium", "Premium", "Pro"]:  # Validez les plans disponibles
                request.user.account_tier = plan
                # Logique pour mettre à jour subscription_end_date et cv_limit si nécessaire
                request.user.save()
                messages.success(request, f"Plan mis à jour vers {plan} avec succès.")
            else:
                messages.error(request, "Plan invalide.")
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du plan : {str(e)}")
            messages.error(request, "Une erreur s'est produite lors de la mise à jour du plan.")
        return redirect("comptes:upgrade")
