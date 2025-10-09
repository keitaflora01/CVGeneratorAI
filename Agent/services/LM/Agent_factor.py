from Agent.services.LM.Agent_factor_tool import LMAgentTool
from Agent.services.LM.creator import LMAgentCreator
from Agent.services.LM.logic import LMLogic
from Agent.services.LM.search_service import LMSearchService
from Agent.services.LM.Tools import LMTools
from Agent.services.Load_llm import llm_loader

class LMAgentFactory:
    @staticmethod
    def create_agent(document_id, user_data, job_description, cv_content=None):
        """
        Crée et configure un agent Lettre de Motivation complet
        """
        # Charger le modèle LLM
        llm = llm_loader.get_llm()
        
        # Initialiser les composants
        search_service = LMSearchService()
        lm_tools = LMTools(llm)
        lm_logic = LMLogic(llm, lm_tools, search_service)
        lm_agent_tool = LMAgentTool(llm, lm_logic)
        
        # Créer l'agent
        agent_creator = LMAgentCreator()
        agent = agent_creator.create_agent(
            document_id=document_id,
            user_data=user_data,
            job_description=job_description,
            cv_content=cv_content,
            lm_tools=lm_tools,
            lm_logic=lm_logic,
            lm_agent_tool=lm_agent_tool
        )
        
        return agent