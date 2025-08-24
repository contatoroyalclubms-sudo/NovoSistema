import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Alert, AlertDescription } from '../ui/alert';
import { useToast } from '../../hooks/use-toast';
import { listaService, usuarioService } from '../../services/api';

interface ListaModalProps {
  isOpen: boolean;
  onClose: () => void;
  lista: any;
  eventoId: number | null;
  onSuccess: () => void;
}

const ListaModal: React.FC<ListaModalProps> = ({
  isOpen,
  onClose,
  lista,
  eventoId,
  onSuccess
}) => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [promoters, setPromoters] = useState<any[]>([]);
  
  const [formData, setFormData] = useState({
    nome: '',
    tipo: 'pagante',
    preco: 0,
    limite_vendas: '',
    promoter_id: '',
    ativa: true,
    descricao: '',
    codigo_cupom: '',
    desconto_percentual: 0
  });

  useEffect(() => {
    if (isOpen) {
      carregarPromoters();
      if (lista) {
        setFormData({
          nome: lista.nome || '',
          tipo: lista.tipo || 'pagante',
          preco: lista.preco || 0,
          limite_vendas: lista.limite_vendas?.toString() || '',
          promoter_id: lista.promoter_id?.toString() || '',
          ativa: lista.ativa !== false,
          descricao: lista.descricao || '',
          codigo_cupom: lista.codigo_cupom || '',
          desconto_percentual: lista.desconto_percentual || 0
        });
      } else {
        setFormData({
          nome: '',
          tipo: 'pagante',
          preco: 0,
          limite_vendas: '',
          promoter_id: '',
          ativa: true,
          descricao: '',
          codigo_cupom: '',
          desconto_percentual: 0
        });
      }
      setError(null);
    }
  }, [isOpen, lista]);

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
    
    if (!formData.nome.trim()) {
      setError('Nome da lista é obrigatório');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const listaData = {
        ...formData,
        evento_id: eventoId,
        limite_vendas: formData.limite_vendas ? parseInt(formData.limite_vendas) : null,
        promoter_id: formData.promoter_id ? parseInt(formData.promoter_id) : null
      };

      if (lista) {
        await listaService.atualizar(lista.id, listaData);
        toast({
          title: "Sucesso",
          description: "Lista atualizada com sucesso",
        });
      } else {
        await listaService.criar(listaData);
        toast({
          title: "Sucesso",
          description: "Lista criada com sucesso",
        });
      }

      onSuccess();
      onClose();
    } catch (err: any) {
      let errorMessage = 'Erro ao salvar lista';
      
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
          errorMessage = err.response.data.detail
            .map((error: any) => error.msg || error.message || 'Erro de validação')
            .join(', ');
        } else if (typeof err.response.data.detail === 'object') {
          errorMessage = err.response.data.detail.msg || err.response.data.detail.message || 'Erro de validação';
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
            {lista ? 'Editar Lista' : 'Nova Lista'}
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
              <Label htmlFor="nome">Nome da Lista *</Label>
              <Input
                id="nome"
                value={formData.nome}
                onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                placeholder="Ex: VIP Camarote"
                required
              />
            </div>

            <div>
              <Label htmlFor="tipo">Tipo *</Label>
              <select
                id="tipo"
                className="w-full mt-1 p-2 border rounded-md"
                value={formData.tipo}
                onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}
                required
              >
                <option value="vip">VIP</option>
                <option value="promoter">Promoter</option>
                <option value="aniversario">Aniversário</option>
                <option value="free">Cortesia</option>
                <option value="desconto">Desconto</option>
                <option value="pagante">Pagante</option>
              </select>
            </div>

            <div>
              <Label htmlFor="preco">Preço (R$)</Label>
              <Input
                id="preco"
                type="number"
                min="0"
                step="0.01"
                value={formData.preco}
                onChange={(e) => setFormData({ ...formData, preco: parseFloat(e.target.value) || 0 })}
              />
            </div>

            <div>
              <Label htmlFor="limite_vendas">Limite de Vendas</Label>
              <Input
                id="limite_vendas"
                type="number"
                min="0"
                value={formData.limite_vendas}
                onChange={(e) => setFormData({ ...formData, limite_vendas: e.target.value })}
                placeholder="Deixe vazio para ilimitado"
              />
            </div>

            <div>
              <Label htmlFor="promoter_id">Promoter Responsável</Label>
              <select
                id="promoter_id"
                className="w-full mt-1 p-2 border rounded-md"
                value={formData.promoter_id}
                onChange={(e) => setFormData({ ...formData, promoter_id: e.target.value })}
              >
                <option value="">Nenhum promoter</option>
                {promoters.map((promoter) => (
                  <option key={promoter.id} value={promoter.id}>
                    {promoter.nome}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <Label htmlFor="desconto_percentual">Desconto (%)</Label>
              <Input
                id="desconto_percentual"
                type="number"
                min="0"
                max="100"
                step="0.1"
                value={formData.desconto_percentual}
                onChange={(e) => setFormData({ ...formData, desconto_percentual: parseFloat(e.target.value) || 0 })}
              />
            </div>
          </div>

          <div>
            <Label htmlFor="codigo_cupom">Código do Cupom</Label>
            <Input
              id="codigo_cupom"
              value={formData.codigo_cupom}
              onChange={(e) => setFormData({ ...formData, codigo_cupom: e.target.value })}
              placeholder="Ex: VIP2024"
            />
          </div>

          <div>
            <Label htmlFor="descricao">Descrição</Label>
            <textarea
              id="descricao"
              className="w-full mt-1 p-2 border rounded-md"
              rows={3}
              value={formData.descricao}
              onChange={(e) => setFormData({ ...formData, descricao: e.target.value })}
              placeholder="Descrição da lista..."
            />
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="ativa"
              checked={formData.ativa}
              onChange={(e) => setFormData({ ...formData, ativa: e.target.checked })}
            />
            <Label htmlFor="ativa">Lista ativa</Label>
          </div>

          <div className="flex justify-end space-x-2 pt-4">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Salvando...' : (lista ? 'Atualizar' : 'Criar')}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default ListaModal;
