from langchain.tools import BaseTool
import json

class CVTools(BaseTool):
    name = "CVTools"
    description = "Collection d'outils pour la génération et l'optimisation de CV"
    
    def __init__(self, llm):
        super().__init__()
        self.llm = llm
    
    def _run(self, action, **kwargs):
        """Exécute différentes actions liées aux CV"""
        if action == "extract_skills":
            return self.extract_skills_from_text(kwargs.get('text', ''))
        elif action == "match_skills":
            return self.match_skills(
                kwargs.get('job_skills', []),
                kwargs.get('candidate_skills', [])
            )
        elif action == "generate_summary":
            return self.generate_professional_summary(
                kwargs.get('experiences', []),
                kwargs.get('target_role', '')
            )
        else:
            return {"error": "Action non supportée"}
    
    def extract_skills_from_text(self, text):
        """Extrait les compétences d'un texte"""
        # Implémentation simplifiée - utiliser NLP dans une version réelle
        skills_keywords = [
            "Python", "JavaScript", "React", "Node.js", "SQL", "NoSQL", "AWS",
            "Docker", "Kubernetes", "Machine Learning", "AI", "Data Analysis",
            "Project Management", "Agile", "Scrum", "Communication", "Leadership"
        ]
        
        found_skills = []
        for skill in skills_keywords:
            if skill.lower() in text.lower():
                found_skills.append(skill)
        
        return found_skills
    
    def match_skills(self, job_skills, candidate_skills):
        """Calcule la correspondance entre les compétences requises et celles du candidat"""
        match_percentage = 0
        missing_skills = []
        
        if job_skills:
            matched_skills = [skill for skill in job_skills if skill in candidate_skills]
            match_percentage = (len(matched_skills) / len(job_skills)) * 100
            missing_skills = [skill for skill in job_skills if skill not in candidate_skills]
        
        return {
            "match_percentage": round(match_percentage, 2),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills
        }
    
    def generate_professional_summary(self, experiences, target_role):
        """Génère un résumé professionnel personnalisé"""
        prompt = f"""
        Génère un résumé professionnel concis (3-4 phrases) pour un candidat postulant à un poste de {target_role}.
        
        Expériences: {experiences}
        
        Le résumé doit:
        1. Mentionner les années d'expérience pertinentes
        2. Mettre en avant les réalisations principales
        3. Exprimer l'enthousiasme pour le poste visé
        4. Utiliser un ton professionnel et confiant
        """
        
        # Utiliser le LLM pour générer le résumé
        from langchain import PromptTemplate
        from langchain.chains import LLMChain
        
        template = PromptTemplate(
            input_variables=["experiences", "target_role"],
            template=prompt
        )
        
        chain = LLMChain(llm=self.llm, prompt=template)
        return chain.run(experiences=experiences, target_role=target_role)
    
    async def _arun(self, action, **kwargs):
        """Version asynchrone"""
        return self._run(action, **kwargs)