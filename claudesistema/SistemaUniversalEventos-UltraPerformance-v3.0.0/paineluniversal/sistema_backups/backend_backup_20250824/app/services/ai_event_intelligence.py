"""
AI-Powered Event Intelligence System
Sistema Universal de Gestão de Eventos - ULTRA-EXPERT

Módulo avançado de inteligência artificial para:
- Geração inteligente de conteúdo de eventos
- Sistema de recomendações baseado em ML
- Otimização automática de eventos
- Analytics preditivos para participação
- Personalização avançada de experiências
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
import openai
from openai import AsyncOpenAI
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import pandas as pd
import redis.asyncio as aioredis

from ..core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class EventInsight:
    """Estrutura para insights de eventos"""
    event_id: str
    insight_type: str
    confidence_score: float
    recommendations: List[str]
    predicted_metrics: Dict[str, float]
    generated_content: Optional[Dict[str, str]] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

@dataclass
class PersonalizationProfile:
    """Perfil de personalização do usuário"""
    user_id: str
    preferences: Dict[str, float]
    event_history: List[str]
    engagement_score: float
    predicted_interests: List[str]
    last_updated: str

class AIEventIntelligenceEngine:
    """
    Motor de Inteligência Artificial para Eventos
    
    Funcionalidades:
    1. Geração inteligente de conteúdo
    2. Sistema de recomendações ML
    3. Otimização automática de eventos
    4. Analytics preditivos
    5. Personalização avançada
    """
    
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.redis_client = None
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.recommendation_model = None
        self.user_profiles: Dict[str, PersonalizationProfile] = {}
        self.event_embeddings: Dict[str, np.ndarray] = {}
        
    async def initialize(self):
        """Inicializar o sistema de IA"""
        try:
            # Conectar ao Redis para cache
            self.redis_client = aioredis.from_url(
                settings.REDIS_URL or "redis://localhost:6379"
            )
            
            # Carregar modelos pré-treinados se existirem
            await self._load_existing_models()
            
            logger.info("✅ AI Event Intelligence Engine initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing AI Engine: {e}")
            raise
    
    async def _load_existing_models(self):
        """Carregar modelos existentes do cache"""
        try:
            if self.redis_client:
                # Carregar perfis de usuário
                user_profiles_data = await self.redis_client.get("ai:user_profiles")
                if user_profiles_data:
                    profiles_dict = json.loads(user_profiles_data)
                    for user_id, profile_data in profiles_dict.items():
                        self.user_profiles[user_id] = PersonalizationProfile(**profile_data)
                
                # Carregar embeddings de eventos
                embeddings_data = await self.redis_client.get("ai:event_embeddings")
                if embeddings_data:
                    embeddings_dict = json.loads(embeddings_data)
                    for event_id, embedding_list in embeddings_dict.items():
                        self.event_embeddings[event_id] = np.array(embedding_list)
                        
        except Exception as e:
            logger.warning(f"⚠️ Could not load existing models: {e}")

    async def generate_intelligent_event_content(
        self, 
        event_data: Dict[str, Any],
        content_types: List[str] = None
    ) -> Dict[str, str]:
        """
        Gerar conteúdo inteligente para eventos usando GPT-4
        
        Args:
            event_data: Dados do evento
            content_types: Tipos de conteúdo a gerar
            
        Returns:
            Dict com conteúdo gerado por tipo
        """
        if content_types is None:
            content_types = ["description", "marketing_copy", "social_media", "email_subject", "hashtags"]
        
        generated_content = {}
        
        try:
            # Análise contextual do evento
            event_context = await self._analyze_event_context(event_data)
            
            for content_type in content_types:
                prompt = self._build_content_generation_prompt(
                    event_data, content_type, event_context
                )
                
                response = await self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system", 
                            "content": "Você é um especialista em marketing de eventos e copywriting, criando conteúdo altamente envolvente e convertível."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=settings.OPENAI_MAX_TOKENS,
                    temperature=settings.OPENAI_TEMPERATURE,
                    frequency_penalty=0.1,
                    presence_penalty=0.1
                )
                
                generated_content[content_type] = response.choices[0].message.content.strip()
                
                # Pequeno delay para respeitar rate limits
                await asyncio.sleep(0.1)
            
            # Cache do conteúdo gerado
            if self.redis_client:
                cache_key = f"ai:generated_content:{event_data.get('id', 'unknown')}"
                await self.redis_client.setex(
                    cache_key, 
                    3600 * 24,  # 24 horas
                    json.dumps(generated_content)
                )
            
            logger.info(f"✨ Generated intelligent content for event {event_data.get('name', 'Unknown')}")
            return generated_content
            
        except Exception as e:
            logger.error(f"❌ Error generating intelligent content: {e}")
            return self._fallback_content(event_data, content_types)

    def _build_content_generation_prompt(
        self, 
        event_data: Dict[str, Any], 
        content_type: str, 
        context: Dict[str, Any]
    ) -> str:
        """Construir prompt específico para tipo de conteúdo"""
        
        base_info = f"""
        INFORMAÇÕES DO EVENTO:
        Nome: {event_data.get('name', 'N/A')}
        Tipo: {event_data.get('type', 'N/A')}
        Data: {event_data.get('date', 'N/A')}
        Local: {event_data.get('location', 'N/A')}
        Público-alvo: {event_data.get('target_audience', 'Geral')}
        Capacidade: {event_data.get('capacity', 'N/A')}
        Preço: {event_data.get('price', 'Gratuito')}
        
        CONTEXTO INTELIGENTE:
        Categoria de público: {context.get('audience_category', 'Misto')}
        Nível de interesse estimado: {context.get('interest_level', 'Alto')}
        Tendências relevantes: {', '.join(context.get('trending_topics', []))}
        """
        
        prompts = {
            "description": f"""
            {base_info}
            
            Crie uma descrição ULTRA-ENVOLVENTE e profissional que:
            ✨ Capture a essência única do evento
            🎯 Fale diretamente com o público-alvo
            🔥 Use gatilhos mentais de urgência e exclusividade
            💎 Destaque benefícios transformadores
            📈 Inclua elementos de prova social
            
            Estrutura: 3-4 parágrafos, linguagem persuasiva mas profissional.
            """,
            
            "marketing_copy": f"""
            {base_info}
            
            Crie um copy de marketing IRRESISTÍVEL que:
            🚀 Comece com um hook poderoso
            💫 Use técnicas de storytelling
            ⚡ Inclua call-to-action magnético
            🎁 Crie senso de urgência/escassez
            🏆 Destaque transformação/resultado
            
            Formato: Ideal para landing page, máximo 200 palavras.
            """,
            
            "social_media": f"""
            {base_info}
            
            Crie posts para redes sociais que VIRALIZAM:
            📱 3 versões: Instagram, LinkedIn, Twitter
            🔥 Use emojis estratégicos
            #️⃣ Inclua hashtags relevantes
            📸 Sugira elementos visuais
            💬 Inclua pergunta para engajamento
            
            Cada post deve ser otimizado para sua plataforma.
            """,
            
            "email_subject": f"""
            {base_info}
            
            Crie 5 assuntos de email IRRESISTÍVEIS que garantam alta taxa de abertura:
            📧 Use curiosidade e urgência
            🎯 Personalize para o público
            ⚡ Máximo 50 caracteres
            🔥 Evite spam words
            ✨ Seja específico e benefício-focado
            
            Ordene por potencial de conversão.
            """,
            
            "hashtags": f"""
            {base_info}
            
            Crie estratégia completa de hashtags:
            🏷️ 10 hashtags de nicho específico
            📈 5 hashtags populares (alta busca)
            🎯 3 hashtags de marca/evento
            🌟 2 hashtags trending atuais
            
            Inclua volume estimado de busca e estratégia de uso.
            """
        }
        
        return prompts.get(content_type, prompts["description"])

    async def _analyze_event_context(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisar contexto inteligente do evento"""
        
        # Análise básica do tipo de evento
        event_type = event_data.get('type', '').lower()
        
        # Categorização de público
        audience_categories = {
            'workshop': 'Profissionais em busca de conhecimento',
            'conference': 'Executivos e especialistas',
            'networking': 'Empreendedores e profissionais',
            'concert': 'Jovens e entusiastas musicais',
            'seminar': 'Estudantes e profissionais',
            'party': 'Jovens adultos sociais'
        }
        
        audience_category = audience_categories.get(event_type, 'Público geral')
        
        # Tópicos trending simulados (em produção, integraria com APIs de trend)
        trending_topics = [
            "Inteligência Artificial",
            "Sustentabilidade",
            "Networking Digital",
            "Inovação",
            "Transformação Digital"
        ]
        
        return {
            'audience_category': audience_category,
            'interest_level': 'Alto',
            'trending_topics': trending_topics[:3]
        }

    async def build_recommendation_system(
        self, 
        events_data: List[Dict[str, Any]], 
        user_interactions: List[Dict[str, Any]]
    ) -> None:
        """
        Construir sistema de recomendações baseado em Machine Learning
        
        Args:
            events_data: Lista de dados de eventos
            user_interactions: Lista de interações dos usuários
        """
        try:
            # Criar embeddings dos eventos
            event_texts = []
            event_ids = []
            
            for event in events_data:
                # Combinar features textuais do evento
                text_features = [
                    event.get('name', ''),
                    event.get('description', ''),
                    event.get('type', ''),
                    event.get('category', ''),
                    ' '.join(event.get('tags', []))
                ]
                combined_text = ' '.join(filter(None, text_features))
                event_texts.append(combined_text)
                event_ids.append(event.get('id'))
            
            # Criar matriz TF-IDF
            if event_texts:
                tfidf_matrix = self.tfidf_vectorizer.fit_transform(event_texts)
                
                # Armazenar embeddings
                for i, event_id in enumerate(event_ids):
                    self.event_embeddings[event_id] = tfidf_matrix[i].toarray().flatten()
            
            # Construir perfis de usuários
            await self._build_user_profiles(user_interactions, events_data)
            
            # Treinar modelo de clustering para segmentação
            if len(events_data) > 5:
                embeddings_matrix = np.array(list(self.event_embeddings.values()))
                n_clusters = min(5, len(events_data) // 2)
                self.recommendation_model = KMeans(n_clusters=n_clusters, random_state=42)
                self.recommendation_model.fit(embeddings_matrix)
            
            # Cache dos modelos
            await self._cache_models()
            
            logger.info(f"🤖 Recommendation system built with {len(events_data)} events")
            
        except Exception as e:
            logger.error(f"❌ Error building recommendation system: {e}")

    async def _build_user_profiles(
        self, 
        user_interactions: List[Dict[str, Any]], 
        events_data: List[Dict[str, Any]]
    ) -> None:
        """Construir perfis inteligentes de usuários"""
        
        events_dict = {event['id']: event for event in events_data}
        user_data = {}
        
        # Agregar interações por usuário
        for interaction in user_interactions:
            user_id = interaction.get('user_id')
            if not user_id:
                continue
                
            if user_id not in user_data:
                user_data[user_id] = {
                    'events_attended': [],
                    'event_types': [],
                    'ratings': [],
                    'total_interactions': 0
                }
            
            event_id = interaction.get('event_id')
            if event_id in events_dict:
                event = events_dict[event_id]
                user_data[user_id]['events_attended'].append(event_id)
                user_data[user_id]['event_types'].append(event.get('type', ''))
                user_data[user_id]['ratings'].append(interaction.get('rating', 5))
                user_data[user_id]['total_interactions'] += 1
        
        # Criar perfis de personalização
        for user_id, data in user_data.items():
            # Calcular preferências por tipo de evento
            type_counts = {}
            for event_type in data['event_types']:
                type_counts[event_type] = type_counts.get(event_type, 0) + 1
            
            total_types = len(data['event_types'])
            preferences = {
                event_type: count / total_types 
                for event_type, count in type_counts.items()
            } if total_types > 0 else {}
            
            # Calcular score de engajamento
            avg_rating = np.mean(data['ratings']) if data['ratings'] else 3.0
            interaction_factor = min(data['total_interactions'] / 10, 1.0)
            engagement_score = (avg_rating / 5.0) * interaction_factor
            
            # Predizer interesses futuros
            predicted_interests = list(type_counts.keys())[:3]
            
            # Criar perfil
            profile = PersonalizationProfile(
                user_id=user_id,
                preferences=preferences,
                event_history=data['events_attended'],
                engagement_score=engagement_score,
                predicted_interests=predicted_interests,
                last_updated=datetime.utcnow().isoformat()
            )
            
            self.user_profiles[user_id] = profile

    async def get_personalized_recommendations(
        self, 
        user_id: str, 
        available_events: List[Dict[str, Any]],
        limit: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Obter recomendações personalizadas para usuário
        
        Args:
            user_id: ID do usuário
            available_events: Eventos disponíveis
            limit: Limite de recomendações
            
        Returns:
            Lista de (event_id, score) ordenada por relevância
        """
        try:
            user_profile = self.user_profiles.get(user_id)
            if not user_profile:
                # Retornar recomendações populares para usuários novos
                return await self._get_popular_events(available_events, limit)
            
            recommendations = []
            
            for event in available_events:
                event_id = event.get('id')
                
                # Skip eventos já participados
                if event_id in user_profile.event_history:
                    continue
                
                score = await self._calculate_recommendation_score(user_profile, event)
                recommendations.append((event_id, score))
            
            # Ordenar por score e retornar top eventos
            recommendations.sort(key=lambda x: x[1], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"❌ Error getting personalized recommendations: {e}")
            return []

    async def _calculate_recommendation_score(
        self, 
        user_profile: PersonalizationProfile, 
        event: Dict[str, Any]
    ) -> float:
        """Calcular score de recomendação usando múltiplos fatores"""
        
        score = 0.0
        
        # Fator 1: Preferência por tipo de evento (40% do peso)
        event_type = event.get('type', '').lower()
        type_preference = user_profile.preferences.get(event_type, 0)
        score += type_preference * 0.4
        
        # Fator 2: Similaridade semântica com eventos passados (30% do peso)
        event_id = event.get('id')
        if event_id in self.event_embeddings:
            semantic_score = await self._calculate_semantic_similarity(
                user_profile, event_id
            )
            score += semantic_score * 0.3
        
        # Fator 3: Engajamento histórico do usuário (20% do peso)
        score += user_profile.engagement_score * 0.2
        
        # Fator 4: Popularidade e tendências do evento (10% do peso)
        popularity_score = await self._calculate_popularity_score(event)
        score += popularity_score * 0.1
        
        return min(score, 1.0)  # Normalizar entre 0 e 1

    async def _calculate_semantic_similarity(
        self, 
        user_profile: PersonalizationProfile, 
        event_id: str
    ) -> float:
        """Calcular similaridade semântica com eventos do histórico"""
        
        if not user_profile.event_history or event_id not in self.event_embeddings:
            return 0.0
        
        target_embedding = self.event_embeddings[event_id]
        similarities = []
        
        for past_event_id in user_profile.event_history[-5:]:  # Últimos 5 eventos
            if past_event_id in self.event_embeddings:
                past_embedding = self.event_embeddings[past_event_id]
                similarity = cosine_similarity([target_embedding], [past_embedding])[0][0]
                similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.0

    async def _calculate_popularity_score(self, event: Dict[str, Any]) -> float:
        """Calcular score de popularidade do evento"""
        
        # Fatores de popularidade simulados (em produção, usar dados reais)
        capacity = event.get('capacity', 100)
        registered = event.get('registered_count', 0)
        
        # Taxa de ocupação
        occupancy_rate = registered / max(capacity, 1)
        
        # Score baseado na ocupação (eventos com 50-80% são mais atraentes)
        if 0.5 <= occupancy_rate <= 0.8:
            return 1.0
        elif occupancy_rate < 0.5:
            return occupancy_rate * 2  # Linear até 50%
        else:
            return max(0.2, 2 - occupancy_rate)  # Decrescente após 80%

    async def _get_popular_events(
        self, 
        events: List[Dict[str, Any]], 
        limit: int
    ) -> List[Tuple[str, float]]:
        """Obter eventos populares para usuários novos"""
        
        popular_events = []
        
        for event in events:
            popularity_score = await self._calculate_popularity_score(event)
            popular_events.append((event.get('id'), popularity_score))
        
        popular_events.sort(key=lambda x: x[1], reverse=True)
        return popular_events[:limit]

    async def predict_event_success(
        self, 
        event_data: Dict[str, Any],
        historical_data: List[Dict[str, Any]] = None
    ) -> EventInsight:
        """
        Predizer sucesso de evento usando analytics preditivos
        
        Args:
            event_data: Dados do evento
            historical_data: Dados históricos similares
            
        Returns:
            Insights e predições
        """
        try:
            event_id = event_data.get('id', 'unknown')
            
            # Análise preditiva usando GPT-4
            prediction_prompt = self._build_prediction_prompt(event_data, historical_data)
            
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em analytics de eventos com capacidade de predição precisa baseada em dados."
                    },
                    {"role": "user", "content": prediction_prompt}
                ],
                max_tokens=800,
                temperature=0.3  # Baixa temperatura para predições mais precisas
            )
            
            prediction_text = response.choices[0].message.content
            
            # Extrair métricas preditas (simplificado)
            predicted_metrics = {
                "attendance_rate": 0.75,  # Em produção, extrair do texto da IA
                "satisfaction_score": 4.2,
                "engagement_level": 0.85,
                "revenue_projection": event_data.get('capacity', 100) * event_data.get('price', 0) * 0.75,
                "social_media_reach": event_data.get('capacity', 100) * 3
            }
            
            # Gerar recomendações específicas
            recommendations = await self._extract_recommendations_from_prediction(prediction_text)
            
            insight = EventInsight(
                event_id=event_id,
                insight_type="success_prediction",
                confidence_score=0.85,
                recommendations=recommendations,
                predicted_metrics=predicted_metrics
            )
            
            # Cache do insight
            if self.redis_client:
                cache_key = f"ai:insight:{event_id}"
                await self.redis_client.setex(
                    cache_key,
                    3600 * 6,  # 6 horas
                    json.dumps(asdict(insight))
                )
            
            logger.info(f"🔮 Generated success prediction for event {event_id}")
            return insight
            
        except Exception as e:
            logger.error(f"❌ Error predicting event success: {e}")
            return EventInsight(
                event_id=event_data.get('id', 'unknown'),
                insight_type="error",
                confidence_score=0.0,
                recommendations=["Erro na análise preditiva"],
                predicted_metrics={}
            )

    def _build_prediction_prompt(
        self, 
        event_data: Dict[str, Any], 
        historical_data: List[Dict[str, Any]] = None
    ) -> str:
        """Construir prompt para predição de sucesso"""
        
        prompt = f"""
        ANÁLISE PREDITIVA DE EVENTO
        
        DADOS DO EVENTO:
        Nome: {event_data.get('name')}
        Tipo: {event_data.get('type')}
        Data: {event_data.get('date')}
        Horário: {event_data.get('time')}
        Local: {event_data.get('location')}
        Capacidade: {event_data.get('capacity')}
        Preço: R$ {event_data.get('price', 0)}
        Público-alvo: {event_data.get('target_audience')}
        Categoria: {event_data.get('category')}
        
        ANÁLISE SOLICITADA:
        Com base nos dados fornecidos, forneça uma análise preditiva DETALHADA incluindo:
        
        1. PREDIÇÃO DE PARTICIPAÇÃO:
        - Taxa de ocupação esperada (%)
        - Número estimado de participantes
        - Fatores que influenciam a participação
        
        2. PREDIÇÃO DE SATISFAÇÃO:
        - Score de satisfação esperado (1-5)
        - Aspectos que podem gerar satisfação
        - Possíveis pontos de fricção
        
        3. PREDIÇÃO DE ENGAJAMENTO:
        - Nível de interação esperado
        - Potencial viral nas redes sociais
        - Probabilidade de recomendação
        
        4. PREDIÇÃO FINANCEIRA:
        - Receita estimada
        - ROI projetado
        - Custos críticos a considerar
        
        5. RECOMENDAÇÕES ESTRATÉGICAS:
        - 5 ações específicas para maximizar sucesso
        - Alertas e riscos a monitorar
        - Otimizações recomendadas
        
        Seja específico, use números quando possível e justifique suas predições.
        """
        
        if historical_data:
            prompt += f"\n\nDADOS HISTÓRICOS SIMILARES:\n"
            for i, hist_event in enumerate(historical_data[:3], 1):
                prompt += f"{i}. {hist_event.get('name')} - Participação: {hist_event.get('attendance_rate', 'N/A')}%, Satisfação: {hist_event.get('satisfaction', 'N/A')}\n"
        
        return prompt

    async def _extract_recommendations_from_prediction(self, prediction_text: str) -> List[str]:
        """Extrair recomendações do texto de predição"""
        
        recommendations = []
        lines = prediction_text.split('\n')
        
        in_recommendations = False
        for line in lines:
            line = line.strip()
            if 'recomendações' in line.lower() or 'ações' in line.lower():
                in_recommendations = True
                continue
            
            if in_recommendations and line:
                # Extrair recomendações numeradas ou com bullets
                if any(line.startswith(marker) for marker in ['1.', '2.', '3.', '4.', '5.', '-', '•']):
                    # Limpar marcadores
                    clean_rec = line
                    for marker in ['1.', '2.', '3.', '4.', '5.', '-', '•']:
                        clean_rec = clean_rec.replace(marker, '').strip()
                    
                    if clean_rec:
                        recommendations.append(clean_rec)
                
                # Parar se encontrar nova seção
                if line.isupper() or line.startswith('6.'):
                    break
        
        return recommendations[:5]  # Máximo 5 recomendações

    async def optimize_event_automatically(
        self, 
        event_id: str, 
        current_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Otimizar evento automaticamente baseado em métricas atuais
        
        Args:
            event_id: ID do evento
            current_metrics: Métricas atuais do evento
            
        Returns:
            Otimizações sugeridas e implementáveis
        """
        try:
            # Análise de performance atual
            performance_analysis = await self._analyze_current_performance(current_metrics)
            
            # Gerar otimizações usando IA
            optimization_prompt = f"""
            OTIMIZAÇÃO AUTOMÁTICA DE EVENTO
            
            ID do Evento: {event_id}
            
            MÉTRICAS ATUAIS:
            {json.dumps(current_metrics, indent=2)}
            
            ANÁLISE DE PERFORMANCE:
            {json.dumps(performance_analysis, indent=2)}
            
            Forneça otimizações AUTOMATIZÁVEIS específicas:
            
            1. OTIMIZAÇÕES DE PREÇO:
            - Ajustes de precificação dinâmica
            - Estratégias de desconto
            - Bundling de produtos
            
            2. OTIMIZAÇÕES DE MARKETING:
            - Ajustes em campanhas
            - Segmentação de público
            - Canais de divulgação
            
            3. OTIMIZAÇÕES DE EXPERIÊNCIA:
            - Melhorias na agenda
            - Recursos adicionais
            - Personalização
            
            4. OTIMIZAÇÕES OPERACIONAIS:
            - Ajustes de capacidade
            - Logística melhorada
            - Tecnologia adicional
            
            Para cada otimização, inclua:
            - Impacto esperado (alto/médio/baixo)
            - Facilidade de implementação (1-10)
            - Tempo de implementação
            - Métrica alvo a melhorar
            
            Formato: JSON estruturado para fácil parsing.
            """
            
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em otimização de eventos com foco em implementações automatizáveis e mensuráveis."
                    },
                    {"role": "user", "content": optimization_prompt}
                ],
                max_tokens=1000,
                temperature=0.4
            )
            
            optimization_text = response.choices[0].message.content
            
            # Processar otimizações (simplificado para demonstração)
            optimizations = {
                "pricing_optimizations": [
                    {
                        "action": "dynamic_pricing",
                        "description": "Implementar preços dinâmicos baseados na demanda",
                        "impact": "alto",
                        "implementation_ease": 8,
                        "target_metric": "revenue"
                    }
                ],
                "marketing_optimizations": [
                    {
                        "action": "audience_segmentation",
                        "description": "Segmentar campanhas por perfil de participante",
                        "impact": "médio",
                        "implementation_ease": 6,
                        "target_metric": "attendance_rate"
                    }
                ],
                "experience_optimizations": [
                    {
                        "action": "personalized_agenda",
                        "description": "Criar agendas personalizadas por interesse",
                        "impact": "alto",
                        "implementation_ease": 5,
                        "target_metric": "satisfaction_score"
                    }
                ],
                "operational_optimizations": [
                    {
                        "action": "capacity_adjustment",
                        "description": "Ajustar capacidade baseado na demanda predita",
                        "impact": "médio",
                        "implementation_ease": 9,
                        "target_metric": "occupancy_rate"
                    }
                ],
                "ai_generated_text": optimization_text,
                "timestamp": datetime.utcnow().isoformat(),
                "confidence_score": 0.8
            }
            
            logger.info(f"🔧 Generated automatic optimizations for event {event_id}")
            return optimizations
            
        except Exception as e:
            logger.error(f"❌ Error generating automatic optimizations: {e}")
            return {"error": str(e)}

    async def _analyze_current_performance(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Analisar performance atual do evento"""
        
        analysis = {
            "overall_score": 0.0,
            "strong_areas": [],
            "improvement_areas": [],
            "critical_issues": []
        }
        
        # Definir benchmarks
        benchmarks = {
            "attendance_rate": 0.8,
            "satisfaction_score": 4.0,
            "engagement_level": 0.7,
            "conversion_rate": 0.15,
            "revenue_per_participant": 100
        }
        
        scores = []
        for metric, value in metrics.items():
            if metric in benchmarks:
                benchmark = benchmarks[metric]
                score = min(value / benchmark, 1.2)  # Cap at 120% of benchmark
                scores.append(score)
                
                if score >= 1.1:
                    analysis["strong_areas"].append(f"{metric}: {value} (excelente)")
                elif score < 0.7:
                    analysis["improvement_areas"].append(f"{metric}: {value} (abaixo do esperado)")
                if score < 0.5:
                    analysis["critical_issues"].append(f"{metric}: {value} (crítico)")
        
        analysis["overall_score"] = np.mean(scores) if scores else 0.0
        
        return analysis

    async def _cache_models(self):
        """Cache dos modelos treinados"""
        try:
            if self.redis_client:
                # Cache perfis de usuário
                profiles_dict = {
                    user_id: asdict(profile) 
                    for user_id, profile in self.user_profiles.items()
                }
                await self.redis_client.setex(
                    "ai:user_profiles",
                    3600 * 24,  # 24 horas
                    json.dumps(profiles_dict)
                )
                
                # Cache embeddings de eventos
                embeddings_dict = {
                    event_id: embedding.tolist() 
                    for event_id, embedding in self.event_embeddings.items()
                }
                await self.redis_client.setex(
                    "ai:event_embeddings",
                    3600 * 24,  # 24 horas
                    json.dumps(embeddings_dict)
                )
                
        except Exception as e:
            logger.warning(f"⚠️ Could not cache models: {e}")

    def _fallback_content(
        self, 
        event_data: Dict[str, Any], 
        content_types: List[str]
    ) -> Dict[str, str]:
        """Conteúdo de fallback se IA falhar"""
        
        event_name = event_data.get('name', 'Evento Especial')
        
        fallback = {}
        for content_type in content_types:
            if content_type == "description":
                fallback[content_type] = f"Participe do {event_name}, um evento único que você não pode perder!"
            elif content_type == "marketing_copy":
                fallback[content_type] = f"🎉 {event_name} está chegando! Garante sua vaga agora!"
            elif content_type == "social_media":
                fallback[content_type] = f"📅 {event_name} - Não perca! #evento #imperdivel"
            elif content_type == "email_subject":
                fallback[content_type] = f"🎪 {event_name} - Últimas vagas!"
            elif content_type == "hashtags":
                fallback[content_type] = f"#{event_name.replace(' ', '')} #evento #networking"
            else:
                fallback[content_type] = f"Conteúdo sobre {event_name}"
        
        return fallback

    async def cleanup(self):
        """Limpeza de recursos"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            logger.info("🧹 AI Event Intelligence Engine cleanup completed")
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")

# Instância global do motor de IA
ai_intelligence_engine = AIEventIntelligenceEngine()