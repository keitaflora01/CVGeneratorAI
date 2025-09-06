import os
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from django.conf import settings

class LLMLoader:
    _instance = None
    _llm_cache = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMLoader, cls).__new__(cls)
        return cls._instance
    
    def get_llm(self, model_name="gpt-4", temperature=0.7, max_tokens=2000):
        cache_key = f"{model_name}_{temperature}_{max_tokens}"
        
        if cache_key not in self._llm_cache:
            try:
                # Configuration pour OpenAI
                llm = ChatOpenAI(
                    model_name=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    openai_api_key=settings.OPENAI_API_KEY
                )
                self._llm_cache[cache_key] = llm
            except Exception as e:
                raise Exception(f"Erreur lors du chargement du modèle {model_name}: {str(e)}")
        
        return self._llm_cache[cache_key]
    
    def get_alternative_llm(self, model_name="gpt-3.5-turbo", temperature=0.7, max_tokens=2000):
        """Fournit un modèle alternatif en cas de problème avec le modèle principal"""
        return self.get_llm(model_name, temperature, max_tokens)

# Instance singleton
llm_loader = LLMLoader()