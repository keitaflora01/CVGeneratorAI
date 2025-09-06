import requests
from django.conf import settings

class LMSearchService:
    def __init__(self):
        self.api_key = settings.GOOGLE_SEARCH_API_KEY if hasattr(settings, 'GOOGLE_SEARCH_API_KEY') else None
        self.search_engine_id = settings.SEARCH_ENGINE_ID if hasattr(settings, 'SEARCH_ENGINE_ID') else None
    
    def get_company_info(self, company_name):
        """
        Récupère des informations sur une entreprise pour personnaliser la lettre
        """
        # Implémentation avec API de recherche si disponible
        if self.api_key and self.search_engine_id and company_name:
            try:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    'key': self.api_key,
                    'cx': self.search_engine_id,
                    'q': f"{company_name} valeurs culture entreprise"
                }
                
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    items = response.json().get('items', [])
                    
                    # Analyser les résultats pour extraire des informations sur la culture
                    culture_info = self._extract_culture_info(items)
                    
                    return {
                        "company_name": company_name,
                        "culture_info": culture_info,
                        "source": "google_search"
                    }
            except:
                pass
        
        # Fallback avec des informations génériques
        return {
            "company_name": company_name,
            "culture_info": {
                "values": ["Innovation", "Collaboration", "Excellence"],
                "description": f"{company_name} est reconnue pour son engagement envers l'innovation et l'excellence."
            },
            "source": "default"
        }
    
    def _extract_culture_info(self, search_results):
        """
        Extrait des informations sur la culture d'entreprise à partir des résultats de recherche
        """
        # Implémentation simplifiée - utiliser NLP dans une version réelle
        common_values = [
            "innovation", "collaboration", "excellence", "diversité", "inclusion",
            "responsabilité", "qualité", "service client", "intégrité", "transparence"
        ]
        
        found_values = []
        description = ""
        
        for item in search_results[:2]:  # Analyser les 2 premiers résultats
            snippet = item.get('snippet', '').lower()
            title = item.get('title', '').lower()
            
            for value in common_values:
                if value in snippet or value in title:
                    found_values.append(value.capitalize())
            
            # Prendre la première description significative
            if not description and len(snippet) > 50:
                description = snippet[:200] + "..."
        
        # Éviter les doublons
        found_values = list(set(found_values))
        
        return {
            "values": found_values[:5],  # Limiter à 5 valeurs
            "description": description or "Entreprise dynamique et innovante."
        }
    
    def find_company_achievements(self, company_name):
        """
        Recherche les réalisations récentes de l'entreprise
        """
        # Implémentation simplifiée
        achievements_map = {
            "Google": ["Lancement de nouveaux produits AI", "Expansion sur de nouveaux marchés"],
            "Amazon": ["Innovation dans le cloud computing", "Développement durable"],
            "Microsoft": ["Avancées dans l'IA generative", "Engagement carbone négatif"],
            "Apple": ["Innovation produit", "Engagement environnemental"]
        }
        
        # Trouver la correspondance la plus proche
        for key in achievements_map:
            if key.lower() in company_name.lower():
                return achievements_map[key]
        
        # Retourner des réalisations génériques
        return ["Innovation continue", "Croissance soutenue", "Engagement client"]