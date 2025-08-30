import React from "react"
import { useRouter } from "next/router"
import { ArrowLeft } from "lucide-react"

export default function CashlessPage() {
  const router = useRouter()

  const handleBackToDashboard = () => {
    router.push("/")
  }

  const mesas = Array.from({length: 20}, (_, i) => ({
    numero: i + 1,
    status: i % 3 === 0 ? 'disponivel' : i % 3 === 1 ? 'ocupada' : 'fechando'
  }))

  const getStatusColor = (status) => {
    switch(status) {
      case 'disponivel': return 'bg-green-100 border-green-300 text-green-800'
      case 'ocupada': return 'bg-yellow-100 border-yellow-300 text-yellow-800'
      case 'fechando': return 'bg-red-100 border-red-300 text-red-800'
      default: return 'bg-gray-100 border-gray-300 text-gray-800'
    }
  }

  const getStatusText = (status) => {
    switch(status) {
      case 'disponivel': return 'Disponível'
      case 'ocupada': return 'Ocupada'
      case 'fechando': return 'Fechando'
      default: return 'Indefinido'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-gradient-to-r from-purple-600 to-blue-600 shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-yellow-500 p-2 rounded-lg">
                <span className="text-white font-bold text-xl">💳</span>
              </div>
              <div>
                <h1 className="text-white text-xl font-bold">Sistema Cashless</h1>
                <p className="text-purple-200 text-sm">Gestão de Comandas e Mesas</p>
              </div>
            </div>
          </div>
        </div>
      </header>
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Navigation Back */}
          <div className="mb-6">
            <button
              onClick={handleBackToDashboard}
              className="flex items-center gap-2 text-white border border-white/20 hover:bg-white/10 px-4 py-2 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Voltar ao Dashboard
            </button>
          </div>

          {/* Page Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-white mb-4">
              Sistema Cashless
            </h1>
            <p className="text-gray-300 text-lg">
              Gestão inteligente de comandas e mesas
            </p>
          </div>

          {/* Grid de Mesas/Comandas */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-8 border border-white/20">
            <h2 className="text-2xl font-bold text-white mb-6">Mesas e Comandas</h2>
            
            <div className="grid grid-cols-5 gap-4">
              {mesas.map((mesa) => (
                <div
                  key={mesa.numero}
                  className={`p-4 rounded-lg border-2 transition-all duration-200 hover:scale-105 cursor-pointer ${getStatusColor(mesa.status)}`}
                >
                  <div className="text-center">
                    <div className="text-2xl font-bold mb-2">
                      Mesa {mesa.numero}
                    </div>
                    <div className="text-sm font-medium">
                      {getStatusText(mesa.status)}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Status ETAPA 1 */}
            <div className="mt-8 pt-6 border-t border-white/20 text-center text-white">
              <p className="text-lg mb-2">🎯 ETAPA 1 - PÁGINA BASE</p>
              <p className="text-gray-300 text-sm">
                Grid 5x5 com 20 mesas/comandas e status visuais implementados
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
