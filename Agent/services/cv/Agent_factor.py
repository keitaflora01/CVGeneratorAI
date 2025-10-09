from Agent.services.cv.Agent_factor_tool import CVAgentTool
from Agent.services.cv.creator import CVAgentCreator
from Agent.services.cv.logic import CVLogic
from Agent.services.cv.search_service import CVSearchService
from Agent.services.cv.Tools import CVTools
from Agent.services.Load_llm import llm_loader

class CVAgentFactory:
    @staticmethod
    def create_agent(document_id, user_data, job_description):
        """
        Crée et configure un agent CV complet
        """
        # Charger le modèle LLM
        llm = llm_loader.get_llm()
        
        # Initialiser les composants
        search_service = CVSearchService()
        cv_tools = CVTools(llm)
        cv_logic = CVLogic(llm, cv_tools, search_service)
        cv_agent_tool = CVAgentTool(llm, cv_logic)
        
        # Créer l'agent
        agent_creator = CVAgentCreator()
        agent = agent_creator.create_agent(
            document_id=document_id,
            user_data=user_data,
            job_description=job_description,
            cv_tools=cv_tools,
            cv_logic=cv_logic,
            cv_agent_tool=cv_agent_tool
        )
        
        return agent