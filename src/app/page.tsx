"use client"

import React from "react"
import { motion } from "framer-motion"
import Header from "@/components/dashboard/Header"
import MetricsGrid from "@/components/dashboard/MetricsGrid"
import InteractiveCharts from "@/components/charts/InteractiveCharts"
import { CustomersTable, ProductsTable } from "@/components/tables/SmartTable"
import NotificationSystem from "@/components/notifications/NotificationSystem"

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Header />
      
      <main className="max-w-7xl mx-auto p-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Dashboard Ultra Avançado
          </h2>
          <p className="text-gray-600">
            Sistema revolucionário de eventos com IA integrada - SPRINT 1 (Foundation)
          </p>
        </motion.div>

        <MetricsGrid />

        <InteractiveCharts />

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2, duration: 0.6 }}
          className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-8"
        >
          <CustomersTable />
          <ProductsTable />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.6 }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8"
        >
          <div className="bg-white rounded-xl shadow-lg p-6 border-0">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              🚀 SPRINT 1 - Foundation
            </h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-700">Next.js 14 + TypeScript configurado</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-700">Tailwind CSS + Framer Motion integrados</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-700">Sistema de design base criado</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-700">Layout responsivo adaptativo</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <span className="text-sm text-gray-700">Deploy Railway em progresso...</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-0">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              🎯 Próximos Sprints
            </h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span className="text-sm text-gray-700">SPRINT 2: Core Dashboard (7 dias)</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                <span className="text-sm text-gray-700">SPRINT 3: IA Integration (7 dias)</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                <span className="text-sm text-gray-700">SPRINT 4: 3D & Advanced (5 dias)</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span className="text-sm text-gray-700">SPRINT 5: Polish & Deploy (3 dias)</span>
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.0, duration: 0.6 }}
          className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl shadow-xl p-8 text-white"
        >
          <h3 className="text-2xl font-bold mb-4">
            🏆 Superior à Meep - Diferencial Competitivo
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h4 className="font-semibold mb-2">🤖 IA Preditiva</h4>
              <p className="text-sm opacity-90">
                94%+ precisão em previsões vs. análises manuais básicas
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">📊 Gráficos 3D</h4>
              <p className="text-sm opacity-90">
                Visualizações interativas vs. gráficos 2D estáticos
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">⚡ Performance</h4>
              <p className="text-sm opacity-90">
                Sub-segundo em todas operações vs. performance média/lenta
              </p>
            </div>
          </div>
        </motion.div>
      </main>
      
      <NotificationSystem />
    </div>
  )
}
