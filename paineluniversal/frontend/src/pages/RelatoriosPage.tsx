import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { eventosService } from '../services/eventos'
import { pdvService } from '../services/pdv'
import { formatCurrency, formatDate } from '../lib/utils'
import { BarChart3, Download, Calendar, DollarSign, TrendingUp, Users } from 'lucide-react'

export default function RelatoriosPage() {
  const [stats, setStats] = useState<any>(null)
  const [vendas, setVendas] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [dateRange, setDateRange] = useState({
    inicio: '',
    fim: ''
  })

  useEffect(() => {
    loadRelatorios()
  }, [])

  const loadRelatorios = async () => {
    try {
      setLoading(true)
      
      // Carregar dados em paralelo
      const [eventosStats, relatorioVendas, vendasDia] = await Promise.all([
        eventosService.getEstatisticas(),
        pdvService.getRelatorioVendas(dateRange.inicio, dateRange.fim),
        pdvService.getVendasDia()
      ])

      setStats(eventosStats)
      setVendas({ relatorio: relatorioVendas, hoje: vendasDia })
    } catch (error) {
      console.error('Erro ao carregar relatórios:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDateFilter = () => {
    loadRelatorios()
  }

  const exportarRelatorio = () => {
    // Simular export de relatório
    alert('Funcionalidade de exportação será implementada em breve!')
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Relatórios</h1>
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
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Relatórios e Análises</h1>
        <Button onClick={exportarRelatorio} className="flex items-center gap-2">
          <Download className="h-4 w-4" />
          Exportar Relatório
        </Button>
      </div>

      {/* Filtros de data */}
      <Card>
        <CardHeader>
          <CardTitle>Filtros</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <Input
                type="date"
                label="Data Início"
                value={dateRange.inicio}
                onChange={(e) => setDateRange(prev => ({ ...prev, inicio: e.target.value }))}
              />
            </div>
            <div className="flex-1">
              <Input
                type="date"
                label="Data Fim"
                value={dateRange.fim}
                onChange={(e) => setDateRange(prev => ({ ...prev, fim: e.target.value }))}
              />
            </div>
            <Button onClick={handleDateFilter}>
              Aplicar Filtros
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Métricas Principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Eventos</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_eventos || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.eventos_ativos || 0} ativos
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Vendas Hoje</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(vendas?.hoje?.total_valor || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              {vendas?.hoje?.total_quantidade || 0} transações
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Vendas</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(vendas?.relatorio?.total_valor || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              {vendas?.relatorio?.total_vendas || 0} vendas no período
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Participantes</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_participantes || 0}</div>
            <p className="text-xs text-muted-foreground">
              Em todos os eventos
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Gráficos e Tabelas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Produtos Mais Vendidos */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart3 className="h-5 w-5 mr-2" />
              Produtos Mais Vendidos
            </CardTitle>
          </CardHeader>
          <CardContent>
            {vendas?.relatorio?.produtos_mais_vendidos?.length > 0 ? (
              <div className="space-y-4">
                {vendas.relatorio.produtos_mais_vendidos.slice(0, 5).map((item: any, index: number) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="text-sm font-medium">{item.produto?.nome}</h4>
                      <p className="text-xs text-gray-500">
                        {item.quantidade_total} unidades vendidas
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold">
                        {formatCurrency(item.valor_total)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">
                Nenhum dado de vendas disponível
              </p>
            )}
          </CardContent>
        </Card>

        {/* Eventos por Categoria */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Calendar className="h-5 w-5 mr-2" />
              Eventos por Categoria
            </CardTitle>
          </CardHeader>
          <CardContent>
            {stats?.eventos_por_categoria && Object.keys(stats.eventos_por_categoria).length > 0 ? (
              <div className="space-y-4">
                {Object.entries(stats.eventos_por_categoria).map(([categoria, quantidade]: [string, any]) => (
                  <div key={categoria} className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="text-sm font-medium capitalize">{categoria}</h4>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold">{quantidade} eventos</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">
                Nenhum evento por categoria disponível
              </p>
            )}
          </CardContent>
        </Card>

        {/* Ranking de Vendedores */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Users className="h-5 w-5 mr-2" />
              Ranking de Vendedores
            </CardTitle>
          </CardHeader>
          <CardContent>
            {vendas?.relatorio?.vendedores_ranking?.length > 0 ? (
              <div className="space-y-4">
                {vendas.relatorio.vendedores_ranking.slice(0, 5).map((vendedor: any, index: number) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-200">
                        <span className="text-xs font-medium">#{index + 1}</span>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium">
                          {vendedor.vendedor?.full_name || vendedor.vendedor?.username}
                        </h4>
                        <p className="text-xs text-gray-500">
                          {vendedor.total_vendas} vendas
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold">
                        {formatCurrency(vendedor.total_valor)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">
                Nenhum dado de vendedor disponível
              </p>
            )}
          </CardContent>
        </Card>

        {/* Vendas por Dia */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="h-5 w-5 mr-2" />
              Vendas por Dia
            </CardTitle>
          </CardHeader>
          <CardContent>
            {vendas?.relatorio?.vendas_por_dia?.length > 0 ? (
              <div className="space-y-4">
                {vendas.relatorio.vendas_por_dia.slice(-7).map((dia: any, index: number) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="text-sm font-medium">{formatDate(dia.data)}</h4>
                      <p className="text-xs text-gray-500">
                        {dia.quantidade} vendas
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold">
                        {formatCurrency(dia.valor)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">
                Nenhum dado de vendas diárias disponível
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
