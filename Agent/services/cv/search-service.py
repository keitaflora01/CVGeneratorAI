import requests
from django.conf import settings

class CVSearchService:
    def __init__(self):
        self.api_key = settings.GOOGLE_SEARCH_API_KEY if hasattr(settings, 'GOOGLE_SEARCH_API_KEY') else None
        self.search_engine_id = settings.SEARCH_ENGINE_ID if hasattr(settings, 'SEARCH_ENGINE_ID') else None
    
    def find_skill_alternatives(self, missing_skills, existing_skills):
        """
        Trouve des alternatives ou des formations pour les compétences manquantes
        """
        alternatives = {}
        
        for skill in missing_skills:
            # Recherche d'alternatives basée sur les compétences existantes
            similar_skills = self._find_similar_skills(skill, existing_skills)
            
            # Recherche de formations en ligne
            courses = self._find_online_courses(skill)
            
            alternatives[skill] = {
                "similar_skills": similar_skills,
                "online_courses": courses
            }
        
        return alternatives
    
    def _find_similar_skills(self, target_skill, existing_skills):
        """
        Trouve des compétences similaires dans le profil existant
        """
        # Implémentation simplifiée - dans un vrai système, utiliser une base de données de compétences
        similar_skills_map = {
            "React": ["JavaScript", "TypeScript", "Frontend", "Web Development"],
            "Node.js": ["JavaScript", "Backend", "API Development"],
            "Python": ["Django", "Flask", "Data Analysis", "Automation"],
            "Machine Learning": ["Data Science", "AI", "Python", "Statistics"],
            # Ajouter d'autres mappings...
        }
        
        return similar_skills_map.get(target_skill, [])
    
    def _find_online_courses(self, skill):
        """
        Recherche des cours en ligne pour une compétence spécifique
        """
        # Implémentation simplifiée
        courses_map = {
            "React": ["Cours React sur Udemy", "Formation React sur OpenClassrooms"],
            "Node.js": ["Node.js Master Class", "Formation Node.js complète"],
            "Python": ["Python for Everybody", "Automate the Boring Stuff with Python"],
            "Machine Learning": ["Machine Learning A-Z", "Coursera Machine Learning"],
        }
        
        return courses_map.get(skill, [f"Cours {skill} sur les plateformes d'apprentissage"])
    
    def search_industry_trends(self, job_title):
        """
        Recherche les tendances de l'industrie pour un poste spécifique
        """
        # Implémentation avec API de recherche si disponible
        if self.api_key and self.search_engine_id:
            try:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    'key': self.api_key,
                    'cx': self.search_engine_id,
                    'q': f"{job_title} tendances 2024 compétences requises"
                }
                
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    return response.json().get('items', [])[:3]  # Retourner les 3 premiers résultats
            except:
                pass
        
        # Fallback si l'API n'est pas configurée ou en cas d'erreur
        return [
            {"title": "Tendances des compétences pour 2024", "link": "#", "snippet": "Les compétences en IA et cloud computing sont très demandées."}
        ]