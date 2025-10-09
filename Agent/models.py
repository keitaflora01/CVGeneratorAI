from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
import os

def cv_image_path(instance, filename):
    # Générer le chemin pour l'image du CV
    return f'cv_images/user_{instance.document.user.id}/{instance.document.id}/{filename}'

class Document(models.Model):
    DOCUMENT_TYPES = (
        ('CV', 'Curriculum Vitae'),
        ('LM', 'Lettre de Motivation'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('processing', 'En traitement'),
        ('completed', 'Terminé'),
        ('error', 'Erreur'),
    )
    
    LANGUE_CHOICES = (
        ('fr', 'Français'),
        ('en', 'Anglais'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=2, choices=DOCUMENT_TYPES)
    titre = models.CharField(max_length=255)
    poste = models.CharField(max_length=255)
    entreprise = models.CharField(max_length=255, blank=True)
    linkedin_url = models.URLField(max_length=255, blank=True, null=True)
    github_url = models.URLField(max_length=255, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True)
    langue = models.CharField(max_length=2, choices=LANGUE_CHOICES, default='fr')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    statut = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    score = models.IntegerField(default=0)
    contenu = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    template_utilise = models.CharField(max_length=100, default='default')
    
    class Meta:
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.titre} - {self.get_type_display()}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('Agent:document_detail', kwargs={'document_id': self.id})
    
    @property
    def etapes(self):
        """Propriété pour accéder aux étapes dans les templates"""
        return self.etape_traitement_set.all().order_by('ordre')


class EtapeTraitement(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('processing', 'En traitement'),
        ('completed', 'Terminé'),
        ('error', 'Erreur'),
    )
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='etape_traitement_set')
    nom = models.CharField(max_length=100)
    ordre = models.IntegerField()
    statut = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    details = models.TextField(blank=True)
    date_debut = models.DateTimeField(null=True, blank=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['ordre']
    
    def __str__(self):
        return f"{self.document.titre} - {self.nom}"


class CVImage(models.Model):
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='cv_image')
    image = models.ImageField(upload_to=cv_image_path, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image pour {self.document.titre}"
    
    def delete(self, *args, **kwargs):
        # Supprimer le fichier image lors de la suppression de l'objet
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)
