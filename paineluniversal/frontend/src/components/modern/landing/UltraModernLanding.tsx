import React, { useState, useEffect } from 'react';
import { 
  Calendar, ArrowRight, Sparkles, Zap, Shield, Users, 
  BarChart3, Star, CheckCircle, Play, Award, Rocket, 
  Brain, Eye, Target, TrendingUp, Clock, Lock, Cpu, 
  Scan, Fingerprint
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const UltraModernLanding = () => {
  const navigate = useNavigate();
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ 
        x: (e.clientX / window.innerWidth) * 100, 
        y: (e.clientY / window.innerHeight) * 100 
      });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const features = [
    {
      icon: Scan,
      title: "Check-in Biométrico",
      description: "Reconhecimento facial e impressão digital em segundos",
      gradient: "from-emerald-500 to-cyan-500",
      stats: "99.9% precisão"
    },
    {
      icon: Brain,
      title: "IA Preditiva",
      description: "Analytics avançados com machine learning para insights únicos",
      gradient: "from-purple-500 to-pink-500",
      stats: "10x mais insights"
    },
    {
      icon: Lock,
      title: "Segurança Quântica",
      description: "Criptografia de última geração para proteção total",
      gradient: "from-blue-500 to-indigo-500",
      stats: "Proteção militar"
    }
  ];

  const stats = [
    { number: "50K+", label: "Eventos Realizados" },
    { number: "2M+", label: "Check-ins Processados" },
    { number: "99.99%", label: "Uptime Garantido" }
  ];

  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      
      {/* Dynamic Neural Background */}
      <div className="fixed inset-0 z-0">
        <div 
          className="absolute inset-0 opacity-50"
          style={{
            background: `
              radial-gradient(circle at 25% 25%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
              radial-gradient(circle at 75% 75%, rgba(236, 72, 153, 0.15) 0%, transparent 50%),
              radial-gradient(circle at ${mousePosition.x}% ${mousePosition.y}%, rgba(59, 130, 246, 0.1) 0%, transparent 30%)
            `
          }}
        />
      </div>

      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 backdrop-blur-2xl bg-black/20 border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl blur-lg opacity-50" />
                <div className="relative bg-gradient-to-r from-purple-500 to-pink-500 p-2 rounded-xl">
                  <Calendar className="w-6 h-6 text-white" />
                </div>
              </div>
              <span className="text-2xl font-black bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                EventsAI
              </span>
            </div>
            
            <div className="flex items-center space-x-4">
              <button 
                onClick={() => navigate('/login')}
                className="text-gray-300 hover:text-white transition-colors font-medium"
              >
                Login
              </button>
              <button 
                onClick={() => navigate('/login')}
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white px-6 py-2 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105"
              >
                Acessar Sistema
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 min-h-screen flex items-center pt-20">
        <div className="max-w-7xl mx-auto px-6 py-20">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            
            {/* Left Content */}
            <div className="space-y-8">
              
              <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30 rounded-full px-6 py-3">
                <Sparkles className="w-4 h-4 text-purple-400" />
                <span className="text-purple-300 text-sm font-semibold">Sistema Já em Funcionamento</span>
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              </div>

              <h1 className="text-6xl lg:text-7xl font-black leading-tight">
                <span className="bg-gradient-to-r from-white via-purple-200 to-pink-200 bg-clip-text text-transparent">
                  Eventos
                </span>
                <br />
                <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent">
                  Inteligentes
                </span>
              </h1>

              <p className="text-xl text-gray-300 leading-relaxed max-w-lg">
                Plataforma de eventos com IA, biometria e automação completa. 
                Sistema já operacional com milhares de eventos realizados.
              </p>

              <div className="flex flex-col sm:flex-row gap-4">
                <button 
                  onClick={() => navigate('/login')}
                  className="group relative overflow-hidden bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white px-8 py-4 rounded-2xl font-bold text-lg transition-all duration-500 transform hover:scale-105 shadow-2xl"
                >
                  <div className="flex items-center space-x-3">
                    <Rocket className="w-5 h-5" />
                    <span>Acessar Sistema</span>
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </div>
                </button>
              </div>
            </div>

            {/* Right Visual - Dashboard Preview */}
            <div className="relative">
              <div 
                className="backdrop-blur-2xl bg-gradient-to-br from-white/10 to-white/5 border border-white/20 rounded-3xl p-8 shadow-2xl"
                style={{
                  transform: `perspective(1000px) rotateY(${(mousePosition.x - 50) * 0.1}deg) rotateX(${(mousePosition.y - 50) * 0.05}deg)`
                }}
              >
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-red-400 rounded-full" />
                    <div className="w-3 h-3 bg-yellow-400 rounded-full" />
                    <div className="w-3 h-3 bg-green-400 rounded-full" />
                  </div>
                  <div className="text-xs text-gray-400">EventsAI Dashboard</div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-white font-semibold">Tech Conference 2025</h3>
                    <span className="bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-xs font-semibold">
                      Ao Vivo
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    {stats.map((stat, i) => (
                      <div key={i} className="bg-black/30 rounded-xl p-3 text-center">
                        <div className="text-lg font-bold text-white">{stat.number}</div>
                        <div className="text-xs text-gray-400">{stat.label}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 py-32">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-20">
            <h2 className="text-5xl font-black bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent mb-6">
              Recursos Revolucionários
            </h2>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Cada recurso desenvolvido com IA e machine learning
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div 
                key={index}
                className="group relative backdrop-blur-2xl bg-gradient-to-br from-white/[0.08] to-white/[0.02] border border-white/10 rounded-3xl p-8 hover:bg-white/[0.12] transition-all duration-500"
              >
                <div className="relative mb-6">
                  <div className={`absolute inset-0 bg-gradient-to-r ${feature.gradient} rounded-2xl blur-xl opacity-50`} />
                  <div className={`relative bg-gradient-to-r ${feature.gradient} p-4 rounded-2xl w-16 h-16 flex items-center justify-center`}>
                    <feature.icon className="w-8 h-8 text-white" />
                  </div>
                </div>

                <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
                <p className="text-gray-400 mb-4">{feature.description}</p>
                <span className={`bg-gradient-to-r ${feature.gradient} bg-clip-text text-transparent font-semibold text-sm`}>
                  {feature.stats}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 py-32">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <div className="backdrop-blur-2xl bg-gradient-to-br from-purple-500/20 via-pink-500/20 to-cyan-500/20 border border-white/20 rounded-3xl p-16">
            
            <h2 className="text-5xl font-black bg-gradient-to-r from-white via-purple-200 to-pink-200 bg-clip-text text-transparent mb-6">
              Pronto para Revolucionar Seus Eventos?
            </h2>
            
            <p className="text-xl text-gray-300 mb-10 max-w-2xl mx-auto">
              Sistema já funcionando com milhares de eventos realizados
            </p>

            <button
              onClick={() => navigate('/login')}
              className="group relative overflow-hidden bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white px-10 py-5 rounded-2xl font-bold text-xl transition-all duration-500 transform hover:scale-105 shadow-2xl"
            >
              <div className="flex items-center space-x-3">
                <span>Acessar Sistema Agora</span>
                <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
              </div>
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default UltraModernLanding;
