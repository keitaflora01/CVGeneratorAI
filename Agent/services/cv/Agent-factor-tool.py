from langchain.agents import Tool
from langchain.tools import BaseTool

class CVAgentTool(BaseTool):
    name = "CVGenerator"
    description = "Génère un CV personnalisé basé sur le profil utilisateur et la description de poste"
    
    def __init__(self, llm, cv_logic):
        super().__init__()
        self.llm = llm
        self.cv_logic = cv_logic
    
    def _run(self, user_data, job_description):
        """Génère un CV personnalisé"""
        try:
            # Analyser la description de poste
            job_analysis = self.cv_logic.analyze_job_description(job_description)
            
            # Adapter le profil utilisateur
            adapted_profile = self.cv_logic.adapt_profile_to_job(user_data, job_analysis)
            
            # Générer le CV
            cv_content = self.cv_logic.generate_cv_content(adapted_profile, job_analysis)
            
            return {
                "success": True,
                "cv_content": cv_content,
                "job_analysis": job_analysis,
                "adapted_profile": adapted_profile
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _arun(self, user_data, job_description):
        """Version asynchrone de la génération de CV"""
        # Implémentation asynchrone si nécessaire
        return self._run(user_data, job_description)