from django.db import models
from django.conf import settings
from Agent.models import Document

class LMAgent(models.Model):
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='lm_agent')
    version = models.CharField(max_length=20, default='1.0')
    modele_utilise = models.CharField(max_length=100, default='gpt-4')
    parametres = models.JSONField(default=dict)
    performances = models.JSONField(default=dict)  # Métriques d'évaluation
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lm_agents'
    
    def __str__(self):
        return f"LM Agent for {self.document.titre}"