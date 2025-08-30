import React, { useState } from 'react';

/**
 * 🎨 Design System Neural Futurista - Demo Component
 * Demonstra todas as funcionalidades do design system ultra-moderno
 */

const DesignSystemDemo: React.FC = () => {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme === 'light' ? 'dark' : 'light');
  };

  return (
    <div data-theme={theme} className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-8 space-neural">
      {/* Header com Theme Toggle */}
      <div className="glass p-6 mb-8 flex justify-between items-center">
        <h1 className="text-display-1 font-display">Design System Neural</h1>
        <button 
          onClick={toggleTheme}
          className="glass hover-lift px-6 py-3 rounded-xl font-semibold transition-all duration-300"
        >
          {theme === 'dark' ? '☀️ Light' : '🌙 Dark'} Mode
        </button>
      </div>

      {/* Grid de Demonstrações */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        
        {/* 🎨 Paleta de Cores */}
        <div className="glass p-6 space-y-4">
          <h2 className="text-heading-2 font-display">🌈 Cores Neurais</h2>
          
          <div className="space-y-3">
            <div className="gradient-neural h-12 rounded-lg flex items-center justify-center">
              <span className="font-semibold text-white">Gradiente Neural</span>
            </div>
            
            <div className="gradient-secondary h-12 rounded-lg flex items-center justify-center">
              <span className="font-semibold text-white">Gradiente Cibernético</span>
            </div>
            
            <div className="gradient-holographic h-12 rounded-lg flex items-center justify-center">
              <span className="font-semibold text-white">Holográfico</span>
            </div>
          </div>
          
          {/* Estado de Cores */}
          <div className="grid grid-cols-2 gap-2">
            <div className="h-8 bg-green-500 rounded flex items-center justify-center text-xs font-semibold text-white">Success</div>
            <div className="h-8 bg-yellow-500 rounded flex items-center justify-center text-xs font-semibold text-white">Warning</div>
            <div className="h-8 bg-red-500 rounded flex items-center justify-center text-xs font-semibold text-white">Error</div>
            <div className="h-8 bg-blue-500 rounded flex items-center justify-center text-xs font-semibold text-white">Info</div>
          </div>
        </div>

        {/* ✨ Efeitos Visuais */}
        <div className="glass p-6 space-y-4">
          <h2 className="text-heading-2 font-display">✨ Efeitos Visuais</h2>
          
          <div className="space-y-4">
            <div className="neomorphic p-4 text-center">
              <span className="font-semibold">Neumorphism</span>
            </div>
            
            <div className="glass-strong p-4 text-center">
              <span className="font-semibold">Glassmorphism 3.0</span>
            </div>
            
            <div className="border-holographic p-4 text-center">
              <span className="font-semibold">Border Holográfico</span>
            </div>
            
            <div className="shadow-cosmic p-4 bg-white rounded-lg text-center">
              <span className="font-semibold text-gray-800">Sombra Cósmica</span>
            </div>
          </div>
        </div>

        {/* 🔤 Tipografia */}
        <div className="glass p-6 space-y-4">
          <h2 className="text-heading-2 font-display">📝 Tipografia</h2>
          
          <div className="space-y-3">
            <div className="text-display-1 font-display">Display 1</div>
            <div className="text-display-2 font-display">Display 2</div>
            <div className="text-heading-1">Heading 1</div>
            <div className="text-heading-2">Heading 2</div>
            <div className="text-body-lg">Body Large</div>
            <div className="text-body">Body Regular</div>
            <div className="text-body-sm">Body Small</div>
            <div className="text-caption">Caption Text</div>
            <div className="font-mono text-sm">Código Monospace</div>
          </div>
        </div>

        {/* 🎭 Animações */}
        <div className="glass p-6 space-y-4">
          <h2 className="text-heading-2 font-display">🎭 Animações</h2>
          
          <div className="space-y-4">
            <div className="animate-glow p-4 bg-purple-600 rounded-lg text-center text-white font-semibold">
              Glow Effect
            </div>
            
            <div className="animate-pulse-neural p-4 bg-blue-600 rounded-lg text-center text-white font-semibold">
              Pulse Neural
            </div>
            
            <div className="animate-float p-4 bg-pink-600 rounded-lg text-center text-white font-semibold">
              Float Effect
            </div>
            
            <div className="state-loading p-4 bg-gray-600 rounded-lg text-center text-white font-semibold">
              Loading Shimmer
            </div>
          </div>
        </div>

        {/* 🎪 Interatividade */}
        <div className="glass p-6 space-y-4">
          <h2 className="text-heading-2 font-display">🎮 Interatividade</h2>
          
          <div className="space-y-4">
            <button className="w-full gradient-neural hover-lift p-4 rounded-lg text-white font-semibold interactive">
              Botão Neural
            </button>
            
            <button className="w-full neomorphic hover-lift p-4 rounded-lg font-semibold interactive">
              Botão Neomorph
            </button>
            
            <div className="glass hover-lift interactive p-4 rounded-lg text-center cursor-pointer">
              Card Interativo
            </div>
            
            <input 
              type="text" 
              placeholder="Input com Focus Neural" 
              className="w-full p-3 rounded-lg glass focus-neural"
            />
          </div>
        </div>

        {/* 🌟 Utilidades */}
        <div className="glass p-6 space-y-4">
          <h2 className="text-heading-2 font-display">🔧 Utilidades</h2>
          
          <div className="space-y-4">
            <div className="transform-gpu hover:scale-105 transition-transform p-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg text-white text-center">
              Transform GPU
            </div>
            
            <div className="shadow-neural p-3 bg-white rounded-lg text-center text-gray-800">
              Sombra Neural
            </div>
            
            <div className="shadow-holographic p-3 bg-white rounded-lg text-center text-gray-800">
              Sombra Holográfica
            </div>
            
            <div className="glass-dark p-3 rounded-lg text-center text-white">
              Glass Dark
            </div>
          </div>
        </div>
      </div>

      {/* Footer com Info */}
      <div className="glass mt-8 p-6 text-center">
        <p className="text-body mb-2">
          🚀 <strong>Design System Neural Futurista v3.0</strong>
        </p>
        <p className="text-body-sm text-gray-400">
          Sistema criado para estar 10 anos à frente do mercado em design e UX
        </p>
        <div className="mt-4 flex justify-center space-x-4">
          <span className="px-3 py-1 bg-green-500 text-white text-xs rounded-full">Glassmorphism 3.0</span>
          <span className="px-3 py-1 bg-blue-500 text-white text-xs rounded-full">Neural Colors</span>
          <span className="px-3 py-1 bg-purple-500 text-white text-xs rounded-full">Holographic</span>
          <span className="px-3 py-1 bg-pink-500 text-white text-xs rounded-full">Ultra Modern</span>
        </div>
      </div>
    </div>
  );
};

export default DesignSystemDemo;