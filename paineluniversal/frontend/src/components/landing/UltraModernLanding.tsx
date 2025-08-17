import React, { useState, useEffect } from 'react';
import { 
  Calendar, ArrowRight, Sparkles, Zap, Shield, Users, 
  BarChart3, Smartphone, Globe, Star, CheckCircle, 
  Play, Award, Rocket, Brain, Eye, Target, 
  TrendingUp, Clock, Lock, Cpu, Scan, Fingerprint
} from 'lucide-react';

const UltraModernLanding = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [scrollY, setScrollY] = useState(0);
  const [currentTestimonial, setCurrentTestimonial] = useState(0);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ 
        x: (e.clientX / window.innerWidth) * 100, 
        y: (e.clientY / window.innerHeight) * 100 
      });
    };

    const handleScroll = () => setScrollY(window.scrollY);

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('scroll', handleScroll);
    
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  // Auto-rotate testimonials
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTestimonial(prev => (prev + 1) % 3);
    }, 4000);
    return () => clearInterval(interval);
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
    },
    {
      icon: Zap,
      title: "Tempo Real",
      description: "Sincronização instantânea em todos os dispositivos",
      gradient: "from-yellow-500 to-orange-500",
      stats: "<1ms latência"
    },
    {
      icon: Target,
      title: "Automação Inteligente",
      description: "Workflows automatizados que se adaptam ao seu evento",
      gradient: "from-rose-500 to-red-500",
      stats: "90% menos trabalho"
    },
    {
      icon: Cpu,
      title: "Edge Computing",
      description: "Processamento local para performance máxima offline",
      gradient: "from-violet-500 to-purple-500",
      stats: "100% uptime"
    }
  ];

  const testimonials = [
    {
      name: "Maria Silva",
      role: "Event Director",
      company: "Global Events",
      text: "Revolucionou completamente como gerenciamos eventos. A IA preditiva nos ajudou a aumentar a satisfação em 40%.",
      rating: 5,
      image: "https://images.unsplash.com/photo-1494790108755-2616b612b5c6?w=400&h=400&fit=crop&crop=face"
    },
    {
      name: "João Santos",
      role: "CEO",
      company: "TechCorp",
      text: "O check-in biométrico eliminou completamente as filas. Nossos eventos agora são 300% mais eficientes.",
      rating: 5,
      image: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face"
    },
    {
      name: "Ana Costa",
      role: "Marketing Manager",
      company: "StartupHub",
      text: "Os insights de IA nos permitiram entender nosso público como nunca antes. ROI aumentou 250%.",
      rating: 5,
      image: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop&crop=face"
    }
  ];

  const stats = [
    { number: "50K+", label: "Eventos Realizados", growth: "+300%" },
    { number: "2M+", label: "Check-ins Processados", growth: "+250%" },
    { number: "99.99%", label: "Uptime Garantido", growth: "Sempre" },
    { number: "500ms", label: "Tempo de Response", growth: "-80%" }
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
        
        {/* Animated Particles */}
        <div className="absolute inset-0">
          {[...Array(60)].map((_, i) => (
            <div
              key={i}
              className="absolute animate-particle"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDuration: `${5 + Math.random() * 10}s`,
                animationDelay: `${Math.random() * 5}s`
              }}
            >
              <div 
                className="w-1 h-1 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full opacity-60"
                style={{ boxShadow: '0 0 10px currentColor' }}
              />
            </div>
          ))}
        </div>
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
            
            <div className="hidden md:flex items-center space-x-8">
              {['Recursos', 'Preços', 'Cases', 'Contato'].map((item) => (
                <button key={item} className="text-gray-300 hover:text-white transition-all duration-300 font-medium">
                  {item}
                </button>
              ))}
            </div>

            <div className="flex items-center space-x-4">
              <button className="text-gray-300 hover:text-white transition-colors font-medium">
                Login
              </button>
              <button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white px-6 py-2 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105">
                Demo Gratuita
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
              
              {/* Badge */}
              <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30 rounded-full px-6 py-3">
                <Sparkles className="w-4 h-4 text-purple-400" />
                <span className="text-purple-300 text-sm font-semibold">Nova Geração de Eventos</span>
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              </div>

              {/* Main Title */}
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
                Transforme seus eventos em experiências inesquecíveis.
              </p>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4">
                <button className="group relative overflow-hidden bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white px-8 py-4 rounded-2xl font-bold text-lg transition-all duration-500 transform hover:scale-105 shadow-2xl">
                  <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                  <div className="flex items-center space-x-3">
                    <Rocket className="w-5 h-5" />
                    <span>Começar Agora</span>
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </div>
                </button>

                <button className="group backdrop-blur-xl bg-white/10 border border-white/20 text-white px-8 py-4 rounded-2xl font-semibold text-lg hover:bg-white/20 transition-all duration-300">
                  <div className="flex items-center space-x-3">
                    <Play className="w-5 h-5" />
                    <span>Ver Demo</span>
                  </div>
                </button>
              </div>

              {/* Social Proof */}
              <div className="pt-8">
                <p className="text-gray-400 text-sm mb-4">Confiado por empresas líderes</p>
                <div className="flex items-center space-x-8 opacity-60">
                  {['Google', 'Microsoft', 'Amazon', 'Meta'].map((company) => (
                    <span key={company} className="text-gray-400 font-semibold text-lg">
                      {company}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Visual */}
            <div className="relative">
              <div className="relative z-10">
                
                {/* Main Dashboard Preview */}
                <div 
                  className="backdrop-blur-2xl bg-gradient-to-br from-white/10 to-white/5 border border-white/20 rounded-3xl p-8 shadow-2xl"
                  style={{
                    transform: `perspective(1000px) rotateY(${(mousePosition.x - 50) * 0.1}deg) rotateX(${(mousePosition.y - 50) * 0.05}deg)`
                  }}
                >
                  {/* Mock Dashboard Header */}
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-3">
                      <div className="w-3 h-3 bg-red-400 rounded-full" />
                      <div className="w-3 h-3 bg-yellow-400 rounded-full" />
                      <div className="w-3 h-3 bg-green-400 rounded-full" />
                    </div>
                    <div className="text-xs text-gray-400">EventsAI Dashboard</div>
                  </div>

                  {/* Mock Content */}
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-white font-semibold">Tech Conference 2025</h3>
                      <span className="bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-xs font-semibold">
                        Ao Vivo
                      </span>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                      {stats.slice(0, 3).map((stat, i) => (
                        <div key={i} className="bg-black/30 rounded-xl p-3 text-center">
                          <div className="text-lg font-bold text-white">{stat.number}</div>
                          <div className="text-xs text-gray-400">{stat.label}</div>
                        </div>
                      ))}
                    </div>

                    <div className="bg-black/30 rounded-xl p-4">
                      <div className="flex items-center space-x-3 mb-3">
                        <Eye className="w-4 h-4 text-blue-400" />
                        <span className="text-white text-sm font-semibold">Check-ins em Tempo Real</span>
                      </div>
                      <div className="space-y-2">
                        {[1, 2, 3].map((_, i) => (
                          <div key={i} className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full" />
                            <div className="flex-1">
                              <div className="text-white text-sm">Participante #{1000 + i}</div>
                              <div className="text-gray-400 text-xs">Entrada confirmada • Biometria</div>
                            </div>
                            <CheckCircle className="w-4 h-4 text-green-400" />
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Floating Cards */}
                <div 
                  className="absolute -top-8 -right-8 backdrop-blur-xl bg-purple-500/20 border border-purple-500/30 rounded-2xl p-4 animate-float"
                >
                  <div className="flex items-center space-x-3">
                    <Brain className="w-6 h-6 text-purple-400" />
                    <div>
                      <div className="text-white text-sm font-semibold">IA Ativa</div>
                      <div className="text-purple-300 text-xs">Analisando comportamento</div>
                    </div>
                  </div>
                </div>

                <div 
                  className="absolute -bottom-4 -left-8 backdrop-blur-xl bg-cyan-500/20 border border-cyan-500/30 rounded-2xl p-4 animate-float-delayed"
                >
                  <div className="flex items-center space-x-3">
                    <Shield className="w-6 h-6 text-cyan-400" />
                    <div>
                      <div className="text-white text-sm font-semibold">Seguro</div>
                      <div className="text-cyan-300 text-xs">Criptografia quântica</div>
                    </div>
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
          
          {/* Section Header */}
          <div className="text-center mb-20">
            <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-500/20 to-cyan-500/20 border border-blue-500/30 rounded-full px-6 py-3 mb-8">
              <Zap className="w-4 h-4 text-blue-400" />
              <span className="text-blue-300 text-sm font-semibold">Tecnologia Avançada</span>
            </div>
            
            <h2 className="text-5xl font-black bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent mb-6">
              Recursos Revolucionários
            </h2>
            
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Cada recurso foi desenvolvido com IA e machine learning para entregar a melhor experiência possível
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div 
                key={index}
                className="group relative backdrop-blur-2xl bg-gradient-to-br from-white/[0.08] to-white/[0.02] border border-white/10 rounded-3xl p-8 hover:bg-white/[0.12] transition-all duration-500 cursor-pointer"
                style={{
                  animationDelay: `${index * 0.1}s`
                }}
              >
                {/* Icon */}
                <div className="relative mb-6">
                  <div className={`absolute inset-0 bg-gradient-to-r ${feature.gradient} rounded-2xl blur-xl opacity-50 group-hover:opacity-70 transition-opacity`} />
                  <div className={`relative bg-gradient-to-r ${feature.gradient} p-4 rounded-2xl w-16 h-16 flex items-center justify-center shadow-2xl`}>
                    <feature.icon className="w-8 h-8 text-white" />
                  </div>
                </div>

                {/* Content */}
                <h3 className="text-xl font-bold text-white mb-3 group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-purple-400 group-hover:to-pink-400 group-hover:bg-clip-text transition-all duration-300">
                  {feature.title}
                </h3>
                
                <p className="text-gray-400 mb-4 leading-relaxed">
                  {feature.description}
                </p>

                <div className="flex items-center justify-between">
                  <span className={`bg-gradient-to-r ${feature.gradient} bg-clip-text text-transparent font-semibold text-sm`}>
                    {feature.stats}
                  </span>
                  <ArrowRight className="w-4 h-4 text-gray-500 group-hover:text-white group-hover:translate-x-1 transition-all duration-300" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="relative z-10 py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="backdrop-blur-2xl bg-gradient-to-r from-purple-500/10 via-pink-500/10 to-cyan-500/10 border border-white/20 rounded-3xl p-12">
            
            <div className="text-center mb-12">
              <h2 className="text-4xl font-black bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent mb-4">
                Números que Impressionam
              </h2>
              <p className="text-gray-400">Resultados reais de clientes que transformaram seus eventos</p>
            </div>

            <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
              {stats.map((stat, index) => (
                <div key={index} className="text-center group">
                  <div className="relative mb-4">
                    <div className="text-4xl lg:text-5xl font-black bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent mb-2">
                      {stat.number}
                    </div>
                    <div className="text-gray-300 font-semibold mb-2">{stat.label}</div>
                    <div className="inline-flex items-center space-x-1 bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-xs font-semibold">
                      <TrendingUp className="w-3 h-3" />
                      <span>{stat.growth}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="relative z-10 py-32">
        <div className="max-w-7xl mx-auto px-6">
          
          <div className="text-center mb-20">
            <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border border-yellow-500/30 rounded-full px-6 py-3 mb-8">
              <Award className="w-4 h-4 text-yellow-400" />
              <span className="text-yellow-300 text-sm font-semibold">Clientes Satisfeitos</span>
            </div>
            
            <h2 className="text-5xl font-black bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent mb-6">
              O que Dizem Sobre Nós
            </h2>
          </div>

          {/* Testimonial Carousel */}
          <div className="relative">
            <div className="backdrop-blur-2xl bg-gradient-to-br from-white/10 to-white/5 border border-white/20 rounded-3xl p-12 text-center">
              
              {/* Stars */}
              <div className="flex justify-center space-x-1 mb-6">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-6 h-6 text-yellow-400 fill-current" />
                ))}
              </div>

              {/* Quote */}
              <blockquote className="text-2xl text-gray-300 mb-8 max-w-4xl mx-auto leading-relaxed">
                "{testimonials[currentTestimonial].text}"
              </blockquote>

              {/* Author */}
              <div className="flex items-center justify-center space-x-4">
                <img 
                  src={testimonials[currentTestimonial].image}
                  alt={testimonials[currentTestimonial].name}
                  className="w-16 h-16 rounded-full object-cover border-2 border-purple-500/50"
                />
                <div className="text-left">
                  <div className="text-white font-semibold text-lg">
                    {testimonials[currentTestimonial].name}
                  </div>
                  <div className="text-gray-400">
                    {testimonials[currentTestimonial].role} • {testimonials[currentTestimonial].company}
                  </div>
                </div>
              </div>

              {/* Dots */}
              <div className="flex justify-center space-x-3 mt-8">
                {testimonials.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentTestimonial(index)}
                    className={`w-3 h-3 rounded-full transition-all duration-300 ${
                      currentTestimonial === index 
                        ? 'bg-purple-500 scale-125' 
                        : 'bg-gray-600 hover:bg-gray-500'
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 py-32">
        <div className="max-w-4xl mx-auto px-6 text-center">
          
          <div className="backdrop-blur-2xl bg-gradient-to-br from-purple-500/20 via-pink-500/20 to-cyan-500/20 border border-white/20 rounded-3xl p-16">
            
            <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-full px-6 py-3 mb-8">
              <Rocket className="w-4 h-4 text-green-400" />
              <span className="text-green-300 text-sm font-semibold">Comece Hoje</span>
            </div>

            <h2 className="text-5xl font-black bg-gradient-to-r from-white via-purple-200 to-pink-200 bg-clip-text text-transparent mb-6">
              Pronto para Revolucionar Seus Eventos?
            </h2>
            
            <p className="text-xl text-gray-300 mb-10 max-w-2xl mx-auto">
              Junte-se a milhares de organizadores que já transformaram seus eventos com nossa plataforma de IA
            </p>

            <div className="flex flex-col sm:flex-row gap-6 justify-center">
              <button className="group relative overflow-hidden bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white px-10 py-5 rounded-2xl font-bold text-xl transition-all duration-500 transform hover:scale-105 shadow-2xl">
                <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                <div className="flex items-center space-x-3">
                  <span>Teste Grátis por 30 Dias</span>
                  <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                </div>
              </button>

              <button className="backdrop-blur-xl bg-white/10 border border-white/20 text-white px-10 py-5 rounded-2xl font-semibold text-xl hover:bg-white/20 transition-all duration-300">
                Agendar Demo
              </button>
            </div>

            <div className="mt-8 text-gray-400 text-sm">
              ✓ Sem cartão de crédito ✓ Setup em 5 minutos ✓ Suporte 24/7
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/10 py-16">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8">
            
            {/* Brand */}
            <div className="space-y-4">
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
              <p className="text-gray-400">
                A próxima geração de gestão de eventos com inteligência artificial.
              </p>
            </div>

            {/* Links */}
            {[
              {
                title: "Produto",
                links: ["Recursos", "Preços", "Integrações", "API"]
              },
              {
                title: "Empresa",
                links: ["Sobre", "Blog", "Carreiras", "Contato"]
              },
              {
                title: "Suporte",
                links: ["Central de Ajuda", "Documentação", "Status", "Comunidade"]
              }
            ].map((section, index) => (
              <div key={index} className="space-y-4">
                <h4 className="text-white font-semibold">{section.title}</h4>
                <ul className="space-y-2">
                  {section.links.map((link) => (
                    <li key={link}>
                      <button className="text-gray-400 hover:text-white transition-colors">
                        {link}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="border-t border-white/10 mt-16 pt-8 flex flex-col md:flex-row justify-between items-center">
            <div className="text-gray-400 text-sm">
              © 2025 EventsAI. Todos os direitos reservados.
            </div>
            <div className="flex items-center space-x-6 mt-4 md:mt-0">
              <button className="text-gray-400 hover:text-white transition-colors text-sm">
                Privacidade
              </button>
              <button className="text-gray-400 hover:text-white transition-colors text-sm">
                Termos
              </button>
              <button className="text-gray-400 hover:text-white transition-colors text-sm">
                Cookies
              </button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default UltraModernLanding;
