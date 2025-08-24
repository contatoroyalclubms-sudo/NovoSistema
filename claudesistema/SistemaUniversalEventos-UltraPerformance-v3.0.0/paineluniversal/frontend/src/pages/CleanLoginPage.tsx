import { useState } from 'react';
import {
  Mail, Lock, Eye, EyeOff, ArrowRight,
  Rocket, Sparkles, Shield, Zap, Heart,
  Brain, Fingerprint, BarChart3
} from 'lucide-react';

const CleanLoginPage = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);

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

  return (
    <div className="min-h-screen bg-slate-900 flex">

      {/* Left Side - Branding/Visual */}
      <div className="hidden lg:flex lg:w-3/5 relative overflow-hidden">

        {/* Background com gradiente animado */}
        <div className="absolute inset-0 bg-gradient-to-br from-purple-900 via-pink-900 to-slate-900">
          {/* Overlay com padrão */}
          <div className="absolute inset-0 opacity-20">
            <div className="w-full h-full" style={{
              backgroundImage: `radial-gradient(circle at 25% 25%, rgba(139, 92, 246, 0.4) 0%, transparent 50%), 
                               radial-gradient(circle at 75% 75%, rgba(236, 72, 153, 0.4) 0%, transparent 50%)`
            }} />
          </div>
        </div>

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-center p-16 text-white">

          {/* Logo Principal */}
          <div className="mb-12">
            <div className="flex items-center space-x-4 mb-8">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-3xl blur-2xl opacity-75" />
                <div className="relative bg-gradient-to-r from-purple-500 to-pink-500 p-6 rounded-3xl">
                  <Rocket className="w-16 h-16 text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-6xl font-black bg-gradient-to-r from-white via-purple-200 to-pink-200 bg-clip-text text-transparent">
                  EventosIA
                </h1>
                <p className="text-2xl text-purple-300 font-bold">A Próxima Geração</p>
              </div>
            </div>
          </div>

          {/* Main Message */}
          <div className="space-y-8 max-w-2xl">
            <div className="inline-flex items-center space-x-3 bg-white/10 backdrop-blur-xl border border-white/20 rounded-full px-8 py-4">
              <Sparkles className="w-6 h-6 text-yellow-400" />
              <span className="text-white font-bold text-lg">Tecnologia do Futuro</span>
            </div>

            <h2 className="text-5xl font-black leading-tight">
              <span className="text-white">Eventos Inteligentes com</span>
              <br />
              <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent">
                IA Avançada
              </span>
            </h2>

            <p className="text-2xl text-purple-100 leading-relaxed">
              A única plataforma que combina <strong>Inteligência Artificial</strong>,
              <strong> Biometria Facial</strong> e <strong>Blockchain</strong>
              para revolucionar seus eventos.
            </p>
          </div>

          {/* Features Cards */}
          <div className="grid grid-cols-3 gap-6 mt-16">
            <div className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl p-6 text-center hover:bg-white/20 transition-all duration-300">
              <Brain className="w-12 h-12 text-purple-400 mx-auto mb-4" />
              <h3 className="text-white font-bold text-lg mb-2">IA Generativa</h3>
              <p className="text-purple-200 text-sm">GPT-4 integrado</p>
            </div>

            <div className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl p-6 text-center hover:bg-white/20 transition-all duration-300">
              <Fingerprint className="w-12 h-12 text-pink-400 mx-auto mb-4" />
              <h3 className="text-white font-bold text-lg mb-2">Biometria 3D</h3>
              <p className="text-purple-200 text-sm">Check-in facial</p>
            </div>

            <div className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl p-6 text-center hover:bg-white/20 transition-all duration-300">
              <BarChart3 className="w-12 h-12 text-cyan-400 mx-auto mb-4" />
              <h3 className="text-white font-bold text-lg mb-2">Analytics IA</h3>
              <p className="text-purple-200 text-sm">Insights em tempo real</p>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-2/5 flex items-center justify-center p-8 lg:p-16 bg-slate-900 relative">

        {/* Background Effects */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/3 right-1/3 w-96 h-96 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-1/3 left-1/3 w-80 h-80 bg-gradient-to-br from-cyan-500/20 to-blue-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
        </div>

        {/* Mobile Logo */}
        <div className="lg:hidden absolute top-8 left-8 flex items-center space-x-3">
          <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-3 rounded-xl">
            <Rocket className="w-6 h-6 text-white" />
          </div>
          <span className="text-2xl font-black text-white">EventosIA</span>
        </div>

        {/* Form Container */}
        <div className="w-full max-w-md relative z-10">

          {/* Header */}
          <div className="text-center mb-12">
            <h3 className="text-4xl font-black text-white mb-4">
              {isLogin ? 'Bem-vindo de volta!' : 'Crie sua conta'}
            </h3>
            <p className="text-lg text-gray-300">
              {isLogin
                ? 'Entre na plataforma do futuro'
                : 'Comece sua jornada conosco'
              }
            </p>
          </div>

          {/* Form Fields */}
          <div className="space-y-6">

            {/* Email */}
            <div>
              <label className="block text-sm font-bold text-gray-300 mb-3 uppercase tracking-wider">
                E-mail
              </label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="w-full pl-12 pr-4 py-4 bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300 text-lg"
                  placeholder="Digite seu e-mail"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-bold text-gray-300 mb-3 uppercase tracking-wider">
                Senha
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="w-full pl-12 pr-12 py-4 bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300 text-lg"
                  placeholder="Digite sua senha"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Options */}
            {isLogin && (
              <div className="flex items-center justify-between">
                <label className="flex items-center space-x-2 text-gray-300 cursor-pointer">
                  <input type="checkbox" className="w-4 h-4 text-purple-500 bg-transparent border-gray-300 rounded focus:ring-purple-500" />
                  <span className="text-sm">Lembrar de mim</span>
                </label>
                <button className="text-sm text-purple-400 hover:text-purple-300 transition-colors">
                  Esqueci minha senha
                </button>
              </div>
            )}

            {/* Submit Button */}
            <button
              onClick={handleSubmit}
              className="group w-full relative overflow-hidden bg-gradient-to-r from-purple-600 via-pink-600 to-purple-600 hover:from-purple-500 hover:via-pink-500 hover:to-purple-500 text-white py-5 rounded-2xl font-bold text-xl transition-all duration-300 transform hover:scale-[1.02] shadow-2xl hover:shadow-purple-500/25"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
              <div className="flex items-center justify-center space-x-3 relative">
                <span>{isLogin ? 'Entrar na Plataforma' : 'Criar Conta Grátis'}</span>
                <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
              </div>
            </button>

            {/* Toggle */}
            <div className="text-center pt-6">
              <span className="text-gray-400">
                {isLogin ? 'Novo por aqui?' : 'Já tem conta?'}
              </span>
              <button
                onClick={() => setIsLogin(!isLogin)}
                className="ml-2 text-purple-400 hover:text-purple-300 font-bold transition-colors"
              >
                {isLogin ? 'Criar conta grátis' : 'Fazer login'}
              </button>
            </div>
          </div>

          {/* Trust Indicators */}
          <div className="flex items-center justify-center space-x-8 mt-12 text-sm text-gray-400">
            <div className="flex items-center space-x-2">
              <Shield className="w-4 h-4 text-green-400" />
              <span>100% Seguro</span>
            </div>
            <div className="flex items-center space-x-2">
              <Zap className="w-4 h-4 text-yellow-400" />
              <span>Super Rápido</span>
            </div>
            <div className="flex items-center space-x-2">
              <Heart className="w-4 h-4 text-pink-400" />
              <span>Confiável</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CleanLoginPage;
