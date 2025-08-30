import React, { useState, useEffect } from 'react';
import { 
  Scan, User, CheckCircle, AlertTriangle, 
  Fingerprint, Eye, Brain, Zap, Shield, 
  Clock, Users, BarChart3, Activity
} from 'lucide-react';
import { 
  UltraButton, 
  UltraCard, 
  UltraBadge, 
  GradientTitle, 
  NeuralContainer,
  UltraInput,
  QuantumSpinner,
  UltraTooltip
} from '../ui/UltraModern';

interface CheckinData {
  id: string;
  nome: string;
  documento: string;
  metodo: 'qr' | 'biometria' | 'documento';
  timestamp: Date;
  status: 'sucesso' | 'erro' | 'pendente';
}

interface EventoStats {
  totalCheckins: number;
  capacidade: number;
  checkinsHora: number;
  tempoMedio: number;
}

const UltraModernCheckin: React.FC = () => {
  const [metodoAtivo, setMetodoAtivo] = useState<'qr' | 'biometria' | 'documento'>('qr');
  const [documentoInput, setDocumentoInput] = useState('');
  const [checkinsRecentes, setCheckinsRecentes] = useState<CheckinData[]>([]);
  const [stats, setStats] = useState<EventoStats | null>(null);
  const [scanning, setScanning] = useState(false);
  const [biometriaAtiva, setBiometriaAtiva] = useState(false);

  useEffect(() => {
    // Simular dados em tempo real
    setStats({
      totalCheckins: 1247,
      capacidade: 2000,
      checkinsHora: 156,
      tempoMedio: 2.3
    });

    setCheckinsRecentes([
      {
        id: '1',
        nome: 'Maria Silva',
        documento: '123.456.789-01',
        metodo: 'biometria',
        timestamp: new Date(),
        status: 'sucesso'
      },
      {
        id: '2',
        nome: 'João Santos',
        documento: '987.654.321-02',
        metodo: 'qr',
        timestamp: new Date(Date.now() - 30000),
        status: 'sucesso'
      },
      {
        id: '3',
        nome: 'Ana Costa',
        documento: '456.789.123-03',
        metodo: 'documento',
        timestamp: new Date(Date.now() - 60000),
        status: 'erro'
      }
    ]);
  }, []);

  const handleCheckin = async () => {
    setScanning(true);
    
    // Simular processo de check-in
    setTimeout(() => {
      const novoCheckin: CheckinData = {
        id: Math.random().toString(),
        nome: 'Participante ' + Math.floor(Math.random() * 1000),
        documento: documentoInput || 'Escaneado',
        metodo: metodoAtivo,
        timestamp: new Date(),
        status: 'sucesso'
      };

      setCheckinsRecentes(prev => [novoCheckin, ...prev.slice(0, 9)]);
      setStats(prev => prev ? { ...prev, totalCheckins: prev.totalCheckins + 1 } : null);
      setDocumentoInput('');
      setScanning(false);
    }, 2000);
  };

  const ativarBiometria = () => {
    setBiometriaAtiva(true);
    setMetodoAtivo('biometria');
    setTimeout(() => setBiometriaAtiva(false), 5000);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'sucesso': return 'text-green-400';
      case 'erro': return 'text-red-400';
      case 'pendente': return 'text-yellow-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'sucesso': return <CheckCircle className="w-4 h-4" />;
      case 'erro': return <AlertTriangle className="w-4 h-4" />;
      case 'pendente': return <Clock className="w-4 h-4" />;
      default: return <User className="w-4 h-4" />;
    }
  };

  return (
    <NeuralContainer className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="text-center mb-12">
          <GradientTitle level={1} glow>
            Check-in Inteligente
          </GradientTitle>
          <p className="text-xl text-gray-300 mt-4">
            Sistema de entrada com IA, biometria e reconhecimento avançado
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <UltraCard variant="glass" hover>
            <div className="text-center">
              <div className="relative mb-4">
                <div className="absolute inset-0 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-2xl blur-xl opacity-50" />
                <div className="relative bg-gradient-to-r from-emerald-500 to-cyan-500 p-3 rounded-2xl w-fit mx-auto">
                  <Users className="w-8 h-8 text-white" />
                </div>
              </div>
              <p className="text-3xl font-black text-white">{stats?.totalCheckins}</p>
              <p className="text-gray-400 text-sm">Total Check-ins</p>
            </div>
          </UltraCard>

          <UltraCard variant="glass" hover>
            <div className="text-center">
              <div className="relative mb-4">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl blur-xl opacity-50" />
                <div className="relative bg-gradient-to-r from-blue-500 to-purple-500 p-3 rounded-2xl w-fit mx-auto">
                  <BarChart3 className="w-8 h-8 text-white" />
                </div>
              </div>
              <p className="text-3xl font-black text-white">{stats?.capacidade}</p>
              <p className="text-gray-400 text-sm">Capacidade</p>
            </div>
          </UltraCard>

          <UltraCard variant="glass" hover>
            <div className="text-center">
              <div className="relative mb-4">
                <div className="absolute inset-0 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-2xl blur-xl opacity-50" />
                <div className="relative bg-gradient-to-r from-yellow-500 to-orange-500 p-3 rounded-2xl w-fit mx-auto">
                  <Activity className="w-8 h-8 text-white" />
                </div>
              </div>
              <p className="text-3xl font-black text-white">{stats?.checkinsHora}</p>
              <p className="text-gray-400 text-sm">Por Hora</p>
            </div>
          </UltraCard>

          <UltraCard variant="glass" hover>
            <div className="text-center">
              <div className="relative mb-4">
                <div className="absolute inset-0 bg-gradient-to-r from-pink-500 to-red-500 rounded-2xl blur-xl opacity-50" />
                <div className="relative bg-gradient-to-r from-pink-500 to-red-500 p-3 rounded-2xl w-fit mx-auto">
                  <Zap className="w-8 h-8 text-white" />
                </div>
              </div>
              <p className="text-3xl font-black text-white">{stats?.tempoMedio}s</p>
              <p className="text-gray-400 text-sm">Tempo Médio</p>
            </div>
          </UltraCard>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          
          {/* Área de Check-in */}
          <div className="lg:col-span-2">
            <UltraCard variant="gradient" glow>
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-white mb-4">Métodos de Check-in</h3>
                <div className="flex justify-center gap-4">
                  <UltraButton
                    variant={metodoAtivo === 'qr' ? 'primary' : 'ghost'}
                    onClick={() => setMetodoAtivo('qr')}
                    size="sm"
                  >
                    <Scan className="w-4 h-4 mr-2" />
                    QR Code
                  </UltraButton>
                  <UltraButton
                    variant={metodoAtivo === 'biometria' ? 'primary' : 'ghost'}
                    onClick={ativarBiometria}
                    size="sm"
                  >
                    <Fingerprint className="w-4 h-4 mr-2" />
                    Biometria
                  </UltraButton>
                  <UltraButton
                    variant={metodoAtivo === 'documento' ? 'primary' : 'ghost'}
                    onClick={() => setMetodoAtivo('documento')}
                    size="sm"
                  >
                    <User className="w-4 h-4 mr-2" />
                    Documento
                  </UltraButton>
                </div>
              </div>

              {/* Área de Scan QR */}
              {metodoAtivo === 'qr' && (
                <div className="text-center space-y-6">
                  <div className="relative mx-auto w-64 h-64 border-4 border-dashed border-purple-500/50 rounded-3xl flex items-center justify-center">
                    {scanning ? (
                      <QuantumSpinner size="lg" />
                    ) : (
                      <div className="text-center">
                        <Scan className="w-16 h-16 text-purple-400 mx-auto mb-4" />
                        <p className="text-gray-400">Posicione o QR Code</p>
                      </div>
                    )}
                    
                    {/* Animação de scan */}
                    {scanning && (
                      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-500 to-pink-500 animate-pulse" />
                    )}
                  </div>
                  
                  <UltraButton 
                    variant="primary" 
                    size="lg" 
                    onClick={handleCheckin}
                    disabled={scanning}
                    shimmer
                  >
                    {scanning ? 'Processando...' : 'Iniciar Scan'}
                  </UltraButton>
                </div>
              )}

              {/* Área de Biometria */}
              {metodoAtivo === 'biometria' && (
                <div className="text-center space-y-6">
                  <div className="relative mx-auto w-64 h-64 bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 rounded-3xl flex items-center justify-center">
                    {biometriaAtiva ? (
                      <div className="text-center">
                        <div className="relative">
                          <Eye className="w-16 h-16 text-cyan-400 mx-auto animate-pulse" />
                          <div className="absolute inset-0 bg-cyan-400/20 rounded-full animate-ping" />
                        </div>
                        <p className="text-cyan-400 mt-4 font-semibold">Escaneando...</p>
                      </div>
                    ) : (
                      <div className="text-center">
                        <Fingerprint className="w-16 h-16 text-cyan-400 mx-auto mb-4" />
                        <p className="text-gray-400">Posicione o dedo ou olhe para a câmera</p>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex gap-4 justify-center">
                    <UltraTooltip content="Reconhecimento facial">
                      <UltraButton variant="secondary" size="md" onClick={ativarBiometria}>
                        <Eye className="w-5 h-5 mr-2" />
                        Face ID
                      </UltraButton>
                    </UltraTooltip>
                    <UltraTooltip content="Digital">
                      <UltraButton variant="secondary" size="md" onClick={ativarBiometria}>
                        <Fingerprint className="w-5 h-5 mr-2" />
                        Touch ID
                      </UltraButton>
                    </UltraTooltip>
                  </div>
                </div>
              )}

              {/* Área de Documento */}
              {metodoAtivo === 'documento' && (
                <div className="space-y-6">
                  <div className="max-w-md mx-auto">
                    <UltraInput
                      placeholder="Digite CPF, RG ou nome completo"
                      value={documentoInput}
                      onChange={setDocumentoInput}
                      icon={<User className="w-5 h-5" />}
                      glow
                    />
                  </div>
                  
                  <div className="text-center">
                    <UltraButton 
                      variant="primary" 
                      size="lg" 
                      onClick={handleCheckin}
                      disabled={!documentoInput || scanning}
                      shimmer
                    >
                      {scanning ? 'Validando...' : 'Fazer Check-in'}
                    </UltraButton>
                  </div>
                </div>
              )}

              {/* IA Status */}
              <div className="mt-8 p-4 backdrop-blur-xl bg-black/30 rounded-2xl">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Brain className="w-6 h-6 text-purple-400" />
                    <div>
                      <p className="text-white font-semibold">IA de Segurança Ativa</p>
                      <p className="text-gray-400 text-sm">Análise comportamental em tempo real</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Shield className="w-5 h-5 text-green-400" />
                    <UltraBadge variant="success">Proteção Ativa</UltraBadge>
                  </div>
                </div>
              </div>
            </UltraCard>
          </div>

          {/* Check-ins Recentes */}
          <div>
            <UltraCard variant="glass">
              <h3 className="text-xl font-bold text-white mb-6">Check-ins Recentes</h3>
              
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {checkinsRecentes.map((checkin) => (
                  <div 
                    key={checkin.id}
                    className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-xl p-4 hover:bg-white/10 transition-all duration-300"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-white font-semibold text-sm">{checkin.nome}</span>
                      <div className={`flex items-center space-x-1 ${getStatusColor(checkin.status)}`}>
                        {getStatusIcon(checkin.status)}
                        <span className="text-xs capitalize">{checkin.status}</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between text-xs text-gray-400">
                      <span>{checkin.documento}</span>
                      <span>{checkin.timestamp.toLocaleTimeString()}</span>
                    </div>
                    
                    <div className="mt-2">
                      <UltraBadge 
                        variant={checkin.metodo === 'biometria' ? 'primary' : checkin.metodo === 'qr' ? 'secondary' : 'warning'}
                        size="sm"
                      >
                        {checkin.metodo}
                      </UltraBadge>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="mt-6 pt-4 border-t border-white/10">
                <UltraButton variant="ghost" size="sm" className="w-full">
                  Ver Todos os Check-ins
                </UltraButton>
              </div>
            </UltraCard>
          </div>
        </div>
      </div>
    </NeuralContainer>
  );
};

export default UltraModernCheckin;
