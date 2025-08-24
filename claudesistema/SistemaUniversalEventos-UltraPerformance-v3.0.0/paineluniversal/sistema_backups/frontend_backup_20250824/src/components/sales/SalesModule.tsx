import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Alert, AlertDescription } from '../ui/alert';
import { eventoService, listaService, transacaoService, type Evento, type Lista, type Transacao } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const SalesModule: React.FC = () => {
  const { usuario } = useAuth();
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [eventoSelecionado, setEventoSelecionado] = useState<number | null>(null);
  const [listas, setListas] = useState<Lista[]>([]);
  const [transacoes, setTransacoes] = useState<Transacao[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [novaVenda, setNovaVenda] = useState({
    cpf_comprador: '',
    nome_comprador: '',
    email_comprador: '',
    telefone_comprador: '',
    lista_id: 0,
    quantidade: 1
  });

  useEffect(() => {
    carregarEventos();
  }, []);

  useEffect(() => {
    if (eventoSelecionado) {
      carregarListas();
      carregarTransacoes();
    }
  }, [eventoSelecionado]);

  const carregarEventos = async () => {
    try {
      setLoading(true);
      const eventosData = await eventoService.listar(usuario?.empresa_id);
      setEventos(eventosData.filter(e => e.status === 'ativo'));
    } catch (error) {
      setError('Erro ao carregar eventos');
    } finally {
      setLoading(false);
    }
  };

  const carregarListas = async () => {
    if (!eventoSelecionado) return;
    
    try {
      const listasData = await listaService.listarPorEvento(eventoSelecionado);
      setListas(listasData.filter(l => l.ativa));
    } catch (error) {
      setError('Erro ao carregar listas');
    }
  };

  const carregarTransacoes = async () => {
    if (!eventoSelecionado) return;
    
    try {
      const transacoesData = await transacaoService.listar(eventoSelecionado);
      setTransacoes(transacoesData);
    } catch (error) {
      setError('Erro ao carregar transações');
    }
  };

  const formatarCPF = (cpf: string) => {
    const numbers = cpf.replace(/\D/g, '');
    return numbers.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  };

  const handleCpfChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatarCPF(e.target.value);
    setNovaVenda({ ...novaVenda, cpf_comprador: formatted });
  };

  const handleSubmitVenda = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const cpfNumbers = novaVenda.cpf_comprador.replace(/\D/g, '');
      
      if (cpfNumbers.length !== 11) {
        setError('CPF deve ter 11 dígitos');
        setLoading(false);
        return;
      }

      if (!novaVenda.lista_id) {
        setError('Selecione uma lista');
        setLoading(false);
        return;
      }

      const listaSelecionada = listas.find(l => l.id === novaVenda.lista_id);
      if (!listaSelecionada) {
        setError('Lista não encontrada');
        setLoading(false);
        return;
      }

      const dadosVenda = {
        cpf_comprador: cpfNumbers,
        nome_comprador: novaVenda.nome_comprador,
        email_comprador: novaVenda.email_comprador,
        telefone_comprador: novaVenda.telefone_comprador,
        valor: listaSelecionada.preco * novaVenda.quantidade,
        lista_id: novaVenda.lista_id,
        evento_id: eventoSelecionado!,
        quantidade: novaVenda.quantidade
      };

      await transacaoService.criar(dadosVenda);
      
      setSuccess('Venda realizada com sucesso!');
      setNovaVenda({
        cpf_comprador: '',
        nome_comprador: '',
        email_comprador: '',
        telefone_comprador: '',
        lista_id: 0,
        quantidade: 1
      });
      
      carregarTransacoes();
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erro ao processar venda');
    } finally {
      setLoading(false);
    }
  };

  const formatarMoeda = (valor: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor);
  };

  const formatarData = (data: string) => {
    return new Date(data).toLocaleString('pt-BR');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'aprovada': return 'text-green-600';
      case 'pendente': return 'text-yellow-600';
      case 'rejeitada': return 'text-red-600';
      case 'cancelada': return 'text-gray-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Vendas</h1>
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Nova Venda</CardTitle>
            <CardDescription>Registrar nova venda de ingresso</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmitVenda} className="space-y-4">
              <div>
                <Label htmlFor="evento">Evento</Label>
                <select
                  id="evento"
                  className="w-full p-2 border border-gray-300 rounded-md"
                  value={eventoSelecionado || ''}
                  onChange={(e) => setEventoSelecionado(Number(e.target.value))}
                  required
                >
                  <option value="">Selecione um evento</option>
                  {eventos.map(evento => (
                    <option key={evento.id} value={evento.id}>
                      {evento.nome} - {new Date(evento.data_evento).toLocaleDateString('pt-BR')}
                    </option>
                  ))}
                </select>
              </div>

              {eventoSelecionado && (
                <>
                  <div>
                    <Label htmlFor="lista">Lista/Tipo de Ingresso</Label>
                    <select
                      id="lista"
                      className="w-full p-2 border border-gray-300 rounded-md"
                      value={novaVenda.lista_id}
                      onChange={(e) => setNovaVenda({ ...novaVenda, lista_id: Number(e.target.value) })}
                      required
                    >
                      <option value="">Selecione uma lista</option>
                      {listas.map(lista => (
                        <option key={lista.id} value={lista.id}>
                          {lista.nome} - {formatarMoeda(lista.preco)} ({lista.tipo})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <Label htmlFor="cpf">CPF do Comprador</Label>
                    <Input
                      id="cpf"
                      type="text"
                      placeholder="000.000.000-00"
                      value={novaVenda.cpf_comprador}
                      onChange={handleCpfChange}
                      maxLength={14}
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="nome">Nome Completo</Label>
                    <Input
                      id="nome"
                      type="text"
                      placeholder="Nome completo do comprador"
                      value={novaVenda.nome_comprador}
                      onChange={(e) => setNovaVenda({ ...novaVenda, nome_comprador: e.target.value })}
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="email">E-mail</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="email@exemplo.com"
                      value={novaVenda.email_comprador}
                      onChange={(e) => setNovaVenda({ ...novaVenda, email_comprador: e.target.value })}
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="telefone">Telefone</Label>
                    <Input
                      id="telefone"
                      type="tel"
                      placeholder="(11) 99999-9999"
                      value={novaVenda.telefone_comprador}
                      onChange={(e) => setNovaVenda({ ...novaVenda, telefone_comprador: e.target.value })}
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="quantidade">Quantidade</Label>
                    <Input
                      id="quantidade"
                      type="number"
                      min="1"
                      max="10"
                      value={novaVenda.quantidade}
                      onChange={(e) => setNovaVenda({ ...novaVenda, quantidade: Number(e.target.value) })}
                      required
                    />
                  </div>

                  <Button type="submit" disabled={loading} className="w-full">
                    {loading ? 'Processando...' : 'Registrar Venda'}
                  </Button>
                </>
              )}
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Vendas Recentes</CardTitle>
            <CardDescription>
              {eventoSelecionado ? 'Últimas vendas do evento selecionado' : 'Selecione um evento para ver as vendas'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {eventoSelecionado ? (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {transacoes.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">Nenhuma venda encontrada</p>
                ) : (
                  transacoes.slice(0, 10).map(transacao => (
                    <div key={transacao.id} className="border-b pb-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium">{transacao.nome_comprador}</p>
                          <p className="text-sm text-gray-600">CPF: {formatarCPF(transacao.cpf_comprador)}</p>
                          <p className="text-sm text-gray-600">{transacao.email_comprador}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold">{formatarMoeda(transacao.valor)}</p>
                          <p className={`text-sm ${getStatusColor(transacao.status)}`}>
                            {transacao.status.toUpperCase()}
                          </p>
                        </div>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatarData(transacao.criado_em)}
                      </p>
                    </div>
                  ))
                )}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">
                Selecione um evento para visualizar as vendas
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SalesModule;
