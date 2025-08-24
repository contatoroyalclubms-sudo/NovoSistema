import React, { useState, useEffect } from 'react';
import { Eye, EyeOff, Calendar, Sparkles, ArrowRight, Shield, Fingerprint } from 'lucide-react';
import { useAuth } from '../../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const NextGenLogin = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [formData, setFormData] = useState({
    cpf: '',
    senha: ''
  });

  const { login } = useAuth();
  const navigate = useNavigate();

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      await login(formData);
      navigate('/dashboard');
    } catch (error) {
      console.error('Erro no login:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatCPF = (value: string) => {
    const numbers = value.replace(/\D/g, '');
    return numbers.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      
      <div 
        className="absolute inset-0 opacity-70"
        style={{
          background: `radial-gradient(circle at ${mousePosition.x}% ${mousePosition.y}%, 
            rgba(139, 92, 246, 0.3) 0%, 
            rgba(236, 72, 153, 0.2) 25%, 
            rgba(59, 130, 246, 0.1) 50%, 
            transparent 70%)`
        }}
      />

      <div className="relative z-10 min-h-screen flex">
        
        {/* Left Side - Features */}
        <div className="hidden lg:flex lg:w-1/2 flex-col justify-center items-center p-12">
          <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-10 text-center max-w-lg">
            
            <div className="relative mb-10">
              <div className="absolute inset-0 bg-gradient-to-r from-violet-500 via-purple-500 to-pink-500 rounded-full blur-2xl opacity-60 animate-pulse" />
              <div className="relative bg-gradient-to-br from-violet-500 via-purple-500 to-pink-500 p-8 rounded-full w-24 h-24 mx-auto flex items-center justify-center">
                <Calendar className="w-12 h-12 text-white" />
              </div>
            </div>

            <h1 className="text-5xl font-black bg-gradient-to-r from-white via-gray-100 to-gray-300 bg-clip-text text-transparent mb-6">
              Sistema de Eventos
              <span className="block text-3xl bg-gradient-to-r from-violet-400 to-pink-400 bg-clip-text text-transparent">
                Next Generation
              </span>
            </h1>
            
            <p className="text-gray-300 text-lg mb-10">
              Plataforma de eventos com IA, realidade aumentada e automação inteligente
            </p>

            <div className="grid grid-cols-3 gap-4 text-center">
              {[
                { number: "50K+", label: "Eventos" },
                { number: "2M+", label: "Usuários" },
                { number: "99.9%", label: "Uptime" }
              ].map((stat, index) => (
                <div key={index} className="backdrop-blur-xl bg-white/[0.05] border border-white/[0.1] rounded-xl p-4">
                  <div className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                    {stat.number}
                  </div>
                  <div className="text-xs text-gray-400">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Side - Login Form */}
        <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
          <div className="w-full max-w-md">
            
            <div className="backdrop-blur-2xl bg-gradient-to-br from-white/[0.12] to-white/[0.04] border border-white/[0.1] rounded-[2rem] p-10 shadow-2xl">
              
              <div className="text-center mb-8">
                <div className="inline-flex items-center space-x-3 bg-gradient-to-r from-violet-500/20 via-purple-500/20 to-pink-500/20 border border-violet-500/30 rounded-full px-6 py-3 mb-6">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  <Sparkles className="w-4 h-4 text-violet-400" />
                  <span className="text-violet-300 text-sm font-semibold">Sistema Online</span>
                </div>
                
                <h2 className="text-4xl font-black bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent mb-3">
                  Acesso Seguro
                </h2>
                <p className="text-gray-400">Entre com suas credenciais para continuar</p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                
                <div className="space-y-3">
                  <label className="block text-sm font-semibold text-gray-300 uppercase tracking-wide">
                    CPF
                  </label>
                  <div className="relative group">
                    <input
                      type="text"
                      value={formData.cpf}
                      onChange={(e) => setFormData({...formData, cpf: formatCPF(e.target.value)})}
                      placeholder="000.000.000-00"
                      className="w-full px-6 py-5 bg-black/20 border border-white/[0.08] rounded-2xl text-white placeholder-gray-500 focus:bg-black/30 focus:border-violet-500/50 focus:ring-4 focus:ring-violet-500/20 transition-all duration-500 font-mono text-lg"
                      maxLength={14}
                      required
                    />
                    <div className="absolute right-5 top-1/2 transform -translate-y-1/2">
                      <Fingerprint className="w-5 h-5 text-gray-500" />
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <label className="block text-sm font-semibold text-gray-300 uppercase tracking-wide">
                    Senha
                  </label>
                  <div className="relative group">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={formData.senha}
                      onChange={(e) => setFormData({...formData, senha: e.target.value})}
                      placeholder="Digite sua senha"
                      className="w-full px-6 py-5 pr-16 bg-black/20 border border-white/[0.08] rounded-2xl text-white placeholder-gray-500 focus:bg-black/30 focus:border-violet-500/50 focus:ring-4 focus:ring-violet-500/20 transition-all duration-500 text-lg"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-5 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white transition-all duration-300"
                    >
                      {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full relative overflow-hidden bg-gradient-to-r from-violet-600 via-purple-600 to-pink-600 hover:from-violet-500 hover:via-purple-500 hover:to-pink-500 text-white py-5 px-8 rounded-2xl font-bold text-lg transition-all duration-500 transform hover:scale-[1.02] focus:ring-4 focus:ring-violet-500/30 disabled:opacity-70 shadow-2xl group"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                  
                  {isLoading ? (
                    <div className="flex items-center justify-center space-x-3">
                      <div className="w-6 h-6 border-3 border-white/30 border-t-white rounded-full animate-spin" />
                      <span>Autenticando...</span>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center space-x-3">
                      <Shield className="w-5 h-5" />
                      <span>Entrar no Sistema</span>
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </div>
                  )}
                </button>
              </form>

              <div className="text-center mt-6">
                <button 
                  onClick={() => navigate('/login')}
                  className="text-gray-400 hover:text-white text-sm transition-colors"
                >
                  Usar login clássico
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NextGenLogin;
