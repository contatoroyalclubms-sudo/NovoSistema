import { useState, useEffect } from 'react';
import {
  Mail, Lock, Eye, EyeOff, ArrowRight,
  Rocket, Sparkles, Shield, Zap, Heart,
  Brain, Fingerprint, BarChart3, Users,
  TrendingUp, Globe, ChevronLeft, ChevronRight
} from 'lucide-react';

const MeepStyleLanding = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [currentSlide, setCurrentSlide] = useState(0);

  const slides = [
    {
      title: "Eventos Corporativos de Alto Nível",
      description: "Transforme suas conferências e workshops com IA generativa e biometria facial para uma experiência premium.",
      image: "https://images.unsplash.com/photo-1515187029135-18ee286d815b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80",
      badge: "🏢 Corporativo",
      stats: "500+ empresas"
    },
    {
      title: "Festivais e Shows Inesquecíveis",
      description: "Gerencie multidões com check-in facial instantâneo e PDV integrado para vendas em tempo real.",
      image: "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80",
      badge: "🎵 Entretenimento",
      stats: "2M+ participantes"
    },
    {
      title: "Casamentos e Eventos Sociais",
      description: "Crie memórias únicas com tecnologia invisível que garante segurança e praticidade para seus convidados.",
      image: "https://images.unsplash.com/photo-1519225421980-715cb0215aed?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80",
      badge: "💝 Social",
      stats: "99.9% satisfação"
    },
    {
      title: "Eventos Esportivos e Competições",
      description: "Gerencie competições complexas com analytics em tempo real e segurança biométrica avançada.",
      image: "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80",
      badge: "🏆 Esportes",
      stats: "150+ países"
    }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length);
    }, 5000);
    return () => clearInterval(timer);
  }, [slides.length]);

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % slides.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);
  };

  const handleSubmit = () => {
    if (!email || !password) {
      alert('Por favor, preencha todos os campos');
      return;
    }

    console.log('Dados de login:', { email, password, type: isLogin ? 'login' : 'cadastro' });

    // Simulação de sucesso - Aqui você integraria com sua API
    alert(`${isLogin ? 'Login' : 'Cadastro'} realizado com sucesso!`);

    // Redirecionamento após login
    window.location.href = '/';
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  const currentSlideData = slides[currentSlide];

  return (
    <div className="min-h-screen bg-slate-900 flex">

      {/* Left Side - Visual Carousel */}
      <div className="hidden lg:flex lg:w-3/5 relative overflow-hidden">

        {/* Background Image */}
        <div className="absolute inset-0">
          <img
            src={currentSlideData.image}
            alt={currentSlideData.title}
            className="w-full h-full object-cover transition-all duration-1000"
          />
          {/* Overlay gradiente */}
          <div className="absolute inset-0 bg-gradient-to-br from-purple-900/80 via-pink-900/60 to-slate-900/90" />
        </div>

        {/* Navigation Arrows */}
        <button
          onClick={prevSlide}
          className="absolute left-8 top-1/2 transform -translate-y-1/2 z-20 p-3 rounded-full bg-white/20 backdrop-blur-xl border border-white/30 text-white hover:bg-white/30 transition-all duration-300"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>

        <button
          onClick={nextSlide}
          className="absolute right-8 top-1/2 transform -translate-y-1/2 z-20 p-3 rounded-full bg-white/20 backdrop-blur-xl border border-white/30 text-white hover:bg-white/30 transition-all duration-300"
        >
          <ChevronRight className="w-6 h-6" />
        </button>

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-center p-16 text-white">

          {/* Logo Principal */}
          <div className="mb-8">
            <div className="flex items-center space-x-4 mb-6">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl blur-xl opacity-75" />
                <div className="relative bg-gradient-to-r from-purple-500 to-pink-500 p-4 rounded-2xl">
                  <Rocket className="w-12 h-12 text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-4xl font-black bg-gradient-to-r from-white via-purple-200 to-pink-200 bg-clip-text text-transparent">
                  EventosIA
                </h1>
                <p className="text-lg text-purple-300 font-bold">Next Generation</p>
              </div>
            </div>
          </div>

          {/* Slide Content */}
          <div className="space-y-6 max-w-2xl">

            {/* Badge */}
            <div className="inline-flex items-center space-x-2 bg-white/20 backdrop-blur-xl border border-white/30 rounded-full px-6 py-3">
              <span className="text-white font-bold">{currentSlideData.badge}</span>
            </div>

            {/* Title */}
            <h2 className="text-4xl font-black leading-tight text-white">
              {currentSlideData.title}
            </h2>

            {/* Description */}
            <p className="text-xl text-purple-100 leading-relaxed">
              {currentSlideData.description}
            </p>

            {/* Stats */}
            <div className="flex items-center space-x-8 pt-4">
              <div className="flex items-center space-x-2">
                <TrendingUp className="w-6 h-6 text-green-400" />
                <span className="text-white font-bold">{currentSlideData.stats}</span>
              </div>
              <div className="flex items-center space-x-2">
                <Shield className="w-6 h-6 text-blue-400" />
                <span className="text-white font-bold">100% Seguro</span>
              </div>
            </div>
          </div>

          {/* Slide Indicators */}
          <div className="absolute bottom-16 left-16 flex space-x-3">
            {slides.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentSlide(index)}
                className={`w-3 h-3 rounded-full transition-all duration-300 ${index === currentSlide
                    ? 'bg-white scale-125'
                    : 'bg-white/40 hover:bg-white/60'
                  }`}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-2/5 flex items-center justify-center p-8 lg:p-12 bg-slate-900 relative">

        {/* Background Effects */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 right-1/4 w-80 h-80 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-1/4 left-1/4 w-72 h-72 bg-gradient-to-br from-cyan-500/20 to-blue-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
        </div>

        {/* Mobile Logo */}
        <div className="lg:hidden absolute top-6 left-6 flex items-center space-x-3">
          <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-2 rounded-lg">
            <Rocket className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-black text-white">EventosIA</span>
        </div>

        {/* Form Container */}
        <div className="w-full max-w-md relative z-10">

          {/* Header */}
          <div className="text-center mb-8">
            <h3 className="text-3xl font-black text-white mb-3">
              {isLogin ? 'Bem-vindo!' : 'Criar Conta'}
            </h3>
            <p className="text-gray-300">
              {isLogin
                ? 'Acesse sua conta para continuar'
                : 'Junte-se à revolução dos eventos'
              }
            </p>
          </div>

          {/* Social Login */}
          <div className="grid grid-cols-2 gap-4 mb-8">
            <button className="flex items-center justify-center space-x-3 py-3 px-4 bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl text-white hover:bg-white/20 transition-all duration-300">
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
              </svg>
              <span className="text-sm font-semibold">Google</span>
            </button>

            <button className="flex items-center justify-center space-x-3 py-3 px-4 bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl text-white hover:bg-white/20 transition-all duration-300">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z" />
              </svg>
              <span className="text-sm font-semibold">Twitter</span>
            </button>
          </div>

          {/* Divider */}
          <div className="relative mb-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-white/20"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-slate-900 text-gray-400">ou continue com email</span>
            </div>
          </div>

          {/* Form Fields */}
          <div className="space-y-5">

            {/* Email */}
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">
                E-mail
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="w-full pl-10 pr-4 py-3 bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300"
                  placeholder="seu@email.com"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">
                Senha
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="w-full pl-10 pr-10 py-3 bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Options */}
            {isLogin && (
              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center space-x-2 text-gray-300 cursor-pointer">
                  <input type="checkbox" className="w-4 h-4 text-purple-500 bg-transparent border-gray-300 rounded focus:ring-purple-500" />
                  <span>Lembrar</span>
                </label>
                <button className="text-purple-400 hover:text-purple-300 transition-colors">
                  Esqueci a senha
                </button>
              </div>
            )}

            {/* Submit Button */}
            <button
              onClick={handleSubmit}
              className="group w-full relative overflow-hidden bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white py-4 rounded-xl font-bold text-lg transition-all duration-300 transform hover:scale-[1.02] shadow-xl hover:shadow-purple-500/25"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
              <div className="flex items-center justify-center space-x-2 relative">
                <span>{isLogin ? 'Entrar' : 'Criar Conta'}</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </div>
            </button>

            {/* Toggle */}
            <div className="text-center pt-4">
              <span className="text-gray-400 text-sm">
                {isLogin ? 'Novo aqui?' : 'Já tem conta?'}
              </span>
              <button
                onClick={() => setIsLogin(!isLogin)}
                className="ml-2 text-purple-400 hover:text-purple-300 font-semibold transition-colors text-sm"
              >
                {isLogin ? 'Criar conta' : 'Entrar'}
              </button>
            </div>
          </div>

          {/* Trust Indicators */}
          <div className="flex items-center justify-center space-x-6 mt-8 text-xs text-gray-400">
            <div className="flex items-center space-x-1">
              <Shield className="w-4 h-4 text-green-400" />
              <span>Seguro</span>
            </div>
            <div className="flex items-center space-x-1">
              <Zap className="w-4 h-4 text-yellow-400" />
              <span>Rápido</span>
            </div>
            <div className="flex items-center space-x-1">
              <Heart className="w-4 h-4 text-pink-400" />
              <span>Confiável</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MeepStyleLanding;
