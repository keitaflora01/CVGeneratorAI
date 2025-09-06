import re
from langchain import PromptTemplate
from langchain.chains import LLMChain

class LMLogic:
    def __init__(self, llm, lm_tools, search_service):
        self.llm = llm
        self.lm_tools = lm_tools
        self.search_service = search_service
    
    def analyze_job_and_company(self, job_description):
        """
        Analyse la description de poste et recherche des informations sur l'entreprise
        """
        # Extraire le nom de l'entreprise si possible
        company_name = self._extract_company_name(job_description)
        
        prompt_template = PromptTemplate(
            input_variables=["job_description", "company_name"],
            template="""
            Analysez cette description de poste et extrayez les informations clés pour une lettre de motivation:
            
            {job_description}
            
            Entreprise: {company_name}
            
            Veuillez retourner un JSON structuré avec:
            - company_values: valeurs probables de l'entreprise
            - job_requirements: exigences principales du poste
            - motivation_triggers: éléments qui pourraient motiver un candidat
            - tone_suggestion: ton approprié pour la lettre (formel, enthousiaste, etc.)
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        result = chain.run(job_description=job_description, company_name=company_name)
        
        # Extraire le JSON de la réponse
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            import json
            try:
                analysis = json.loads(json_match.group())
                analysis['company_name'] = company_name
                return analysis
            except:
                pass
        
        # Fallback
        return {
            "company_name": company_name,
            "company_values": ["Excellence", "Innovation", "Collaboration"],
            "job_requirements": [],
            "motivation_triggers": [],
            "tone_suggestion": "professionnel"
        }
    
    def _extract_company_name(self, text):
        """Tente d'extraire le nom de l'entreprise du texte"""
        # Implémentation simplifiée - utiliser NER dans une version réelle
        patterns = [
            r"chez\s+([A-Z][a-zA-Z\s&]+)",
            r"à\s+([A-Z][a-zA-Z\s&]+)",
            r"entreprise\s+([A-Z][a-zA-Z\s&]+)",
            r"chez\s+([A-Z][a-zA-Z\s&]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Cette entreprise"
    
    def generate_motivation_letter(self, user_data, job_analysis, cv_content=None):
        """
        Génère une lettre de motivation personnalisée
        """
        prompt_template = PromptTemplate(
            input_variables=["user_data", "job_analysis", "cv_content"],
            template="""
            Rédigez une lettre de motivation persuasive en français pour le poste suivant:
            
            ANALYSE DU POSTE ET ENTREPRISE:
            {job_analysis}
            
            PROFIL DU CANDIDAT:
            {user_data}
            
            CONTENU DU CV (pour référence):
            {cv_content}
            
            La lettre doit:
            1. Commencer par une introduction percutante
            2. Mentionner pourquoi le candidat est intéressé par cette entreprise spécifique
            3. Mettre en avant 2-3 compétences/expériences les plus pertinentes
            4. Expliquer comment le candidat peut apporter de la valeur
            5. Se terminer par un appel à l'action pour un entretien
            6. Utiliser le ton: {tone}
            
            Longueur: environ 250-300 mots.
            """
        )
        
        tone = job_analysis.get('tone_suggestion', 'professionnel')
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        
        return chain.run(
            user_data=str(user_data),
            job_analysis=str(job_analysis),
            cv_content=cv_content or "Non fourni",
            tone=tone
        )
    
    def personalize_letter(self, letter_content, contact_name=None, company_details=None):
        """
        Personnalise la lettre avec des détails spécifiques
        """
        if contact_name:
            letter_content = letter_content.replace("Madame, Monsieur,", f"Madame {contact_name},")
            letter_content = letter_content.replace("Cher recruteur,", f"Cher {contact_name},")
        
        if company_details and 'company_values' in company_details:
            # Ajouter une phrase sur les valeurs de l'entreprise
            values = company_details['company_values']
            if values:
                values_phrase = f"Je suis particulièrement attiré(e) par votre engagement envers {', '.join(values[:-1])} et {values[-1]}."
                
                # Insérer après la première phrase
                lines = letter_content.split('\n')
                if len(lines) > 1:
                    lines[1] = lines[1] + " " + values_phrase
                    letter_content = '\n'.join(lines)
        
        return letter_content