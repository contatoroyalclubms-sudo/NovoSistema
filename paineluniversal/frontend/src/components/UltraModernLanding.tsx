import { useState, useEffect } from 'react';
import {
  Calendar, ArrowRight, CheckCircle, BarChart3,
  Brain, QrCode, ShoppingCart, Trophy, Bot,
  Sparkles, Activity, Zap, Shield, Star,
  Users, TrendingUp, Globe, Smartphone,
  ChevronDown, Menu, X, Play, Fingerprint,
  CreditCard, Target, Cpu, BarChart4, Eye,
  Rocket, Award, Heart, Clock, MousePointer,
  Layers, Infinity, Mic, Video, MessageSquare
} from 'lucide-react';

const UltraModernLanding = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [scrollY, setScrollY] = useState(0);
  const [isVisible, setIsVisible] = useState({});

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Animação de entrada para seções
  const AnimatedSection = ({ children, delay = 0, className = "" }: {
    children: React.ReactNode;
    delay?: number;
    className?: string;
  }) => {
    return (
      <div
        className={`opacity-0 translate-y-8 animate-[fadeInUp_0.8s_ease-out_${delay}s_forwards] ${className}`}
        style={{ animationDelay: `${delay}s` }}
      >
        {children}
      </div>
    );
  };

  const features = [
    {
      icon: Brain,
      title: "IA Generativa Avançada",
      description: "GPT-4 integrado para criação automática de conteúdo",
      highlights: ["Copy de marketing", "Descrições automáticas", "Análise preditiva"],
      gradient: "from-purple-500 via-violet-500 to-purple-600",
      bgGlow: "bg-purple-500/20",
      iconBg: "bg-purple-500",
      trend: "🔥 Trending"
    },
    {
      icon: Eye,
      title: "Biometria Facial 3D",
      description: "Reconhecimento facial em tempo real com IA",
      highlights: ["Liveness detection", "Anti-spoofing", "99.9% precisão"],
      gradient: "from-pink-500 via-rose-500 to-pink-600",
      bgGlow: "bg-pink-500/20",
      iconBg: "bg-pink-500",
      trend: "🚀 New"
    },
    {
      icon: Layers,
      title: "Metaverso Integration",
      description: "Eventos híbridos com realidade virtual",
      highlights: ["VR experiences", "Avatar customization", "3D environments"],
      gradient: "from-cyan-500 via-blue-500 to-cyan-600",
      bgGlow: "bg-cyan-500/20",
      iconBg: "bg-cyan-500",
      trend: "🌟 Hot"
    },
    {
      icon: Infinity,
      title: "Blockchain & NFTs",
      description: "Ingressos NFT com prova de presença",
      highlights: ["Smart contracts", "POAP tokens", "Collectible tickets"],
      gradient: "from-emerald-500 via-green-500 to-emerald-600",
      bgGlow: "bg-emerald-500/20",
      iconBg: "bg-emerald-500",
      trend: "💎 Premium"
    },
    {
      icon: Mic,
      title: "Live Streaming 4K",
      description: "Transmissão multi-plataforma simultânea",
      highlights: ["4K ultra HD", "Multi-streaming", "Interactive chat"],
      gradient: "from-orange-500 via-red-500 to-orange-600",
      bgGlow: "bg-orange-500/20",
      iconBg: "bg-orange-500",
      trend: "📺 Live"
    },
    {
      icon: MessageSquare,
      title: "AI Chatbot 24/7",
      description: "Assistente virtual para participantes",
      highlights: ["Natural language", "Multi-idiomas", "Voice commands"],
      gradient: "from-indigo-500 via-purple-500 to-indigo-600",
      bgGlow: "bg-indigo-500/20",
      iconBg: "bg-indigo-500",
      trend: "🤖 Smart"
    }
  ];

  const stats = [
    { value: "50K+", label: "Eventos Criados", icon: Calendar, color: "text-purple-400" },
    { value: "2M+", label: "Participantes", icon: Users, color: "text-pink-400" },
    { value: "R$ 1B+", label: "Em Vendas", icon: TrendingUp, color: "text-cyan-400" },
    { value: "99.9%", label: "Uptime", icon: Shield, color: "text-emerald-400" },
    { value: "< 0.5s", label: "Check-in Time", icon: Zap, color: "text-yellow-400" },
    { value: "150+", label: "Países", icon: Globe, color: "text-blue-400" }
  ];

  const testimonials = [
    {
      name: "Sarah Johnson",
      role: "CEO - TechEvents Global",
      content: "A IA do EventosIA aumentou nossa eficiência em 300%. O reconhecimento facial eliminou filas e a automação nos poupa 40h por evento.",
      rating: 5,
      avatar: "SJ",
      company: "TechEvents",
      metric: "+300% eficiência"
    },
    {
      name: "Marcus Silva",
      role: "Diretor - MegaFest Brazil",
      content: "Processamos 100K ingressos NFT em um único evento. A integração blockchain garante autenticidade e cria valor duradouro.",
      rating: 5,
      avatar: "MS",
      company: "MegaFest",
      metric: "100K NFTs vendidos"
    },
    {
      name: "Dr. Elena Rodriguez",
      role: "Event Innovation Lab",
      content: "O metaverso híbrido expandiu nosso alcance global. Eventos presenciais + virtuais simultâneos são o futuro.",
      rating: 5,
      avatar: "ER",
      company: "Innovation Lab",
      metric: "5x alcance global"
    }
  ];

  const PricingCard = ({ plan, price, features, highlighted = false, badge = null }: {
    plan: string;
    price: string;
    features: string[];
    highlighted?: boolean;
    badge?: string | null;
  }) => (
    <div className={`relative ${highlighted ? 'scale-105 z-10' : ''}`}>
      {badge && (
        <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 z-20">
          <span className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-1 rounded-full text-sm font-bold shadow-lg">
            {badge}
          </span>
        </div>
      )}

      <div className={`relative backdrop-blur-xl ${highlighted ? 'bg-white/20 border-2 border-purple-300/50' : 'bg-white/10 border border-white/20'} rounded-3xl p-8 shadow-2xl transition-all duration-500 hover:scale-105 group`}>
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

        <div className="relative z-10">
          <h3 className="text-2xl font-bold text-white mb-2">{plan}</h3>
          <div className="mb-6">
            <span className="text-4xl font-black bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
              {price}
            </span>
            {price !== "Custom" && <span className="text-gray-400">/mês</span>}
          </div>

          <ul className="space-y-3 mb-8">
            {features.map((feature, i) => (
              <li key={i} className="flex items-center space-x-3 text-gray-300">
                <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                <span>{feature}</span>
              </li>
            ))}
          </ul>

          <button className={`w-full py-4 rounded-2xl font-bold text-lg transition-all duration-300 ${highlighted
              ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white shadow-xl transform hover:scale-105'
              : 'bg-white/10 border border-white/20 text-white hover:bg-white/20'
            }`}>
            {highlighted ? 'Começar Agora' : 'Saiba Mais'}
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-900 text-white overflow-hidden relative">

      {/* Fundo Animado Ultra-Moderno */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {/* Gradiente Base */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900/20 to-slate-900" />

        {/* Malha Animada */}
        <div
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: `radial-gradient(circle at 25% 25%, rgba(139, 92, 246, 0.3) 0%, transparent 50%), 
                             radial-gradient(circle at 75% 75%, rgba(236, 72, 153, 0.3) 0%, transparent 50%)`,
            animation: 'pulse 4s ease-in-out infinite alternate'
          }}
        />

        {/* Partículas Flutuantes */}
        {[...Array(30)].map((_, i) => (
          <div
            key={i}
            className="absolute rounded-full bg-white/10 animate-pulse"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              width: `${Math.random() * 6 + 2}px`,
              height: `${Math.random() * 6 + 2}px`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${3 + Math.random() * 4}s`
            }}
          />
        ))}

        {/* Efeito de Paralaxe */}
        <div
          className="absolute inset-0"
          style={{
            background: `radial-gradient(circle at ${50 + scrollY * 0.05}% ${50 + scrollY * 0.03}%, rgba(139, 92, 246, 0.1) 0%, transparent 70%)`,
          }}
        />
      </div>

      {/* Navigation Ultra-Moderna */}
      <nav className="relative z-50 border-b border-white/10 backdrop-blur-2xl bg-slate-900/80">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between h-20">

            {/* Logo Futurista */}
            <div className="flex items-center space-x-3">
              <div className="relative group">
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl blur-lg opacity-75 group-hover:opacity-100 transition-opacity duration-300" />
                <div className="relative bg-gradient-to-r from-purple-500 to-pink-500 p-3 rounded-2xl">
                  <Rocket className="w-8 h-8 text-white" />
                </div>
              </div>
              <div>
                <span className="text-3xl font-black bg-gradient-to-r from-white via-purple-200 to-pink-200 bg-clip-text text-transparent">
                  EventosIA
                </span>
                <div className="text-xs text-purple-400 font-semibold">2024 Edition</div>
              </div>
            </div>

            {/* Menu Desktop */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-300 hover:text-white transition-colors relative group">
                Tecnologias
                <div className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-purple-500 to-pink-500 group-hover:w-full transition-all duration-300" />
              </a>
              <a href="#pricing" className="text-gray-300 hover:text-white transition-colors relative group">
                Planos
                <div className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-purple-500 to-pink-500 group-hover:w-full transition-all duration-300" />
              </a>
              <a href="#testimonials" className="text-gray-300 hover:text-white transition-colors relative group">
                Cases
                <div className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-purple-500 to-pink-500 group-hover:w-full transition-all duration-300" />
              </a>

              {/* CTA Futurista */}
              <button className="group relative overflow-hidden bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white px-6 py-3 rounded-2xl font-bold transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-2xl">
                <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                <span className="relative">Começar Grátis</span>
              </button>
            </div>

            {/* Mobile Menu */}
            <button
              className="md:hidden relative z-50"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-2 rounded-xl">
                {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </div>
            </button>
          </div>

          {/* Mobile Menu Dropdown */}
          {isMenuOpen && (
            <div className="md:hidden absolute top-20 left-0 right-0 backdrop-blur-2xl bg-slate-900/95 border-b border-white/10 p-6">
              <div className="flex flex-col space-y-4">
                <a href="#features" className="text-gray-300 hover:text-white transition-colors">Tecnologias</a>
                <a href="#pricing" className="text-gray-300 hover:text-white transition-colors">Planos</a>
                <a href="#testimonials" className="text-gray-300 hover:text-white transition-colors">Cases</a>
                <button className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-2xl font-semibold mt-4">
                  Começar Grátis
                </button>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section Ultra-Futurista */}
      <section className="relative z-10 min-h-screen flex items-center pt-20">
        <div className="max-w-7xl mx-auto px-6 py-20">
          <div className="grid lg:grid-cols-2 gap-16 items-center">

            {/* Left Content */}
            <AnimatedSection className="space-y-8">

              {/* Badges Flutuantes */}
              <div className="flex flex-wrap gap-3">
                <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-300/30 rounded-full px-4 py-2 backdrop-blur-xl">
                  <Sparkles className="w-4 h-4 text-purple-400" />
                  <span className="text-purple-300 text-sm font-semibold">Powered by GPT-4</span>
                </div>

                <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-300/30 rounded-full px-4 py-2 backdrop-blur-xl">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  <span className="text-green-300 text-sm font-semibold">Sistema Ativo</span>
                </div>
              </div>

              {/* Título Mega-Impactante */}
              <h1 className="text-6xl lg:text-8xl font-black leading-none">
                <span className="bg-gradient-to-r from-white via-purple-200 to-pink-200 bg-clip-text text-transparent">
                  Eventos
                </span>
                <br />
                <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent relative">
                  do Futuro
                  <div className="absolute -top-4 -right-4 text-2xl">🚀</div>
                </span>
              </h1>

              <p className="text-2xl text-gray-300 leading-relaxed max-w-2xl">
                Primeira plataforma com <strong className="text-white">IA Generativa</strong>,
                <strong className="text-white"> Biometria 3D</strong> e
                <strong className="text-white"> Blockchain</strong> integrados.
                <br />
                <span className="text-purple-400">O futuro dos eventos chegou.</span>
              </p>

              {/* CTAs Inovadores */}
              <div className="flex flex-col sm:flex-row gap-6">
                <button className="group relative overflow-hidden bg-gradient-to-r from-purple-600 via-pink-600 to-purple-600 hover:from-purple-500 hover:via-pink-500 hover:to-purple-500 text-white px-10 py-5 rounded-3xl font-bold text-xl transition-all duration-500 transform hover:scale-105 shadow-2xl hover:shadow-purple-500/25 bg-[length:200%_200%] animate-[gradient_3s_ease_infinite]">
                  <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/30 to-white/0 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                  <div className="flex items-center space-x-3 relative">
                    <span>Começar Grátis Agora</span>
                    <ArrowRight className="w-6 h-6 group-hover:translate-x-2 transition-transform" />
                  </div>
                </button>

                <button className="flex items-center space-x-4 backdrop-blur-xl bg-white/10 border border-white/20 text-white px-10 py-5 rounded-3xl font-semibold text-xl hover:bg-white/20 transition-all duration-300 group">
                  <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-2 rounded-full">
                    <Play className="w-6 h-6" />
                  </div>
                  <span>Demo Interativa</span>
                </button>
              </div>

              {/* Trust Indicators Avançados */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-8">
                <div className="text-center">
                  <CheckCircle className="w-6 h-6 text-green-400 mx-auto mb-2" />
                  <span className="text-sm text-gray-400">30 dias grátis</span>
                </div>
                <div className="text-center">
                  <Shield className="w-6 h-6 text-blue-400 mx-auto mb-2" />
                  <span className="text-sm text-gray-400">ISO 27001</span>
                </div>
                <div className="text-center">
                  <Clock className="w-6 h-6 text-purple-400 mx-auto mb-2" />
                  <span className="text-sm text-gray-400">Setup 5min</span>
                </div>
                <div className="text-center">
                  <Heart className="w-6 h-6 text-pink-400 mx-auto mb-2" />
                  <span className="text-sm text-gray-400">99% satisfação</span>
                </div>
              </div>
            </AnimatedSection>

            {/* Right Content - Dashboard 3D */}
            <AnimatedSection delay={0.3} className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500/30 via-pink-500/30 to-cyan-500/30 rounded-3xl blur-3xl animate-pulse" />

              <div className="relative backdrop-blur-2xl bg-white/10 border border-white/20 rounded-3xl p-8 shadow-2xl transform hover:scale-105 transition-all duration-500">

                {/* Header Dashboard */}
                <div className="flex items-center justify-between mb-8">
                  <h3 className="text-2xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                    Dashboard IA
                  </h3>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse" />
                    <span className="text-green-400 text-sm font-semibold">Live</span>
                  </div>
                </div>

                {/* Métricas Tempo Real */}
                <div className="grid grid-cols-2 gap-6 mb-8">
                  <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/20 rounded-2xl p-6 border border-purple-300/30">
                    <div className="flex items-center space-x-3 mb-3">
                      <Brain className="w-8 h-8 text-purple-400" />
                      <span className="text-purple-300 font-semibold">IA Analytics</span>
                    </div>
                    <div className="text-3xl font-black text-white mb-1">2,847</div>
                    <div className="text-green-400 text-sm">+32% vs ontem</div>
                  </div>

                  <div className="bg-gradient-to-br from-pink-500/20 to-pink-600/20 rounded-2xl p-6 border border-pink-300/30">
                    <div className="flex items-center space-x-3 mb-3">
                      <Eye className="w-8 h-8 text-pink-400" />
                      <span className="text-pink-300 font-semibold">Face ID</span>
                    </div>
                    <div className="text-3xl font-black text-white mb-1">99.9%</div>
                    <div className="text-green-400 text-sm">Precisão</div>
                  </div>
                </div>

                {/* Gráfico Simulado */}
                <div className="bg-gradient-to-r from-cyan-500/10 to-blue-500/10 rounded-2xl p-6 border border-cyan-300/30">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-cyan-300 font-semibold">Revenue Stream</span>
                    <TrendingUp className="w-5 h-5 text-cyan-400" />
                  </div>

                  <div className="h-32 flex items-end space-x-2">
                    {[40, 65, 45, 80, 55, 90, 70, 95].map((height, i) => (
                      <div
                        key={i}
                        className="bg-gradient-to-t from-cyan-500 to-blue-400 rounded-t flex-1 transition-all duration-1000 hover:from-purple-500 hover:to-pink-500"
                        style={{ height: `${height}%` }}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </AnimatedSection>
          </div>
        </div>
      </section>

      {/* Stats Section Ultra-Impactante */}
      <section className="relative z-10 py-20 border-y border-white/10">
        <div className="max-w-7xl mx-auto px-6">
          <AnimatedSection className="text-center mb-16">
            <h2 className="text-4xl font-black mb-4">
              <span className="bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                Números que Impressionam
              </span>
            </h2>
            <p className="text-xl text-gray-300">Resultados reais de clientes que escolheram o futuro</p>
          </AnimatedSection>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
            {stats.map((stat, index) => (
              <AnimatedSection key={index} delay={index * 0.1} className="text-center group">
                <div className="relative backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-8 hover:bg-white/10 transition-all duration-500 transform hover:scale-105 hover:-translate-y-2">

                  {/* Ícone Flutuante */}
                  <div className="flex justify-center mb-6">
                    <div className="relative">
                      <div className="absolute inset-0 bg-gradient-to-r from-purple-500/50 to-pink-500/50 rounded-2xl blur-lg group-hover:blur-xl transition-all duration-500" />
                      <div className="relative bg-gradient-to-r from-purple-500/20 to-pink-500/20 p-4 rounded-2xl border border-white/20">
                        <stat.icon className={`w-8 h-8 ${stat.color}`} />
                      </div>
                    </div>
                  </div>

                  {/* Valor Animado */}
                  <div className="text-4xl lg:text-5xl font-black bg-gradient-to-r from-white via-gray-200 to-white bg-clip-text text-transparent mb-3 group-hover:scale-110 transition-transform duration-300">
                    {stat.value}
                  </div>

                  {/* Label */}
                  <div className="text-gray-400 font-medium">{stat.label}</div>
                </div>
              </AnimatedSection>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section - Tecnologias do Futuro */}
      <section id="features" className="relative z-10 py-20">
        <div className="max-w-7xl mx-auto px-6">

          {/* Header da Seção */}
          <AnimatedSection className="text-center mb-20">
            <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-300/30 rounded-full px-6 py-3 mb-8">
              <Cpu className="w-5 h-5 text-purple-400" />
              <span className="text-purple-300 font-semibold">Tecnologias Emergentes</span>
            </div>

            <h2 className="text-6xl font-black mb-8">
              <span className="bg-gradient-to-r from-white via-purple-200 to-pink-200 bg-clip-text text-transparent">
                Recursos que Definem
              </span>
              <br />
              <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent">
                o Futuro dos Eventos
              </span>
            </h2>

            <p className="text-2xl text-gray-300 max-w-4xl mx-auto">
              Integração completa de IA, Blockchain, Metaverso e Biometria em uma única plataforma
            </p>
          </AnimatedSection>

          {/* Grid de Features */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <AnimatedSection key={index} delay={index * 0.1} className="group relative">

                {/* Badge Trending */}
                <div className="absolute -top-3 -right-3 z-20">
                  <span className="bg-gradient-to-r from-yellow-400 to-orange-500 text-black px-3 py-1 rounded-full text-xs font-bold shadow-lg">
                    {feature.trend}
                  </span>
                </div>

                {/* Glow Effect */}
                <div className={`absolute inset-0 ${feature.bgGlow} rounded-3xl blur-2xl opacity-0 group-hover:opacity-100 transition-all duration-700`} />

                {/* Card Principal */}
                <div className="relative backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-8 hover:bg-white/10 transition-all duration-500 transform group-hover:scale-105 group-hover:-translate-y-2">

                  {/* Ícone com Efeito 3D */}
                  <div className="flex justify-center mb-8">
                    <div className="relative">
                      <div className={`absolute inset-0 bg-gradient-to-r ${feature.gradient} rounded-3xl blur-lg opacity-75 group-hover:opacity-100 transition-opacity duration-300`} />
                      <div className={`relative ${feature.iconBg} p-6 rounded-3xl transform group-hover:rotate-6 transition-transform duration-300`}>
                        <feature.icon className="w-12 h-12 text-white" />
                      </div>
                    </div>
                  </div>

                  {/* Conteúdo */}
                  <h3 className="text-3xl font-bold text-white mb-4 group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-white group-hover:to-gray-300 group-hover:bg-clip-text transition-all duration-300">
                    {feature.title}
                  </h3>

                  <p className="text-gray-300 mb-8 leading-relaxed text-lg">
                    {feature.description}
                  </p>

                  {/* Highlights */}
                  <ul className="space-y-3">
                    {feature.highlights.map((highlight, i) => (
                      <li key={i} className="flex items-center space-x-3">
                        <div className={`w-2 h-2 bg-gradient-to-r ${feature.gradient} rounded-full`} />
                        <span className="text-gray-300 font-medium">{highlight}</span>
                      </li>
                    ))}
                  </ul>

                  {/* Botão de Ação */}
                  <button className={`mt-8 w-full py-4 rounded-2xl font-semibold transition-all duration-300 bg-gradient-to-r ${feature.gradient} opacity-0 group-hover:opacity-100 text-white transform translate-y-4 group-hover:translate-y-0`}>
                    Explorar Recurso
                  </button>
                </div>
              </AnimatedSection>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section Ultra-Premium */}
      <section id="pricing" className="relative z-10 py-20 bg-gradient-to-r from-slate-800/50 to-slate-900/50">
        <div className="max-w-7xl mx-auto px-6">

          <AnimatedSection className="text-center mb-20">
            <h2 className="text-6xl font-black mb-8">
              <span className="bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                Planos para Cada
              </span>
              <br />
              <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                Tipo de Evento
              </span>
            </h2>
            <p className="text-2xl text-gray-300">Desde startups até mega eventos globais</p>
          </AnimatedSection>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">

            {/* Starter Plan */}
            <PricingCard
              plan="Starter"
              price="R$ 199"
              features={[
                "Até 1.000 participantes",
                "IA básica para descrições",
                "Check-in por QR Code",
                "Dashboard em tempo real",
                "Suporte por email",
                "Relatórios básicos"
              ]}
            />

            {/* Pro Plan - Highlighted */}
            <PricingCard
              plan="Professional"
              price="R$ 499"
              badge="🚀 Mais Popular"
              highlighted={true}
              features={[
                "Até 10.000 participantes",
                "IA completa + GPT-4",
                "Biometria facial 3D",
                "PDV integrado",
                "Streaming 4K",
                "NFT tickets",
                "Suporte prioritário",
                "Analytics avançados"
              ]}
            />

            {/* Enterprise Plan */}
            <PricingCard
              plan="Enterprise"
              price="Custom"
              features={[
                "Participantes ilimitados",
                "Metaverso integration",
                "Blockchain completo",
                "White-label",
                "API personalizada",
                "Suporte dedicado 24/7",
                "Onboarding premium",
                "Custom features"
              ]}
            />
          </div>

          {/* CTA Section */}
          <AnimatedSection delay={0.5} className="text-center mt-16">
            <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-12 max-w-4xl mx-auto">
              <h3 className="text-4xl font-bold mb-6 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                Pronto para Revolucionar seus Eventos?
              </h3>
              <p className="text-xl text-gray-300 mb-8">
                30 dias grátis • Setup em 5 minutos • Sem cartão de crédito
              </p>

              <div className="flex flex-col sm:flex-row gap-6 justify-center">
                <button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white px-12 py-4 rounded-2xl font-bold text-xl transition-all duration-300 transform hover:scale-105 shadow-2xl">
                  Começar Gratuitamente
                </button>
                <button className="backdrop-blur-xl bg-white/10 border border-white/20 text-white px-12 py-4 rounded-2xl font-semibold text-xl hover:bg-white/20 transition-all duration-300">
                  Falar com Especialista
                </button>
              </div>
            </div>
          </AnimatedSection>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="relative z-10 py-20">
        <div className="max-w-7xl mx-auto px-6">

          <AnimatedSection className="text-center mb-20">
            <h2 className="text-6xl font-black mb-8">
              <span className="bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                Cases de Sucesso
              </span>
              <br />
              <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                que Inspiram
              </span>
            </h2>
            <p className="text-2xl text-gray-300">Resultados reais de quem já vive o futuro</p>
          </AnimatedSection>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <AnimatedSection key={index} delay={index * 0.2} className="relative group">

                <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 via-pink-500/10 to-cyan-500/10 rounded-3xl blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-700" />

                <div className="relative backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-8 hover:bg-white/10 transition-all duration-500 transform group-hover:scale-105">

                  {/* Rating Stars */}
                  <div className="flex items-center space-x-1 mb-6">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="w-6 h-6 text-yellow-400 fill-current" />
                    ))}
                  </div>

                  {/* Metric Badge */}
                  <div className="inline-block bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-300/30 rounded-full px-4 py-2 mb-6">
                    <span className="text-green-300 font-semibold text-sm">{testimonial.metric}</span>
                  </div>

                  {/* Quote */}
                  <p className="text-gray-300 mb-8 italic leading-relaxed text-lg">
                    "{testimonial.content}"
                  </p>

                  {/* Author */}
                  <div className="flex items-center space-x-4">
                    <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
                      {testimonial.avatar}
                    </div>
                    <div>
                      <div className="font-bold text-white text-lg">{testimonial.name}</div>
                      <div className="text-gray-400">{testimonial.role}</div>
                      <div className="text-purple-400 font-semibold text-sm">{testimonial.company}</div>
                    </div>
                  </div>
                </div>
              </AnimatedSection>
            ))}
          </div>
        </div>
      </section>

      {/* Footer Ultra-Moderno */}
      <footer className="relative z-10 border-t border-white/10 py-20">
        <div className="max-w-7xl mx-auto px-6">

          {/* Footer Header */}
          <div className="text-center mb-16">
            <div className="flex items-center justify-center space-x-4 mb-6">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl blur-lg opacity-75" />
                <div className="relative bg-gradient-to-r from-purple-500 to-pink-500 p-3 rounded-2xl">
                  <Rocket className="w-8 h-8 text-white" />
                </div>
              </div>
              <span className="text-4xl font-black bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                EventosIA
              </span>
            </div>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Construindo o futuro dos eventos com tecnologia de ponta e inovação constante.
            </p>
          </div>

          {/* Footer Links */}
          <div className="grid md:grid-cols-4 gap-8 mb-16">

            <div>
              <h4 className="font-bold text-white text-lg mb-6">Produto</h4>
              <div className="space-y-3 text-gray-400">
                <div className="hover:text-white transition-colors cursor-pointer">Funcionalidades</div>
                <div className="hover:text-white transition-colors cursor-pointer">Integrações</div>
                <div className="hover:text-white transition-colors cursor-pointer">API</div>
                <div className="hover:text-white transition-colors cursor-pointer">Roadmap</div>
              </div>
            </div>

            <div>
              <h4 className="font-bold text-white text-lg mb-6">Soluções</h4>
              <div className="space-y-3 text-gray-400">
                <div className="hover:text-white transition-colors cursor-pointer">Eventos Corporativos</div>
                <div className="hover:text-white transition-colors cursor-pointer">Festivais</div>
                <div className="hover:text-white transition-colors cursor-pointer">Conferências</div>
                <div className="hover:text-white transition-colors cursor-pointer">Esports</div>
              </div>
            </div>

            <div>
              <h4 className="font-bold text-white text-lg mb-6">Empresa</h4>
              <div className="space-y-3 text-gray-400">
                <div className="hover:text-white transition-colors cursor-pointer">Sobre</div>
                <div className="hover:text-white transition-colors cursor-pointer">Blog</div>
                <div className="hover:text-white transition-colors cursor-pointer">Carreiras</div>
                <div className="hover:text-white transition-colors cursor-pointer">Contato</div>
              </div>
            </div>

            <div>
              <h4 className="font-bold text-white text-lg mb-6">Suporte</h4>
              <div className="space-y-3 text-gray-400">
                <div className="hover:text-white transition-colors cursor-pointer">Central de Ajuda</div>
                <div className="hover:text-white transition-colors cursor-pointer">Documentação</div>
                <div className="hover:text-white transition-colors cursor-pointer">Status</div>
                <div className="hover:text-white transition-colors cursor-pointer">Comunidade</div>
              </div>
            </div>
          </div>

          {/* Footer Bottom */}
          <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400 mb-4 md:mb-0">
              &copy; 2024 EventosIA. Todos os direitos reservados.
            </p>
            <div className="flex items-center space-x-6 text-gray-400">
              <div className="hover:text-white transition-colors cursor-pointer">Privacidade</div>
              <div className="hover:text-white transition-colors cursor-pointer">Termos</div>
              <div className="hover:text-white transition-colors cursor-pointer">Cookies</div>
            </div>
          </div>
        </div>
      </footer>

      {/* CSS personalizado para animações */}
      <style>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes gradient {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        
        .animate-float {
          animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
      `}</style>
    </div>
  );
};

export default UltraModernLanding;
