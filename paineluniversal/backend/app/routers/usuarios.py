from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_, extract
from typing import List, Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext

from ..database import get_db
from ..models import Usuario, Empresa, TipoUsuario, PromoterEvento, Transacao
from ..schemas import (
    UsuarioCreate, UsuarioUpdate, UsuarioResponse, UsuarioDetalhado,
    AlterarSenha, PerfilUsuario
)
from ..auth import obter_usuario_atual, verificar_permissao_admin, hash_password
from ..utils.cpf_validator import validar_cpf, formatar_cpf

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/", response_model=UsuarioResponse)
async def criar_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_admin)
):
    """Criar novo usuário (apenas admins)"""
    
    # Validar CPF
    if not validar_cpf(usuario.cpf):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF inválido"
        )
    
    # Verificar se CPF já existe
    cpf_formatado = formatar_cpf(usuario.cpf)
    usuario_existente = db.query(Usuario).filter(Usuario.cpf == cpf_formatado).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já cadastrado"
        )
    
    # Verificar se email já existe
    email_existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if email_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Verificar se empresa existe
    empresa = db.query(Empresa).filter(Empresa.id == usuario.empresa_id).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    # Hash da senha
    senha_hash = hash_password(usuario.senha)
    
    # Criar usuário
    db_usuario = Usuario(
        cpf=cpf_formatado,
        nome=usuario.nome,
        email=usuario.email,
        telefone=usuario.telefone,
        tipo=usuario.tipo,
        senha_hash=senha_hash,
        empresa_id=usuario.empresa_id
    )
    
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    return UsuarioResponse(
        id=db_usuario.id,
        cpf=db_usuario.cpf,
        nome=db_usuario.nome,
        email=db_usuario.email,
        telefone=db_usuario.telefone,
        tipo=db_usuario.tipo.value,
        ativo=db_usuario.ativo,
        empresa_id=db_usuario.empresa_id,
        empresa_nome=empresa.nome,
        ultimo_login=db_usuario.ultimo_login,
        criado_em=db_usuario.criado_em
    )

@router.get("/", response_model=List[UsuarioResponse])
async def listar_usuarios(
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[str] = None,
    ativo: Optional[bool] = None,
    empresa_id: Optional[int] = None,
    busca: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Listar usuários com filtros"""
    
    query = db.query(Usuario).join(Empresa)
    
    # Filtro de acesso
    if usuario_atual.tipo.value != "admin":
        query = query.filter(Usuario.empresa_id == usuario_atual.empresa_id)
    
    # Aplicar filtros
    if tipo:
        query = query.filter(Usuario.tipo == tipo)
    
    if ativo is not None:
        query = query.filter(Usuario.ativo == ativo)
    
    if empresa_id:
        if usuario_atual.tipo.value != "admin":
            # Não-admins só veem da própria empresa
            if empresa_id != usuario_atual.empresa_id:
                raise HTTPException(status_code=403, detail="Acesso negado")
        query = query.filter(Usuario.empresa_id == empresa_id)
    
    if busca:
        query = query.filter(
            or_(
                Usuario.nome.ilike(f"%{busca}%"),
                Usuario.email.ilike(f"%{busca}%"),
                Usuario.cpf.ilike(f"%{busca}%")
            )
        )
    
    usuarios = query.order_by(desc(Usuario.criado_em)).offset(skip).limit(limit).all()
    
    return [UsuarioResponse(
        id=u.id,
        cpf=u.cpf,
        nome=u.nome,
        email=u.email,
        telefone=u.telefone,
        tipo=u.tipo.value,
        ativo=u.ativo,
        empresa_id=u.empresa_id,
        empresa_nome=u.empresa.nome,
        ultimo_login=u.ultimo_login,
        criado_em=u.criado_em
    ) for u in usuarios]

@router.get("/{usuario_id}", response_model=UsuarioDetalhado)
async def obter_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter dados detalhados de um usuário"""
    
    # Verificar acesso
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.id != usuario_id):
        # Verificar se é da mesma empresa
        usuario_solicitado = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario_solicitado or usuario_solicitado.empresa_id != usuario_atual.empresa_id:
            raise HTTPException(status_code=403, detail="Acesso negado")
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Calcular estatísticas se for promoter
    estatisticas = {}
    if usuario.tipo == TipoUsuario.PROMOTER:
        # Vendas totais
        total_vendas = db.query(func.count(Transacao.id)).filter(
            Transacao.promoter_id == usuario_id,
            Transacao.status == "aprovada"
        ).scalar() or 0
        
        # Receita gerada
        receita_total = db.query(func.sum(Transacao.valor)).filter(
            Transacao.promoter_id == usuario_id,
            Transacao.status == "aprovada"
        ).scalar() or 0
        
        # Eventos trabalhados
        eventos_trabalhados = db.query(func.count(func.distinct(PromoterEvento.evento_id))).filter(
            PromoterEvento.promoter_id == usuario_id
        ).scalar() or 0
        
        # Vendas no mês atual
        inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        vendas_mes = db.query(func.count(Transacao.id)).filter(
            Transacao.promoter_id == usuario_id,
            Transacao.status == "aprovada",
            Transacao.criado_em >= inicio_mes
        ).scalar() or 0
        
        estatisticas = {
            "total_vendas": total_vendas,
            "receita_total": float(receita_total),
            "eventos_trabalhados": eventos_trabalhados,
            "vendas_mes_atual": vendas_mes,
            "ticket_medio": float(receita_total / total_vendas) if total_vendas > 0 else 0
        }
    
    return UsuarioDetalhado(
        id=usuario.id,
        cpf=usuario.cpf,
        nome=usuario.nome,
        email=usuario.email,
        telefone=usuario.telefone,
        tipo=usuario.tipo.value,
        ativo=usuario.ativo,
        empresa_id=usuario.empresa_id,
        empresa_nome=usuario.empresa.nome,
        ultimo_login=usuario.ultimo_login,
        criado_em=usuario.criado_em,
        estatisticas=estatisticas
    )

@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def atualizar_usuario(
    usuario_id: int,
    usuario_update: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Atualizar dados de um usuário"""
    
    # Verificar acesso
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.id != usuario_id):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verificar se não é da mesma empresa (para não-admins)
    if (usuario_atual.tipo.value != "admin" and 
        usuario.empresa_id != usuario_atual.empresa_id):
        raise HTTPException(status_code=403, detail="Usuário não pertence à sua empresa")
    
    # Validar CPF se fornecido
    if usuario_update.cpf:
        if not validar_cpf(usuario_update.cpf):
            raise HTTPException(status_code=400, detail="CPF inválido")
        
        cpf_formatado = formatar_cpf(usuario_update.cpf)
        
        # Verificar se CPF já existe (exceto o próprio usuário)
        cpf_existente = db.query(Usuario).filter(
            Usuario.cpf == cpf_formatado,
            Usuario.id != usuario_id
        ).first()
        
        if cpf_existente:
            raise HTTPException(status_code=400, detail="CPF já cadastrado")
    
    # Validar email se fornecido
    if usuario_update.email:
        email_existente = db.query(Usuario).filter(
            Usuario.email == usuario_update.email,
            Usuario.id != usuario_id
        ).first()
        
        if email_existente:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Validar tipo (apenas admins podem alterar)
    if usuario_update.tipo and usuario_atual.tipo.value != "admin":
        raise HTTPException(status_code=403, detail="Apenas admins podem alterar tipo de usuário")
    
    # Atualizar campos
    for field, value in usuario_update.dict(exclude_unset=True).items():
        if field == "cpf" and value:
            setattr(usuario, field, formatar_cpf(value))
        elif value is not None:
            setattr(usuario, field, value)
    
    db.commit()
    db.refresh(usuario)
    
    return UsuarioResponse(
        id=usuario.id,
        cpf=usuario.cpf,
        nome=usuario.nome,
        email=usuario.email,
        telefone=usuario.telefone,
        tipo=usuario.tipo.value,
        ativo=usuario.ativo,
        empresa_id=usuario.empresa_id,
        empresa_nome=usuario.empresa.nome,
        ultimo_login=usuario.ultimo_login,
        criado_em=usuario.criado_em
    )

@router.post("/{usuario_id}/alterar-senha")
async def alterar_senha(
    usuario_id: int,
    dados_senha: AlterarSenha,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Alterar senha de um usuário"""
    
    # Verificar acesso
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.id != usuario_id):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Se não for admin, verificar senha atual
    if usuario_atual.tipo.value != "admin":
        if not pwd_context.verify(dados_senha.senha_atual, usuario.senha_hash):
            raise HTTPException(status_code=400, detail="Senha atual incorreta")
    
    # Validar nova senha
    if len(dados_senha.nova_senha) < 6:
        raise HTTPException(status_code=400, detail="Nova senha deve ter pelo menos 6 caracteres")
    
    if dados_senha.nova_senha != dados_senha.confirmar_senha:
        raise HTTPException(status_code=400, detail="Confirmação de senha não confere")
    
    # Atualizar senha
    usuario.senha_hash = hash_password(dados_senha.nova_senha)
    db.commit()
    
    return {"mensagem": "Senha alterada com sucesso"}

@router.post("/{usuario_id}/toggle-ativo")
async def toggle_ativo_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_admin)
):
    """Ativar/desativar usuário (apenas admins)"""
    
    if usuario_id == usuario_atual.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível alterar status do próprio usuário"
        )
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    usuario.ativo = not usuario.ativo
    db.commit()
    
    status_texto = "ativado" if usuario.ativo else "desativado"
    return {"mensagem": f"Usuário {status_texto} com sucesso"}

@router.get("/{usuario_id}/perfil", response_model=PerfilUsuario)
async def obter_perfil(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter perfil público do usuário"""
    
    # Verificar se pode ver o perfil
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.id != usuario_id):
        # Verificar se é da mesma empresa
        usuario_solicitado = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario_solicitado or usuario_solicitado.empresa_id != usuario_atual.empresa_id:
            raise HTTPException(status_code=403, detail="Acesso negado")
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Dados básicos do perfil
    perfil = {
        "id": usuario.id,
        "nome": usuario.nome,
        "tipo": usuario.tipo.value,
        "empresa_nome": usuario.empresa.nome,
        "membro_desde": usuario.criado_em
    }
    
    # Adicionar estatísticas se for promoter
    if usuario.tipo == TipoUsuario.PROMOTER:
        # Últimas 5 vendas
        ultimas_vendas = db.query(Transacao).filter(
            Transacao.promoter_id == usuario_id,
            Transacao.status == "aprovada"
        ).order_by(desc(Transacao.criado_em)).limit(5).all()
        
        perfil["ultimas_vendas"] = [
            {
                "id": v.id,
                "valor": float(v.valor),
                "evento_nome": v.evento.nome if v.evento else "N/A",
                "data": v.criado_em
            }
            for v in ultimas_vendas
        ]
        
        # Ranking no mês
        ranking_mes = db.query(
            func.count(Transacao.id).label('vendas')
        ).filter(
            Transacao.promoter_id == usuario_id,
            Transacao.status == "aprovada",
            extract('month', Transacao.criado_em) == datetime.now().month,
            extract('year', Transacao.criado_em) == datetime.now().year
        ).scalar() or 0
        
        perfil["vendas_mes_atual"] = ranking_mes
    
    return PerfilUsuario(**perfil)

@router.get("/promoters/ranking")
async def obter_ranking_promoters(
    limite: int = Query(20, le=100),
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter ranking de promoters"""
    
    # Definir período
    if not mes:
        mes = datetime.now().month
    if not ano:
        ano = datetime.now().year
    
    # Query base
    query = db.query(
        Usuario.id,
        Usuario.nome,
        func.count(Transacao.id).label('total_vendas'),
        func.sum(Transacao.valor).label('receita_total')
    ).join(
        Transacao, Usuario.id == Transacao.promoter_id
    ).filter(
        Usuario.tipo == TipoUsuario.PROMOTER,
        Transacao.status == "aprovada",
        extract('month', Transacao.criado_em) == mes,
        extract('year', Transacao.criado_em) == ano
    )
    
    # Filtro de empresa para não-admins
    if usuario_atual.tipo.value != "admin":
        query = query.filter(Usuario.empresa_id == usuario_atual.empresa_id)
    
    ranking = query.group_by(
        Usuario.id, Usuario.nome
    ).order_by(
        desc('total_vendas'), desc('receita_total')
    ).limit(limite).all()
    
    return [
        {
            "posicao": i + 1,
            "promoter_id": r.id,
            "nome": r.nome,
            "total_vendas": r.total_vendas,
            "receita_total": float(r.receita_total),
            "mes": mes,
            "ano": ano
        }
        for i, r in enumerate(ranking)
    ]

@router.post("/importar-csv")
async def importar_usuarios_csv(
    arquivo_csv: str,  # Base64 do arquivo CSV
    empresa_id: int,
    senha_padrao: str = "123456",
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_admin)
):
    """Importar usuários de arquivo CSV"""
    
    import csv
    import io
    import base64
    
    try:
        # Decodificar arquivo
        csv_content = base64.b64decode(arquivo_csv).decode('utf-8')
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        
        usuarios_criados = []
        erros = []
        
        for linha_num, linha in enumerate(reader, 1):
            try:
                # Validar campos obrigatórios
                if not all([linha.get('nome'), linha.get('cpf'), linha.get('email')]):
                    erros.append(f"Linha {linha_num}: Campos obrigatórios não preenchidos")
                    continue
                
                # Validar CPF
                cpf = linha['cpf'].strip()
                if not validar_cpf(cpf):
                    erros.append(f"Linha {linha_num}: CPF inválido - {cpf}")
                    continue
                
                cpf_formatado = formatar_cpf(cpf)
                
                # Verificar se já existe
                if db.query(Usuario).filter(Usuario.cpf == cpf_formatado).first():
                    erros.append(f"Linha {linha_num}: CPF já cadastrado - {cpf}")
                    continue
                
                if db.query(Usuario).filter(Usuario.email == linha['email']).first():
                    erros.append(f"Linha {linha_num}: Email já cadastrado - {linha['email']}")
                    continue
                
                # Criar usuário
                tipo_usuario = TipoUsuario(linha.get('tipo', 'promoter'))
                
                novo_usuario = Usuario(
                    cpf=cpf_formatado,
                    nome=linha['nome'].strip(),
                    email=linha['email'].strip(),
                    telefone=linha.get('telefone', '').strip() or None,
                    tipo=tipo_usuario,
                    senha_hash=hash_password(senha_padrao),
                    empresa_id=empresa_id
                )
                
                db.add(novo_usuario)
                usuarios_criados.append(linha['nome'])
                
            except Exception as e:
                erros.append(f"Linha {linha_num}: Erro - {str(e)}")
        
        if usuarios_criados:
            db.commit()
        
        return {
            "usuarios_criados": len(usuarios_criados),
            "usuarios_com_erro": len(erros),
            "lista_criados": usuarios_criados,
            "erros": erros
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar CSV: {str(e)}")

@router.get("/estatisticas/geral")
async def obter_estatisticas_usuarios(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter estatísticas gerais dos usuários"""
    
    query_base = db.query(Usuario)
    
    # Filtro de empresa para não-admins
    if usuario_atual.tipo.value != "admin":
        query_base = query_base.filter(Usuario.empresa_id == usuario_atual.empresa_id)
    
    # Totais por tipo
    total_usuarios = query_base.count()
    total_admins = query_base.filter(Usuario.tipo == TipoUsuario.ADMIN).count()
    total_promoters = query_base.filter(Usuario.tipo == TipoUsuario.PROMOTER).count()
    total_operadores = query_base.filter(Usuario.tipo == TipoUsuario.OPERADOR).count()
    
    # Usuários ativos
    usuarios_ativos = query_base.filter(Usuario.ativo == True).count()
    
    # Últimos logins (último mês)
    um_mes_atras = datetime.now() - timedelta(days=30)
    logins_recentes = query_base.filter(
        Usuario.ultimo_login >= um_mes_atras
    ).count()
    
    # Usuários criados no mês
    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    novos_usuarios_mes = query_base.filter(
        Usuario.criado_em >= inicio_mes
    ).count()
    
    return {
        "total_usuarios": total_usuarios,
        "usuarios_ativos": usuarios_ativos,
        "usuarios_inativos": total_usuarios - usuarios_ativos,
        "por_tipo": {
            "admins": total_admins,
            "promoters": total_promoters,
            "operadores": total_operadores
        },
        "logins_ultimo_mes": logins_recentes,
        "novos_usuarios_mes": novos_usuarios_mes,
        "taxa_atividade": round((logins_recentes / total_usuarios * 100) if total_usuarios > 0 else 0, 2)
    }
