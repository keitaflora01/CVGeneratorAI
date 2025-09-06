from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import LoginView
from django.views import View
from django.http import JsonResponse
from comptes.models import CustomUser
import logging

# Configurer le logger
logger = logging.getLogger(__name__)

# Inscription
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

        if not email or not full_name or not password or not password2:
            error = "Tous les champs sont requis."
        elif password != password2:
            error = "Les mots de passe ne correspondent pas."
        elif CustomUser.objects.filter(email=email).exists():
            error = "Cet email est déjà utilisé."
        else:
            user = CustomUser.objects.create_user(email=email, password=password, full_name=full_name)
            # Ne pas connecter automatiquement, rediriger vers login avec message de succès
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "redirect_url": "/login/?success=Inscription+réussie"})
            return redirect("comptes:login", success="Inscription réussie")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": error})
        return render(request, self.template_name, {"error": error})

# Connexion
class CustomLoginView(View):
    template_name = "accound/pages/login.html"

    def get(self, request):
        success_message = request.GET.get("success", "")
        return render(request, self.template_name, {"success_message": success_message})

    def post(self, request):
        logger.debug("Données POST reçues : %s", request.POST)
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "redirect_url": "/dashboard/"})
            return redirect("dashboard")
        else:
            error = "Email ou mot de passe incorrect."
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "error": error})
            return render(request, self.template_name, {"error": error})

# Déconnexion
class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("comptes:login")