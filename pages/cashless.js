import React from "react"
import { useRouter } from "next/router"
import { ArrowLeft } from "lucide-react"

export default function CashlessPage() {
  const router = useRouter()

  const handleBackToDashboard = () => {
    router.push("/")
  }

  const mockCartoes = [
    { id: 1, numero: '001', cliente: 'Maria Silva', saldo: 45.50, status: 'ativo' },
    { id: 2, numero: '002', cliente: 'João Santos', saldo: 23.80, status: 'ativo' },
    { id: 3, numero: '003', cliente: 'Ana Costa', saldo: 0.00, status: 'bloqueado' },
    { id: 4, numero: '004', cliente: 'Pedro Lima', saldo: 67.25, status: 'ativo' },
    { id: 5, numero: '005', cliente: 'Carla Souza', saldo: 12.90, status: 'ativo' },
    { id: 6, numero: '006', cliente: 'Roberto Alves', saldo: 0.00, status: 'bloqueado' },
    { id: 7, numero: '007', cliente: 'Fernanda Rocha', saldo: 89.40, status: 'ativo' },
    { id: 8, numero: '008', cliente: 'Lucas Martins', saldo: 34.15, status: 'ativo' }
  ]

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
                <p className="text-purple-200 text-sm">Gestão de Cartões e Saldos</p>
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
              Gestão inteligente de cartões e saldos
            </p>
          </div>

          {/* Cartões Cashless */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-8 border border-white/20">
            <h2 className="text-2xl font-bold text-white mb-6">Cartões Cashless</h2>
            
            <div className="grid gap-4">
              {mockCartoes.map(cartao => (
                <div key={cartao.id} className="bg-white p-4 rounded border flex justify-between hover:shadow-lg transition-shadow cursor-pointer">
                  <div>
                    <div className="font-bold text-gray-900">Cartão {cartao.numero}</div>
                    <div className="text-gray-600">{cartao.cliente}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-gray-900">R$ {cartao.saldo.toFixed(2)}</div>
                    <div className={cartao.status === 'ativo' ? 'text-green-600' : 'text-red-600'}>
                      {cartao.status}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Status ETAPA 1 */}
            <div className="mt-8 pt-6 border-t border-white/20 text-center text-white">
              <p className="text-lg mb-2">🎯 ETAPA 1 - PÁGINA BASE ATUALIZADA</p>
              <p className="text-gray-300 text-sm">
                Sistema de cartões cashless com dados de clientes implementado
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
