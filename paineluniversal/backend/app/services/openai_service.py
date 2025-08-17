"""
Serviço de integração com OpenAI
Sistema Universal de Gestão de Eventos
"""

import openai
import asyncio
from typing import Optional, Dict, Any, List
from ..core.openai_config import openai_config

class OpenAIService:
    """Serviço para integração com OpenAI API"""
    
    def __init__(self):
        # Configurar a chave da API
        openai.api_key = openai_config.get_api_key()
    
    async def generate_text(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Gerar texto usando GPT
        
        Args:
            prompt: Texto de entrada
            max_tokens: Máximo de tokens (padrão: configuração)
            temperature: Criatividade do modelo (padrão: configuração)
            model: Modelo a usar (padrão: configuração)
            
        Returns:
            Texto gerado pela IA
        """
        try:
            response = await openai.ChatCompletion.acreate(
                model=model or openai_config.get_model(),
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens or openai_config.get_max_tokens(),
                temperature=temperature or openai_config.get_temperature(),
                timeout=openai_config.TIMEOUT
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Erro ao gerar texto com OpenAI: {str(e)}")
            return "Erro ao processar solicitação de IA"
    
    async def generate_event_description(
        self, 
        event_name: str, 
        event_type: str, 
        details: Optional[str] = None
    ) -> str:
        """
        Gerar descrição para um evento usando IA
        
        Args:
            event_name: Nome do evento
            event_type: Tipo do evento
            details: Detalhes adicionais
            
        Returns:
            Descrição gerada
        """
        prompt = f"""
        Crie uma descrição atrativa e profissional para um evento com as seguintes informações:
        
        Nome: {event_name}
        Tipo: {event_type}
        """
        
        if details:
            prompt += f"\nDetalhes adicionais: {details}"
        
        prompt += """
        
        A descrição deve ser:
        - Atrativa e envolvente
        - Profissional
        - Entre 2-3 parágrafos
        - Focada nos benefícios para os participantes
        - Em português brasileiro
        """
        
        return await self.generate_text(prompt, max_tokens=300)
    
    async def generate_marketing_copy(
        self, 
        event_name: str, 
        target_audience: str,
        key_benefits: List[str]
    ) -> str:
        """
        Gerar copy de marketing para um evento
        
        Args:
            event_name: Nome do evento
            target_audience: Público-alvo
            key_benefits: Benefícios principais
            
        Returns:
            Copy de marketing
        """
        benefits_text = "\n".join([f"- {benefit}" for benefit in key_benefits])
        
        prompt = f"""
        Crie um texto de marketing persuasivo para o evento "{event_name}".
        
        Público-alvo: {target_audience}
        
        Benefícios principais:
        {benefits_text}
        
        O texto deve:
        - Ser persuasivo e chamativo
        - Incluir call-to-action
        - Destacar os benefícios
        - Ser adequado para redes sociais
        - Máximo de 2 parágrafos
        - Em português brasileiro
        """
        
        return await self.generate_text(prompt, max_tokens=250)
    
    async def analyze_event_feedback(
        self, 
        feedback_list: List[str]
    ) -> Dict[str, Any]:
        """
        Analisar feedback de eventos usando IA
        
        Args:
            feedback_list: Lista de feedbacks dos participantes
            
        Returns:
            Análise do feedback
        """
        feedbacks_text = "\n".join([f"- {feedback}" for feedback in feedback_list])
        
        prompt = f"""
        Analise os seguintes feedbacks de um evento e forneça:
        
        1. Sentimento geral (positivo/neutro/negativo)
        2. Principais pontos positivos (máximo 3)
        3. Principais pontos de melhoria (máximo 3)
        4. Score geral de 1-10
        5. Recomendações para próximos eventos
        
        Feedbacks:
        {feedbacks_text}
        
        Formate a resposta de forma estruturada e objetiva.
        """
        
        analysis = await self.generate_text(prompt, max_tokens=400)
        
        return {
            "analysis": analysis,
            "total_feedbacks": len(feedback_list),
            "generated_at": "now"
        }
    
    async def suggest_event_improvements(
        self, 
        event_type: str,
        current_features: List[str],
        target_audience: str
    ) -> List[str]:
        """
        Sugerir melhorias para eventos
        
        Args:
            event_type: Tipo do evento
            current_features: Recursos atuais
            target_audience: Público-alvo
            
        Returns:
            Lista de sugestões
        """
        features_text = "\n".join([f"- {feature}" for feature in current_features])
        
        prompt = f"""
        Sugira 5 melhorias inovadoras para um evento do tipo "{event_type}" 
        direcionado para "{target_audience}".
        
        Recursos atuais:
        {features_text}
        
        As sugestões devem ser:
        - Práticas e viáveis
        - Inovadoras
        - Focadas na experiência do participante
        - Específicas e detalhadas
        
        Liste apenas as 5 sugestões, uma por linha, começando com "1.", "2.", etc.
        """
        
        suggestions_text = await self.generate_text(prompt, max_tokens=300)
        
        # Processar as sugestões em lista
        suggestions = []
        for line in suggestions_text.split('\n'):
            if line.strip() and any(line.strip().startswith(f"{i}.") for i in range(1, 6)):
                suggestions.append(line.strip())
        
        return suggestions

# Instância global do serviço
openai_service = OpenAIService()
