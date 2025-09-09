# mon_app/views.py
from django.urls import reverse
from django.views.generic import TemplateView

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from Agent.models import Document
from django.db.models import Q, Avg
from django.urls import reverse

class DashboardView(LoginRequiredMixin, ListView):
    template_name = "user/dashboard.html"
    context_object_name = "documents"
    
    def get_queryset(self):
        """Fetch documents for the current user with optional filtering"""
        queryset = Document.objects.filter(user=self.request.user).order_by('-date_creation')
        
        # Apply filters
        type_filter = self.request.GET.get('type', 'tous')
        if type_filter != 'tous':
            queryset = queryset.filter(type=type_filter)
        
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(titre__icontains=query) |
                Q(poste__icontains=query) |
                Q(entreprise__icontains=query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add statistics and filter values to the context"""
        context = super().get_context_data(**kwargs)
        documents = self.get_queryset()
        
        # Calculate statistics
        documents_count = documents.count()
        processing_count = documents.filter(statut='processing').count()
        completed_count = documents.filter(statut='completed').count()
        success_rate = (completed_count / documents_count * 100) if documents_count > 0 else 0
        average_score = documents.aggregate(Avg('score'))['score__avg'] or 0
        
        context.update({
            'documents_count': documents_count,
            'processing_count': processing_count,
            'success_rate': round(success_rate, 2),
            'average_score': round(average_score, 2),
            'type_filter': self.request.GET.get('type', 'tous'),
            'q': self.request.GET.get('q', ''),
        })
        return context
class GenerateView(TemplateView):
    template_name = "user/generate.html"