"""
Advanced RBAC System - Sprint 5
Sistema Universal de Gestão de Eventos

Sistema completo de controle de acesso baseado em papéis:
- Roles hierárquicos
- Permissions granulares
- Resource-based permissions
- Dynamic role assignment
- Permission inheritance
- Audit logging
- Context-aware access control
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging

from ..models import Usuario, TipoUsuario

logger = logging.getLogger(__name__)


class Permission(str, Enum):
    """Permissões granulares do sistema"""
    
    # Gestão de Eventos
    EVENT_CREATE = "event.create"
    EVENT_READ = "event.read"
    EVENT_UPDATE = "event.update"
    EVENT_DELETE = "event.delete"
    EVENT_MANAGE_ALL = "event.manage_all"
    EVENT_PUBLISH = "event.publish"
    EVENT_CLONE = "event.clone"
    
    # Gestão de Participantes
    PARTICIPANT_CREATE = "participant.create"
    PARTICIPANT_READ = "participant.read"
    PARTICIPANT_UPDATE = "participant.update"
    PARTICIPANT_DELETE = "participant.delete"
    PARTICIPANT_IMPORT = "participant.import"
    PARTICIPANT_EXPORT = "participant.export"
    
    # Check-in
    CHECKIN_PERFORM = "checkin.perform"
    CHECKIN_MANUAL = "checkin.manual"
    CHECKIN_BULK = "checkin.bulk"
    CHECKIN_VIEW_LOGS = "checkin.view_logs"
    CHECKIN_MANAGE_DEVICES = "checkin.manage_devices"
    
    # PDV e Vendas
    PDV_SELL = "pdv.sell"
    PDV_REFUND = "pdv.refund"
    PDV_VIEW_REPORTS = "pdv.view_reports"
    PDV_MANAGE_INVENTORY = "pdv.manage_inventory"
    PDV_CONFIGURE = "pdv.configure"
    
    # Gamificação
    GAMIFICATION_VIEW = "gamification.view"
    GAMIFICATION_MANAGE = "gamification.manage"
    GAMIFICATION_AWARD_POINTS = "gamification.award_points"
    GAMIFICATION_CREATE_ACHIEVEMENTS = "gamification.create_achievements"
    
    # Relatórios e Analytics
    REPORTS_VIEW_BASIC = "reports.view_basic"
    REPORTS_VIEW_ADVANCED = "reports.view_advanced"
    REPORTS_EXPORT = "reports.export"
    ANALYTICS_VIEW = "analytics.view"
    ANALYTICS_ADMIN = "analytics.admin"
    
    # Usuários e Empresas
    USER_CREATE = "user.create"
    USER_READ = "user.read"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"
    USER_MANAGE_ROLES = "user.manage_roles"
    
    # Sistema
    SYSTEM_ADMIN = "system.admin"
    SYSTEM_MONITORING = "system.monitoring"
    SYSTEM_BACKUP = "system.backup"
    SYSTEM_CONFIGURATION = "system.configuration"
    
    # Empresas (Multi-tenant)
    COMPANY_MANAGE = "company.manage"
    COMPANY_VIEW_ALL = "company.view_all"
    COMPANY_BILLING = "company.billing"


class Role(str, Enum):
    """Papéis hierárquicos do sistema"""
    
    # Roles de Sistema
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    
    # Roles de Empresa
    COMPANY_OWNER = "company_owner"
    COMPANY_ADMIN = "company_admin"
    COMPANY_MANAGER = "company_manager"
    
    # Roles de Evento
    EVENT_ORGANIZER = "event_organizer"
    EVENT_MANAGER = "event_manager"
    EVENT_STAFF = "event_staff"
    
    # Roles Operacionais
    CHECKIN_OPERATOR = "checkin_operator"
    PDV_OPERATOR = "pdv_operator"
    SUPPORT_AGENT = "support_agent"
    
    # Roles de Visualização
    ANALYST = "analyst"
    VIEWER = "viewer"
    
    # Roles Especiais
    API_CLIENT = "api_client"
    MOBILE_APP = "mobile_app"


class ResourceType(str, Enum):
    """Tipos de recursos para controle granular"""
    EVENT = "event"
    PARTICIPANT = "participant"
    COMPANY = "company"
    USER = "user"
    REPORT = "report"
    DEVICE = "device"


class AccessContext:
    """Contexto de acesso para decisões de permissão"""
    
    def __init__(self, 
                 user_id: str,
                 company_id: Optional[str] = None,
                 event_id: Optional[str] = None,
                 resource_type: Optional[ResourceType] = None,
                 resource_id: Optional[str] = None,
                 ip_address: Optional[str] = None,
                 user_agent: Optional[str] = None):
        self.user_id = user_id
        self.company_id = company_id
        self.event_id = event_id
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.timestamp = datetime.utcnow()


class RBACSystem:
    """Sistema avançado de controle de acesso baseado em papéis"""
    
    def __init__(self):
        # Definição de permissões por papel
        self.role_permissions = {
            Role.SUPER_ADMIN: {
                Permission.SYSTEM_ADMIN,
                Permission.SYSTEM_MONITORING,
                Permission.SYSTEM_BACKUP,
                Permission.SYSTEM_CONFIGURATION,
                Permission.COMPANY_MANAGE,
                Permission.COMPANY_VIEW_ALL,
                Permission.COMPANY_BILLING,
                Permission.USER_MANAGE_ROLES,
                # Incluir todas as outras permissões
                *[p for p in Permission]
            },
            
            Role.ADMIN: {
                Permission.SYSTEM_MONITORING,
                Permission.COMPANY_MANAGE,
                Permission.USER_CREATE,
                Permission.USER_READ,
                Permission.USER_UPDATE,
                Permission.USER_DELETE,
                Permission.EVENT_MANAGE_ALL,
                Permission.ANALYTICS_ADMIN,
                Permission.REPORTS_VIEW_ADVANCED,
                Permission.REPORTS_EXPORT,
                Permission.GAMIFICATION_MANAGE,
                Permission.PDV_CONFIGURE,
                Permission.CHECKIN_MANAGE_DEVICES
            },
            
            Role.COMPANY_OWNER: {
                Permission.COMPANY_MANAGE,
                Permission.USER_CREATE,
                Permission.USER_READ,
                Permission.USER_UPDATE,
                Permission.USER_MANAGE_ROLES,
                Permission.EVENT_CREATE,
                Permission.EVENT_READ,
                Permission.EVENT_UPDATE,
                Permission.EVENT_DELETE,
                Permission.EVENT_PUBLISH,
                Permission.REPORTS_VIEW_ADVANCED,
                Permission.ANALYTICS_VIEW,
                Permission.GAMIFICATION_MANAGE,
                Permission.PDV_CONFIGURE
            },
            
            Role.COMPANY_ADMIN: {
                Permission.USER_CREATE,
                Permission.USER_READ,
                Permission.USER_UPDATE,
                Permission.EVENT_CREATE,
                Permission.EVENT_READ,
                Permission.EVENT_UPDATE,
                Permission.EVENT_DELETE,
                Permission.EVENT_PUBLISH,
                Permission.PARTICIPANT_CREATE,
                Permission.PARTICIPANT_READ,
                Permission.PARTICIPANT_UPDATE,
                Permission.PARTICIPANT_DELETE,
                Permission.PARTICIPANT_IMPORT,
                Permission.PARTICIPANT_EXPORT,
                Permission.REPORTS_VIEW_ADVANCED,
                Permission.ANALYTICS_VIEW,
                Permission.PDV_CONFIGURE
            },
            
            Role.EVENT_ORGANIZER: {
                Permission.EVENT_CREATE,
                Permission.EVENT_READ,
                Permission.EVENT_UPDATE,
                Permission.EVENT_CLONE,
                Permission.PARTICIPANT_CREATE,
                Permission.PARTICIPANT_READ,
                Permission.PARTICIPANT_UPDATE,
                Permission.PARTICIPANT_IMPORT,
                Permission.PARTICIPANT_EXPORT,
                Permission.CHECKIN_PERFORM,
                Permission.CHECKIN_VIEW_LOGS,
                Permission.PDV_SELL,
                Permission.PDV_VIEW_REPORTS,
                Permission.REPORTS_VIEW_BASIC,
                Permission.ANALYTICS_VIEW,
                Permission.GAMIFICATION_VIEW
            },
            
            Role.EVENT_MANAGER: {
                Permission.EVENT_READ,
                Permission.EVENT_UPDATE,
                Permission.PARTICIPANT_READ,
                Permission.PARTICIPANT_UPDATE,
                Permission.CHECKIN_PERFORM,
                Permission.CHECKIN_MANUAL,
                Permission.PDV_SELL,
                Permission.PDV_REFUND,
                Permission.REPORTS_VIEW_BASIC,
                Permission.GAMIFICATION_VIEW
            },
            
            Role.EVENT_STAFF: {
                Permission.EVENT_READ,
                Permission.PARTICIPANT_READ,
                Permission.CHECKIN_PERFORM,
                Permission.PDV_SELL,
                Permission.GAMIFICATION_VIEW
            },
            
            Role.CHECKIN_OPERATOR: {
                Permission.EVENT_READ,
                Permission.PARTICIPANT_READ,
                Permission.CHECKIN_PERFORM,
                Permission.CHECKIN_MANUAL,
                Permission.CHECKIN_BULK,
                Permission.CHECKIN_VIEW_LOGS
            },
            
            Role.PDV_OPERATOR: {
                Permission.EVENT_READ,
                Permission.PARTICIPANT_READ,
                Permission.PDV_SELL,
                Permission.PDV_REFUND,
                Permission.PDV_VIEW_REPORTS
            },
            
            Role.ANALYST: {
                Permission.EVENT_READ,
                Permission.PARTICIPANT_READ,
                Permission.REPORTS_VIEW_ADVANCED,
                Permission.REPORTS_EXPORT,
                Permission.ANALYTICS_VIEW
            },
            
            Role.VIEWER: {
                Permission.EVENT_READ,
                Permission.PARTICIPANT_READ,
                Permission.REPORTS_VIEW_BASIC,
                Permission.GAMIFICATION_VIEW
            },
            
            Role.API_CLIENT: {
                Permission.EVENT_READ,
                Permission.PARTICIPANT_READ,
                Permission.CHECKIN_PERFORM,
                Permission.PDV_SELL
            },
            
            Role.MOBILE_APP: {
                Permission.EVENT_READ,
                Permission.PARTICIPANT_READ,
                Permission.CHECKIN_PERFORM,
                Permission.GAMIFICATION_VIEW
            }
        }
        
        # Hierarquia de papéis (papel superior herda permissões dos inferiores)
        self.role_hierarchy = {
            Role.SUPER_ADMIN: [Role.ADMIN],
            Role.ADMIN: [Role.COMPANY_ADMIN, Role.ANALYST],
            Role.COMPANY_OWNER: [Role.COMPANY_ADMIN],
            Role.COMPANY_ADMIN: [Role.EVENT_ORGANIZER, Role.COMPANY_MANAGER],
            Role.COMPANY_MANAGER: [Role.EVENT_MANAGER],
            Role.EVENT_ORGANIZER: [Role.EVENT_MANAGER],
            Role.EVENT_MANAGER: [Role.EVENT_STAFF, Role.CHECKIN_OPERATOR, Role.PDV_OPERATOR],
            Role.EVENT_STAFF: [Role.VIEWER],
            Role.ANALYST: [Role.VIEWER]
        }
        
        # Cache de permissões calculadas
        self._permission_cache = {}
    
    def get_user_roles(self, user: Usuario, context: AccessContext = None) -> Set[Role]:
        """
        Obtém papéis do usuário baseado no tipo e contexto
        
        Args:
            user: Objeto do usuário
            context: Contexto da requisição
            
        Returns:
            Set de papéis do usuário
        """
        roles = set()
        
        # Mapear tipo de usuário para papel base
        tipo_to_role = {
            TipoUsuario.ADMIN: Role.ADMIN,
            TipoUsuario.ORGANIZADOR: Role.EVENT_ORGANIZER,
            TipoUsuario.OPERADOR: Role.EVENT_STAFF,
            TipoUsuario.PARTICIPANTE: Role.VIEWER
        }
        
        base_role = tipo_to_role.get(user.tipo, Role.VIEWER)
        roles.add(base_role)
        
        # Papéis adicionais baseados em contexto
        if context:
            # Se é dono da empresa
            if hasattr(user, 'empresa_id') and user.empresa_id == context.company_id:
                if user.tipo == TipoUsuario.ADMIN:
                    roles.add(Role.COMPANY_OWNER)
                elif user.tipo == TipoUsuario.ORGANIZADOR:
                    roles.add(Role.COMPANY_ADMIN)
            
            # Papéis específicos de evento (seria necessário tabela event_roles)
            # Por enquanto, lógica simples baseada no tipo
            if context.event_id:
                if user.tipo == TipoUsuario.ORGANIZADOR:
                    roles.add(Role.EVENT_ORGANIZER)
                elif user.tipo == TipoUsuario.OPERADOR:
                    roles.add(Role.CHECKIN_OPERATOR)
        
        return roles
    
    def get_role_permissions(self, role: Role) -> Set[Permission]:
        """Obtém permissões de um papel, incluindo herança"""
        if role not in self.role_permissions:
            return set()
        
        # Usar cache se disponível
        cache_key = f"role_perms_{role.value}"
        if cache_key in self._permission_cache:
            return self._permission_cache[cache_key]
        
        permissions = self.role_permissions[role].copy()
        
        # Adicionar permissões herdadas
        inherited_roles = self.role_hierarchy.get(role, [])
        for inherited_role in inherited_roles:
            inherited_permissions = self.get_role_permissions(inherited_role)
            permissions.update(inherited_permissions)
        
        # Cache resultado
        self._permission_cache[cache_key] = permissions
        return permissions
    
    def get_user_permissions(self, user: Usuario, context: AccessContext = None) -> Set[Permission]:
        """
        Obtém todas as permissões do usuário
        
        Args:
            user: Objeto do usuário
            context: Contexto da requisição
            
        Returns:
            Set de permissões do usuário
        """
        user_roles = self.get_user_roles(user, context)
        all_permissions = set()
        
        for role in user_roles:
            role_permissions = self.get_role_permissions(role)
            all_permissions.update(role_permissions)
        
        return all_permissions
    
    def has_permission(self, 
                      user: Usuario, 
                      permission: Permission, 
                      context: AccessContext = None) -> bool:
        """
        Verifica se usuário tem permissão específica
        
        Args:
            user: Objeto do usuário
            permission: Permissão a verificar
            context: Contexto da requisição
            
        Returns:
            True se usuário tem a permissão
        """
        try:
            user_permissions = self.get_user_permissions(user, context)
            
            # Super admin sempre tem acesso
            if Permission.SYSTEM_ADMIN in user_permissions:
                return True
            
            # Verificar permissão específica
            has_perm = permission in user_permissions
            
            # Log da verificação (para auditoria)
            self._log_permission_check(user, permission, context, has_perm)
            
            return has_perm
            
        except Exception as e:
            logger.error(f"Erro na verificação de permissão: {e}")
            return False
    
    def has_any_permission(self, 
                          user: Usuario, 
                          permissions: List[Permission], 
                          context: AccessContext = None) -> bool:
        """
        Verifica se usuário tem pelo menos uma das permissões listadas
        
        Args:
            user: Objeto do usuário
            permissions: Lista de permissões
            context: Contexto da requisição
            
        Returns:
            True se usuário tem pelo menos uma permissão
        """
        return any(self.has_permission(user, perm, context) for perm in permissions)
    
    def has_all_permissions(self, 
                           user: Usuario, 
                           permissions: List[Permission], 
                           context: AccessContext = None) -> bool:
        """
        Verifica se usuário tem todas as permissões listadas
        
        Args:
            user: Objeto do usuário
            permissions: Lista de permissões
            context: Contexto da requisição
            
        Returns:
            True se usuário tem todas as permissões
        """
        return all(self.has_permission(user, perm, context) for perm in permissions)
    
    def can_access_resource(self, 
                           user: Usuario, 
                           resource_type: ResourceType,
                           resource_id: str,
                           action: Permission,
                           context: AccessContext = None) -> bool:
        """
        Verifica acesso a recurso específico
        
        Args:
            user: Objeto do usuário
            resource_type: Tipo do recurso
            resource_id: ID do recurso
            action: Ação desejada
            context: Contexto da requisição
            
        Returns:
            True se usuário pode acessar o recurso
        """
        # Criar contexto se não fornecido
        if not context:
            context = AccessContext(
                user_id=str(user.id),
                company_id=str(user.empresa_id) if user.empresa_id else None,
                resource_type=resource_type,
                resource_id=resource_id
            )
        
        # Verificar permissão base
        if not self.has_permission(user, action, context):
            return False
        
        # Verificações específicas por tipo de recurso
        if resource_type == ResourceType.EVENT:
            return self._can_access_event(user, resource_id, action, context)
        elif resource_type == ResourceType.COMPANY:
            return self._can_access_company(user, resource_id, action, context)
        elif resource_type == ResourceType.USER:
            return self._can_access_user(user, resource_id, action, context)
        
        # Para outros recursos, apenas verificar permissão base
        return True
    
    def _can_access_event(self, user: Usuario, event_id: str, action: Permission, context: AccessContext) -> bool:
        """Verifica acesso específico a evento"""
        # Admin sempre pode acessar
        if user.tipo == TipoUsuario.ADMIN:
            return True
        
        # Lógica específica seria implementada aqui
        # Por exemplo: verificar se usuário é organizador do evento
        # Por simplicidade, permitir acesso se da mesma empresa
        return True  # Implementar lógica real baseada no banco
    
    def _can_access_company(self, user: Usuario, company_id: str, action: Permission, context: AccessContext) -> bool:
        """Verifica acesso específico a empresa"""
        # Admin sempre pode acessar
        if user.tipo == TipoUsuario.ADMIN:
            return True
        
        # Usuários só podem acessar própria empresa
        return str(user.empresa_id) == company_id
    
    def _can_access_user(self, user: Usuario, target_user_id: str, action: Permission, context: AccessContext) -> bool:
        """Verifica acesso específico a usuário"""
        # Usuário pode acessar próprios dados
        if str(user.id) == target_user_id:
            return True
        
        # Admin pode acessar qualquer usuário
        if user.tipo == TipoUsuario.ADMIN:
            return True
        
        # Organizadores podem acessar usuários da mesma empresa
        if user.tipo == TipoUsuario.ORGANIZADOR:
            # Seria necessário buscar dados do usuário alvo no banco
            return True  # Implementar verificação real
        
        return False
    
    def _log_permission_check(self, user: Usuario, permission: Permission, context: AccessContext, granted: bool):
        """Log de verificação de permissão para auditoria"""
        log_data = {
            'user_id': str(user.id),
            'user_email': user.email,
            'permission': permission.value,
            'granted': granted,
            'context': {
                'company_id': context.company_id if context else None,
                'event_id': context.event_id if context else None,
                'resource_type': context.resource_type.value if context and context.resource_type else None,
                'resource_id': context.resource_id if context else None,
                'ip_address': context.ip_address if context else None
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Em produção, salvar em tabela de auditoria
        if not granted:
            logger.warning(f"Permission denied: {log_data}")
        else:
            logger.debug(f"Permission granted: {log_data}")
    
    def clear_cache(self):
        """Limpa cache de permissões"""
        self._permission_cache.clear()
        logger.info("Cache de permissões limpo")
    
    def get_permission_summary(self, user: Usuario, context: AccessContext = None) -> Dict[str, Any]:
        """
        Obtém resumo completo das permissões do usuário
        
        Returns:
            Dict com roles, permissions e capabilities
        """
        roles = self.get_user_roles(user, context)
        permissions = self.get_user_permissions(user, context)
        
        # Agrupar permissões por categoria
        categorized_permissions = {}
        for perm in permissions:
            category = perm.value.split('.')[0]
            if category not in categorized_permissions:
                categorized_permissions[category] = []
            categorized_permissions[category].append(perm.value)
        
        return {
            'user_id': str(user.id),
            'user_email': user.email,
            'user_type': user.tipo.value,
            'roles': [role.value for role in roles],
            'total_permissions': len(permissions),
            'permissions_by_category': categorized_permissions,
            'is_admin': Permission.SYSTEM_ADMIN in permissions,
            'is_company_owner': Role.COMPANY_OWNER in roles,
            'context': {
                'company_id': context.company_id if context else None,
                'event_id': context.event_id if context else None
            } if context else None,
            'generated_at': datetime.utcnow().isoformat()
        }


# ================================
# DECORATORS PARA VERIFICAÇÃO DE PERMISSÕES
# ================================

def require_permission(permission: Permission):
    """
    Decorator para endpoints que require permissão específica
    
    Usage:
        @require_permission(Permission.EVENT_CREATE)
        async def create_event(...):
            pass
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Buscar usuário atual dos argumentos (assumindo que está em current_user)
            current_user = kwargs.get('current_user')
            if not current_user:
                raise PermissionError("User not authenticated")
            
            # Criar contexto
            context = AccessContext(user_id=str(current_user.id))
            
            # Verificar permissão
            if not rbac_system.has_permission(current_user, permission, context):
                raise PermissionError(f"Permission denied: {permission.value}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(*permissions: Permission):
    """
    Decorator que require pelo menos uma das permissões listadas
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise PermissionError("User not authenticated")
            
            context = AccessContext(user_id=str(current_user.id))
            
            if not rbac_system.has_any_permission(current_user, list(permissions), context):
                raise PermissionError(f"Permission denied: requires one of {[p.value for p in permissions]}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role: Role):
    """
    Decorator que require papel específico
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise PermissionError("User not authenticated")
            
            context = AccessContext(user_id=str(current_user.id))
            user_roles = rbac_system.get_user_roles(current_user, context)
            
            if role not in user_roles:
                raise PermissionError(f"Role required: {role.value}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# ================================
# INSTÂNCIA GLOBAL
# ================================

rbac_system = RBACSystem()