import React, { useState, useEffect } from 'react';
import { 
  BarChart3, Users, Calendar, TrendingUp, 
  Eye, Zap, Brain, Target, Award, 
  ArrowUp, Activity
} from 'lucide-react';
import { 
  UltraButton, 
  UltraCard, 
  UltraBadge, 
  GradientTitle, 
  NeuralContainer,
  QuantumSpinner,
  UltraTooltip
} from '../ui/UltraModern';

interface DashboardStats {
  totalEventos: number;
  totalCheckins: number;
  receitaTotal: number;
  crescimentoMensal: number;
}

interface EventoAtivo {
  id: number;
  nome: string;
  checkins: number;
  capacidade: number;
  status: 'ativo' | 'pausado' | 'finalizado';
}

const UltraModernDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [eventosAtivos, setEventosAtivos] = useState<EventoAtivo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simular carregamento de dados
    setTimeout(() => {
      setStats({
        totalEventos: 127,
        totalCheckins: 15420,
        receitaTotal: 1247890,
        crescimentoMensal: 23.5
      });

      setEventosAtivos([
        { id: 1, nome: "Tech Conference 2025", checkins: 847, capacidade: 1000, status: 'ativo' },
        { id: 2, nome: "Music Festival", checkins: 2341, capacidade: 3000, status: 'ativo' },
        { id: 3, nome: "Business Summit", checkins: 156, capacidade: 200, status: 'pausado' }
      ]);

      setLoading(false);
    }, 2000);
  }, []);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  if (loading) {
    return (
      <NeuralContainer className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-6">
          <QuantumSpinner size="lg" />
          <GradientTitle level={3} glow>
            Carregando Dashboard...
          </GradientTitle>
          <p className="text-gray-400">Preparando seus dados em tempo real</p>
        </div>
      </NeuralContainer>
    );
  }

  return (
    <NeuralContainer className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
          <div>
            <GradientTitle level={1} glow>
              Dashboard IA
            </GradientTitle>
            <p className="text-xl text-gray-300 mt-2">
              Visão completa dos seus eventos em tempo real
            </p>
          </div>
          
          <div className="flex gap-4">
            <UltraButton variant="ghost" size="md">
              <Eye className="w-5 h-5 mr-2" />
              Modo Análise
            </UltraButton>
            <UltraButton variant="primary" size="md" glow shimmer>
              <Brain className="w-5 h-5 mr-2" />
              IA Insights
            </UltraButton>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          
          {/* Total Eventos */}
          <UltraCard variant="glass" hover glow>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium">Total Eventos</p>
                <p className="text-3xl font-black text-white mt-1">
                  {stats?.totalEventos}
                </p>
                <div className="flex items-center mt-2">
                  <ArrowUp className="w-4 h-4 text-green-400 mr-1" />
                  <span className="text-green-400 text-sm font-semibold">
                    +{stats?.crescimentoMensal}%
                  </span>
                  <span className="text-gray-400 text-sm ml-1">este mês</span>
                </div>
              </div>
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl blur-xl opacity-50" />
                <div className="relative bg-gradient-to-r from-purple-500 to-pink-500 p-4 rounded-2xl">
                  <Calendar className="w-8 h-8 text-white" />
                </div>
              </div>
            </div>
          </UltraCard>

          {/* Total Check-ins */}
          <UltraCard variant="glass" hover glow>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium">Total Check-ins</p>
                <p className="text-3xl font-black text-white mt-1">
                  {stats?.totalCheckins.toLocaleString()}
                </p>
                <div className="flex items-center mt-2">
                  <Activity className="w-4 h-4 text-cyan-400 mr-1" />
                  <span className="text-cyan-400 text-sm font-semibold">
                    Em tempo real
                  </span>
                </div>
              </div>
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-2xl blur-xl opacity-50" />
                <div className="relative bg-gradient-to-r from-cyan-500 to-blue-500 p-4 rounded-2xl">
                  <Users className="w-8 h-8 text-white" />
                </div>
              </div>
            </div>
          </UltraCard>

          {/* Receita Total */}
          <UltraCard variant="glass" hover glow>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium">Receita Total</p>
                <p className="text-3xl font-black text-white mt-1">
                  {formatCurrency(stats?.receitaTotal || 0)}
                </p>
                <div className="flex items-center mt-2">
                  <TrendingUp className="w-4 h-4 text-emerald-400 mr-1" />
                  <span className="text-emerald-400 text-sm font-semibold">
                    +15.2%
                  </span>
                  <span className="text-gray-400 text-sm ml-1">vs último mês</span>
                </div>
              </div>
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-emerald-500 to-green-500 rounded-2xl blur-xl opacity-50" />
                <div className="relative bg-gradient-to-r from-emerald-500 to-green-500 p-4 rounded-2xl">
                  <BarChart3 className="w-8 h-8 text-white" />
                </div>
              </div>
            </div>
          </UltraCard>

          {/* Performance IA */}
          <UltraCard variant="neural" hover glow>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium">Performance IA</p>
                <p className="text-3xl font-black text-white mt-1">98.7%</p>
                <div className="flex items-center mt-2">
                  <Zap className="w-4 h-4 text-yellow-400 mr-1" />
                  <span className="text-yellow-400 text-sm font-semibold">
                    Otimizado
                  </span>
                </div>
              </div>
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-2xl blur-xl opacity-50" />
                <div className="relative bg-gradient-to-r from-yellow-500 to-orange-500 p-4 rounded-2xl">
                  <Brain className="w-8 h-8 text-white" />
                </div>
              </div>
            </div>
          </UltraCard>
        </div>

        {/* Eventos Ativos */}
        <div className="grid lg:grid-cols-3 gap-8">
          
          {/* Lista de Eventos */}
          <div className="lg:col-span-2">
            <UltraCard variant="glass">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-white">Eventos Ativos</h3>
                <UltraBadge variant="primary" pulse>
                  {eventosAtivos.length} ativos
                </UltraBadge>
              </div>
              
              <div className="space-y-4">
                {eventosAtivos.map((evento) => (
                  <div 
                    key={evento.id}
                    className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all duration-300"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-lg font-semibold text-white">{evento.nome}</h4>
                      <UltraBadge 
                        variant={evento.status === 'ativo' ? 'success' : evento.status === 'pausado' ? 'warning' : 'secondary'}
                      >
                        {evento.status}
                      </UltraBadge>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="text-center">
                          <p className="text-2xl font-bold text-white">{evento.checkins}</p>
                          <p className="text-xs text-gray-400">Check-ins</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-white">{evento.capacidade}</p>
                          <p className="text-xs text-gray-400">Capacidade</p>
                        </div>
                      </div>
                      
                      <div className="flex gap-2">
                        <UltraTooltip content="Ver detalhes">
                          <UltraButton variant="ghost" size="sm">
                            <Eye className="w-4 h-4" />
                          </UltraButton>
                        </UltraTooltip>
                        <UltraTooltip content="Análise IA">
                          <UltraButton variant="secondary" size="sm">
                            <Brain className="w-4 h-4" />
                          </UltraButton>
                        </UltraTooltip>
                      </div>
                    </div>
                    
                    {/* Barra de Progresso */}
                    <div className="mt-4">
                      <div className="flex justify-between text-sm text-gray-400 mb-2">
                        <span>Ocupação</span>
                        <span>{Math.round((evento.checkins / evento.capacidade) * 100)}%</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div 
                          className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${(evento.checkins / evento.capacidade) * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </UltraCard>
          </div>

          {/* Insights IA */}
          <div>
            <UltraCard variant="gradient" glow>
              <div className="flex items-center mb-6">
                <div className="relative mr-3">
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl blur-lg opacity-50" />
                  <div className="relative bg-gradient-to-r from-purple-500 to-pink-500 p-2 rounded-xl">
                    <Brain className="w-6 h-6 text-white" />
                  </div>
                </div>
                <h3 className="text-xl font-bold text-white">Insights IA</h3>
              </div>
              
              <div className="space-y-4">
                <div className="backdrop-blur-xl bg-black/30 rounded-xl p-4">
                  <div className="flex items-center mb-2">
                    <Target className="w-4 h-4 text-emerald-400 mr-2" />
                    <span className="text-emerald-400 font-semibold text-sm">Oportunidade</span>
                  </div>
                  <p className="text-white text-sm">
                    O evento "Tech Conference" pode aumentar 15% na ocupação com otimização de horários.
                  </p>
                </div>
                
                <div className="backdrop-blur-xl bg-black/30 rounded-xl p-4">
                  <div className="flex items-center mb-2">
                    <Award className="w-4 h-4 text-yellow-400 mr-2" />
                    <span className="text-yellow-400 font-semibold text-sm">Destaque</span>
                  </div>
                  <p className="text-white text-sm">
                    Check-ins por biometria aumentaram 340% a velocidade de entrada.
                  </p>
                </div>
                
                <div className="backdrop-blur-xl bg-black/30 rounded-xl p-4">
                  <div className="flex items-center mb-2">
                    <TrendingUp className="w-4 h-4 text-blue-400 mr-2" />
                    <span className="text-blue-400 font-semibold text-sm">Tendência</span>
                  </div>
                  <p className="text-white text-sm">
                    Eventos noturnos têm 25% mais engajamento que eventos diurnos.
                  </p>
                </div>
              </div>
              
              <UltraButton variant="quantum" size="md" className="w-full mt-6" shimmer>
                <Brain className="w-4 h-4 mr-2" />
                Análise Completa
              </UltraButton>
            </UltraCard>
          </div>
        </div>
      </div>
    </NeuralContainer>
  );
};

export default UltraModernDashboard;
