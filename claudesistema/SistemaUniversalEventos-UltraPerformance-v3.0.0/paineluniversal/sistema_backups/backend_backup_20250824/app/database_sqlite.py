"""
Sistema Universal - Database sem AsyncPG
Versão com SQLite puro para contornar problemas de dependências
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Configuração do banco SQLite
DB_PATH = Path(__file__).parent / "sistema_universal.db"

def create_connection():
    """Cria conexão com SQLite"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row  # Permite acesso por nome da coluna
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao SQLite: {e}")
        return None

def create_tables():
    """Cria todas as tabelas necessárias"""
    conn = create_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                senha_hash TEXT NOT NULL,
                ativo BOOLEAN DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_login TIMESTAMP,
                tipo_usuario TEXT DEFAULT 'user'
            )
        """)
        
        # Tabela de eventos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                data_evento TIMESTAMP NOT NULL,
                local TEXT,
                preco DECIMAL(10,2) DEFAULT 0.00,
                capacidade INTEGER DEFAULT 100,
                ativo BOOLEAN DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                criado_por INTEGER,
                FOREIGN KEY (criado_por) REFERENCES usuarios (id)
            )
        """)
        
        # Tabela de produtos (estoque/PDV)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                preco DECIMAL(10,2) NOT NULL,
                categoria TEXT,
                estoque INTEGER DEFAULT 0,
                ativo BOOLEAN DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de transações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL, -- 'venda', 'estorno', 'ajuste'
                valor DECIMAL(10,2) NOT NULL,
                descricao TEXT,
                evento_id INTEGER,
                usuario_id INTEGER,
                data_transacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (evento_id) REFERENCES eventos (id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        """)
        
        # Tabela de check-ins
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evento_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                data_checkin TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'confirmado',
                FOREIGN KEY (evento_id) REFERENCES eventos (id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        """)
        
        # Tabelas do sistema WhatsApp
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS whatsapp_configuracoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER,
                api_token TEXT,
                webhook_url TEXT,
                numero_remetente TEXT,
                ativo BOOLEAN DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS whatsapp_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                conteudo TEXT NOT NULL,
                variaveis TEXT, -- JSON com variáveis do template
                ativo BOOLEAN DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS whatsapp_campanhas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                template_id INTEGER,
                evento_id INTEGER,
                lista_id INTEGER,
                filtro_status TEXT,
                mensagem_personalizada TEXT,
                agendamento TIMESTAMP,
                status TEXT DEFAULT 'pendente', -- pendente, executando, concluida, cancelada
                total_destinatarios INTEGER DEFAULT 0,
                total_enviados INTEGER DEFAULT 0,
                total_entregues INTEGER DEFAULT 0,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_execucao TIMESTAMP,
                criado_por INTEGER,
                FOREIGN KEY (template_id) REFERENCES whatsapp_templates (id),
                FOREIGN KEY (evento_id) REFERENCES eventos (id),
                FOREIGN KEY (criado_por) REFERENCES usuarios (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS whatsapp_mensagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campanha_id INTEGER,
                telefone TEXT NOT NULL,
                nome_destinatario TEXT,
                mensagem TEXT NOT NULL,
                status TEXT DEFAULT 'pendente', -- pendente, enviado, entregue, lido, falha
                tentativas INTEGER DEFAULT 0,
                erro TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_envio TIMESTAMP,
                data_entrega TIMESTAMP,
                FOREIGN KEY (campanha_id) REFERENCES whatsapp_campanhas (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS whatsapp_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                acao TEXT NOT NULL,
                detalhes TEXT,
                usuario_id INTEGER,
                data_log TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        """)
        
        # Tabelas para Analytics e Relatórios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT UNIQUE NOT NULL,
                cache_data TEXT NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_expiracao TIMESTAMP NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relatorios_agendados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                tipo TEXT NOT NULL, -- eventos, vendas, whatsapp
                periodo TEXT NOT NULL, -- 1d, 7d, 30d
                formato TEXT DEFAULT 'json', -- json, csv
                agendamento TEXT NOT NULL, -- cron expression
                ativo BOOLEAN DEFAULT 1,
                ultimo_envio TIMESTAMP,
                proximo_envio TIMESTAMP,
                email_destinatarios TEXT, -- JSON array
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metricas_tempo_real (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metrica TEXT NOT NULL,
                valor REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                dados_extra TEXT -- JSON com dados adicionais
            )
        """)
        
        conn.commit()
        logger.info("✅ Tabelas SQLite criadas com sucesso")
        
        # Inserir dados de exemplo se não existirem
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        if cursor.fetchone()[0] == 0:
            create_sample_data(conn)
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")
        return False
    finally:
        conn.close()

def create_sample_data(conn):
    """Cria dados de exemplo"""
    try:
        cursor = conn.cursor()
        
        # Usuário admin
        cursor.execute("""
            INSERT INTO usuarios (email, nome, senha_hash, tipo_usuario)
            VALUES ('admin@sistema.com', 'Administrador', 'hash_senha_admin', 'admin')
        """)
        
        # Usuário teste
        cursor.execute("""
            INSERT INTO usuarios (email, nome, senha_hash, tipo_usuario)
            VALUES ('user@teste.com', 'Usuário Teste', 'hash_senha_user', 'user')
        """)
        
        # Evento exemplo
        cursor.execute("""
            INSERT INTO eventos (nome, descricao, data_evento, local, preco, capacidade, criado_por)
            VALUES ('Evento Teste', 'Evento de demonstração', '2024-12-31 20:00:00', 'Local Teste', 50.00, 100, 1)
        """)
        
        # Produtos exemplo
        produtos_exemplo = [
            ('Água', 'Água mineral 500ml', 3.00, 'Bebidas', 100),
            ('Refrigerante', 'Refrigerante lata 350ml', 5.00, 'Bebidas', 50),
            ('Sanduíche', 'Sanduíche natural', 12.00, 'Comidas', 30),
            ('Ingresso VIP', 'Acesso VIP ao evento', 100.00, 'Ingressos', 20)
        ]
        
        for produto in produtos_exemplo:
            cursor.execute("""
                INSERT INTO produtos (nome, descricao, preco, categoria, estoque)
                VALUES (?, ?, ?, ?, ?)
            """, produto)
        
        # Configuração WhatsApp exemplo
        cursor.execute("""
            INSERT INTO whatsapp_configuracoes (empresa_id, api_token, numero_remetente, ativo)
            VALUES (1, 'token_demo_whatsapp_api', '5511999887766', 1)
        """)
        
        # Templates WhatsApp exemplo
        templates_whatsapp = [
            ('Boas-vindas Evento', 'evento', 'Olá {nome}! Seja bem-vindo(a) ao {evento}. Check-in realizado com sucesso às {horario}.', '["nome", "evento", "horario"]'),
            ('Lembrete Check-in', 'lembrete', 'Oi {nome}! Não esqueça de fazer seu check-in no evento {evento} que começará em breve.', '["nome", "evento"]'),
            ('Agradecimento', 'pos_evento', 'Obrigado por participar do {evento}, {nome}! Esperamos vê-lo(a) novamente em breve.', '["nome", "evento"]'),
            ('Promocional PDV', 'vendas', 'Oferta especial para você, {nome}! {produto} por apenas R$ {preco}. Válido até {data_limite}.', '["nome", "produto", "preco", "data_limite"]')
        ]
        
        for template in templates_whatsapp:
            cursor.execute("""
                INSERT INTO whatsapp_templates (nome, categoria, conteudo, variaveis)
                VALUES (?, ?, ?, ?)
            """, template)
        
        conn.commit()
        logger.info("✅ Dados de exemplo criados")
        
    except Exception as e:
        logger.error(f"Erro ao criar dados de exemplo: {e}")

# Funções de consulta simples
def get_all_usuarios():
    """Retorna todos os usuários"""
    conn = create_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, nome, ativo, data_criacao, tipo_usuario FROM usuarios WHERE ativo = 1")
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Erro ao buscar usuários: {e}")
        return []
    finally:
        conn.close()

def get_all_eventos():
    """Retorna todos os eventos"""
    conn = create_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.*, u.nome as criador_nome 
            FROM eventos e 
            LEFT JOIN usuarios u ON e.criado_por = u.id 
            WHERE e.ativo = 1
        """)
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Erro ao buscar eventos: {e}")
        return []
    finally:
        conn.close()

def get_all_produtos():
    """Retorna todos os produtos"""
    conn = create_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos WHERE ativo = 1")
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Erro ao buscar produtos: {e}")
        return []
    finally:
        conn.close()

def get_dashboard_stats():
    """Retorna estatísticas para o dashboard"""
    conn = create_connection()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor()
        
        stats = {}
        
        # Total de usuários
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE ativo = 1")
        stats['total_usuarios'] = cursor.fetchone()[0]
        
        # Total de eventos
        cursor.execute("SELECT COUNT(*) FROM eventos WHERE ativo = 1")
        stats['total_eventos'] = cursor.fetchone()[0]
        
        # Total de produtos
        cursor.execute("SELECT COUNT(*) FROM produtos WHERE ativo = 1")
        stats['total_produtos'] = cursor.fetchone()[0]
        
        # Total de transações hoje
        cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(valor), 0) 
            FROM transacoes 
            WHERE DATE(data_transacao) = DATE('now')
        """)
        row = cursor.fetchone()
        stats['transacoes_hoje'] = row[0]
        stats['vendas_hoje'] = float(row[1])
        
        # Check-ins hoje
        cursor.execute("""
            SELECT COUNT(*) FROM checkins 
            WHERE DATE(data_checkin) = DATE('now')
        """)
        stats['checkins_hoje'] = cursor.fetchone()[0]
        
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        return {}
    finally:
        conn.close()

if __name__ == "__main__":
    # Teste da criação do banco
    success = create_tables()
    if success:
        print("✅ Database SQLite configurado com sucesso!")
        print(f"📁 Arquivo do banco: {DB_PATH}")
        
        # Teste de consultas
        print("\n📊 Estatísticas:")
        stats = get_dashboard_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
    else:
        print("❌ Erro ao configurar database")
