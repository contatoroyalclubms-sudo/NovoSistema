import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { eventosService, Evento } from '../services/eventos'
import { formatDate, formatCurrency } from '../lib/utils'
import { Calendar, MapPin, Users, Plus, Search } from 'lucide-react'

function EventosPage() {
  const [eventos, setEventos] = useState<Evento[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filteredEventos, setFilteredEventos] = useState<Evento[]>([])

  useEffect(() => {
    loadEventos()
  }, [])

  useEffect(() => {
    if (searchTerm) {
      setFilteredEventos(
        eventos.filter(evento =>
          evento.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
          evento.descricao?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          evento.categoria?.toLowerCase().includes(searchTerm.toLowerCase())
        )
      )
    } else {
      setFilteredEventos(eventos)
    }
  }, [searchTerm, eventos])

  const loadEventos = async () => {
    try {
      setLoading(true)
      const response = await eventosService.getEventos(1, 20)
      setEventos(response.data)
      setFilteredEventos(response.data)
    } catch (error) {
      console.error('Erro ao carregar eventos:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ativo': return 'bg-green-100 text-green-800'
      case 'planejado': return 'bg-blue-100 text-blue-800'
      case 'finalizado': return 'bg-gray-100 text-gray-800'
      case 'cancelado': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Eventos</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
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
        <h1 className="text-3xl font-bold text-gray-900">Gestão de Eventos</h1>
        <Button className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Novo Evento
        </Button>
      </div>

      {/* Barra de busca */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="Buscar eventos..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Lista de eventos */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredEventos.map((evento) => (
          <Card key={evento.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <CardTitle className="text-lg line-clamp-2">{evento.nome}</CardTitle>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(evento.status)}`}>
                  {evento.status}
                </span>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {evento.descricao && (
                <p className="text-sm text-gray-600 line-clamp-2">
                  {evento.descricao}
                </p>
              )}
              
              <div className="space-y-2">
                <div className="flex items-center text-sm text-gray-500">
                  <Calendar className="h-4 w-4 mr-2" />
                  {formatDate(evento.data_inicio)} - {formatDate(evento.data_fim)}
                </div>
                
                {evento.local && (
                  <div className="flex items-center text-sm text-gray-500">
                    <MapPin className="h-4 w-4 mr-2" />
                    {evento.local}
                  </div>
                )}
                
                <div className="flex items-center text-sm text-gray-500">
                  <Users className="h-4 w-4 mr-2" />
                  {evento.participantes_atuais}/{evento.capacidade_maxima || '∞'} participantes
                </div>
              </div>

              {evento.preco && evento.preco > 0 && (
                <div className="text-lg font-semibold text-green-600">
                  {formatCurrency(evento.preco)}
                </div>
              )}

              <div className="flex space-x-2">
                <Button variant="outline" size="sm" className="flex-1">
                  Ver Detalhes
                </Button>
                <Button size="sm" className="flex-1">
                  Gerenciar
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredEventos.length === 0 && !loading && (
        <div className="text-center py-12">
          <Calendar className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Nenhum evento encontrado</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm ? 'Tente uma busca diferente.' : 'Comece criando um novo evento.'}
          </p>
          {!searchTerm && (
            <div className="mt-6">
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Criar Primeiro Evento
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export { EventosPage }
