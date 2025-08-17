import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Alert, AlertDescription } from '../ui/alert';
import { useToast } from '../../hooks/use-toast';
import { financeiroService, usuarioService } from '../../services/api';

interface MovimentacaoModalProps {
  isOpen: boolean;
  onClose: () => void;
  movimentacao: any;
  eventoId: number | null;
  onSuccess: () => void;
}

const MovimentacaoModal: React.FC<MovimentacaoModalProps> = ({
  isOpen,
  onClose,
  movimentacao,
  eventoId,
  onSuccess
}) => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [promoters, setPromoters] = useState<any[]>([]);
  
  const [formData, setFormData] = useState({
    tipo: 'entrada',
    categoria: '',
    descricao: '',
    valor: '',
    promoter_id: '',
    numero_documento: '',
    observacoes: '',
    data_vencimento: '',
    data_pagamento: '',
    metodo_pagamento: '',
    status: 'pendente'
  });

  useEffect(() => {
    if (isOpen) {
      carregarPromoters();
      if (movimentacao) {
        setFormData({
          tipo: movimentacao.tipo || 'entrada',
          categoria: movimentacao.categoria || '',
          descricao: movimentacao.descricao || '',
          valor: movimentacao.valor?.toString() || '',
          promoter_id: movimentacao.promoter_id?.toString() || '',
          numero_documento: movimentacao.numero_documento || '',
          observacoes: movimentacao.observacoes || '',
          data_vencimento: movimentacao.data_vencimento || '',
          data_pagamento: movimentacao.data_pagamento || '',
          metodo_pagamento: movimentacao.metodo_pagamento || '',
          status: movimentacao.status || 'pendente'
        });
      } else {
        setFormData({
          tipo: 'entrada',
          categoria: '',
          descricao: '',
          valor: '',
          promoter_id: '',
          numero_documento: '',
          observacoes: '',
          data_vencimento: '',
          data_pagamento: '',
          metodo_pagamento: '',
          status: 'pendente'
        });
      }
      setError(null);
    }
  }, [isOpen, movimentacao]);

  const carregarPromoters = async () => {
    try {
      const promotersData = await usuarioService.listarPromoters();
      setPromoters(promotersData);
    } catch (error) {
      console.error('Erro ao carregar promoters:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!eventoId) {
      setError('Selecione um evento primeiro');
      return;
    }
    
    if (!formData.categoria.trim() || !formData.descricao.trim() || !formData.valor) {
      setError('Preencha todos os campos obrigatórios');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const movimentacaoData = {
        ...formData,
        evento_id: eventoId,
        valor: parseFloat(formData.valor),
        promoter_id: formData.promoter_id ? parseInt(formData.promoter_id) : null
      };

      if (movimentacao) {
        await financeiroService.atualizarMovimentacao(movimentacao.id, movimentacaoData);
        toast({
          title: "Sucesso",
          description: "Movimentação atualizada com sucesso",
        });
      } else {
        await financeiroService.criarMovimentacao(movimentacaoData);
        toast({
          title: "Sucesso",
          description: "Movimentação criada com sucesso",
        });
      }

      onSuccess();
      onClose();
    } catch (err: any) {
      let errorMessage = 'Erro ao salvar movimentação';
      
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
          errorMessage = err.response.data.detail
            .map((error: any) => error.msg || error.message || 'Erro de validação')
            .join(', ');
        }
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {movimentacao ? 'Editar Movimentação' : 'Nova Movimentação Financeira'}
          </DialogTitle>
        </DialogHeader>

        {error && (
          <Alert className="border-red-200 bg-red-50">
            <AlertDescription className="text-red-800">{error}</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="tipo">Tipo *</Label>
              <select
                id="tipo"
                className="w-full mt-1 p-2 border rounded-md"
                value={formData.tipo}
                onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}
                required
              >
                <option value="entrada">Entrada</option>
                <option value="saida">Saída</option>
                <option value="ajuste">Ajuste</option>
                <option value="repasse_promoter">Repasse Promoter</option>
                <option value="receita_vendas">Receita Vendas</option>
                <option value="receita_listas">Receita Listas</option>
              </select>
            </div>

            <div>
              <Label htmlFor="categoria">Categoria *</Label>
              <Input
                id="categoria"
                value={formData.categoria}
                onChange={(e) => setFormData({ ...formData, categoria: e.target.value })}
                placeholder="Ex: Bebidas, Segurança, Marketing"
                required
              />
            </div>

            <div className="md:col-span-2">
              <Label htmlFor="descricao">Descrição *</Label>
              <Input
                id="descricao"
                value={formData.descricao}
                onChange={(e) => setFormData({ ...formData, descricao: e.target.value })}
                placeholder="Descrição detalhada da movimentação"
                required
              />
            </div>

            <div>
              <Label htmlFor="valor">Valor (R$) *</Label>
              <Input
                id="valor"
                type="number"
                min="0"
                step="0.01"
                value={formData.valor}
                onChange={(e) => setFormData({ ...formData, valor: e.target.value })}
                placeholder="0,00"
                required
              />
            </div>

            <div>
              <Label htmlFor="status">Status</Label>
              <select
                id="status"
                className="w-full mt-1 p-2 border rounded-md"
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              >
                <option value="pendente">Pendente</option>
                <option value="aprovada">Aprovada</option>
                <option value="cancelada">Cancelada</option>
              </select>
            </div>

            {formData.tipo === 'repasse_promoter' && (
              <div>
                <Label htmlFor="promoter_id">Promoter</Label>
                <select
                  id="promoter_id"
                  className="w-full mt-1 p-2 border rounded-md"
                  value={formData.promoter_id}
                  onChange={(e) => setFormData({ ...formData, promoter_id: e.target.value })}
                >
                  <option value="">Selecione um promoter</option>
                  {promoters.map((promoter) => (
                    <option key={promoter.id} value={promoter.id}>
                      {promoter.nome}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div>
              <Label htmlFor="numero_documento">Número do Documento</Label>
              <Input
                id="numero_documento"
                value={formData.numero_documento}
                onChange={(e) => setFormData({ ...formData, numero_documento: e.target.value })}
                placeholder="Ex: NF-001, REC-123"
              />
            </div>

            <div>
              <Label htmlFor="metodo_pagamento">Método de Pagamento</Label>
              <select
                id="metodo_pagamento"
                className="w-full mt-1 p-2 border rounded-md"
                value={formData.metodo_pagamento}
                onChange={(e) => setFormData({ ...formData, metodo_pagamento: e.target.value })}
              >
                <option value="">Selecione</option>
                <option value="dinheiro">Dinheiro</option>
                <option value="pix">PIX</option>
                <option value="cartao_credito">Cartão de Crédito</option>
                <option value="cartao_debito">Cartão de Débito</option>
                <option value="transferencia">Transferência</option>
                <option value="boleto">Boleto</option>
              </select>
            </div>

            <div>
              <Label htmlFor="data_vencimento">Data de Vencimento</Label>
              <Input
                id="data_vencimento"
                type="date"
                value={formData.data_vencimento}
                onChange={(e) => setFormData({ ...formData, data_vencimento: e.target.value })}
              />
            </div>

            <div>
              <Label htmlFor="data_pagamento">Data de Pagamento</Label>
              <Input
                id="data_pagamento"
                type="date"
                value={formData.data_pagamento}
                onChange={(e) => setFormData({ ...formData, data_pagamento: e.target.value })}
              />
            </div>
          </div>

          <div>
            <Label htmlFor="observacoes">Observações</Label>
            <textarea
              id="observacoes"
              className="w-full mt-1 p-2 border rounded-md"
              rows={3}
              value={formData.observacoes}
              onChange={(e) => setFormData({ ...formData, observacoes: e.target.value })}
              placeholder="Observações adicionais..."
            />
          </div>

          <div className="flex justify-end space-x-2 pt-4">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Salvando...' : (movimentacao ? 'Atualizar' : 'Criar')}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default MovimentacaoModal;
