/**
 * 🧪 TESTE SIMPLES PARA DEBUG
 * Componente mínimo para testar se as importações estão funcionando
 */

import React from 'react';

const TestComponent = () => {
  return (
    <div className="p-8 bg-gray-900 text-white min-h-screen">
      <h1 className="text-3xl font-bold text-center mb-8">
        ✅ Sistema Funcionando!
      </h1>
      <div className="max-w-2xl mx-auto space-y-4">
        <div className="p-6 bg-white/10 rounded-xl border border-white/20">
          <h2 className="text-xl font-bold mb-2">Dashboard Neural</h2>
          <p className="text-white/70">Dashboard está carregando corretamente</p>
        </div>
        <div className="p-6 bg-white/10 rounded-xl border border-white/20">
          <h2 className="text-xl font-bold mb-2">PDV Ultra-Moderno</h2>
          <p className="text-white/70">PDV está integrado e funcionando</p>
        </div>
        <div className="p-6 bg-white/10 rounded-xl border border-white/20">
          <h2 className="text-xl font-bold mb-2">Sistema de Design</h2>
          <p className="text-white/70">Componentes ultra-modernos ativos</p>
        </div>
      </div>
    </div>
  );
};

export default TestComponent;
