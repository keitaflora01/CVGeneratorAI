from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
import json
import time
import base64
import uuid
import os

from Agent.models import Document, EtapeTraitement, CVImage
from django.db import models  # Ajoutez cette importation
import json
import time
from django.views.decorators.csrf import csrf_exempt
# Importez vos factories si elles existent, sinon commentez ou adaptez
# from Agent.services.cv.Agent_factor import CVAgentFactory
# from Agent.services.LM.Agent_factor import LMAgentFactory
User = get_user_model()

@csrf_exempt
def generate_document(request):
    """Page de génération de documents"""
    print("➡️ [generate_document] Méthode HTTP :", request.method)

    if request.method == 'POST':
        try:
            print("📥 Données POST reçues :", request.POST.dict())
            print("📂 Fichiers reçus :", request.FILES)

            target_role = request.POST.get('targetRole', '')
            company = request.POST.get('company', '')
            keywords = request.POST.get('keywords', '')
            tone = request.POST.get('tone', 'professionnel')
            job_description = request.POST.get('jobDescription', '')
            document_type = request.POST.get('documentType', 'CV')
            
            if not target_role or not job_description:
                return render(request, 'user/generate.html', {
                    'error': 'Le poste ciblé et la description sont obligatoires'
                })

            # Use AnonymousUser safely
            user = request.user if request.user.is_authenticated else None

            document = Document.objects.create(
                user=user,  # can be None
                type=document_type,
                titre=f"{document_type} pour {target_role}",
                poste=target_role,
                entreprise=company,
                statut='processing',
                metadata={
                    'keywords': keywords,
                    'tone': tone,
                    'job_description_preview': job_description[:100] + '...' if job_description else ''
                }
            )
            print("✅ Document créé avec ID :", document.id)

            # CV image handling
            if 'cv_image' in request.FILES and document_type == 'CV':
                cv_image = request.FILES['cv_image']
                if cv_image.size > 2 * 1024 * 1024:
                    document.delete()
                    return render(request, 'user/generate.html', {
                        'error': 'L\'image ne doit pas dépasser 2MB'
                    })
                CVImage.objects.create(
                    document=document,
                    image=cv_image,
                    description=f"Photo professionnelle pour {target_role}"
                )

            # Create processing steps
            etapes_data = [
                {"nom": "Analyse de l'offre d'emploi", "ordre": 1},
                {"nom": "Adaptation du profil", "ordre": 2},
                {"nom": "Génération du contenu", "ordre": 3},
                {"nom": "Optimisation", "ordre": 4},
                {"nom": "Validation finale", "ordre": 5},
            ]
            for etape_data in etapes_data:
                EtapeTraitement.objects.create(document=document, **etape_data)

            # Simulate document completion
            document.statut = 'completed'
            document.score = 85
            document.contenu = f"""
# CV pour {target_role}

## Informations personnelles
Nom: {request.user.get_full_name() if request.user.is_authenticated else 'Anonyme'}
Email: {request.user.email if request.user.is_authenticated else 'N/A'}
Poste ciblé: {target_role}
Entreprise: {company}

## Compétences
{keywords if keywords else 'Python, Django, JavaScript, React, SQL'}

Généré automatiquement avec l'IA le {time.strftime('%d/%m/%Y')}
"""
            document.save()

            # Mark steps as completed
            for etape in document.etape_traitement_set.all():
                etape.statut = 'completed'
                etape.save()

            return redirect('dashboard')

        except Exception as e:
            return render(request, 'user/generate.html', {
                'error': f'Une erreur est survenue: {str(e)}'
            })

    return render(request, 'user/generate.html')

def _get_user_data(user, document_type):
    """Récupère les données utilisateur depuis la base"""
    profile_data = {
        'name': f"{user.first_name} {user.last_name}" if user.first_name else user.username,
        'email': user.email,
    }
    
    # Ajoutez ici la logique pour récupérer les données réelles de votre utilisateur
    # Si vous avez un modèle Profile, utilisez-le
    
    # Données simulées pour la démo
    profile_data.update({
        'skills': ['Python', 'Django', 'JavaScript', 'React', 'SQL'],
        'experiences': [
            {
                'title': 'Développeur Full Stack',
                'company': 'Tech Solutions',
                'duration': '2020 - Present',
                'description': 'Développement d\'applications web full stack'
            }
        ],
        'education': [
            {
                'degree': 'Master en Informatique',
                'school': 'Université Paris-Saclay',
                'year': '2020'
            }
        ]
    })
    
    return profile_data

# ... le reste de vos vues ...

@login_required
def document_detail(request, document_id):
    """Détails d'un document"""
    document = get_object_or_404(Document, id=document_id, user=request.user)
    
    # Préparer le contexte pour le template
    context = {
        'document': document,
        'etapes': document.etape_traitement_set.all().order_by('ordre')
    }
    
    # Ajouter l'image si c'est un CV
    if document.type == 'CV' and hasattr(document, 'cv_image'):
        context['cv_image'] = document.cv_image
    
    return render(request, 'user/generate_document.html', context)

@login_required
def download_document(request, document_id):
    """Télécharger un document généré"""
    document = get_object_or_404(Document, id=document_id, user=request.user)
    
    if document.statut != 'completed':
        return JsonResponse({'error': 'Document non prêt'})
    
    # Déterminer le type MIME et l'extension
    if document.type == 'CV':
        filename = f"CV_{document.poste.replace(' ', '_')}.pdf"
        content_type = 'application/pdf'
    else:
        filename = f"Lettre_Motivation_{document.entreprise.replace(' ', '_')}.pdf"
        content_type = 'application/pdf'
    
    # Générer le PDF (implémentation simplifiée)
    pdf_content = generate_pdf(document)
    
    response = HttpResponse(pdf_content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

def generate_pdf(document):
    """Génère le PDF du document (implémentation simplifiée)"""
    # Cette fonction devrait utiliser une librairie de génération PDF
    # Pour l'exemple, on retourne le contenu textuel
    return document.contenu.encode('utf-8')

@csrf_exempt
@login_required
def upload_cv_image(request, document_id):
    """API pour uploader une image pour un CV"""
    if request.method == 'POST':
        document = get_object_or_404(Document, id=document_id, user=request.user)
        
        if document.type != 'CV':
            return JsonResponse({'success': False, 'error': 'Document must be a CV'})
        
        if 'image' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No image provided'})
        
        # Créer ou mettre à jour l'image CV
        image_file = request.FILES['image']
        cv_image, created = CVImage.objects.get_or_create(document=document)
        cv_image.image = image_file
        cv_image.description = f"Photo professionnelle pour {document.poste}"
        cv_image.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Image uploaded successfully',
            'image_url': cv_image.image.url
        })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

@csrf_exempt
@login_required
def update_document_status(request, document_id):
    """API pour mettre à jour le statut d'un document (utilisé par les workers)"""
    if request.method == 'POST':
        document = get_object_or_404(Document, id=document_id, user=request.user)
        
        data = json.loads(request.body)
        new_status = data.get('status')
        score = data.get('score', 0)
        
        if new_status in dict(Document.STATUS_CHOICES).keys():
            document.statut = new_status
            document.score = score
            document.save()
            
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': False, 'error': 'Statut invalide'})
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})