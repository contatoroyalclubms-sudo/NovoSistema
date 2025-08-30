import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { useToast } from '../../hooks/use-toast';
import { Search, Download, QrCode, UserCheck, Users } from 'lucide-react';
import { transacaoService, checkinService } from '../../services/api';

interface ConvidadosModalProps {
  isOpen: boolean;
  onClose: () => void;
  lista: any;
}

const ConvidadosModal: React.FC<ConvidadosModalProps> = ({
  isOpen,
  onClose,
  lista
}) => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [convidados, setConvidados] = useState<any[]>([]);
  const [filteredConvidados, setFilteredConvidados] = useState<any[]>([]);
  const [busca, setBusca] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    if (isOpen && lista) {
      carregarConvidados();
    }
  }, [isOpen, lista]);

  useEffect(() => {
    let filtered = convidados;
    
    if (busca) {
      filtered = filtered.filter(convidado => 
        convidado.cpf_comprador.includes(busca) ||
        convidado.nome_comprador.toLowerCase().includes(busca.toLowerCase())
      );
    }
    
    if (statusFilter === 'presente') {
      filtered = filtered.filter(convidado => convidado.checkin_realizado);
    } else if (statusFilter === 'ausente') {
      filtered = filtered.filter(convidado => !convidado.checkin_realizado);
    }
    
    setFilteredConvidados(filtered);
  }, [convidados, busca, statusFilter]);

  const carregarConvidados = async () => {
    if (!lista) return;
    
    try {
      setLoading(true);
      const transacoes = await transacaoService.listar(lista.evento_id);
      const convidadosLista = transacoes.filter(t => 
        t.lista_id === lista.id && t.status === 'aprovada'
      );
      
      const convidadosComCheckin = await Promise.all(
        convidadosLista.map(async (convidado) => {
          try {
            const checkins = await checkinService.listarCheckins(lista.evento_id);
            const checkin = checkins.find(c => c.cpf === convidado.cpf_comprador);
            return {
              ...convidado,
              checkin_realizado: !!checkin,
              data_checkin: checkin?.checkin_em
            };
          } catch {
            return {
              ...convidado,
              checkin_realizado: false,
              data_checkin: null
            };
          }
        })
      );
      
      setConvidados(convidadosComCheckin);
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao carregar convidados",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const formatCPF = (cpf: string) => {
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR');
  };

  if (!lista) return null;

  const totalConvidados = convidados.length;
  const presentes = convidados.filter(c => c.checkin_realizado).length;
  const ausentes = totalConvidados - presentes;
  const taxaPresenca = totalConvidados > 0 ? (presentes / totalConvidados * 100) : 0;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Convidados - {lista.nome}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">{totalConvidados}</p>
                  <p className="text-sm text-gray-600">Total Convidados</p>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">{presentes}</p>
                  <p className="text-sm text-gray-600">Presentes</p>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-red-600">{ausentes}</p>
                  <p className="text-sm text-gray-600">Ausentes</p>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-purple-600">{taxaPresenca.toFixed(1)}%</p>
                  <p className="text-sm text-gray-600">Taxa Presença</p>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <Label>Buscar por CPF ou Nome</Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Digite CPF ou nome..."
                  value={busca}
                  onChange={(e) => setBusca(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div>
              <Label>Status</Label>
              <select
                className="w-full mt-1 p-2 border rounded-md"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="">Todos</option>
                <option value="presente">Presentes</option>
                <option value="ausente">Ausentes</option>
              </select>
            </div>
          </div>

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Carregando convidados...</p>
            </div>
          ) : filteredConvidados.length === 0 ? (
            <div className="text-center py-8">
              <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p className="text-gray-500">Nenhum convidado encontrado</p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredConvidados.map((convidado) => (
                <Card key={convidado.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <div>
                            <h4 className="font-semibold">{convidado.nome_comprador}</h4>
                            <p className="text-sm text-gray-600">{formatCPF(convidado.cpf_comprador)}</p>
                            {convidado.email_comprador && (
                              <p className="text-sm text-gray-600">{convidado.email_comprador}</p>
                            )}
                            {convidado.telefone_comprador && (
                              <p className="text-sm text-gray-600">{convidado.telefone_comprador}</p>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-3">
                        <div className="text-center">
                          <Badge 
                            className={convidado.checkin_realizado 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                            }
                          >
                            {convidado.checkin_realizado ? 'PRESENTE' : 'AUSENTE'}
                          </Badge>
                          {convidado.data_checkin && (
                            <p className="text-xs text-gray-500 mt-1">
                              {formatDate(convidado.data_checkin)}
                            </p>
                          )}
                        </div>
                        
                        <div className="text-center">
                          <QrCode className="h-6 w-6 text-gray-400 mx-auto" />
                          <p className="text-xs text-gray-500 mt-1">
                            {convidado.qr_code_ticket}
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
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

export default ConvidadosModal;
