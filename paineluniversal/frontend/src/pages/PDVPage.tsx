import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { pdvService, Produto, ItemVenda } from '../services/pdv'
import { formatCurrency } from '../lib/utils'
import { ShoppingCart, Package, Plus, Minus, Trash2, CreditCard } from 'lucide-react'

function PDVPage() {
  const [produtos, setProdutos] = useState<Produto[]>([])
  const [carrinho, setCarrinho] = useState<ItemVenda[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)

  useEffect(() => {
    loadProdutos()
  }, [])

  useEffect(() => {
    const novoTotal = carrinho.reduce((acc, item) => acc + item.subtotal, 0)
    setTotal(novoTotal)
  }, [carrinho])

  const loadProdutos = async () => {
    try {
      setLoading(true)
      const response = await pdvService.getProdutos(1, 50, {
        is_ativo: true,
        search: searchTerm
      })
      setProdutos(response.data)
    } catch (error) {
      console.error('Erro ao carregar produtos:', error)
    } finally {
      setLoading(false)
    }
  }

  const adicionarAoCarrinho = (produto: Produto) => {
    const itemExistente = carrinho.find(item => item.produto_id === produto.id)
    
    if (itemExistente) {
      setCarrinho(carrinho.map(item =>
        item.produto_id === produto.id
          ? {
              ...item,
              quantidade: item.quantidade + 1,
              subtotal: (item.quantidade + 1) * item.preco_unitario
            }
          : item
      ))
    } else {
      const novoItem: ItemVenda = {
        produto_id: produto.id,
        produto,
        quantidade: 1,
        preco_unitario: produto.preco,
        subtotal: produto.preco
      }
      setCarrinho([...carrinho, novoItem])
    }
  }

  const removerDoCarrinho = (produtoId: number) => {
    const itemExistente = carrinho.find(item => item.produto_id === produtoId)
    
    if (itemExistente && itemExistente.quantidade > 1) {
      setCarrinho(carrinho.map(item =>
        item.produto_id === produtoId
          ? {
              ...item,
              quantidade: item.quantidade - 1,
              subtotal: (item.quantidade - 1) * item.preco_unitario
            }
          : item
      ))
    } else {
      setCarrinho(carrinho.filter(item => item.produto_id !== produtoId))
    }
  }

  const limparCarrinho = () => {
    setCarrinho([])
  }

  const finalizarVenda = async () => {
    if (carrinho.length === 0) return

    try {
      setLoading(true)
      const vendaData = {
        itens: carrinho.map(item => ({
          produto_id: item.produto_id,
          quantidade: item.quantidade,
          preco_unitario: item.preco_unitario
        })),
        forma_pagamento: 'dinheiro' as const
      }

      await pdvService.createVenda(vendaData)
      setCarrinho([])
      alert('Venda realizada com sucesso!')
    } catch (error) {
      console.error('Erro ao finalizar venda:', error)
      alert('Erro ao finalizar venda')
    } finally {
      setLoading(false)
    }
  }

  const produtosFiltrados = produtos.filter(produto =>
    produto.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
    produto.categoria.toLowerCase().includes(searchTerm.toLowerCase()) ||
    produto.codigo_barras?.includes(searchTerm)
  )

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">PDV - Ponto de Venda</h1>
        <div className="flex items-center space-x-4">
          <span className="text-lg font-semibold">
            Total: {formatCurrency(total)}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Lista de Produtos */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex space-x-4">
            <Input
              placeholder="Buscar produtos ou código de barras..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1"
            />
            <Button onClick={loadProdutos} disabled={loading}>
              Buscar
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {produtosFiltrados.map((produto) => (
              <Card key={produto.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="space-y-2">
                    <h3 className="font-medium line-clamp-2">{produto.nome}</h3>
                    <p className="text-sm text-gray-500">{produto.categoria}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-lg font-semibold text-green-600">
                        {formatCurrency(produto.preco)}
                      </span>
                      <span className="text-xs text-gray-500">
                        Estoque: {produto.estoque_atual}
                      </span>
                    </div>
                    <Button
                      onClick={() => adicionarAoCarrinho(produto)}
                      disabled={produto.estoque_atual <= 0}
                      className="w-full"
                      size="sm"
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Adicionar
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {produtosFiltrados.length === 0 && !loading && (
            <div className="text-center py-8">
              <Package className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">
                Nenhum produto encontrado
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Tente uma busca diferente.
              </p>
            </div>
          )}
        </div>

        {/* Carrinho */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <ShoppingCart className="h-5 w-5 mr-2" />
                Carrinho ({carrinho.length} {carrinho.length === 1 ? 'item' : 'itens'})
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {carrinho.length === 0 ? (
                <p className="text-gray-500 text-center py-4">
                  Carrinho vazio
                </p>
              ) : (
                <>
                  <div className="space-y-3 max-h-64 overflow-y-auto">
                    {carrinho.map((item) => (
                      <div key={item.produto_id} className="flex items-center justify-between p-2 border rounded">
                        <div className="flex-1">
                          <h4 className="text-sm font-medium line-clamp-1">
                            {item.produto?.nome}
                          </h4>
                          <p className="text-xs text-gray-500">
                            {formatCurrency(item.preco_unitario)} x {item.quantidade}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button
                            variant="outline"
                            size="icon"
                            onClick={() => removerDoCarrinho(item.produto_id)}
                            className="h-6 w-6"
                          >
                            <Minus className="h-3 w-3" />
                          </Button>
                          <span className="text-sm font-medium">{item.quantidade}</span>
                          <Button
                            variant="outline"
                            size="icon"
                            onClick={() => adicionarAoCarrinho(item.produto!)}
                            className="h-6 w-6"
                          >
                            <Plus className="h-3 w-3" />
                          </Button>
                        </div>
                        <div className="text-right ml-2">
                          <p className="text-sm font-semibold">
                            {formatCurrency(item.subtotal)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="border-t pt-4 space-y-3">
                    <div className="flex justify-between items-center text-lg font-semibold">
                      <span>Total:</span>
                      <span className="text-green-600">{formatCurrency(total)}</span>
                    </div>

                    <div className="space-y-2">
                      <Button
                        onClick={finalizarVenda}
                        disabled={loading}
                        className="w-full"
                      >
                        <CreditCard className="h-4 w-4 mr-2" />
                        Finalizar Venda
                      </Button>
                      <Button
                        variant="outline"
                        onClick={limparCarrinho}
                        className="w-full"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Limpar Carrinho
                      </Button>
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export { PDVPage }
