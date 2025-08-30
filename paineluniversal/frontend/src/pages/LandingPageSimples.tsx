import React from 'react'

const LandingPageSimples = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-slate-900 to-pink-900">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <header className="text-center mb-16">
          <h1 className="text-6xl font-black text-white mb-6">
            🚀 <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">EventosIA</span>
          </h1>
          <p className="text-2xl text-slate-300 max-w-3xl mx-auto">
            A próxima geração de gestão de eventos com inteligência artificial
          </p>
        </header>

        {/* Cards principais */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-slate-700">
            <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center mb-6">
              <span className="text-2xl">🧠</span>
            </div>
            <h3 className="text-2xl font-bold text-white mb-4">IA Integrada</h3>
            <p className="text-slate-300 leading-relaxed">
              Inteligência artificial avançada para otimizar cada aspecto do seu evento automaticamente.
            </p>
          </div>

          <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-slate-700">
            <div className="w-16 h-16 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-xl flex items-center justify-center mb-6">
              <span className="text-2xl">📱</span>
            </div>
            <h3 className="text-2xl font-bold text-white mb-4">Check-in Biométrico</h3>
            <p className="text-slate-300 leading-relaxed">
              Reconhecimento facial avançado para entrada segura e instantânea nos eventos.
            </p>
          </div>

          <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-slate-700">
            <div className="w-16 h-16 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-xl flex items-center justify-center mb-6">
              <span className="text-2xl">💳</span>
            </div>
            <h3 className="text-2xl font-bold text-white mb-4">PDV Completo</h3>
            <p className="text-slate-300 leading-relaxed">
              Sistema de vendas integrado com controle de estoque e relatórios em tempo real.
            </p>
          </div>
        </div>

        {/* Stats */}
        <div className="bg-slate-800/30 backdrop-blur-sm rounded-3xl p-12 border border-slate-700/50 mb-16">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400 mb-2">
                1000+
              </div>
              <p className="text-slate-300">Eventos Realizados</p>
            </div>
            <div>
              <div className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 mb-2">
                50k+
              </div>
              <p className="text-slate-300">Participantes</p>
            </div>
            <div>
              <div className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400 mb-2">
                98%
              </div>
              <p className="text-slate-300">Satisfação</p>
            </div>
            <div>
              <div className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-400 mb-2">
                24/7
              </div>
              <p className="text-slate-300">Suporte</p>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center">
          <button className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-12 py-4 rounded-xl font-bold text-xl hover:shadow-2xl transition-all mb-4">
            COMEÇAR AGORA - GRÁTIS
          </button>
          <p className="text-slate-400">✓ 30 dias grátis ✓ Sem cartão ✓ Setup gratuito</p>
        </div>
      </div>
    </div>
  )
}

export default LandingPageSimples
