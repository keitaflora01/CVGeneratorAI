from Agent.models import Document, EtapeTraitement
from Agent.models.LM_Agent import LMAgent

class LMAgentCreator:
    def create_agent(self, document_id, user_data, job_description, cv_content, lm_tools, lm_logic, lm_agent_tool):
        """
        Crée et enregistre un agent Lettre de Motivation dans la base de données
        """
        try:
            # Récupérer le document
            document = Document.objects.get(id=document_id)
            
            # Créer l'agent LM
            lm_agent = LMAgent.objects.create(
                document=document,
                version="1.0",
                modele_utilise="gpt-4",
                parametres={
                    "temperature": 0.7,
                    "max_tokens": 1500,
                    "user_data_keys": list(user_data.keys()) if user_data else [],
                    "cv_provided": cv_content is not None
                }
            )
            
            # Créer les étapes de traitement
            etapes = [
                {"nom": "Analyse de l'entreprise", "ordre": 1},
                {"nom": "Identification des motivations", "ordre": 2},
                {"nom": "Rédaction de la lettre", "ordre": 3},
                {"nom": "Personnalisation", "ordre": 4},
                {"nom": "Validation finale", "ordre": 5},
            ]
            
            for etape_data in etapes:
                EtapeTraitement.objects.create(
                    document=document,
                    **etape_data
                )
            
            return {
                "agent": lm_agent,
                "document": document,
                "tools": lm_tools,
                "logic": lm_logic,
                "agent_tool": lm_agent_tool
            }
            
        except Exception as e:
            raise Exception(f"Erreur lors de la création de l'agent LM: {str(e)}")