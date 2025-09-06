from django.contrib import admin
from .models import Document, EtapeTraitement, CVImage

class EtapeTraitementInline(admin.TabularInline):
    model = EtapeTraitement
    extra = 0
    readonly_fields = ['nom', 'ordre', 'statut', 'details', 'date_debut', 'date_fin']

class CVImageInline(admin.StackedInline):
    model = CVImage
    extra = 0
    readonly_fields = ['date_creation']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['titre', 'type', 'user', 'poste', 'entreprise', 'statut', 'score', 'date_creation']
    list_filter = ['type', 'statut', 'date_creation', 'template_utilise']
    search_fields = ['titre', 'poste', 'entreprise', 'user__username']
    inlines = [EtapeTraitementInline, CVImageInline]
    readonly_fields = ['date_creation', 'date_mise_a_jour']

@admin.register(EtapeTraitement)
class EtapeTraitementAdmin(admin.ModelAdmin):
    list_display = ['nom', 'document', 'ordre', 'statut', 'date_debut', 'date_fin']
    list_filter = ['statut', 'nom']
    readonly_fields = ['date_debut', 'date_fin']

@admin.register(CVImage)
class CVImageAdmin(admin.ModelAdmin):
    list_display = ['document', 'description', 'date_creation']
    list_filter = ['date_creation']
    readonly_fields = ['date_creation']