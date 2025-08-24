import React, { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { eventosService } from '../services/eventos'
import { pdvService } from '../services/pdv'
import { formatCurrency, formatDate } from '../lib/utils'
import { Calendar, ShoppingCart, TrendingUp, Users } from 'lucide-react'

interface DashboardStats {
  eventos: {
    total: number
    ativos: number
    finalizados: number
    participantes: number
  }
  vendas: {
    hoje: { quantidade: number; valor: number }
    produtos_baixo_estoque: number
  }
}

function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)

      // Carregar estatísticas em paralelo
      const [eventosStats, vendasHoje, produtosBaixoEstoque] = await Promise.all([
        eventosService.getEstatisticas(),
        pdvService.getVendasDia(),
        pdvService.getProdutosEstoqueBaixo()
      ])

      setStats({
        eventos: {
          total: eventosStats.total_eventos,
          ativos: eventosStats.eventos_ativos,
          finalizados: eventosStats.eventos_finalizados,
          participantes: eventosStats.total_participantes
        },
        vendas: {
          hoje: {
            quantidade: vendasHoje.total_quantidade,
            valor: vendasHoje.total_valor
          },
          produtos_baixo_estoque: produtosBaixoEstoque.length
        }
      })
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-20 bg-gray-200 rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Visão geral do sistema - {formatDate(new Date())}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total de Eventos */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Eventos</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.eventos.total || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.eventos.ativos || 0} ativos
            </p>
          </CardContent>
        </Card>

        {/* Total de Participantes */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Participantes</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.eventos.participantes || 0}</div>
            <p className="text-xs text-muted-foreground">
              Total nos eventos
            </p>
          </CardContent>
        </Card>

        {/* Vendas Hoje */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Vendas Hoje</CardTitle>
            <ShoppingCart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(stats?.vendas.hoje.valor || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              {stats?.vendas.hoje.quantidade || 0} vendas
            </p>
          </CardContent>
        </Card>

        {/* Produtos em Baixo Estoque */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Estoque Baixo</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {stats?.vendas.produtos_baixo_estoque || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Produtos precisam reposição
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Seções adicionais */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Eventos Recentes</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-500">
              Carregando eventos recentes...
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Vendas Recentes</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-500">
              Carregando vendas recentes...
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export { DashboardPage }
