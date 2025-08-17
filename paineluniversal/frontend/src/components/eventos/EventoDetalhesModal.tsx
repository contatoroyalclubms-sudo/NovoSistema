import React from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { 
  Calendar, 
  MapPin, 
  Users, 
  DollarSign, 
  TrendingUp,
  UserCheck,
  Star
} from 'lucide-react';
import { EventoDetalhado } from '../../services/api';

interface EventoDetalhesModalProps {
  evento: EventoDetalhado | null;
  isOpen: boolean;
  onClose: () => void;
}

const EventoDetalhesModal: React.FC<EventoDetalhesModalProps> = ({
  evento,
  isOpen,
  onClose
}) => {
  if (!evento) return null;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ativo': return 'bg-green-100 text-green-800';
      case 'cancelado': return 'bg-red-100 text-red-800';
      case 'finalizado': return 'bg-gray-100 text-gray-800';
      default: return 'bg-blue-100 text-blue-800';
    }
  };

  const getStatusFinanceiroColor = (status: string) => {
    switch (status) {
      case 'alto': return 'bg-green-100 text-green-800';
      case 'medio': return 'bg-yellow-100 text-yellow-800';
      case 'baixo': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusFinanceiroLabel = (status: string) => {
    switch (status) {
      case 'alto': return 'Alto';
      case 'medio': return 'Médio';
      case 'baixo': return 'Baixo';
      default: return 'Sem Vendas';
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>{evento.nome}</span>
            <div className="flex gap-2">
              <Badge className={getStatusColor(evento.status)}>
                {evento.status}
              </Badge>
              <Badge className={getStatusFinanceiroColor(evento.status_financeiro)}>
                {getStatusFinanceiroLabel(evento.status_financeiro)}
              </Badge>
            </div>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  Informações do Evento
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm text-gray-500">Data e Hora</p>
                  <p className="font-medium">
                    {new Date(evento.data_evento).toLocaleDateString('pt-BR', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-500">Local</p>
                  <p className="font-medium flex items-center gap-1">
                    <MapPin className="h-4 w-4" />
                    {evento.local}
                  </p>
                </div>
                
                {evento.endereco && (
                  <div>
                    <p className="text-sm text-gray-500">Endereço</p>
                    <p className="font-medium">{evento.endereco}</p>
                  </div>
                )}
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Limite de Idade</p>
                    <p className="font-medium">{evento.limite_idade}+</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Capacidade</p>
                    <p className="font-medium">{evento.capacidade_maxima}</p>
                  </div>
                </div>
                
                {evento.descricao && (
                  <div>
                    <p className="text-sm text-gray-500">Descrição</p>
                    <p className="text-sm">{evento.descricao}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Resumo Financeiro
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <DollarSign className="h-8 w-8 mx-auto text-blue-600 mb-2" />
                    <p className="text-2xl font-bold text-blue-600">
                      R$ {evento.receita_total.toFixed(2)}
                    </p>
                    <p className="text-sm text-gray-600">Receita Total</p>
                  </div>
                  
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <Users className="h-8 w-8 mx-auto text-green-600 mb-2" />
                    <p className="text-2xl font-bold text-green-600">
                      {evento.total_vendas}
                    </p>
                    <p className="text-sm text-gray-600">Total de Vendas</p>
                  </div>
                  
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <UserCheck className="h-8 w-8 mx-auto text-purple-600 mb-2" />
                    <p className="text-2xl font-bold text-purple-600">
                      {evento.total_checkins}
                    </p>
                    <p className="text-sm text-gray-600">Check-ins</p>
                  </div>
                  
                  <div className="text-center p-4 bg-orange-50 rounded-lg">
                    <Star className="h-8 w-8 mx-auto text-orange-600 mb-2" />
                    <p className="text-2xl font-bold text-orange-600">
                      {evento.total_checkins > 0 ? 
                        ((evento.total_checkins / evento.total_vendas) * 100).toFixed(1) : 
                        '0'
                      }%
                    </p>
                    <p className="text-sm text-gray-600">Taxa de Presença</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {evento.promoters_vinculados.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Promoters Vinculados
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {evento.promoters_vinculados.map((promoter) => (
                    <div 
                      key={promoter.id} 
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                    >
                      <div>
                        <p className="font-medium">{promoter.nome}</p>
                        <p className="text-sm text-gray-600">
                          Vendas: {promoter.vendas_realizadas}
                          {promoter.meta_vendas && ` / ${promoter.meta_vendas}`}
                        </p>
                      </div>
                      <div className="text-right">
                        {promoter.comissao_percentual > 0 && (
                          <p className="text-sm text-gray-600">
                            Comissão: {promoter.comissao_percentual}%
                          </p>
                        )}
                        {promoter.meta_vendas && (
                          <div className="w-24 bg-gray-200 rounded-full h-2 mt-1">
                            <div 
                              className="bg-blue-600 h-2 rounded-full" 
                              style={{ 
                                width: `${Math.min((promoter.vendas_realizadas / promoter.meta_vendas) * 100, 100)}%` 
                              }}
                            ></div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          <div className="text-xs text-gray-500 text-center">
            Criado em: {new Date(evento.criado_em).toLocaleDateString('pt-BR')}
            {evento.atualizado_em && (
              <> • Atualizado em: {new Date(evento.atualizado_em).toLocaleDateString('pt-BR')}</>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default EventoDetalhesModal;
