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

          {/* ETAPA 2: Formulário Básico */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-8 border border-white/20">
            <form className="space-y-6">
              {/* Nome do Evento */}
              <div>
                <label htmlFor="eventName" className="block text-white text-sm font-medium mb-2">
                  Nome do Evento *
                </label>
                <input
                  type="text"
                  id="eventName"
                  name="eventName"
                  required
                  className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Digite o nome do evento"
                />
              </div>

              {/* Data e Hora */}
              <div>
                <label htmlFor="eventDateTime" className="block text-white text-sm font-medium mb-2">
                  Data e Hora *
                </label>
                <input
                  type="datetime-local"
                  id="eventDateTime"
                  name="eventDateTime"
                  required
                  className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>

              {/* Local */}
              <div>
                <label htmlFor="eventLocation" className="block text-white text-sm font-medium mb-2">
                  Local *
                </label>
                <input
                  type="text"
                  id="eventLocation"
                  name="eventLocation"
                  required
                  className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Digite o local do evento"
                />
              </div>

              {/* Descrição */}
              <div>
                <label htmlFor="eventDescription" className="block text-white text-sm font-medium mb-2">
                  Descrição *
                </label>
                <textarea
                  id="eventDescription"
                  name="eventDescription"
                  required
                  rows={4}
                  className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                  placeholder="Descreva os detalhes do evento"
                />
              </div>

              {/* Botão Criar Evento */}
              <div className="pt-4">
                <button
                  type="submit"
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-transparent"
                >
                  Criar Evento
                </button>
              </div>
            </form>

            {/* Status ETAPA 2 */}
            <div className="mt-8 pt-6 border-t border-white/20 text-center text-white">
              <p className="text-lg mb-2">🎯 ETAPA 2 - FORMULÁRIO BÁSICO</p>
              <p className="text-gray-300 text-sm">
                Campos obrigatórios implementados com validação HTML5
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
