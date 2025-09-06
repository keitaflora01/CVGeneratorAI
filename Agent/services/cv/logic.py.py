import re
from langchain import PromptTemplate
from langchain.chains import LLMChain

class CVLogic:
    def __init__(self, llm, cv_tools, search_service):
        self.llm = llm
        self.cv_tools = cv_tools
        self.search_service = search_service
    
    def analyze_job_description(self, job_description):
        """
        Analyse la description de poste pour en extraire les exigences clés
        """
        prompt_template = PromptTemplate(
            input_variables=["job_description"],
            template="""
            Analysez cette description de poste et extrayez les informations clés:
            
            {job_description}
            
            Veuillez retourner un JSON structuré avec:
            - job_title: le titre du poste
            - required_skills: liste des compétences requises
            - preferred_skills: liste des compétences préférées
            - experience_level: niveau d'expérience requis
            - keywords: mots-clés importants
            - company_culture: indices sur la culture d'entreprise
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        result = chain.run(job_description=job_description)
        
        # Extraire le JSON de la réponse
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            import json
            try:
                return json.loads(json_match.group())
            except:
                # Fallback si le parsing JSON échoue
                return {
                    "job_title": "Poste analysé",
                    "required_skills": [],
                    "preferred_skills": [],
                    "experience_level": "Non spécifié",
                    "keywords": [],
                    "company_culture": "Non spécifié"
                }
        
        return result
    
    def adapt_profile_to_job(self, user_data, job_analysis):
        """
        Adapte le profil utilisateur aux exigences du poste
        """
        # Implémentation de l'adaptation du profil
        adapted_profile = user_data.copy()
        
        # Ajouter les compétences manquantes mais requises
        required_skills = job_analysis.get('required_skills', [])
        user_skills = user_data.get('skills', [])
        
        # Identifier les compétences manquantes
        missing_skills = [skill for skill in required_skills if skill not in user_skills]
        
        if missing_skills:
            adapted_profile['missing_skills'] = missing_skills
            # Suggérer des formations ou expériences similaires
            adapted_profile['skill_suggestions'] = self.search_service.find_skill_alternatives(
                missing_skills, user_skills
            )
        
        return adapted_profile
    
    def generate_cv_content(self, adapted_profile, job_analysis):
        """
        Génère le contenu du CV basé sur le profil adapté
        """
        prompt_template = PromptTemplate(
            input_variables=["profile", "job_analysis"],
            template="""
            Créez un CV professionnel en français basé sur le profil suivant et l'analyse de poste.
            
            PROFIL:
            {profile}
            
            ANALYSE DU POSTE:
            {job_analysis}
            
            Le CV doit être structuré avec:
            1. En-tête avec informations personnelles
            2. Profil professionnel summary
            3. Expériences professionnelles (mettre en avant les expériences pertinentes)
            4. Formations
            5. Compétences (adapter aux exigences du poste)
            6. Langues et certifications
            
            Utilisez un ton professionnel et mettez en avant les correspondances avec le poste.
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        return chain.run(profile=str(adapted_profile), job_analysis=str(job_analysis))
    
    def optimize_cv_seo(self, cv_content, keywords):
        """
        Optimise le CV pour les systèmes de tracking ATS
        """
        # Implémentation de l'optimisation SEO
        optimized_content = cv_content
        
        for keyword in keywords:
            # S'assurer que les mots-clés importants sont présents
            if keyword.lower() not in optimized_content.lower():
                # Trouver un endroit approprié pour ajouter le mot-clé
                optimized_content = self._insert_keyword(optimized_content, keyword)
        
        return optimized_content
    
    def _insert_keyword(self, content, keyword):
        """Insère un mot-clé de manière contextuelle dans le contenu"""
        # Implémentation simplifiée
        lines = content.split('\n')
        
        # Essayer d'insérer dans la section compétences
        for i, line in enumerate(lines):
            if 'compétences' in line.lower() or 'skills' in line.lower():
                # Insérer après le titre de section
                if i + 1 < len(lines):
                    lines.insert(i + 1, f"- {keyword}")
                    return '\n'.join(lines)
        
        # Sinon ajouter à la fin
        return content + f"\n\nCompétences: {keyword}"
    
# Ajoutez cette méthode à la classe CVLogic
def generate_cv_with_image(self, adapted_profile, job_analysis, image_data=None):
    """
    Génère le contenu du CV en incluant une référence à l'image si disponible
    """
    image_reference = ""
    if image_data and image_data.get('has_image'):
        image_reference = f"\n![Photo professionnelle]({image_data.get('image_url', '')})"
    
    prompt_template = PromptTemplate(
        input_variables=["profile", "job_analysis", "image_reference"],
        template="""
        Créez un CV professionnel en français basé sur le profil suivant et l'analyse de poste.
        
        PROFIL:
        {profile}
        
        ANALYSE DU POSTE:
        {job_analysis}
        
        {image_reference}
        
        Le CV doit être structuré avec:
        1. En-tête avec informations personnelles
        2. Profil professionnel summary
        3. Expériences professionnelles (mettre en avant les expériences pertinentes)
        4. Formations
        5. Compétences (adapter aux exigences du poste)
        6. Langues et certifications
        
        Si une image est fournie, inclure une mention appropriée dans l'en-tête.
        Utilisez un ton professionnel et mettez en avant les correspondances avec le poste.
        """
    )
    
    chain = LLMChain(llm=self.llm, prompt=prompt_template)
    return chain.run(
        profile=str(adapted_profile), 
        job_analysis=str(job_analysis),
        image_reference=image_reference
    )
