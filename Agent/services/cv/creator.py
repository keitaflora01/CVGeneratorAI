from Agent.models import Document, EtapeTraitement
from Agent.models.Agent import CVAgent

class CVAgentCreator:
    def create_agent(self, document_id, user_data, job_description, cv_tools, cv_logic, cv_agent_tool):
        """
        Crée et enregistre un agent CV dans la base de données
        """
        try:
            # Récupérer le document
            document = Document.objects.get(id=document_id)
            
            # Créer l'agent CV
            cv_agent = CVAgent.objects.create(
                document=document,
                version="1.0",
                modele_utilise="gpt-4",
                parametres={
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "user_data_keys": list(user_data.keys()) if user_data else []
                }
            )
            
            # Créer les étapes de traitement
            etapes = [
                {"nom": "Analyse de l'offre d'emploi", "ordre": 1},
                {"nom": "Adaptation du profil", "ordre": 2},
                {"nom": "Génération du contenu", "ordre": 3},
                {"nom": "Optimisation SEO", "ordre": 4},
                {"nom": "Validation finale", "ordre": 5},
            ]
            
            for etape_data in etapes:
                EtapeTraitement.objects.create(
                    document=document,
                    **etape_data
                )
            
            return {
                "agent": cv_agent,
                "document": document,
                "tools": cv_tools,
                "logic": cv_logic,
                "agent_tool": cv_agent_tool
            }
            
        except Exception as e:
            raise Exception(f"Erreur lors de la création de l'agent CV: {str(e)}")