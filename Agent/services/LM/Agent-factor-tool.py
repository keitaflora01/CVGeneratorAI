from langchain.tools import BaseTool

class LMAgentTool(BaseTool):
    name = "LMGenerator"
    description = "Génère une lettre de motivation personnalisée basée sur le profil utilisateur, la description de poste et le CV"
    
    def __init__(self, llm, lm_logic):
        super().__init__()
        self.llm = llm
        self.lm_logic = lm_logic
    
    def _run(self, user_data, job_description, cv_content=None):
        """Génère une lettre de motivation personnalisée"""
        try:
            # Analyser la description de poste et l'entreprise
            job_analysis = self.lm_logic.analyze_job_and_company(job_description)
            
            # Générer la lettre de motivation
            lm_content = self.lm_logic.generate_motivation_letter(
                user_data, job_analysis, cv_content
            )
            
            return {
                "success": True,
                "lm_content": lm_content,
                "job_analysis": job_analysis
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _arun(self, user_data, job_description, cv_content=None):
        """Version asynchrone"""
        return self._run(user_data, job_description, cv_content)