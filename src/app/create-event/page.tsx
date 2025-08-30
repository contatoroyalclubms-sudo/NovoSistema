"use client"

import React from "react"
import Header from "../../components/dashboard/Header"
import { ArrowLeft } from "lucide-react"
import { useRouter } from "next/navigation"

export default function CreateEventPage() {
  const router = useRouter()

  const handleBackToDashboard = () => {
    router.push("/")
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
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
              Criar Novo Evento
            </h1>
            <p className="text-gray-300 text-lg">
              Configure seu evento com nossa plataforma inteligente
            </p>
          </div>

          {/* Content Area - Ready for ETAPA 2 */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-8 border border-white/20">
            <div className="text-center text-white">
              <p className="text-xl mb-4">🎯 ETAPA 1 CONCLUÍDA</p>
              <p className="text-gray-300">
                Página de criação de eventos criada com sucesso!
              </p>
              <p className="text-gray-400 mt-2">
                Aguardando confirmação para prosseguir com ETAPA 2 (Formulário Básico)
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
