import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { useToast } from '../../hooks/use-toast';
import { 
  Plus, Filter, Download, Upload, Users, 
  Eye, Edit, BarChart3, Crown
} from 'lucide-react';
import { eventoService, listaService, usuarioService } from '../../services/api';
import ListaModal from './ListaModal';
import ConvidadosModal from './ConvidadosModal';
import ImportarConvidadosModal from './ImportarConvidadosModal';
import DashboardListasModal from './DashboardListasModal';

interface ListaLocal {
  id: number;
  nome: string;
  tipo: string;
  preco: number;
  limite_vendas?: number;
  vendas_realizadas: number;
  ativa: boolean;
  evento_id: number;
  promoter_id?: number;
  total_convidados?: number;
  convidados_presentes?: number;
  taxa_presenca?: number;
  receita_gerada?: number;
  promoter_nome?: string;
  criado_em: string;
}

const ListasModule: React.FC = () => {
  const { toast } = useToast();
  
  const [eventos, setEventos] = useState<any[]>([]);
  const [eventoSelecionado, setEventoSelecionado] = useState<number | null>(null);
  const [listas, setListas] = useState<ListaLocal[]>([]);
  const [promoters, setPromoters] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [filtros, setFiltros] = useState({
    busca: '',
    tipo: '',
    promoter_id: '',
    ativa: ''
  });
  
  const [listaModal, setListaModal] = useState<{ open: boolean; lista: ListaLocal | null }>({ open: false, lista: null });
  const [convidadosModal, setConvidadosModal] = useState<{ open: boolean; lista: ListaLocal | null }>({ open: false, lista: null });
  const [importarModal, setImportarModal] = useState<{ open: boolean; lista: ListaLocal | null }>({ open: false, lista: null });
  const [dashboardModal, setDashboardModal] = useState<{ open: boolean; evento: number | null }>({ open: false, evento: null });

  useEffect(() => {
    carregarEventos();
    carregarPromoters();
  }, []);

  useEffect(() => {
    if (eventoSelecionado) {
      carregarListas();
    }
  }, [eventoSelecionado, filtros]);

  const carregarEventos = async () => {
    try {
      const eventosData = await eventoService.listar();
      setEventos(eventosData.filter(e => e.status === 'ativo'));
      if (eventosData.length > 0) {
        setEventoSelecionado(eventosData[0].id);
      }
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao carregar eventos",
        variant: "destructive"
      });
    }
  };

  const carregarPromoters = async () => {
    try {
      const promotersData = await usuarioService.listarPromoters();
      setPromoters(promotersData);
    } catch (error) {
      console.error('Erro ao carregar promoters:', error);
    }
  };

  const carregarListas = async () => {
    if (!eventoSelecionado) return;
    
    try {
      setLoading(true);
      const listasData = await listaService.listarPorEvento(eventoSelecionado);
      
      let listasFiltradas = listasData as unknown as ListaLocal[];
      
      if (filtros.busca) {
        listasFiltradas = listasFiltradas.filter(lista => 
          lista.nome.toLowerCase().includes(filtros.busca.toLowerCase())
        );
      }
      
      if (filtros.tipo) {
        listasFiltradas = listasFiltradas.filter(lista => lista.tipo === filtros.tipo);
      }
      
      if (filtros.promoter_id) {
        listasFiltradas = listasFiltradas.filter(lista => 
          lista.promoter_id?.toString() === filtros.promoter_id
        );
      }
      
      if (filtros.ativa !== '') {
        listasFiltradas = listasFiltradas.filter(lista => 
          lista.ativa === (filtros.ativa === 'true')
        );
      }
      
      setListas(listasFiltradas);
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao carregar listas",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExportarLista = async (lista: ListaLocal, formato: 'csv' | 'excel') => {
    try {
      const blob = await listaService.exportarConvidados(lista.id, formato);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `lista_${lista.nome}.${formato === 'excel' ? 'xlsx' : 'csv'}`;
      a.click();
      window.URL.revokeObjectURL(url);
      
      toast({
        title: "Sucesso",
        description: `Lista exportada em ${formato.toUpperCase()}`,
      });
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao exportar lista",
        variant: "destructive"
      });
    }
  };

  const getTipoColor = (tipo: string) => {
    const colors: Record<string, string> = {
      'vip': 'bg-purple-100 text-purple-800',
      'promoter': 'bg-blue-100 text-blue-800',
      'aniversario': 'bg-pink-100 text-pink-800',
      'free': 'bg-green-100 text-green-800',
      'desconto': 'bg-yellow-100 text-yellow-800',
      'pagante': 'bg-gray-100 text-gray-800'
    };
    return colors[tipo] || 'bg-gray-100 text-gray-800';
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  return (
    <div className="space-y-6 p-4">
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">Listas &amp; Convidados</h1>
          <p className="text-gray-600">Gestão inteligente de listas e convidados</p>
        </div>
        
        <div className="flex flex-wrap gap-2">
          <Button 
            onClick={() => setListaModal({ open: true, lista: null })}
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Nova Lista
          </Button>
          
          <Button 
            variant="outline"
            onClick={() => setDashboardModal({ open: true, evento: eventoSelecionado })}
            className="flex items-center gap-2"
          >
            <BarChart3 className="h-4 w-4" />
            Dashboard
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filtros
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div>
              <Label>Evento</Label>
              <select
                className="w-full mt-1 p-2 border rounded-md"
                value={eventoSelecionado || ''}
                onChange={(e) => setEventoSelecionado(parseInt(e.target.value))}
              >
                <option value="">Selecione um evento</option>
                {eventos.map((evento) => (
                  <option key={evento.id} value={evento.id}>
                    {evento.nome}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <Label>Buscar Lista</Label>
              <Input
                placeholder="Nome da lista..."
                value={filtros.busca}
                onChange={(e) => setFiltros({ ...filtros, busca: e.target.value })}
              />
            </div>
            
            <div>
              <Label>Tipo</Label>
              <select
                className="w-full mt-1 p-2 border rounded-md"
                value={filtros.tipo}
                onChange={(e) => setFiltros({ ...filtros, tipo: e.target.value })}
              >
                <option value="">Todos os tipos</option>
                <option value="vip">VIP</option>
                <option value="promoter">Promoter</option>
                <option value="aniversario">Aniversário</option>
                <option value="free">Cortesia</option>
                <option value="desconto">Desconto</option>
                <option value="pagante">Pagante</option>
              </select>
            </div>
            
            <div>
              <Label>Promoter</Label>
              <select
                className="w-full mt-1 p-2 border rounded-md"
                value={filtros.promoter_id}
                onChange={(e) => setFiltros({ ...filtros, promoter_id: e.target.value })}
              >
                <option value="">Todos os promoters</option>
                {promoters.map((promoter) => (
                  <option key={promoter.id} value={promoter.id}>
                    {promoter.nome}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <Label>Status</Label>
              <select
                className="w-full mt-1 p-2 border rounded-md"
                value={filtros.ativa}
                onChange={(e) => setFiltros({ ...filtros, ativa: e.target.value })}
              >
                <option value="">Todos</option>
                <option value="true">Ativas</option>
                <option value="false">Inativas</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Carregando listas...</p>
        </div>
      ) : listas.length === 0 ? (
        <Card>
          <CardContent className="text-center py-8">
            <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p className="text-gray-500">Nenhuma lista encontrada</p>
            <Button 
              onClick={() => setListaModal({ open: true, lista: null })}
              className="mt-4"
            >
              Criar primeira lista
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {listas.map((lista) => (
            <Card key={lista.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">{lista.nome}</CardTitle>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge className={getTipoColor(lista.tipo)}>
                        {lista.tipo.toUpperCase()}
                      </Badge>
                      {!lista.ativa && (
                        <Badge variant="secondary">INATIVA</Badge>
                      )}
                    </div>
                  </div>
                  {lista.promoter_nome && (
                    <div className="text-right">
                      <Crown className="h-4 w-4 text-yellow-500 inline" />
                      <p className="text-xs text-gray-600">{lista.promoter_nome}</p>
                    </div>
                  )}
                </div>
              </CardHeader>
              
              <CardContent className="space-y-3">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">Preço</p>
                    <p className="font-semibold">{formatCurrency(lista.preco)}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Convidados</p>
                    <p className="font-semibold">
                      {lista.total_convidados || lista.vendas_realizadas}
                      {lista.limite_vendas && ` / ${lista.limite_vendas}`}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">Presentes</p>
                    <p className="font-semibold text-green-600">
                      {lista.convidados_presentes || 0}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">Taxa Presença</p>
                    <p className="font-semibold text-blue-600">
                      {lista.taxa_presenca?.toFixed(1) || '0.0'}%
                    </p>
                  </div>
                </div>
                
                {lista.receita_gerada && (
                  <div className="pt-2 border-t">
                    <p className="text-gray-600 text-sm">Receita Gerada</p>
                    <p className="font-semibold text-green-600">
                      {formatCurrency(lista.receita_gerada)}
                    </p>
                  </div>
                )}
                
                <div className="flex flex-wrap gap-1 pt-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setConvidadosModal({ open: true, lista: lista })}
                    className="flex items-center gap-1"
                  >
                    <Eye className="h-3 w-3" />
                    Ver
                  </Button>
                  
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setListaModal({ open: true, lista: lista })}
                    className="flex items-center gap-1"
                  >
                    <Edit className="h-3 w-3" />
                    Editar
                  </Button>
                  
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setImportarModal({ open: true, lista: lista })}
                    className="flex items-center gap-1"
                  >
                    <Upload className="h-3 w-3" />
                    Importar
                  </Button>
                  
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleExportarLista(lista, 'excel')}
                    className="flex items-center gap-1"
                  >
                    <Download className="h-3 w-3" />
                    Excel
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Modais */}
      <ListaModal
        isOpen={listaModal.open}
        onClose={() => setListaModal({ open: false, lista: null })}
        lista={listaModal.lista}
        eventoId={eventoSelecionado}
        onSuccess={carregarListas}
      />
      
      <ConvidadosModal
        isOpen={convidadosModal.open}
        onClose={() => setConvidadosModal({ open: false, lista: null })}
        lista={convidadosModal.lista}
      />
      
      <ImportarConvidadosModal
        isOpen={importarModal.open}
        onClose={() => setImportarModal({ open: false, lista: null })}
        lista={importarModal.lista}
        onSuccess={carregarListas}
      />
      
      <DashboardListasModal
        isOpen={dashboardModal.open}
        onClose={() => setDashboardModal({ open: false, evento: null })}
        eventoId={dashboardModal.evento}
      />
    </div>
  );
};

export default ListasModule;
