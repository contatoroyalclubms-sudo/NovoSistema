/**
 * Interactive Charts Component - Sprint 5
 * Sistema Universal de Gestão de Eventos
 * 
 * Advanced chart components with:
 * - Interactive visualizations
 * - Real-time data updates
 * - Customizable filters
 * - Export capabilities
 * - Responsive design
 */

import React, { useState, useMemo, useCallback } from 'react';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  ScatterChart, Scatter, FunnelChart, Funnel, LabelList
} from 'recharts';
import { 
  TrendingUp, TrendingDown, Download, Filter, Calendar, 
  BarChart3, PieChart as PieChartIcon, Activity, Zap 
} from 'lucide-react';

interface ChartData {
  name: string;
  value: number;
  [key: string]: any;
}

interface FilterOptions {
  dateRange: 'day' | 'week' | 'month' | 'quarter' | 'year';
  category?: string;
  eventType?: string;
}

interface InteractiveChartProps {
  data: ChartData[];
  type: 'line' | 'area' | 'bar' | 'pie' | 'radar' | 'scatter' | 'funnel';
  title: string;
  description?: string;
  height?: number;
  xDataKey?: string;
  yDataKey?: string;
  colors?: string[];
  showFilters?: boolean;
  showExport?: boolean;
  animate?: boolean;
  onDataClick?: (data: any) => void;
  onFilterChange?: (filters: FilterOptions) => void;
}

const DEFAULT_COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1'
];

const CustomTooltip = ({ active, payload, label, formatter }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
        <p className="text-gray-900 font-medium">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-sm" style={{ color: entry.color }}>
            {`${entry.name}: ${formatter ? formatter(entry.value) : entry.value}`}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const ChartFilters: React.FC<{
  onFilterChange: (filters: FilterOptions) => void;
  currentFilters: FilterOptions;
}> = ({ onFilterChange, currentFilters }) => {
  return (
    <div className="flex items-center space-x-4 mb-4">
      <div className="flex items-center space-x-2">
        <Calendar className="h-4 w-4 text-gray-500" />
        <select
          value={currentFilters.dateRange}
          onChange={(e) => onFilterChange({
            ...currentFilters,
            dateRange: e.target.value as FilterOptions['dateRange']
          })}
          className="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="day">Último dia</option>
          <option value="week">Última semana</option>
          <option value="month">Último mês</option>
          <option value="quarter">Último trimestre</option>
          <option value="year">Último ano</option>
        </select>
      </div>
      
      <div className="flex items-center space-x-2">
        <Filter className="h-4 w-4 text-gray-500" />
        <select
          value={currentFilters.category || ''}
          onChange={(e) => onFilterChange({
            ...currentFilters,
            category: e.target.value || undefined
          })}
          className="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Todas categorias</option>
          <option value="eventos">Eventos</option>
          <option value="checkin">Check-in</option>
          <option value="vendas">Vendas</option>
          <option value="usuarios">Usuários</option>
        </select>
      </div>
    </div>
  );
};

const ExportButton: React.FC<{ onExport: (format: 'png' | 'pdf' | 'csv') => void }> = ({ onExport }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-1 px-3 py-1 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded hover:bg-gray-50"
      >
        <Download className="h-4 w-4" />
        <span>Exportar</span>
      </button>
      
      {isOpen && (
        <div className="absolute right-0 mt-1 w-32 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
          <button
            onClick={() => { onExport('png'); setIsOpen(false); }}
            className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50"
          >
            PNG
          </button>
          <button
            onClick={() => { onExport('pdf'); setIsOpen(false); }}
            className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50"
          >
            PDF
          </button>
          <button
            onClick={() => { onExport('csv'); setIsOpen(false); }}
            className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50"
          >
            CSV
          </button>
        </div>
      )}
    </div>
  );
};

export const InteractiveChart: React.FC<InteractiveChartProps> = ({
  data,
  type,
  title,
  description,
  height = 300,
  xDataKey = 'name',
  yDataKey = 'value',
  colors = DEFAULT_COLORS,
  showFilters = false,
  showExport = false,
  animate = true,
  onDataClick,
  onFilterChange
}) => {
  const [filters, setFilters] = useState<FilterOptions>({
    dateRange: 'month'
  });

  const handleFilterChange = useCallback((newFilters: FilterOptions) => {
    setFilters(newFilters);
    onFilterChange?.(newFilters);
  }, [onFilterChange]);

  const handleExport = useCallback((format: 'png' | 'pdf' | 'csv') => {
    // Implementar lógica de exportação
    console.log(`Exportando gráfico como ${format}`);
  }, []);

  const processedData = useMemo(() => {
    // Aplicar filtros aos dados
    let filtered = [...data];
    
    // Aqui seria aplicada a lógica de filtro baseada nas opções
    // Por simplicidade, retornando dados originais
    
    return filtered;
  }, [data, filters]);

  const renderChart = () => {
    const commonProps = {
      data: processedData,
      width: '100%',
      height,
      onClick: onDataClick
    };

    switch (type) {
      case 'line':
        return (
          <ResponsiveContainer {...commonProps}>
            <LineChart data={processedData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey={xDataKey} 
                tick={{ fontSize: 12 }}
                stroke="#666"
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                stroke="#666"
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line
                type="monotone"
                dataKey={yDataKey}
                stroke={colors[0]}
                strokeWidth={2}
                dot={{ fill: colors[0], strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: colors[0], strokeWidth: 0 }}
                animationDuration={animate ? 1000 : 0}
              />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'area':
        return (
          <ResponsiveContainer {...commonProps}>
            <AreaChart data={processedData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey={xDataKey} 
                tick={{ fontSize: 12 }}
                stroke="#666"
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                stroke="#666"
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey={yDataKey}
                stroke={colors[0]}
                fill={colors[0]}
                fillOpacity={0.3}
                animationDuration={animate ? 1000 : 0}
              />
            </AreaChart>
          </ResponsiveContainer>
        );

      case 'bar':
        return (
          <ResponsiveContainer {...commonProps}>
            <BarChart data={processedData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey={xDataKey} 
                tick={{ fontSize: 12 }}
                stroke="#666"
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                stroke="#666"
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar 
                dataKey={yDataKey} 
                fill={colors[0]}
                radius={[2, 2, 0, 0]}
                animationDuration={animate ? 1000 : 0}
              />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'pie':
        return (
          <ResponsiveContainer {...commonProps}>
            <PieChart>
              <Pie
                data={processedData}
                cx="50%"
                cy="50%"
                outerRadius={Math.min(height * 0.35, 120)}
                fill="#8884d8"
                dataKey={yDataKey}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                animationDuration={animate ? 1000 : 0}
              >
                {processedData.map((_, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={colors[index % colors.length]} 
                  />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        );

      case 'radar':
        return (
          <ResponsiveContainer {...commonProps}>
            <RadarChart data={processedData}>
              <PolarGrid />
              <PolarAngleAxis dataKey={xDataKey} tick={{ fontSize: 12 }} />
              <PolarRadiusAxis tick={{ fontSize: 12 }} />
              <Radar
                name="Values"
                dataKey={yDataKey}
                stroke={colors[0]}
                fill={colors[0]}
                fillOpacity={0.3}
                animationDuration={animate ? 1000 : 0}
              />
              <Tooltip content={<CustomTooltip />} />
            </RadarChart>
          </ResponsiveContainer>
        );

      case 'scatter':
        return (
          <ResponsiveContainer {...commonProps}>
            <ScatterChart data={processedData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey={xDataKey} 
                tick={{ fontSize: 12 }}
                stroke="#666"
              />
              <YAxis 
                dataKey={yDataKey}
                tick={{ fontSize: 12 }}
                stroke="#666"
              />
              <Tooltip content={<CustomTooltip />} />
              <Scatter 
                fill={colors[0]}
                animationDuration={animate ? 1000 : 0}
              />
            </ScatterChart>
          </ResponsiveContainer>
        );

      case 'funnel':
        return (
          <ResponsiveContainer {...commonProps}>
            <FunnelChart>
              <Tooltip content={<CustomTooltip />} />
              <Funnel
                dataKey={yDataKey}
                data={processedData}
                isAnimationActive={animate}
                animationDuration={1000}
              >
                <LabelList position="center" fill="#fff" stroke="none" />
                {processedData.map((_, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={colors[index % colors.length]} 
                  />
                ))}
              </Funnel>
            </FunnelChart>
          </ResponsiveContainer>
        );

      default:
        return <div>Tipo de gráfico não suportado</div>;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          {description && (
            <p className="text-sm text-gray-600 mt-1">{description}</p>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          {showExport && (
            <ExportButton onExport={handleExport} />
          )}
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <ChartFilters
          currentFilters={filters}
          onFilterChange={handleFilterChange}
        />
      )}

      {/* Chart */}
      <div className="w-full">
        {processedData.length > 0 ? (
          renderChart()
        ) : (
          <div className="flex items-center justify-center h-64 text-gray-500">
            <div className="text-center">
              <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>Nenhum dado disponível</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Componente para múltiplos gráficos
interface AnalyticsDashboardProps {
  charts: Array<{
    id: string;
    data: ChartData[];
    type: InteractiveChartProps['type'];
    title: string;
    description?: string;
    colSpan?: 1 | 2;
  }>;
}

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ charts }) => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {charts.map((chart) => (
          <div
            key={chart.id}
            className={chart.colSpan === 2 ? 'lg:col-span-2' : ''}
          >
            <InteractiveChart
              data={chart.data}
              type={chart.type}
              title={chart.title}
              description={chart.description}
              showFilters={true}
              showExport={true}
              animate={true}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

// Componente de comparação temporal
interface TrendComparisonProps {
  currentData: ChartData[];
  previousData: ChartData[];
  title: string;
  metric: string;
  timeframe: string;
}

export const TrendComparison: React.FC<TrendComparisonProps> = ({
  currentData,
  previousData,
  title,
  metric,
  timeframe
}) => {
  const currentTotal = currentData.reduce((sum, item) => sum + item.value, 0);
  const previousTotal = previousData.reduce((sum, item) => sum + item.value, 0);
  const change = previousTotal > 0 ? ((currentTotal - previousTotal) / previousTotal) * 100 : 0;
  const isPositive = change >= 0;

  const combinedData = currentData.map((current, index) => ({
    name: current.name,
    current: current.value,
    previous: previousData[index]?.value || 0
  }));

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600">Comparação com {timeframe} anterior</p>
        </div>
        
        <div className="text-right">
          <div className="text-2xl font-bold text-gray-900">
            {new Intl.NumberFormat('pt-BR').format(currentTotal)}
          </div>
          <div className={`flex items-center justify-end mt-1 ${
            isPositive ? 'text-green-600' : 'text-red-600'
          }`}>
            {isPositive ? (
              <TrendingUp className="h-4 w-4 mr-1" />
            ) : (
              <TrendingDown className="h-4 w-4 mr-1" />
            )}
            <span className="text-sm font-medium">
              {Math.abs(change).toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={combinedData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Bar dataKey="previous" fill="#94a3b8" name="Anterior" />
          <Bar dataKey="current" fill="#3b82f6" name="Atual" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default InteractiveChart;