import React from 'react'
import { Star, Zap } from 'lucide-react'

const TailwindTest = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-slate-900 to-pink-900 p-8">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-6xl font-black text-white mb-8">
          🚀 TESTE TAILWIND
        </h1>
        
        <div className="bg-slate-800/40 backdrop-blur-xl rounded-3xl p-8 border border-slate-700/50 mb-8">
          <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 mb-6">
            Se você vê CORES e GRADIENTES, o Tailwind está funcionando! ✨
          </h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 p-6 rounded-xl border border-purple-500/30">
              <Star className="w-12 h-12 text-purple-400 mx-auto mb-4" />
              <h3 className="text-white font-bold text-xl">Gradiente Purple</h3>
              <p className="text-slate-300">Este card tem gradiente purple</p>
            </div>
            
            <div className="bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 p-6 rounded-xl border border-emerald-500/30">
              <Zap className="w-12 h-12 text-emerald-400 mx-auto mb-4" />
              <h3 className="text-white font-bold text-xl">Gradiente Emerald</h3>
              <p className="text-slate-300">Este card tem gradiente emerald</p>
            </div>
            
            <div className="bg-gradient-to-r from-pink-500/20 to-purple-500/20 p-6 rounded-xl border border-pink-500/30">
              <Star className="w-12 h-12 text-pink-400 mx-auto mb-4" />
              <h3 className="text-white font-bold text-xl">Gradiente Pink</h3>
              <p className="text-slate-300">Este card tem gradiente pink</p>
            </div>
          </div>
        </div>
        
        <button className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-12 py-4 rounded-xl font-bold text-xl hover:shadow-2xl transition-all">
          BOTÃO COM GRADIENTE
        </button>
        
        <div className="mt-8 p-6 bg-emerald-500/10 border border-emerald-500/30 rounded-xl">
          <p className="text-emerald-400 font-bold text-lg">
            ✅ Se você vê este texto VERDE e os gradientes acima, o Tailwind está funcionando perfeitamente!
          </p>
          <p className="text-white mt-2">
            Agora podemos corrigir a landing page principal.
          </p>
        </div>
        
        <div className="mt-8 p-6 bg-red-500/10 border border-red-500/30 rounded-xl">
          <p className="text-red-400 font-bold text-lg">
            ❌ Se você vê apenas texto branco sem cores/gradientes, o Tailwind NÃO está funcionando.
          </p>
          <p className="text-white mt-2">
            Neste caso, precisamos depurar mais.
          </p>
        </div>
      </div>
    </div>
  )
}

export default TailwindTest
