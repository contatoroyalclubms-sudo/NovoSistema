from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta, date
from decimal import Decimal

from ..models import (
    Produto, MovimentoEstoque, VendaPDV, ItemVendaPDV, Usuario,
    Categoria, Evento, TipoUsuario, TipoPagamento
)
from ..schemas import RelatorioEstoque, AlertaEstoque

class EstoqueService:
    def __init__(self, db: Session):
        self.db = db
    
    async def registrar_movimento(
        self,
        produto_id: str,  # UUID como string
        tipo_movimento: str,
        quantidade: int,
        motivo: str,
        usuario_id: str,  # UUID como string
        venda_id: Optional[str] = None  # UUID como string
    ) -> MovimentoEstoque:
        """Registrar movimentação de estoque"""
        
        # Validar tipo de movimento
        tipos_validos = ["entrada", "saida", "ajuste"]
        if tipo_movimento not in tipos_validos:
            raise ValueError(f"Tipo de movimento inválido. Use: {', '.join(tipos_validos)}")
        
        # Validar quantidade
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
        
        # Buscar produto
        produto = self.db.query(Produto).filter(Produto.id == produto_id).first()
        if not produto:
            raise ValueError("Produto não encontrado")
        
        # Validar usuário
        usuario = self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            raise ValueError("Usuário não encontrado")
        
        # Calcular novo estoque
        estoque_anterior = produto.quantidade_estoque
        
        if tipo_movimento == "entrada":
            novo_estoque = estoque_anterior + quantidade
        elif tipo_movimento == "saida":
            if estoque_anterior < quantidade and not produto.permite_venda_sem_estoque:
                raise ValueError(f"Estoque insuficiente. Disponível: {estoque_anterior}, Solicitado: {quantidade}")
            novo_estoque = max(0, estoque_anterior - quantidade)
        else:  # ajuste
            # Para ajuste, a quantidade representa o valor absoluto da diferença
            # A direção é determinada pela diferença entre estoque atual e novo
            if motivo.startswith("Ajuste manual"):
                # Para ajustes manuais, calcular baseado na quantidade informada
                diferenca = quantidade if "entrada" in motivo else -quantidade
                novo_estoque = max(0, estoque_anterior + diferenca)
            else:
                novo_estoque = quantidade  # Quantidade absoluta
        
        # Criar movimento
        movimento = MovimentoEstoque(
            produto_id=produto_id,
            tipo_movimento=tipo_movimento,
            quantidade=quantidade,
            estoque_anterior=estoque_anterior,
            estoque_atual=novo_estoque,
            motivo=motivo,
            venda_id=venda_id,
            usuario_id=usuario_id
        )
        
        # Atualizar estoque do produto
        produto.quantidade_estoque = novo_estoque
        produto.atualizado_em = datetime.now()
        
        # Salvar no banco
        self.db.add(movimento)
        self.db.commit()
        self.db.refresh(movimento)
        
        return movimento
    
    async def processar_venda_pdv(self, venda_id: str) -> List[MovimentoEstoque]:
        """Processar saída de estoque para venda PDV"""
        
        venda = self.db.query(VendaPDV).filter(VendaPDV.id == venda_id).first()
        if not venda:
            raise ValueError("Venda não encontrada")
        
        if venda.status != "APROVADA":
            raise ValueError("Apenas vendas aprovadas podem movimentar estoque")
        
        # Verificar se já foi processado
        movimento_existente = self.db.query(MovimentoEstoque).filter(
            MovimentoEstoque.venda_id == venda_id
        ).first()
        
        if movimento_existente:
            raise ValueError("Venda já foi processada no estoque")
        
        # Processar itens da venda
        movimentos = []
        itens_venda = self.db.query(ItemVendaPDV).filter(ItemVendaPDV.venda_id == venda_id).all()
        
        for item in itens_venda:
            movimento = await self.registrar_movimento(
                produto_id=str(item.produto_id),
                tipo_movimento="saida",
                quantidade=item.quantidade,
                motivo=f"Venda PDV #{venda.numero_venda}",
                usuario_id=str(venda.usuario_vendedor_id),
                venda_id=str(venda_id)
            )
            movimentos.append(movimento)
        
        return movimentos
    
    async def estornar_venda_pdv(self, venda_id: str, motivo: str, usuario_id: str) -> List[MovimentoEstoque]:
        """Estornar movimentações de uma venda PDV"""
        
        # Buscar movimentos da venda
        movimentos_venda = self.db.query(MovimentoEstoque).filter(
            MovimentoEstoque.venda_id == venda_id,
            MovimentoEstoque.tipo_movimento == "saida"
        ).all()
        
        if not movimentos_venda:
            raise ValueError("Nenhuma movimentação encontrada para esta venda")
        
        movimentos_estorno = []
        
        for movimento_original in movimentos_venda:
            # Criar movimento de entrada (estorno)
            movimento_estorno = await self.registrar_movimento(
                produto_id=str(movimento_original.produto_id),
                tipo_movimento="entrada",
                quantidade=movimento_original.quantidade,
                motivo=f"Estorno venda #{venda_id}: {motivo}",
                usuario_id=str(usuario_id)
            )
            movimentos_estorno.append(movimento_estorno)
        
        return movimentos_estorno
    
    def obter_produtos_estoque_baixo(self, usuario_atual: Usuario, evento_id: Optional[str] = None) -> List[Produto]:
        """Obter produtos com estoque baixo"""
        
        query = self.db.query(Produto).filter(
            Produto.ativo == True,
            Produto.quantidade_estoque <= Produto.estoque_minimo
        )
        
        if usuario_atual.tipo.value != "admin":
            query = query.filter(Produto.empresa_id == usuario_atual.empresa_id)
        
        if evento_id:
            query = query.filter(Produto.evento_id == evento_id)
        
        return query.order_by(Produto.quantidade_estoque).all()
    
    def obter_produtos_sem_estoque(self, usuario_atual: Usuario, evento_id: Optional[str] = None) -> List[Produto]:
        """Obter produtos sem estoque"""
        
        query = self.db.query(Produto).filter(
            Produto.ativo == True,
            Produto.quantidade_estoque == 0
        )
        
        if usuario_atual.tipo.value != "admin":
            query = query.filter(Produto.empresa_id == usuario_atual.empresa_id)
        
        if evento_id:
            query = query.filter(Produto.evento_id == evento_id)
        
        return query.order_by(Produto.nome).all()
    
    async def calcular_valor_estoque(
        self, 
        usuario_atual: Usuario, 
        evento_id: Optional[str] = None,  # UUID como string
        categoria_id: Optional[str] = None  # UUID como string
    ) -> Dict[str, Any]:
        """Calcular valor total do estoque"""
        
        query = self.db.query(Produto).filter(Produto.ativo == True)
        
        if usuario_atual.tipo.value != "admin":
            query = query.filter(Produto.empresa_id == usuario_atual.empresa_id)
        
        if evento_id:
            query = query.filter(Produto.evento_id == evento_id)
        
        if categoria_id:
            query = query.filter(Produto.categoria_id == categoria_id)
        
        produtos = query.all()
        
        valor_custo_total = Decimal(0)
        valor_venda_total = Decimal(0)
        quantidade_total = 0
        
        for produto in produtos:
            quantidade = produto.quantidade_estoque
            quantidade_total += quantidade
            
            if produto.preco_custo:
                valor_custo_total += quantidade * produto.preco_custo
            
            valor_venda_total += quantidade * produto.preco_venda
        
        return {
            "total_produtos": len(produtos),
            "quantidade_total": quantidade_total,
            "valor_custo_total": float(valor_custo_total),
            "valor_venda_total": float(valor_venda_total),
            "margem_potencial": float(valor_venda_total - valor_custo_total),
            "margem_percentual": float((valor_venda_total - valor_custo_total) / valor_venda_total * 100) if valor_venda_total > 0 else 0
        }
    
    async def obter_movimentacoes_periodo(
        self,
        usuario_atual: Usuario,
        data_inicio: date,
        data_fim: date,
        produto_id: Optional[str] = None,  # UUID como string
        tipo_movimento: Optional[str] = None
    ) -> List[MovimentoEstoque]:
        """Obter movimentações de um período"""
        
        query = self.db.query(MovimentoEstoque).join(Produto)
        
        if usuario_atual.tipo.value != "admin":
            query = query.filter(Produto.empresa_id == usuario_atual.empresa_id)
        
        query = query.filter(
            func.date(MovimentoEstoque.criado_em) >= data_inicio,
            func.date(MovimentoEstoque.criado_em) <= data_fim
        )
        
        if produto_id:
            query = query.filter(MovimentoEstoque.produto_id == produto_id)
        
        if tipo_movimento:
            query = query.filter(MovimentoEstoque.tipo_movimento == tipo_movimento)
        
        return query.order_by(desc(MovimentoEstoque.criado_em)).all()
    
    async def obter_top_produtos_vendidos(
        self,
        usuario_atual: Usuario,
        data_inicio: date,
        data_fim: date,
        evento_id: Optional[str] = None,  # UUID como string
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Obter produtos mais vendidos no período"""
        
        query = self.db.query(
            MovimentoEstoque.produto_id,
            Produto.nome,
            Produto.codigo,
            func.sum(MovimentoEstoque.quantidade).label('total_vendido')
        ).join(
            Produto, MovimentoEstoque.produto_id == Produto.id
        ).filter(
            MovimentoEstoque.tipo_movimento == "saida",
            func.date(MovimentoEstoque.criado_em) >= data_inicio,
            func.date(MovimentoEstoque.criado_em) <= data_fim,
            MovimentoEstoque.venda_id.isnot(None)  # Apenas vendas, não ajustes
        )
        
        if usuario_atual.tipo.value != "admin":
            query = query.filter(Produto.empresa_id == usuario_atual.empresa_id)
        
        if evento_id:
            query = query.filter(Produto.evento_id == evento_id)
        
        resultados = query.group_by(
            MovimentoEstoque.produto_id, Produto.nome, Produto.codigo
        ).order_by(
            desc('total_vendido')
        ).limit(limit).all()
        
        return [
            {
                "produto_id": r.produto_id,
                "nome": r.nome,
                "codigo": r.codigo,
                "total_vendido": r.total_vendido,
                "posicao": i + 1
            }
            for i, r in enumerate(resultados)
        ]
    
    async def gerar_relatorio_estoque(
        self,
        usuario_atual: Usuario,
        evento_id: Optional[str] = None,  # UUID como string
        categoria_id: Optional[str] = None,  # UUID como string
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> RelatorioEstoque:
        """Gerar relatório completo de estoque"""
        
        if not data_inicio:
            data_inicio = date.today().replace(day=1)  # Início do mês
        if not data_fim:
            data_fim = date.today()
        
        # Valor total do estoque
        valor_estoque = await self.calcular_valor_estoque(
            usuario_atual, 
            str(evento_id) if evento_id else None, 
            str(categoria_id) if categoria_id else None
        )
        
        # Produtos com estoque baixo
        produtos_baixo = self.obter_produtos_estoque_baixo(
            usuario_atual, 
            str(evento_id) if evento_id else None
        )
        
        # Produtos sem estoque
        produtos_sem = self.obter_produtos_sem_estoque(
            usuario_atual, 
            str(evento_id) if evento_id else None
        )
        
        # Movimentações do período
        movimentacoes_periodo = await self.obter_movimentacoes_periodo(
            usuario_atual, data_inicio, data_fim
        )
        
        # Entradas e saídas do período
        entradas_periodo = sum(
            m.quantidade for m in movimentacoes_periodo 
            if m.tipo_movimento == "entrada"
        )
        
        saidas_periodo = sum(
            m.quantidade for m in movimentacoes_periodo 
            if m.tipo_movimento == "saida"
        )
        
        # Top produtos vendidos
        top_vendidos = await self.obter_top_produtos_vendidos(
            usuario_atual, 
            data_inicio, 
            data_fim, 
            str(evento_id) if evento_id else None
        )
        
        # Movimentações por dia
        movimentacoes_por_dia = {}
        for movimento in movimentacoes_periodo:
            dia = movimento.criado_em.date().isoformat()
            if dia not in movimentacoes_por_dia:
                movimentacoes_por_dia[dia] = {"entradas": 0, "saidas": 0}
            
            if movimento.tipo_movimento == "entrada":
                movimentacoes_por_dia[dia]["entradas"] += movimento.quantidade
            elif movimento.tipo_movimento == "saida":
                movimentacoes_por_dia[dia]["saidas"] += movimento.quantidade
        
        # Produtos por categoria
        query_categorias = self.db.query(
            Categoria.nome,
            func.count(Produto.id).label('total_produtos'),
            func.sum(Produto.quantidade_estoque).label('total_estoque')
        ).outerjoin(
            Produto, Categoria.id == Produto.categoria_id
        ).filter(
            Produto.ativo == True
        )
        
        if usuario_atual.tipo.value != "admin":
            query_categorias = query_categorias.filter(Categoria.empresa_id == usuario_atual.empresa_id)
        
        if evento_id:
            query_categorias = query_categorias.filter(Produto.evento_id == evento_id)
        
        produtos_por_categoria = {}
        for categoria in query_categorias.group_by(Categoria.nome).all():
            produtos_por_categoria[categoria.nome or "Sem categoria"] = {
                "total_produtos": categoria.total_produtos or 0,
                "total_estoque": categoria.total_estoque or 0
            }
        
        return RelatorioEstoque(
            valor_total_estoque=valor_estoque["valor_custo_total"],
            valor_potencial_venda=valor_estoque["valor_venda_total"],
            margem_potencial=valor_estoque["margem_potencial"],
            total_produtos=valor_estoque["total_produtos"],
            produtos_estoque_baixo=len(produtos_baixo),
            produtos_sem_estoque=len(produtos_sem),
            entradas_periodo=entradas_periodo,
            saidas_periodo=saidas_periodo,
            saldo_periodo=entradas_periodo - saidas_periodo,
            movimentacoes_por_dia=movimentacoes_por_dia,
            top_produtos_vendidos=top_vendidos,
            produtos_por_categoria=produtos_por_categoria,
            periodo_inicio=data_inicio,
            periodo_fim=data_fim,
            gerado_em=datetime.now()
        )
    
    async def verificar_disponibilidade_venda(
        self, 
        itens_venda: List[Dict[str, Any]]
    ) -> Tuple[bool, List[str]]:
        """Verificar se há estoque disponível para uma venda"""
        
        disponivel = True
        mensagens = []
        
        for item in itens_venda:
            produto_id = item.get("produto_id")
            quantidade_solicitada = item.get("quantidade", 0)
            
            produto = self.db.query(Produto).filter(Produto.id == produto_id).first()
            
            if not produto:
                disponivel = False
                mensagens.append(f"Produto ID {produto_id} não encontrado")
                continue
            
            if not produto.ativo:
                disponivel = False
                mensagens.append(f"Produto {produto.nome} está inativo")
                continue
            
            if produto.quantidade_estoque < quantidade_solicitada:
                if not produto.permite_venda_sem_estoque:
                    disponivel = False
                    mensagens.append(
                        f"Estoque insuficiente para {produto.nome}. "
                        f"Disponível: {produto.quantidade_estoque}, "
                        f"Solicitado: {quantidade_solicitada}"
                    )
                else:
                    mensagens.append(
                        f"Atenção: {produto.nome} será vendido com estoque negativo"
                    )
        
        return disponivel, mensagens
    
    async def reservar_estoque(
        self, 
        itens_venda: List[Dict[str, Any]], 
        tempo_reserva_minutos: int = 15
    ) -> str:
        """Reservar estoque temporariamente para uma venda"""
        
        # Implementar sistema de reserva se necessário
        # Por simplicidade, vamos apenas verificar disponibilidade
        disponivel, mensagens = await self.verificar_disponibilidade_venda(itens_venda)
        
        if not disponivel:
            raise ValueError(f"Não é possível reservar estoque: {'; '.join(mensagens)}")
        
        # Gerar ID de reserva
        import uuid
        reserva_id = str(uuid.uuid4())
        
        # TODO: Implementar tabela de reservas se necessário
        # Por enquanto, apenas retorna o ID
        
        return reserva_id
    
    async def liberar_reserva(self, reserva_id: str):
        """Liberar reserva de estoque"""
        
        # TODO: Implementar liberação de reserva
        # Por enquanto, apenas log
        pass
    
    def obter_historico_produto(
        self, 
        produto_id: str,  # UUID como string
        usuario_atual: Usuario,
        limit: int = 50
    ) -> List[MovimentoEstoque]:
        """Obter histórico de movimentações de um produto"""
        
        # Verificar se produto pertence à empresa do usuário
        produto = self.db.query(Produto).filter(Produto.id == produto_id).first()
        if not produto:
            raise ValueError("Produto não encontrado")
        
        if (usuario_atual.tipo.value != "admin" and 
            produto.empresa_id != usuario_atual.empresa_id):
            raise ValueError("Produto não pertence à sua empresa")
        
        return self.db.query(MovimentoEstoque).filter(
            MovimentoEstoque.produto_id == produto_id
        ).order_by(
            desc(MovimentoEstoque.criado_em)
        ).limit(limit).all()
    
    async def processar_entrada_estoque_lote(
        self, 
        entradas: List[Dict[str, Any]], 
        usuario_id: str
    ) -> List[MovimentoEstoque]:
        """Processar múltiplas entradas de estoque em lote"""
        
        movimentos = []
        
        for entrada in entradas:
            try:
                movimento = await self.registrar_movimento(
                    produto_id=str(entrada["produto_id"]),
                    tipo_movimento="entrada",
                    quantidade=entrada["quantidade"],
                    motivo=entrada.get("motivo", "Entrada em lote"),
                    usuario_id=str(usuario_id)
                )
                movimentos.append(movimento)
                
            except Exception as e:
                # Log do erro, mas continua processando outras entradas
                print(f"Erro ao processar entrada do produto {entrada['produto_id']}: {str(e)}")
                continue
        
        return movimentos
