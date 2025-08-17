import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Alert, AlertDescription } from '../ui/alert';
import { 
  Calendar, 
  MapPin, 
  Users, 
  DollarSign, 
  Plus, 
  Search, 
  Filter,
  Download,
  Edit,
  Trash2,
  Eye,
  UserPlus
} from 'lucide-react';
import { eventoService, Evento, EventoDetalhado, EventoFiltros } from '../../services/api';
import EventoModal from './EventoModal';
import EventoDetalhesModal from './EventoDetalhesModal';
import PromoterModal from './PromoterModal';

const EventosModule: React.FC = () => {
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  const [modalAberto, setModalAberto] = useState(false);
  const [detalhesModalAberto, setDetalhesModalAberto] = useState(false);
  const [promoterModalAberto, setPromoterModalAberto] = useState(false);
  const [eventoSelecionado, setEventoSelecionado] = useState<Evento | null>(null);
  const [eventoDetalhado, setEventoDetalhado] = useState<EventoDetalhado | null>(null);
  
  const [filtros, setFiltros] = useState<EventoFiltros>({});
  const [mostrarFiltros, setMostrarFiltros] = useState(false);
  const [busca, setBusca] = useState('');

  useEffect(() => {
    carregarEventos();
  }, []);

  const carregarEventos = async () => {
    try {
      setLoading(true);
      setError(null);
      
      let eventosData: Evento[];
      if (Object.keys(filtros).length > 0 || busca) {
        const filtrosCompletos = { ...filtros };
        if (busca) {
          filtrosCompletos.nome = busca;
        }
        eventosData = await eventoService.buscar(filtrosCompletos);
      } else {
        eventosData = await eventoService.listar();
      }
      
      setEventos(eventosData);
    } catch (err) {
      setError('Erro ao carregar eventos');
      console.error('Erro ao carregar eventos:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSalvarEvento = async (eventoData: any) => {
    try {
      setError(null);
      
      if (eventoSelecionado) {
        await eventoService.atualizar(eventoSelecionado.id, eventoData);
        setSuccess('Evento atualizado com sucesso!');
      } else {
        await eventoService.criar(eventoData);
        setSuccess('Evento criado com sucesso!');
      }
      
      setModalAberto(false);
      setEventoSelecionado(null);
      carregarEventos();
      
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao salvar evento');
    }
  };

  const handleCancelarEvento = async (evento: Evento) => {
    if (!confirm(`Tem certeza que deseja cancelar o evento "${evento.nome}"?`)) {
      return;
    }
    
    try {
      setError(null);
      await eventoService.cancelar(evento.id);
      setSuccess('Evento cancelado com sucesso!');
      carregarEventos();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao cancelar evento');
    }
  };

  const handleVerDetalhes = async (evento: Evento) => {
    try {
      setError(null);
      const detalhes = await eventoService.obterDetalhado(evento.id);
      setEventoDetalhado(detalhes);
      setDetalhesModalAberto(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao carregar detalhes do evento');
    }
  };

  const handleExportarCSV = async (evento: Evento) => {
    try {
      setError(null);
      const blob = await eventoService.exportarCSV(evento.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `evento_${evento.id}_vendas.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      setSuccess('CSV exportado com sucesso!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao exportar CSV');
    }
  };

  const handleExportarPDF = async (evento: Evento) => {
    try {
      setError(null);
      const blob = await eventoService.exportarPDF(evento.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `evento_${evento.id}_relatorio.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      setSuccess('PDF exportado com sucesso!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao exportar PDF');
    }
  };

  const handleBuscar = () => {
    carregarEventos();
  };

  const handleLimparFiltros = () => {
    setFiltros({});
    setBusca('');
    setMostrarFiltros(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ativo': return 'text-green-600 bg-green-100';
      case 'cancelado': return 'text-red-600 bg-red-100';
      case 'finalizado': return 'text-gray-600 bg-gray-100';
      default: return 'text-blue-600 bg-blue-100';
    }
  };

  const getStatusFinanceiroColor = (status: string) => {
    switch (status) {
      case 'alto': return 'text-green-600 bg-green-100';
      case 'medio': return 'text-yellow-600 bg-yellow-100';
      case 'baixo': return 'text-orange-600 bg-orange-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Carregando eventos...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Gestão de Eventos</h1>
        <Button 
          onClick={() => {
            setEventoSelecionado(null);
            setModalAberto(true);
          }}
          className="flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          Novo Evento
        </Button>
      </div>

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

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Buscar e Filtrar</span>
            <Button
              variant="outline"
              onClick={() => setMostrarFiltros(!mostrarFiltros)}
              className="flex items-center gap-2"
            >
              <Filter className="h-4 w-4" />
              {mostrarFiltros ? 'Ocultar Filtros' : 'Mostrar Filtros'}
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Buscar por nome do evento..."
                value={busca}
                onChange={(e) => setBusca(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleBuscar()}
              />
            </div>
            <Button onClick={handleBuscar} className="flex items-center gap-2">
              <Search className="h-4 w-4" />
              Buscar
            </Button>
            {(Object.keys(filtros).length > 0 || busca) && (
              <Button variant="outline" onClick={handleLimparFiltros}>
                Limpar
              </Button>
            )}
          </div>

          {mostrarFiltros && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t">
              <div>
                <Label htmlFor="status">Status</Label>
                <select
                  id="status"
                  className="w-full mt-1 p-2 border rounded-md"
                  value={filtros.status || ''}
                  onChange={(e) => setFiltros({ ...filtros, status: e.target.value || undefined })}
                >
                  <option value="">Todos</option>
                  <option value="ativo">Ativo</option>
                  <option value="cancelado">Cancelado</option>
                  <option value="finalizado">Finalizado</option>
                </select>
              </div>
              
              <div>
                <Label htmlFor="local">Local</Label>
                <Input
                  id="local"
                  placeholder="Filtrar por local..."
                  value={filtros.local || ''}
                  onChange={(e) => setFiltros({ ...filtros, local: e.target.value || undefined })}
                />
              </div>
              
              <div>
                <Label htmlFor="limite_idade">Limite de Idade Mínimo</Label>
                <Input
                  id="limite_idade"
                  type="number"
                  placeholder="Ex: 18"
                  value={filtros.limite_idade_min || ''}
                  onChange={(e) => setFiltros({ ...filtros, limite_idade_min: e.target.value ? parseInt(e.target.value) : undefined })}
                />
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {eventos.map((evento) => (
          <Card key={evento.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <CardTitle className="text-lg">{evento.nome}</CardTitle>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(evento.status)}`}>
                  {evento.status}
                </span>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Calendar className="h-4 w-4" />
                {new Date(evento.data_evento).toLocaleDateString('pt-BR', {
                  day: '2-digit',
                  month: '2-digit',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
              
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <MapPin className="h-4 w-4" />
                {evento.local}
              </div>
              
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Users className="h-4 w-4" />
                Limite: {evento.limite_idade}+ | Capacidade: {evento.capacidade_maxima}
              </div>

              {evento.descricao && (
                <p className="text-sm text-gray-600 line-clamp-2">
                  {evento.descricao}
                </p>
              )}

              <div className="flex flex-wrap gap-2 pt-3">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleVerDetalhes(evento)}
                  className="flex items-center gap-1"
                >
                  <Eye className="h-3 w-3" />
                  Detalhes
                </Button>
                
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setEventoSelecionado(evento);
                    setModalAberto(true);
                  }}
                  className="flex items-center gap-1"
                >
                  <Edit className="h-3 w-3" />
                  Editar
                </Button>
                
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setEventoSelecionado(evento);
                    setPromoterModalAberto(true);
                  }}
                  className="flex items-center gap-1"
                >
                  <UserPlus className="h-3 w-3" />
                  Promoters
                </Button>
              </div>

              <div className="flex gap-2 pt-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleExportarCSV(evento)}
                  className="flex items-center gap-1 flex-1"
                >
                  <Download className="h-3 w-3" />
                  CSV
                </Button>
                
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleExportarPDF(evento)}
                  className="flex items-center gap-1 flex-1"
                >
                  <Download className="h-3 w-3" />
                  PDF
                </Button>
                
                {evento.status === 'ativo' && (
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => handleCancelarEvento(evento)}
                    className="flex items-center gap-1"
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {eventos.length === 0 && !loading && (
        <Card>
          <CardContent className="text-center py-12">
            <Calendar className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nenhum evento encontrado
            </h3>
            <p className="text-gray-500 mb-4">
              {Object.keys(filtros).length > 0 || busca 
                ? 'Tente ajustar os filtros de busca.' 
                : 'Comece criando seu primeiro evento.'
              }
            </p>
            <Button 
              onClick={() => {
                setEventoSelecionado(null);
                setModalAberto(true);
              }}
              className="flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              Criar Primeiro Evento
            </Button>
          </CardContent>
        </Card>
      )}

      <EventoModal
        evento={eventoSelecionado}
        isOpen={modalAberto}
        onClose={() => {
          setModalAberto(false);
          setEventoSelecionado(null);
        }}
        onSave={handleSalvarEvento}
      />

      <EventoDetalhesModal
        evento={eventoDetalhado}
        isOpen={detalhesModalAberto}
        onClose={() => {
          setDetalhesModalAberto(false);
          setEventoDetalhado(null);
        }}
      />

      <PromoterModal
        evento={eventoSelecionado}
        isOpen={promoterModalAberto}
        onClose={() => {
          setPromoterModalAberto(false);
          setEventoSelecionado(null);
        }}
        onUpdate={carregarEventos}
      />
    </div>
  );
};

export default EventosModule;
