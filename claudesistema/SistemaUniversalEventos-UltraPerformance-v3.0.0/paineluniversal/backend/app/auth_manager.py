"""
Sistema de Autenticação e Autorização
Priority #7: Authentication & Authorization System
"""

import jwt
import bcrypt
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import secrets
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """Roles de usuário no sistema"""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"

@dataclass
class User:
    """Modelo de usuário"""
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    full_name: str = ""
    password_hash: str = ""
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Converte para dicionário (sem senha)"""
        data = asdict(self)
        data.pop('password_hash', None)
        data['role'] = self.role.value if isinstance(self.role, UserRole) else self.role
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.last_login:
            data['last_login'] = self.last_login.isoformat()
        if self.locked_until:
            data['locked_until'] = self.locked_until.isoformat()
        return data

@dataclass
class Session:
    """Modelo de sessão"""
    id: Optional[int] = None
    user_id: int = 0
    token: str = ""
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    ip_address: str = ""
    user_agent: str = ""
    is_active: bool = True

class AuthManager:
    """Gerenciador de Autenticação e Autorização"""
    
    def __init__(self, db_path: str = "auth_database.db"):
        self.db_path = db_path
        self.secret_key = self._get_or_create_secret_key()
        self.token_expiry_hours = 24
        self.max_failed_attempts = 5
        self.lockout_duration_minutes = 30
        
        # Criar tabelas
        self._create_tables()
        self._create_default_admin()
        
        logger.info("[AUTH] AuthManager inicializado")
    
    def _get_or_create_secret_key(self) -> str:
        """Gera ou recupera chave secreta"""
        key_file = Path("auth_secret.key")
        
        if key_file.exists():
            return key_file.read_text().strip()
        else:
            secret = secrets.token_urlsafe(32)
            key_file.write_text(secret)
            return secret
    
    def _create_tables(self):
        """Cria tabelas do sistema de auth"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de usuários
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        full_name TEXT NOT NULL,
                        password_hash TEXT NOT NULL,
                        role TEXT DEFAULT 'user',
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        failed_login_attempts INTEGER DEFAULT 0,
                        locked_until TIMESTAMP
                    )
                """)
                
                # Tabela de sessões
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        token TEXT UNIQUE NOT NULL,
                        expires_at TIMESTAMP NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ip_address TEXT,
                        user_agent TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                
                # Tabela de tentativas de login
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS login_attempts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        ip_address TEXT,
                        success BOOLEAN,
                        attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        user_agent TEXT
                    )
                """)
                
                conn.commit()
                logger.info("[AUTH] Tabelas criadas com sucesso")
                
        except Exception as e:
            logger.error(f"[AUTH] Erro ao criar tabelas: {e}")
    
    def _create_default_admin(self):
        """Cria usuário admin padrão se não existir"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificar se já existe admin
                cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
                admin_count = cursor.fetchone()[0]
                
                if admin_count == 0:
                    # Criar admin padrão
                    admin_password = "admin123"  # Em produção, usar senha segura
                    password_hash = self._hash_password(admin_password)
                    
                    cursor.execute("""
                        INSERT INTO users (username, email, full_name, password_hash, role)
                        VALUES (?, ?, ?, ?, ?)
                    """, ("admin", "admin@sistema.com", "Administrador", password_hash, "admin"))
                    
                    conn.commit()
                    logger.info("[AUTH] Admin padrão criado (username: admin, password: admin123)")
                    
        except Exception as e:
            logger.error(f"[AUTH] Erro ao criar admin padrão: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Hash da senha usando bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica senha contra hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except:
            return False
    
    def _generate_token(self, user: User) -> str:
        """Gera JWT token para o usuário"""
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role.value if isinstance(user.role, UserRole) else user.role,
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def _verify_token(self, token: str) -> Optional[Dict]:
        """Verifica e decodifica JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def register_user(self, username: str, email: str, full_name: str, 
                     password: str, role: UserRole = UserRole.USER) -> Tuple[bool, str, Optional[User]]:
        """Registra novo usuário"""
        try:
            # Validações
            if len(username) < 3:
                return False, "Username deve ter pelo menos 3 caracteres", None
            
            if len(password) < 6:
                return False, "Senha deve ter pelo menos 6 caracteres", None
            
            if "@" not in email:
                return False, "Email inválido", None
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificar se username já existe
                cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
                if cursor.fetchone()[0] > 0:
                    return False, "Username já existe", None
                
                # Verificar se email já existe
                cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,))
                if cursor.fetchone()[0] > 0:
                    return False, "Email já está registrado", None
                
                # Criar usuário
                password_hash = self._hash_password(password)
                cursor.execute("""
                    INSERT INTO users (username, email, full_name, password_hash, role)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, email, full_name, password_hash, role.value))
                
                user_id = cursor.lastrowid
                conn.commit()
                
                # Recuperar usuário criado
                user = self.get_user_by_id(user_id)
                logger.info(f"[AUTH] Usuário registrado: {username}")
                
                return True, "Usuário registrado com sucesso", user
                
        except Exception as e:
            logger.error(f"[AUTH] Erro ao registrar usuário: {e}")
            return False, f"Erro interno: {e}", None
    
    def login(self, username: str, password: str, ip_address: str = "", 
             user_agent: str = "") -> Tuple[bool, str, Optional[str], Optional[User]]:
        """Realiza login do usuário"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Buscar usuário
                cursor.execute("""
                    SELECT id, username, email, full_name, password_hash, role, 
                           is_active, failed_login_attempts, locked_until
                    FROM users WHERE username = ? OR email = ?
                """, (username, username))
                
                user_data = cursor.fetchone()
                
                # Log da tentativa
                cursor.execute("""
                    INSERT INTO login_attempts (username, ip_address, success, user_agent)
                    VALUES (?, ?, ?, ?)
                """, (username, ip_address, False, user_agent))
                
                if not user_data:
                    return False, "Usuário ou senha inválidos", None, None
                
                user = User(
                    id=user_data[0],
                    username=user_data[1],
                    email=user_data[2],
                    full_name=user_data[3],
                    password_hash=user_data[4],
                    role=UserRole(user_data[5]),
                    is_active=bool(user_data[6]),
                    failed_login_attempts=user_data[7],
                    locked_until=datetime.fromisoformat(user_data[8]) if user_data[8] else None
                )
                
                # Verificar se conta está ativa
                if not user.is_active:
                    return False, "Conta desativada", None, None
                
                # Verificar se conta está bloqueada
                if user.locked_until and user.locked_until > datetime.now():
                    return False, f"Conta bloqueada até {user.locked_until.strftime('%H:%M:%S')}", None, None
                
                # Verificar senha
                if not self._verify_password(password, user.password_hash):
                    # Incrementar tentativas falhadas
                    failed_attempts = user.failed_login_attempts + 1
                    locked_until = None
                    
                    if failed_attempts >= self.max_failed_attempts:
                        locked_until = datetime.now() + timedelta(minutes=self.lockout_duration_minutes)
                        logger.warning(f"[AUTH] Conta bloqueada por tentativas: {username}")
                    
                    cursor.execute("""
                        UPDATE users SET failed_login_attempts = ?, locked_until = ?
                        WHERE id = ?
                    """, (failed_attempts, locked_until, user.id))
                    
                    conn.commit()
                    return False, "Usuário ou senha inválidos", None, None
                
                # Login bem-sucedido
                # Resetar tentativas falhadas
                cursor.execute("""
                    UPDATE users SET failed_login_attempts = 0, locked_until = NULL, last_login = ?
                    WHERE id = ?
                """, (datetime.now(), user.id))
                
                # Atualizar log de tentativa para sucesso
                cursor.execute("""
                    UPDATE login_attempts SET success = 1 
                    WHERE username = ? AND ip_address = ? 
                    AND attempted_at = (
                        SELECT MAX(attempted_at) FROM login_attempts 
                        WHERE username = ? AND ip_address = ?
                    )
                """, (username, ip_address, username, ip_address))
                
                # Gerar token
                token = self._generate_token(user)
                
                # Salvar sessão
                expires_at = datetime.now() + timedelta(hours=self.token_expiry_hours)
                cursor.execute("""
                    INSERT INTO sessions (user_id, token, expires_at, ip_address, user_agent)
                    VALUES (?, ?, ?, ?, ?)
                """, (user.id, token, expires_at, ip_address, user_agent))
                
                conn.commit()
                logger.info(f"[AUTH] Login realizado: {username}")
                
                return True, "Login realizado com sucesso", token, user
                
        except Exception as e:
            logger.error(f"[AUTH] Erro no login: {e}")
            return False, f"Erro interno: {e}", None, None
    
    def logout(self, token: str) -> bool:
        """Realiza logout invalidando o token"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE sessions SET is_active = 0 WHERE token = ?
                """, (token,))
                
                conn.commit()
                logger.info("[AUTH] Logout realizado")
                return True
                
        except Exception as e:
            logger.error(f"[AUTH] Erro no logout: {e}")
            return False
    
    def validate_token(self, token: str) -> Optional[User]:
        """Valida token e retorna usuário"""
        try:
            # Verificar token JWT
            payload = self._verify_token(token)
            if not payload:
                return None
            
            # Verificar se sessão está ativa no banco
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT s.is_active, s.expires_at, u.id, u.username, u.email, 
                           u.full_name, u.role, u.is_active
                    FROM sessions s
                    JOIN users u ON s.user_id = u.id
                    WHERE s.token = ? AND s.is_active = 1
                """, (token,))
                
                result = cursor.fetchone()
                if not result:
                    return None
                
                # Verificar se sessão não expirou
                expires_at = datetime.fromisoformat(result[1])
                if expires_at < datetime.now():
                    # Marcar sessão como inativa
                    cursor.execute("UPDATE sessions SET is_active = 0 WHERE token = ?", (token,))
                    conn.commit()
                    return None
                
                # Verificar se usuário está ativo
                if not result[7]:
                    return None
                
                # Retornar usuário
                return User(
                    id=result[2],
                    username=result[3],
                    email=result[4],
                    full_name=result[5],
                    role=UserRole(result[6]),
                    is_active=bool(result[7])
                )
                
        except Exception as e:
            logger.error(f"[AUTH] Erro na validação do token: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Busca usuário por ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, username, email, full_name, role, is_active, 
                           created_at, last_login, failed_login_attempts
                    FROM users WHERE id = ?
                """, (user_id,))
                
                result = cursor.fetchone()
                if not result:
                    return None
                
                return User(
                    id=result[0],
                    username=result[1],
                    email=result[2],
                    full_name=result[3],
                    role=UserRole(result[4]),
                    is_active=bool(result[5]),
                    created_at=datetime.fromisoformat(result[6]) if result[6] else None,
                    last_login=datetime.fromisoformat(result[7]) if result[7] else None,
                    failed_login_attempts=result[8]
                )
                
        except Exception as e:
            logger.error(f"[AUTH] Erro ao buscar usuário: {e}")
            return None
    
    def list_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Lista usuários do sistema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, username, email, full_name, role, is_active, 
                           created_at, last_login, failed_login_attempts
                    FROM users 
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """, (limit, offset))
                
                users = []
                for row in cursor.fetchall():
                    user = User(
                        id=row[0],
                        username=row[1],
                        email=row[2],
                        full_name=row[3],
                        role=UserRole(row[4]),
                        is_active=bool(row[5]),
                        created_at=datetime.fromisoformat(row[6]) if row[6] else None,
                        last_login=datetime.fromisoformat(row[7]) if row[7] else None,
                        failed_login_attempts=row[8]
                    )
                    users.append(user)
                
                return users
                
        except Exception as e:
            logger.error(f"[AUTH] Erro ao listar usuários: {e}")
            return []
    
    def update_user_role(self, user_id: int, new_role: UserRole) -> bool:
        """Atualiza role do usuário"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE users SET role = ? WHERE id = ?
                """, (new_role.value, user_id))
                
                conn.commit()
                logger.info(f"[AUTH] Role atualizada para usuário {user_id}: {new_role.value}")
                return True
                
        except Exception as e:
            logger.error(f"[AUTH] Erro ao atualizar role: {e}")
            return False
    
    def deactivate_user(self, user_id: int) -> bool:
        """Desativa usuário"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE users SET is_active = 0 WHERE id = ?
                """, (user_id,))
                
                # Invalidar todas as sessões do usuário
                cursor.execute("""
                    UPDATE sessions SET is_active = 0 WHERE user_id = ?
                """, (user_id,))
                
                conn.commit()
                logger.info(f"[AUTH] Usuário {user_id} desativado")
                return True
                
        except Exception as e:
            logger.error(f"[AUTH] Erro ao desativar usuário: {e}")
            return False
    
    def get_auth_stats(self) -> Dict:
        """Estatísticas do sistema de auth"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total de usuários
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]
                
                # Usuários ativos
                cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
                active_users = cursor.fetchone()[0]
                
                # Usuários por role
                cursor.execute("""
                    SELECT role, COUNT(*) FROM users GROUP BY role
                """)
                users_by_role = dict(cursor.fetchall())
                
                # Sessões ativas
                cursor.execute("""
                    SELECT COUNT(*) FROM sessions 
                    WHERE is_active = 1 AND expires_at > datetime('now')
                """)
                active_sessions = cursor.fetchone()[0]
                
                # Tentativas de login (últimas 24h)
                cursor.execute("""
                    SELECT COUNT(*) FROM login_attempts 
                    WHERE attempted_at > datetime('now', '-1 day')
                """)
                recent_attempts = cursor.fetchone()[0]
                
                # Tentativas falhadas (últimas 24h)
                cursor.execute("""
                    SELECT COUNT(*) FROM login_attempts 
                    WHERE attempted_at > datetime('now', '-1 day') AND success = 0
                """)
                failed_attempts = cursor.fetchone()[0]
                
                return {
                    "total_users": total_users,
                    "active_users": active_users,
                    "users_by_role": users_by_role,
                    "active_sessions": active_sessions,
                    "recent_login_attempts": recent_attempts,
                    "failed_login_attempts": failed_attempts,
                    "success_rate": round((recent_attempts - failed_attempts) / recent_attempts * 100, 1) if recent_attempts > 0 else 100
                }
                
        except Exception as e:
            logger.error(f"[AUTH] Erro ao obter estatísticas: {e}")
            return {}

# Instância global
auth_manager = AuthManager()
