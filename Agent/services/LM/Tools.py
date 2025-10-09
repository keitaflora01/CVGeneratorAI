from langchain.tools import BaseTool
from langchain import PromptTemplate
from langchain.chains import LLMChain


class LMTools(BaseTool):
    name = "LMTools"
    description = "Collection d'outils pour la génération et l'optimisation de lettres de motivation"
    
    def __init__(self, llm):
        super().__init__()
        self.llm = llm
    
    def _run(self, action, **kwargs):
        """Exécute différentes actions liées aux lettres de motivation"""
        if action == "analyze_tone":
            return self.analyze_writing_tone(kwargs.get('text', ''))
        elif action == "extract_achievements":
            return self.extract_achievements_from_cv(kwargs.get('cv_content', ''))
        elif action == "generate_opening":
            return self.generate_compelling_opening(
                kwargs.get('company_name', ''),
                kwargs.get('job_title', '')
            )
        else:
            return {"error": "Action non supportée"}
    
    def analyze_writing_tone(self, text):
        """Analyse le ton d'un texte"""
        prompt = f"""
        Analyse le ton de ce texte et catégorise-le:
        
        Texte: {text}
        
        Catégories possibles: formel, enthousiaste, confident, modeste, passionné, professionnel
        
        Retourne un JSON avec:
        - primary_tone: le ton principal
        - secondary_tones: autres tons détectés
        - confidence: niveau de confiance (0-100)
        - suggestions: suggestions d'amélioration si nécessaire
        """
        
        # Utiliser le LLM pour analyser le ton
        from langchain import PromptTemplate
        from langchain.chains import LLMChain
        
        template = PromptTemplate(
            input_variables=["text"],
            template=prompt
        )
        
        chain = LLMChain(llm=self.llm, prompt=template)
        result = chain.run(text=text)
        
        # Essayer de parser le JSON
        try:
            import json
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {
            "primary_tone": "professionnel",
            "secondary_tones": ["formel"],
            "confidence": 75,
            "suggestions": "Le ton semble approprié pour une lettre de motivation professionnelle."
        }
    
    def extract_achievements_from_cv(self, cv_content):
        """Extrait les réalisations principales d'un CV"""
        prompt = f"""
        Extrait les réalisations et accomplissements les plus importants de ce CV:
        
        {cv_content}
        
        Retourne une liste concise des 3-5 réalisations les plus impressionnantes.
        Format: liste à puces avec une phrase par réalisation.
        """
        
        from langchain import PromptTemplate
        from langchain.chains import LLMChain
        
        template = PromptTemplate(
            input_variables=["cv_content"],
            template=prompt
        )
        
        chain = LLMChain(llm=self.llm, prompt=template)
        return chain.run(cv_content=cv_content)
    
    def generate_compelling_opening(self, company_name, job_title):
        """Génère une introduction percutante pour une lettre de motivation"""
        prompt = f"""
        Génère une introduction accrocheuse pour une lettre de motivation adressée à {company_name} pour le poste de {job_title}.
        
        L'introduction doit:
        1. Attirer l'attention du recruteur
        2. Mentionner l'enthousiasme pour l'entreprise et le poste
        3. Introduire brièvement le candidat
        4. Faire environ 2-3 phrases
        
        Ton: professionnel mais enthousiaste.
        """
        

        
        template = PromptTemplate(
            input_variables=["company_name", "job_title"],
            template=prompt
        )
        
        chain = LLMChain(llm=self.llm, prompt=template)
        return chain.run(company_name=company_name, job_title=job_title)
    
    async def _arun(self, action, **kwargs):
        """Version asynchrone"""
        return self._run(action, **kwargs)