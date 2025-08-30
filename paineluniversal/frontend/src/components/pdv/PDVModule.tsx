import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { pdvService } from '@/services/api';
// import { websocketService } from '@/services/websocket';

interface Produto {
  id: number;
  nome: string;
  preco: string | number; // Backend pode retornar como string ou number
  estoque_atual: number;
  codigo_barras?: string;
  categoria?: string;
  imagem_url?: string;
  tipo?: string;
  status?: string;
  descricao?: string;
}

interface ItemCarrinho {
  produto: Produto;
  quantidade: number;
  preco_unitario: number;
  observacoes?: string;
}

interface Comanda {
  id: number;
  numero_comanda: string;
  saldo_atual: string | number; // Backend pode retornar como string ou number
  cpf_cliente?: string;
  nome_cliente?: string;
}

const toNumber = (value: string | number): number => {
  if (typeof value === 'string') {
    return parseFloat(value) || 0;
  }
  return value as number;
};

const PDVModule = () => {
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [carrinho, setCarrinho] = useState<ItemCarrinho[]>([]);
  const [busca, setBusca] = useState('');
  const [comandaSelecionada, setComandaSelecionada] = useState<Comanda | null>(null);
  const [cpfCliente, setCpfCliente] = useState('');
  const [nomeCliente, setNomeCliente] = useState('');
  const [metodoPagamento, setMetodoPagamento] = useState('DINHEIRO');
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const eventoId = 1; // Pegar do contexto ou props

  useEffect(() => {
    carregarProdutos();
    
    // websocketService.connect(eventoId);
    
    // websocketService.on('stock_update', (data) => {
    //   setProdutos(prev => prev.map(p => 
    //     p.id === data.produto_id 
    //       ? { ...p, estoque_atual: data.estoque_atual }
    //       : p
    //   ));
    //   
    //   toast({
    //     title: "Estoque atualizado",
    //     description: `${data.produto_nome}: ${data.estoque_atual} unidades`,
    //   });
    // });
    
    // websocketService.on('new_sale', (data) => {
    //   toast({
    //     title: "Nova venda realizada",
    //     description: `Venda ${data.venda.numero_venda} - R$ ${data.venda.valor_final}`,
    //   });
    // });
    
    // return () => {
    //   websocketService.disconnect();
    // };
  }, [eventoId]);

  const carregarProdutos = async () => {
    try {
      const response = await pdvService.listarProdutos(eventoId);
      setProdutos(Array.isArray(response) ? response : []);
    } catch (error) {
      console.error('Erro ao carregar produtos:', error);
      setProdutos([]);
      toast({
        title: "Erro",
        description: "Erro ao carregar produtos",
        variant: "destructive"
      });
    }
  };

  const buscarProduto = async (codigo: string) => {
    if (!codigo) return;
    
    const produto = produtos.find(p => 
      p.codigo_barras === codigo || 
      p.nome.toLowerCase().includes(codigo.toLowerCase())
    );
    
    if (produto) {
      adicionarAoCarrinho(produto);
      setBusca('');
    } else {
      toast({
        title: "Produto não encontrado",
        description: "Código de barras ou nome não encontrado",
        variant: "destructive"
      });
    }
  };

  const adicionarAoCarrinho = (produto: Produto) => {
    if (produto.estoque_atual <= 0) {
      toast({
        title: "Produto esgotado",
        description: `${produto.nome} não possui estoque`,
        variant: "destructive"
      });
      return;
    }

    const itemExistente = carrinho.find(item => item.produto.id === produto.id);
    
    if (itemExistente) {
      if (itemExistente.quantidade >= produto.estoque_atual) {
        toast({
          title: "Estoque insuficiente",
          description: `Estoque disponível: ${produto.estoque_atual}`,
          variant: "destructive"
        });
        return;
      }
      
      setCarrinho(carrinho.map(item =>
        item.produto.id === produto.id
          ? { ...item, quantidade: item.quantidade + 1 }
          : item
      ));
    } else {
      setCarrinho([...carrinho, {
        produto,
        quantidade: 1,
        preco_unitario: toNumber(produto.preco)
      }]);
    }
  };

  const removerDoCarrinho = (produtoId: number) => {
    setCarrinho(carrinho.filter(item => item.produto.id !== produtoId));
  };

  const alterarQuantidade = (produtoId: number, novaQuantidade: number) => {
    if (novaQuantidade <= 0) {
      removerDoCarrinho(produtoId);
      return;
    }

    const produto = produtos.find(p => p.id === produtoId);
    if (produto && novaQuantidade > produto.estoque_atual) {
      toast({
        title: "Estoque insuficiente",
        description: `Estoque disponível: ${produto.estoque_atual}`,
        variant: "destructive"
      });
      return;
    }

    setCarrinho(carrinho.map(item =>
      item.produto.id === produtoId
        ? { ...item, quantidade: novaQuantidade }
        : item
    ));
  };

  const calcularTotal = () => {
    return carrinho.reduce((total, item) => 
      total + (item.quantidade * item.preco_unitario), 0
    );
  };

  const buscarComanda = async (numeroComanda: string) => {
    try {
      const comandas = await pdvService.listarComandas(eventoId);
      const comanda = comandas.find(c => c.numero_comanda === numeroComanda);
      
      if (comanda) {
        setComandaSelecionada(comanda);
        setCpfCliente(comanda.cpf_cliente || '');
        setNomeCliente(comanda.nome_cliente || '');
        setMetodoPagamento('SALDO_COMANDA');
      } else {
        toast({
          title: "Comanda não encontrada",
          description: "Número da comanda não existe",
          variant: "destructive"
        });
      }
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao buscar comanda",
        variant: "destructive"
      });
    }
  };

  const finalizarVenda = async () => {
    if (carrinho.length === 0) {
      toast({
        title: "Carrinho vazio",
        description: "Adicione produtos ao carrinho",
        variant: "destructive"
      });
      return;
    }

    const total = calcularTotal();
    
    if (metodoPagamento === 'SALDO_COMANDA' && comandaSelecionada) {
      if (toNumber(comandaSelecionada.saldo_atual) < total) {
        toast({
          title: "Saldo insuficiente",
          description: `Saldo disponível: R$ ${toNumber(comandaSelecionada.saldo_atual).toFixed(2)}`,
          variant: "destructive"
        });
        return;
      }
    }

    setLoading(true);
    
    try {
      const vendaData = {
        evento_id: eventoId,
        cpf_cliente: cpfCliente || undefined,
        nome_cliente: nomeCliente || undefined,
        comanda_id: comandaSelecionada?.id,
        itens: carrinho.map(item => ({
          produto_id: item.produto.id,
          quantidade: item.quantidade,
          preco_unitario: item.preco_unitario,
          observacoes: item.observacoes
        })),
        pagamentos: [{
          tipo_pagamento: metodoPagamento,
          valor: total
        }]
      };

      await pdvService.processarVenda(vendaData);
      
      toast({
        title: "Venda realizada!",
        description: `Total: R$ ${total.toFixed(2)}`,
      });

      setCarrinho([]);
      setCpfCliente('');
      setNomeCliente('');
      setComandaSelecionada(null);
      setMetodoPagamento('DINHEIRO');
      
      carregarProdutos();
      
    } catch (error) {
      toast({
        title: "Erro na venda",
        description: "Erro ao processar venda",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const produtosFiltrados = Array.isArray(produtos) ? produtos.filter(produto =>
    produto.nome.toLowerCase().includes(busca.toLowerCase()) ||
    produto.codigo_barras?.includes(busca) ||
    produto.categoria?.toLowerCase().includes(busca.toLowerCase())
  ) : [];

  console.log('Produtos state:', produtos.length);
  console.log('Produtos filtrados:', produtosFiltrados.length);
  console.log('Busca atual:', busca);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
      {/* Produtos */}
      <div className="lg:col-span-2">
        <Card>
          <CardHeader>
            <CardTitle>Produtos</CardTitle>
            <div className="flex gap-2">
              <Input
                placeholder="Buscar produto ou código de barras..."
                value={busca}
                onChange={(e) => setBusca(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    buscarProduto(busca);
                  }
                }}
                className="flex-1"
              />
              <Button onClick={() => buscarProduto(busca)}>
                Buscar
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 max-h-96 overflow-y-auto">
              {produtosFiltrados.map(produto => (
                <Card 
                  key={produto.id} 
                  className="cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => adicionarAoCarrinho(produto)}
                >
                  <CardContent className="p-3">
                    <div className="text-sm font-medium truncate">
                      {produto.nome}
                    </div>
                    <div className="text-lg font-bold text-green-600">
                      R$ {toNumber(produto.preco).toFixed(2)}
                    </div>
                    <div className="flex justify-between items-center mt-2">
                      <Badge variant={produto.estoque_atual > 0 ? "default" : "destructive"}>
                        Est: {produto.estoque_atual}
                      </Badge>
                      {produto.categoria && (
                        <Badge variant="outline" className="text-xs">
                          {produto.categoria}
                        </Badge>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Carrinho e Pagamento */}
      <div className="space-y-4">
        {/* Carrinho */}
        <Card>
          <CardHeader>
            <CardTitle>Carrinho</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {carrinho.map(item => (
                <div key={item.produto.id} className="flex justify-between items-center p-2 border rounded">
                  <div className="flex-1">
                    <div className="font-medium text-sm">{item.produto.nome}</div>
                    <div className="text-xs text-gray-500">
                      R$ {toNumber(item.preco_unitario).toFixed(2)} x {item.quantidade}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => alterarQuantidade(item.produto.id, item.quantidade - 1)}
                    >
                      -
                    </Button>
                    <span className="w-8 text-center">{item.quantidade}</span>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => alterarQuantidade(item.produto.id, item.quantidade + 1)}
                    >
                      +
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => removerDoCarrinho(item.produto.id)}
                    >
                      ×
                    </Button>
                  </div>
                </div>
              ))}
            </div>
            
            {carrinho.length > 0 && (
              <div className="mt-4 pt-4 border-t">
                <div className="text-xl font-bold">
                  Total: R$ {calcularTotal().toFixed(2)}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Dados do Cliente */}
        <Card>
          <CardHeader>
            <CardTitle>Cliente</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <Label htmlFor="cpf">CPF</Label>
              <Input
                id="cpf"
                value={cpfCliente}
                onChange={(e) => setCpfCliente(e.target.value)}
                placeholder="000.000.000-00"
              />
            </div>
            <div>
              <Label htmlFor="nome">Nome</Label>
              <Input
                id="nome"
                value={nomeCliente}
                onChange={(e) => setNomeCliente(e.target.value)}
                placeholder="Nome do cliente"
              />
            </div>
            <div>
              <Label htmlFor="comanda">Número da Comanda</Label>
              <div className="flex gap-2">
                <Input
                  id="comanda"
                  placeholder="Digite o número"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      buscarComanda((e.target as HTMLInputElement).value);
                    }
                  }}
                />
                <Button
                  onClick={() => {
                    const input = document.getElementById('comanda') as HTMLInputElement;
                    buscarComanda(input.value);
                  }}
                >
                  Buscar
                </Button>
              </div>
              {comandaSelecionada && (
                <div className="mt-2 p-2 bg-green-50 rounded">
                  <div className="text-sm">
                    Comanda: {comandaSelecionada.numero_comanda}
                  </div>
                  <div className="text-sm font-medium">
                    Saldo: R$ {toNumber(comandaSelecionada.saldo_atual).toFixed(2)}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Pagamento */}
        <Card>
          <CardHeader>
            <CardTitle>Pagamento</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <Label>Método de Pagamento</Label>
              <select
                value={metodoPagamento}
                onChange={(e) => setMetodoPagamento(e.target.value)}
                className="w-full p-2 border rounded"
              >
                <option value="DINHEIRO">Dinheiro</option>
                <option value="PIX">PIX</option>
                <option value="CARTAO_CREDITO">Cartão de Crédito</option>
                <option value="CARTAO_DEBITO">Cartão de Débito</option>
                <option value="SALDO_COMANDA">Saldo da Comanda</option>
              </select>
            </div>
            
            <Button
              onClick={finalizarVenda}
              disabled={loading || carrinho.length === 0}
              className="w-full"
              size="lg"
            >
              {loading ? 'Processando...' : `Finalizar Venda - R$ ${calcularTotal().toFixed(2)}`}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PDVModule;
