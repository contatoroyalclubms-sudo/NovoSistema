import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  CalendarDaysIcon,
  ClockIcon,
  MapPinIcon,
  UsersIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  ViewColumnsIcon,
  ListBulletIcon,
  Squares2X2Icon
} from '@heroicons/react/24/outline';
import { format, startOfMonth, endOfMonth, startOfWeek, endOfWeek, addDays, isSameMonth, isSameDay, isToday, addMonths, subMonths, parseISO, isWithinInterval } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface Evento {
  id: string;
  nome: string;
  descricao?: string;
  tipo_evento: string;
  status: 'planejamento' | 'ativo' | 'pausado' | 'finalizado' | 'cancelado';
  data_inicio: string;
  data_fim: string;
  local_nome: string;
  local_endereco: string;
  capacidade_maxima?: number;
  valor_entrada: number;
  cor_primaria: string;
  cor_secundaria: string;
  logo_url?: string;
  banner_url?: string;
  organizador_nome?: string;
  total_participantes?: number;
  total_presentes?: number;
  total_confirmados?: number;
  receita_total?: number;
  tags?: string[];
  created_at: string;
  updated_at: string;
}

interface EventCalendarProps {
  eventos?: Evento[];
  onEventClick?: (evento: Evento) => void;
  onEventEdit?: (evento: Evento) => void;
  onEventDelete?: (evento: Evento) => void;
  onCreateEvent?: (date?: Date) => void;
  isLoading?: boolean;
}

type ViewMode = 'month' | 'week' | 'list' | 'grid';

const EventCalendar: React.FC<EventCalendarProps> = ({
  eventos = [],
  onEventClick,
  onEventEdit,
  onEventDelete,
  onCreateEvent,
  isLoading = false
}) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('month');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [showFilters, setShowFilters] = useState(false);

  // Filtrar eventos baseado nos filtros aplicados
  const filteredEventos = useMemo(() => {
    return eventos.filter(evento => {
      const matchesSearch = evento.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          evento.local_nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          evento.organizador_nome?.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesStatus = statusFilter === 'all' || evento.status === statusFilter;
      const matchesType = typeFilter === 'all' || evento.tipo_evento === typeFilter;
      
      return matchesSearch && matchesStatus && matchesType;
    });
  }, [eventos, searchTerm, statusFilter, typeFilter]);

  // Obter eventos para um dia específico
  const getEventsForDate = (date: Date): Evento[] => {
    return filteredEventos.filter(evento => {
      const eventStart = parseISO(evento.data_inicio);
      const eventEnd = parseISO(evento.data_fim);
      return isWithinInterval(date, { start: eventStart, end: eventEnd }) ||
             isSameDay(date, eventStart) ||
             isSameDay(date, eventEnd);
    });
  };

  // Gerar dias do calendário
  const calendarDays = useMemo(() => {
    const monthStart = startOfMonth(currentDate);
    const monthEnd = endOfMonth(currentDate);
    const calendarStart = startOfWeek(monthStart, { weekStartsOn: 0 }); // Domingo
    const calendarEnd = endOfWeek(monthEnd, { weekStartsOn: 0 });

    const days = [];
    let day = calendarStart;

    while (day <= calendarEnd) {
      days.push(day);
      day = addDays(day, 1);
    }

    return days;
  }, [currentDate]);

  // Componente para um evento individual
  const EventCard: React.FC<{ evento: Evento; compact?: boolean }> = ({ evento, compact = false }) => {
    const statusColors = {
      planejamento: 'bg-gray-100 text-gray-800 border-gray-200',
      ativo: 'bg-green-100 text-green-800 border-green-200',
      pausado: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      finalizado: 'bg-blue-100 text-blue-800 border-blue-200',
      cancelado: 'bg-red-100 text-red-800 border-red-200'
    };

    const statusLabels = {
      planejamento: 'Planejamento',
      ativo: 'Ativo',
      pausado: 'Pausado',
      finalizado: 'Finalizado',
      cancelado: 'Cancelado'
    };

    return (
      <motion.div
        layout
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className={`
          bg-white rounded-lg shadow-sm border hover:shadow-md transition-all cursor-pointer
          ${compact ? 'p-2' : 'p-4'}
        `}
        style={{ borderLeftColor: evento.cor_primaria, borderLeftWidth: '4px' }}
        onClick={() => onEventClick?.(evento)}
      >
        <div className="flex justify-between items-start mb-2">
          <h3 className={`font-semibold text-gray-900 ${compact ? 'text-sm' : 'text-base'} line-clamp-1`}>
            {evento.nome}
          </h3>
          
          <div className="flex items-center space-x-1">
            <span className={`
              px-2 py-1 rounded-full text-xs font-medium border
              ${statusColors[evento.status]}
            `}>
              {statusLabels[evento.status]}
            </span>
            
            {!compact && (
              <div className="flex items-center space-x-1 ml-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onEventEdit?.(evento);
                  }}
                  className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                  title="Editar evento"
                >
                  <PencilIcon className="w-4 h-4" />
                </button>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onEventDelete?.(evento);
                  }}
                  className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                  title="Excluir evento"
                >
                  <TrashIcon className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        </div>

        <div className={`space-y-1 ${compact ? 'text-xs' : 'text-sm'} text-gray-600`}>
          <div className="flex items-center space-x-1">
            <ClockIcon className="w-3 h-3 flex-shrink-0" />
            <span>
              {format(parseISO(evento.data_inicio), 'dd/MM HH:mm', { locale: ptBR })}
              {!isSameDay(parseISO(evento.data_inicio), parseISO(evento.data_fim)) && (
                <> - {format(parseISO(evento.data_fim), 'dd/MM HH:mm', { locale: ptBR })}</>
              )}
            </span>
          </div>
          
          <div className="flex items-center space-x-1">
            <MapPinIcon className="w-3 h-3 flex-shrink-0" />
            <span className="truncate">{evento.local_nome}</span>
          </div>
          
          {!compact && (
            <>
              {evento.total_participantes !== undefined && (
                <div className="flex items-center space-x-1">
                  <UsersIcon className="w-3 h-3 flex-shrink-0" />
                  <span>{evento.total_participantes} participantes</span>
                </div>
              )}
              
              {evento.valor_entrada > 0 && (
                <div className="flex items-center justify-between">
                  <span className="font-medium text-green-600">
                    R$ {evento.valor_entrada.toFixed(2)}
                  </span>
                  {evento.receita_total && (
                    <span className="text-xs text-gray-500">
                      Total: R$ {evento.receita_total.toFixed(2)}
                    </span>
                  )}
                </div>
              )}
            </>
          )}
        </div>

        {!compact && evento.tags && evento.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {evento.tags.slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
              >
                {tag}
              </span>
            ))}
            {evento.tags.length > 3 && (
              <span className="text-xs text-gray-500">+{evento.tags.length - 3}</span>
            )}
          </div>
        )}
      </motion.div>
    );
  };

  // Vista de mês
  const MonthView = () => (
    <div className="bg-white rounded-lg shadow-sm border">
      {/* Header do calendário */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setCurrentDate(subMonths(currentDate, 1))}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ChevronLeftIcon className="w-5 h-5" />
          </button>
          
          <h2 className="text-xl font-semibold text-gray-900">
            {format(currentDate, 'MMMM yyyy', { locale: ptBR })}
          </h2>
          
          <button
            onClick={() => setCurrentDate(addMonths(currentDate, 1))}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ChevronRightIcon className="w-5 h-5" />
          </button>
        </div>
        
        <button
          onClick={() => setCurrentDate(new Date())}
          className="px-3 py-1 text-sm text-blue-600 hover:text-blue-800 transition-colors"
        >
          Hoje
        </button>
      </div>

      {/* Dias da semana */}
      <div className="grid grid-cols-7 border-b">
        {['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'].map(day => (
          <div key={day} className="p-3 text-center text-sm font-medium text-gray-700 border-r last:border-r-0">
            {day}
          </div>
        ))}
      </div>

      {/* Calendário */}
      <div className="grid grid-cols-7">
        {calendarDays.map((day, index) => {
          const dayEvents = getEventsForDate(day);
          const isCurrentMonth = isSameMonth(day, currentDate);
          const isSelectedDay = selectedDate && isSameDay(day, selectedDate);
          const isTodayDay = isToday(day);

          return (
            <div
              key={index}
              className={`
                min-h-[120px] p-2 border-r border-b last:border-r-0 cursor-pointer transition-colors
                ${!isCurrentMonth ? 'bg-gray-50' : ''}
                ${isSelectedDay ? 'bg-blue-50' : ''}
                ${isTodayDay ? 'bg-yellow-50' : ''}
                hover:bg-gray-50
              `}
              onClick={() => setSelectedDate(day)}
              onDoubleClick={() => onCreateEvent?.(day)}
            >
              <div className="flex justify-between items-start mb-1">
                <span className={`
                  text-sm font-medium
                  ${!isCurrentMonth ? 'text-gray-400' : 'text-gray-900'}
                  ${isTodayDay ? 'text-blue-600' : ''}
                `}>
                  {format(day, 'd')}
                </span>
                
                {dayEvents.length > 0 && (
                  <span className="bg-blue-100 text-blue-800 text-xs px-1 rounded-full">
                    {dayEvents.length}
                  </span>
                )}
              </div>

              <div className="space-y-1">
                {dayEvents.slice(0, 2).map(evento => (
                  <div
                    key={evento.id}
                    className="px-2 py-1 rounded text-xs font-medium text-white truncate"
                    style={{ backgroundColor: evento.cor_primaria }}
                    title={evento.nome}
                  >
                    {evento.nome}
                  </div>
                ))}
                
                {dayEvents.length > 2 && (
                  <div className="text-xs text-gray-500 px-1">
                    +{dayEvents.length - 2} mais
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );

  // Vista de lista
  const ListView = () => (
    <div className="space-y-4">
      {filteredEventos.length > 0 ? (
        filteredEventos.map(evento => (
          <EventCard key={evento.id} evento={evento} />
        ))
      ) : (
        <div className="text-center py-12">
          <CalendarDaysIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">Nenhum evento encontrado</p>
        </div>
      )}
    </div>
  );

  // Vista de grid
  const GridView = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {filteredEventos.length > 0 ? (
        filteredEventos.map(evento => (
          <EventCard key={evento.id} evento={evento} />
        ))
      ) : (
        <div className="col-span-full text-center py-12">
          <CalendarDaysIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">Nenhum evento encontrado</p>
        </div>
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header com filtros e controles */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-bold text-gray-900">Calendário de Eventos</h1>
          
          {onCreateEvent && (
            <button
              onClick={() => onCreateEvent()}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <PlusIcon className="w-4 h-4 mr-2" />
              Novo Evento
            </button>
          )}
        </div>

        <div className="flex items-center space-x-4">
          {/* Busca */}
          <div className="relative">
            <MagnifyingGlassIcon className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Buscar eventos..."
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Filtros */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`flex items-center px-3 py-2 border rounded-lg transition-colors ${
              showFilters ? 'bg-blue-50 border-blue-200 text-blue-700' : 'border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            <FunnelIcon className="w-4 h-4 mr-2" />
            Filtros
          </button>

          {/* Seletor de vista */}
          <div className="flex items-center border border-gray-300 rounded-lg">
            <button
              onClick={() => setViewMode('month')}
              className={`p-2 ${viewMode === 'month' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'} transition-colors`}
              title="Vista mensal"
            >
              <CalendarDaysIcon className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 border-l ${viewMode === 'list' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'} transition-colors`}
              title="Vista de lista"
            >
              <ListBulletIcon className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 border-l ${viewMode === 'grid' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'} transition-colors`}
              title="Vista de grade"
            >
              <Squares2X2Icon className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Painel de filtros */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-white rounded-lg shadow-sm border p-4"
          >
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Status
                </label>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">Todos os status</option>
                  <option value="planejamento">Planejamento</option>
                  <option value="ativo">Ativo</option>
                  <option value="pausado">Pausado</option>
                  <option value="finalizado">Finalizado</option>
                  <option value="cancelado">Cancelado</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tipo de Evento
                </label>
                <select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">Todos os tipos</option>
                  <option value="festa">Festa</option>
                  <option value="show">Show</option>
                  <option value="conferencia">Conferência</option>
                  <option value="workshop">Workshop</option>
                  <option value="networking">Networking</option>
                  <option value="corporativo">Corporativo</option>
                  <option value="casamento">Casamento</option>
                  <option value="aniversario">Aniversário</option>
                  <option value="outro">Outro</option>
                </select>
              </div>

              <div className="flex items-end">
                <button
                  onClick={() => {
                    setSearchTerm('');
                    setStatusFilter('all');
                    setTypeFilter('all');
                  }}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                >
                  Limpar Filtros
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Conteúdo principal */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-500 mt-4">Carregando eventos...</p>
        </div>
      ) : (
        <AnimatePresence mode="wait">
          <motion.div
            key={viewMode}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            {viewMode === 'month' && <MonthView />}
            {viewMode === 'list' && <ListView />}
            {viewMode === 'grid' && <GridView />}
          </motion.div>
        </AnimatePresence>
      )}

      {/* Detalhes do dia selecionado */}
      <AnimatePresence>
        {selectedDate && viewMode === 'month' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-white rounded-lg shadow-sm border p-6"
          >
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                {format(selectedDate, "d 'de' MMMM 'de' yyyy", { locale: ptBR })}
              </h3>
              <button
                onClick={() => setSelectedDate(null)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                ×
              </button>
            </div>

            <div className="space-y-3">
              {getEventsForDate(selectedDate).length > 0 ? (
                getEventsForDate(selectedDate).map(evento => (
                  <EventCard key={evento.id} evento={evento} compact />
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <CalendarDaysIcon className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                  <p>Nenhum evento neste dia</p>
                  {onCreateEvent && (
                    <button
                      onClick={() => onCreateEvent(selectedDate)}
                      className="mt-2 text-blue-600 hover:text-blue-800 transition-colors"
                    >
                      Criar evento para este dia
                    </button>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default EventCalendar;