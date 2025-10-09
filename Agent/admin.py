from django.contrib import admin
from .models import Document, EtapeTraitement, CVImage

class EtapeTraitementInline(admin.TabularInline):
    model = EtapeTraitement
    extra = 0
    readonly_fields = ['statut', 'date_debut', 'date_fin']  # uniquement l'essentiel

class CVImageInline(admin.StackedInline):
    model = CVImage
    extra = 0
    readonly_fields = ['date_creation']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    # Champs essentiels visibles dans la liste
    list_display = ['titre', 'type', 'user', 'statut', 'date_creation']
    list_filter = ['type', 'statut', 'date_creation']
    search_fields = ['titre', 'user__username']
    
    inlines = [EtapeTraitementInline, CVImageInline]
    
    # Champs non modifiables
    readonly_fields = ['date_creation', 'date_mise_a_jour']

@admin.register(EtapeTraitement)
class EtapeTraitementAdmin(admin.ModelAdmin):
    list_display = ['nom', 'statut', 'date_debut', 'date_fin']
    list_filter = ['statut']
    readonly_fields = ['date_debut', 'date_fin']

@admin.register(CVImage)
class CVImageAdmin(admin.ModelAdmin):
    list_display = ['document', 'date_creation']
    list_filter = ['date_creation']
    readonly_fields = ['date_creation']
