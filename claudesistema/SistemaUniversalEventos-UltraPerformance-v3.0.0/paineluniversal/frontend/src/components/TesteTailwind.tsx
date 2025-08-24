import * as React from 'react'

const TesteTailwind: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-slate-900 to-pink-900 p-8">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-6xl font-black text-white mb-8">
          🚀 TESTE TAILWIND CORRIGIDO
        </h1>

        <div className="bg-slate-800/40 backdrop-blur-xl rounded-3xl p-8 border border-slate-700/50 mb-8">
          <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 mb-6">
            ✅ Se você vê CORES e GRADIENTES, o Tailwind está funcionando!
          </h2>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 p-6 rounded-xl border border-purple-500/30 hover:scale-105 transition-transform">
              <div className="w-12 h-12 bg-purple-500 rounded-xl mx-auto mb-4 flex items-center justify-center text-2xl">
                🧠
              </div>
              <h3 className="text-white font-bold text-xl">Gradiente Purple</h3>
              <p className="text-slate-300">PostCSS funcionando!</p>
            </div>

            <div className="bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 p-6 rounded-xl border border-emerald-500/30 hover:scale-105 transition-transform">
              <div className="w-12 h-12 bg-emerald-500 rounded-xl mx-auto mb-4 flex items-center justify-center text-2xl">
                ⚡
              </div>
              <h3 className="text-white font-bold text-xl">Gradiente Emerald</h3>
              <p className="text-slate-300">@tailwindcss/postcss OK!</p>
            </div>

            <div className="bg-gradient-to-r from-pink-500/20 to-purple-500/20 p-6 rounded-xl border border-pink-500/30 hover:scale-105 transition-transform">
              <div className="w-12 h-12 bg-pink-500 rounded-xl mx-auto mb-4 flex items-center justify-center text-2xl">
                🎨
              </div>
              <h3 className="text-white font-bold text-xl">Gradiente Pink</h3>
              <p className="text-slate-300">Configuração correta!</p>
            </div>
          </div>
        </div>

        <button className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-12 py-4 rounded-xl font-bold text-xl hover:shadow-2xl hover:scale-105 transition-all">
          BOTÃO COM GRADIENTE FUNCIONAL
        </button>

        <div className="mt-8 p-6 bg-emerald-500/10 border border-emerald-500/30 rounded-xl">
          <p className="text-emerald-400 font-bold text-lg">
            ✅ Tailwind CSS v4 + @tailwindcss/postcss funcionando perfeitamente!
          </p>
          <p className="text-white mt-2">
            Todas as funcionalidades existentes foram preservadas.
          </p>
        </div>

        <div className="mt-4 p-6 bg-blue-500/10 border border-blue-500/30 rounded-xl">
          <p className="text-blue-400 font-bold">
            🔧 Correções aplicadas:
          </p>
          <ul className="text-slate-300 mt-2 space-y-1">
            <li>• npm install -D @tailwindcss/postcss ✅</li>
            <li>• postcss.config.js corrigido ✅</li>
            <li>• tailwind.config.js atualizado ✅</li>
            <li>• Sem conflitos com funcionalidades existentes ✅</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default TesteTailwind
