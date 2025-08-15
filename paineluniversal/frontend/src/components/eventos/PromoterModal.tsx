import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Alert, AlertDescription } from '../ui/alert';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { UserPlus, Trash2, Users } from 'lucide-react';
import { Evento, eventoService, usuarioService, PromoterEventoCreate } from '../../services/api';

interface PromoterModalProps {
  evento: Evento | null;
  isOpen: boolean;
  onClose: () => void;
  onUpdate: () => void;
}

const PromoterModal: React.FC<PromoterModalProps> = ({
  evento,
  isOpen,
  onClose,
  onUpdate
}) => {
  const [promoters, setPromoters] = useState<any[]>([]);
  const [promotersVinculados, setPromotersVinculados] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  const [novoPromoter, setNovoPromoter] = useState<PromoterEventoCreate>({
    promoter_id: 0,
    meta_vendas: undefined,
    comissao_percentual: undefined
  });

  useEffect(() => {
    if (isOpen && evento) {
      carregarDados();
    }
  }, [isOpen, evento]);

  const carregarDados = async () => {
    if (!evento) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const [promotersData, eventoDetalhado] = await Promise.all([
        usuarioService.listarPromoters(),
        eventoService.obterDetalhado(evento.id)
      ]);
      
      setPromoters(promotersData);
      setPromotersVinculados(eventoDetalhado.promoters_vinculados);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao carregar dados');
    } finally {
      setLoading(false);
    }
  };

  const handleVincularPromoter = async () => {
    if (!evento || !novoPromoter.promoter_id) return;
    
    try {
      setError(null);
      await eventoService.vincularPromoter(evento.id, novoPromoter);
      setSuccess('Promoter vinculado com sucesso!');
      setNovoPromoter({
        promoter_id: 0,
        meta_vendas: undefined,
        comissao_percentual: undefined
      });
      carregarDados();
      onUpdate();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao vincular promoter');
    }
  };

  const handleDesvincularPromoter = async (promoterId: number) => {
    if (!evento) return;
    
    if (!confirm('Tem certeza que deseja desvincular este promoter?')) {
      return;
    }
    
    try {
      setError(null);
      await eventoService.desvincularPromoter(evento.id, promoterId);
      setSuccess('Promoter desvinculado com sucesso!');
      carregarDados();
      onUpdate();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao desvincular promoter');
    }
  };

  const promotersDisponiveis = promoters.filter(
    promoter => !promotersVinculados.some(vinculado => vinculado.promoter_id === promoter.id)
  );

  if (!evento) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Gestão de Promoters - {evento.nome}
          </DialogTitle>
        </DialogHeader>

        {error && (
          <Alert className="border-red-200 bg-red-50">
            <AlertDescription className="text-red-800">{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="border-green-200 bg-green-50">
            <AlertDescription className="text-green-800">{success}</AlertDescription>
          </Alert>
        )}

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <UserPlus className="h-5 w-5" />
                Vincular Novo Promoter
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="promoter">Promoter</Label>
                  <select
                    id="promoter"
                    className="w-full mt-1 p-2 border rounded-md"
                    value={novoPromoter.promoter_id}
                    onChange={(e) => setNovoPromoter({
                      ...novoPromoter,
                      promoter_id: parseInt(e.target.value)
                    })}
                  >
                    <option value={0}>Selecione um promoter</option>
                    {promotersDisponiveis.map((promoter) => (
                      <option key={promoter.id} value={promoter.id}>
                        {promoter.nome}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <Label htmlFor="meta_vendas">Meta de Vendas</Label>
                  <Input
                    id="meta_vendas"
                    type="number"
                    min="0"
                    placeholder="Ex: 50"
                    value={novoPromoter.meta_vendas || ''}
                    onChange={(e) => setNovoPromoter({
                      ...novoPromoter,
                      meta_vendas: e.target.value ? parseInt(e.target.value) : undefined
                    })}
                  />
                </div>
                
                <div>
                  <Label htmlFor="comissao">Comissão (%)</Label>
                  <Input
                    id="comissao"
                    type="number"
                    min="0"
                    max="100"
                    step="0.1"
                    placeholder="Ex: 10.5"
                    value={novoPromoter.comissao_percentual || ''}
                    onChange={(e) => setNovoPromoter({
                      ...novoPromoter,
                      comissao_percentual: e.target.value ? parseFloat(e.target.value) : undefined
                    })}
                  />
                </div>
              </div>
              
              <Button
                onClick={handleVincularPromoter}
                disabled={!novoPromoter.promoter_id || loading}
                className="w-full"
              >
                Vincular Promoter
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">
                Promoters Vinculados ({promotersVinculados.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-4">Carregando...</div>
              ) : promotersVinculados.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>Nenhum promoter vinculado ao evento</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {promotersVinculados.map((promoter) => (
                    <div 
                      key={promoter.id} 
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                    >
                      <div className="flex-1">
                        <h4 className="font-medium">{promoter.nome}</h4>
                        <div className="flex gap-4 text-sm text-gray-600 mt-1">
                          <span>Vendas: {promoter.vendas_realizadas}</span>
                          {promoter.meta_vendas && (
                            <span>Meta: {promoter.meta_vendas}</span>
                          )}
                          {promoter.comissao_percentual > 0 && (
                            <span>Comissão: {promoter.comissao_percentual}%</span>
                          )}
                        </div>
                        
                        {promoter.meta_vendas && (
                          <div className="mt-2">
                            <div className="flex justify-between text-xs text-gray-600 mb-1">
                              <span>Progresso da Meta</span>
                              <span>
                                {((promoter.vendas_realizadas / promoter.meta_vendas) * 100).toFixed(1)}%
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-blue-600 h-2 rounded-full transition-all" 
                                style={{ 
                                  width: `${Math.min((promoter.vendas_realizadas / promoter.meta_vendas) * 100, 100)}%` 
                                }}
                              ></div>
                            </div>
                          </div>
                        )}
                      </div>
                      
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleDesvincularPromoter(promoter.promoter_id)}
                        className="ml-4"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="flex justify-end pt-4">
          <Button variant="outline" onClick={onClose}>
            Fechar
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default PromoterModal;
