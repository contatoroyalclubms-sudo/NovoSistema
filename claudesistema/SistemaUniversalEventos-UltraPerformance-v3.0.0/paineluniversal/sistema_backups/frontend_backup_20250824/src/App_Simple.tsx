import React, { useState } from 'react'
import './App.css'

function App() {
  const [currentView, setCurrentView] = useState<'dashboard' | 'design-system' | 'pdv'>('dashboard')

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <div className="fixed top-0 left-0 right-0 z-50 bg-black/20 backdrop-blur-xl border-b border-white/10">
        <div className="flex items-center justify-between px-6 py-3">
          <h1 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
            🧠 Sistema Neural Universal
          </h1>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentView('dashboard')}
              className={`px-3 py-1.5 text-sm rounded-lg transition-all ${
                currentView === 'dashboard' 
                  ? 'bg-purple-500 text-white' 
                  : 'bg-white/10 text-white/70 hover:bg-white/20'
              }`}
            >
              📊 Dashboard
            </button>
            
            <button
              onClick={() => setCurrentView('design-system')}
              className={`px-3 py-1.5 text-sm rounded-lg transition-all ${
                currentView === 'design-system' 
                  ? 'bg-purple-500 text-white' 
                  : 'bg-white/10 text-white/70 hover:bg-white/20'
              }`}
            >
              🎨 Design System
            </button>
            
            <button
              onClick={() => setCurrentView('pdv')}
              className={`px-3 py-1.5 text-sm rounded-lg transition-all ${
                currentView === 'pdv' 
                  ? 'bg-purple-500 text-white' 
                  : 'bg-white/10 text-white/70 hover:bg-white/20'
              }`}
            >
              🛒 PDV Ultra-Moderno
            </button>
          </div>
        </div>
      </div>

      {/* Conteúdo Principal */}
      <div className="pt-16 p-8">
        {currentView === 'dashboard' && (
          <div className="max-w-6xl mx-auto space-y-6">
            <h2 className="text-3xl font-bold text-white mb-8">📊 Dashboard Neural Avançado</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="p-6 bg-white/10 rounded-xl border border-white/20">
                <h3 className="text-lg font-bold text-cyan-400 mb-2">Vendas Hoje</h3>
                <p className="text-2xl font-bold text-white">R$ 2.450,80</p>
                <p className="text-green-400 text-sm">+15% vs ontem</p>
              </div>
              
              <div className="p-6 bg-white/10 rounded-xl border border-white/20">
                <h3 className="text-lg font-bold text-purple-400 mb-2">Produtos Vendidos</h3>
                <p className="text-2xl font-bold text-white">127</p>
                <p className="text-green-400 text-sm">+8% vs ontem</p>
              </div>
              
              <div className="p-6 bg-white/10 rounded-xl border border-white/20">
                <h3 className="text-lg font-bold text-pink-400 mb-2">Clientes Ativos</h3>
                <p className="text-2xl font-bold text-white">89</p>
                <p className="text-blue-400 text-sm">Online agora</p>
              </div>
              
              <div className="p-6 bg-white/10 rounded-xl border border-white/20">
                <h3 className="text-lg font-bold text-yellow-400 mb-2">IA Score</h3>
                <p className="text-2xl font-bold text-white">96.5%</p>
                <p className="text-green-400 text-sm">Neural ativo</p>
              </div>
            </div>
            
            <div className="p-6 bg-white/10 rounded-xl border border-white/20">
              <h3 className="text-xl font-bold text-white mb-4">🧠 Status Neural</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-white/70">Backend API</span>
                  <span className="text-green-400">✅ Conectado</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-white/70">WebSocket</span>
                  <span className="text-green-400">✅ Ativo</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-white/70">IA Engine</span>
                  <span className="text-green-400">✅ Processando</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {currentView === 'design-system' && (
          <div className="max-w-4xl mx-auto space-y-6">
            <h2 className="text-3xl font-bold text-white mb-8">🎨 Ultra Design System Neural</h2>
            
            <div className="p-6 bg-white/10 rounded-xl border border-white/20">
              <h3 className="text-xl font-bold text-white mb-4">Botões Ultra-Modernos</h3>
              <div className="space-x-4">
                <button className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-purple-600 text-white rounded-lg hover:scale-105 transition-transform">
                  Neural Primary
                </button>
                <button className="px-4 py-2 bg-white/10 border border-cyan-400/30 text-white rounded-lg hover:bg-white/20 transition-colors">
                  Quantum Ghost
                </button>
                <button className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg hover:shadow-purple-500/25 transition-all">
                  Cosmic Effect
                </button>
              </div>
            </div>
            
            <div className="p-6 bg-white/10 rounded-xl border border-white/20">
              <h3 className="text-xl font-bold text-white mb-4">Cards & Inputs</h3>
              <div className="space-y-4">
                <input 
                  type="text" 
                  placeholder="Input Neural com Glassmorphism..." 
                  className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-xl text-white placeholder-white/50 focus:border-cyan-400/50 focus:outline-none backdrop-blur-xl"
                />
                <div className="p-4 bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-pink-500/10 border border-white/10 rounded-xl">
                  <p className="text-white">Card com gradiente neural e glassmorphism ativo</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {currentView === 'pdv' && (
          <div className="max-w-6xl mx-auto space-y-6">
            <h2 className="text-3xl font-bold text-white mb-8">🛒 PDV Ultra-Moderno com IA</h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-4">
                <div className="p-6 bg-white/10 rounded-xl border border-white/20">
                  <h3 className="text-xl font-bold text-white mb-4">📷 Scanner Neural</h3>
                  <div className="bg-black/30 rounded-lg p-8 text-center border-2 border-dashed border-cyan-400/30">
                    <p className="text-white/70">Scanner de produtos com IA ativo</p>
                    <p className="text-cyan-400 text-sm mt-2">Clique para escanear código de barras</p>
                  </div>
                </div>
                
                <div className="p-6 bg-white/10 rounded-xl border border-white/20">
                  <h3 className="text-xl font-bold text-white mb-4">🛍️ Produtos Disponíveis</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors cursor-pointer">
                      <h4 className="font-bold text-white">🍺 Cerveja IPA</h4>
                      <p className="text-cyan-400">R$ 12,50</p>
                    </div>
                    <div className="p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors cursor-pointer">
                      <h4 className="font-bold text-white">🍔 Hambúrguer</h4>
                      <p className="text-cyan-400">R$ 25,90</p>
                    </div>
                    <div className="p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors cursor-pointer">
                      <h4 className="font-bold text-white">💧 Água 500ml</h4>
                      <p className="text-cyan-400">R$ 3,50</p>
                    </div>
                    <div className="p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors cursor-pointer">
                      <h4 className="font-bold text-white">🍟 Batata Frita</h4>
                      <p className="text-cyan-400">R$ 15,00</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="p-6 bg-white/10 rounded-xl border border-white/20">
                  <h3 className="text-xl font-bold text-white mb-4">🛒 Carrinho</h3>
                  <div className="text-center text-white/50 py-8">
                    Carrinho vazio
                  </div>
                  <div className="border-t border-white/10 pt-4 mt-4">
                    <div className="flex justify-between items-center">
                      <span className="text-white font-bold">Total:</span>
                      <span className="text-2xl font-bold text-cyan-400">R$ 0,00</span>
                    </div>
                  </div>
                </div>
                
                <div className="p-6 bg-white/10 rounded-xl border border-white/20">
                  <h3 className="text-xl font-bold text-white mb-4">🧠 IA Recomendações</h3>
                  <div className="space-y-2">
                    <div className="p-3 bg-purple-500/20 border border-purple-400/30 rounded-lg">
                      <p className="text-sm text-white">🍺 Cerveja combina com 🍔 Hambúrguer</p>
                      <p className="text-xs text-purple-300">Score: 95%</p>
                    </div>
                    <div className="p-3 bg-cyan-500/20 border border-cyan-400/30 rounded-lg">
                      <p className="text-sm text-white">🍟 Batata é o mais vendido hoje</p>
                      <p className="text-xs text-cyan-300">Score: 88%</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
