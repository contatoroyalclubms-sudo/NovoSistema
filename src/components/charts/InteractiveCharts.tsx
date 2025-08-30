"use client"

import React, { useState } from "react"
import { motion } from "framer-motion"
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card"
import { TrendingUp, BarChart3, PieChart as PieChartIcon, Activity } from "lucide-react"

const revenueData = [
  { time: "00:00", revenue: 1200, orders: 45, customers: 23 },
  { time: "02:00", revenue: 800, orders: 32, customers: 18 },
  { time: "04:00", revenue: 600, orders: 25, customers: 15 },
  { time: "06:00", revenue: 1500, orders: 58, customers: 31 },
  { time: "08:00", revenue: 2200, orders: 78, customers: 42 },
  { time: "10:00", revenue: 2800, orders: 95, customers: 55 },
  { time: "12:00", revenue: 3200, orders: 112, customers: 68 },
  { time: "14:00", revenue: 2900, orders: 98, customers: 59 },
  { time: "16:00", revenue: 3500, orders: 125, customers: 75 },
  { time: "18:00", revenue: 4200, orders: 145, customers: 89 },
  { time: "20:00", revenue: 4800, orders: 165, customers: 98 },
  { time: "22:00", revenue: 5200, orders: 178, customers: 105 },
]

const productData = [
  { name: "Cerveja", value: 35, revenue: 2800, color: "#8884d8" },
  { name: "Destilados", value: 25, revenue: 2200, color: "#82ca9d" },
  { name: "Vinhos", value: 20, revenue: 1600, color: "#ffc658" },
  { name: "Refrigerantes", value: 12, revenue: 800, color: "#ff7300" },
  { name: "Energéticos", value: 8, revenue: 600, color: "#00ff88" },
]

const customerFlowData = [
  { hour: "18:00", entrada: 25, saida: 5, total: 20 },
  { hour: "19:00", entrada: 45, saida: 8, total: 57 },
  { hour: "20:00", entrada: 65, saida: 12, total: 110 },
  { hour: "21:00", entrada: 85, saida: 18, total: 177 },
  { hour: "22:00", entrada: 95, saida: 25, total: 247 },
  { hour: "23:00", entrada: 75, saida: 35, total: 287 },
  { hour: "00:00", entrada: 55, saida: 45, total: 297 },
  { hour: "01:00", entrada: 35, saida: 65, total: 267 },
  { hour: "02:00", entrada: 15, saida: 85, total: 197 },
]

interface ChartCardProps {
  title: string
  icon: React.ReactNode
  children: React.ReactNode
  className?: string
}

function ChartCard({ title, icon, children, className = "" }: ChartCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={className}
    >
      <Card className="h-full border-0 shadow-xl">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            {icon}
            {title}
          </CardTitle>
          <div className="text-xs text-gray-500">Tempo Real</div>
        </CardHeader>
        <CardContent className="h-80">
          {children}
        </CardContent>
      </Card>
    </motion.div>
  )
}

export default function InteractiveCharts() {
  const [selectedChart, setSelectedChart] = useState<string | null>(null)
  const [timeRange, setTimeRange] = useState("24h")

  const handleChartClick = (chartType: string) => {
    setSelectedChart(selectedChart === chartType ? null : chartType)
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="flex items-center justify-between"
      >
        <h2 className="text-2xl font-bold text-gray-900">
          📊 Gráficos Interativos Avançados
        </h2>
        <div className="flex gap-2">
          {["1h", "6h", "24h", "7d"].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                timeRange === range
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Trend Chart */}
        <ChartCard
          title="Revenue em Tempo Real"
          icon={<TrendingUp className="h-5 w-5 text-green-600" />}
        >
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={revenueData}>
              <defs>
                <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0.1} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="time" 
                stroke="#666"
                fontSize={12}
              />
              <YAxis 
                stroke="#666"
                fontSize={12}
                tickFormatter={(value) => `R$ ${value}`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#fff",
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                  boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                }}
                formatter={(value: any, name: string) => [
                  name === "revenue" ? `R$ ${value}` : value,
                  name === "revenue" ? "Revenue" : name === "orders" ? "Pedidos" : "Clientes"
                ]}
              />
              <Area
                type="monotone"
                dataKey="revenue"
                stroke="#10b981"
                strokeWidth={3}
                fill="url(#revenueGradient)"
                onClick={() => handleChartClick("revenue")}
                style={{ cursor: "pointer" }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Product Distribution */}
        <ChartCard
          title="Distribuição de Produtos"
          icon={<PieChartIcon className="h-5 w-5 text-purple-600" />}
        >
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={productData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={120}
                paddingAngle={5}
                dataKey="value"
                onClick={() => handleChartClick("products")}
                style={{ cursor: "pointer" }}
              >
                {productData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: "#fff",
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                  boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                }}
                formatter={(value: any, name: string) => [
                  `${value}%`,
                  "Participação"
                ]}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Customer Flow */}
        <ChartCard
          title="Fluxo de Clientes"
          icon={<Activity className="h-5 w-5 text-blue-600" />}
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={customerFlowData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="hour" 
                stroke="#666"
                fontSize={12}
              />
              <YAxis 
                stroke="#666"
                fontSize={12}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#fff",
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                  boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                }}
              />
              <Legend />
              <Bar 
                dataKey="entrada" 
                fill="#10b981" 
                name="Entrada"
                onClick={() => handleChartClick("flow")}
                style={{ cursor: "pointer" }}
              />
              <Bar 
                dataKey="saida" 
                fill="#ef4444" 
                name="Saída"
                onClick={() => handleChartClick("flow")}
                style={{ cursor: "pointer" }}
              />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Performance Metrics */}
        <ChartCard
          title="Métricas de Performance"
          icon={<BarChart3 className="h-5 w-5 text-orange-600" />}
        >
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={revenueData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="time" 
                stroke="#666"
                fontSize={12}
              />
              <YAxis 
                stroke="#666"
                fontSize={12}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#fff",
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                  boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="orders"
                stroke="#8884d8"
                strokeWidth={3}
                dot={{ fill: "#8884d8", strokeWidth: 2, r: 4 }}
                name="Pedidos"
                onClick={() => handleChartClick("performance")}
                style={{ cursor: "pointer" }}
              />
              <Line
                type="monotone"
                dataKey="customers"
                stroke="#82ca9d"
                strokeWidth={3}
                dot={{ fill: "#82ca9d", strokeWidth: 2, r: 4 }}
                name="Clientes"
                onClick={() => handleChartClick("performance")}
                style={{ cursor: "pointer" }}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Drill-down Details */}
      {selectedChart && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.3 }}
          className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            🔍 Drill-down: {selectedChart === "revenue" ? "Revenue Detalhado" : 
                           selectedChart === "products" ? "Análise de Produtos" :
                           selectedChart === "flow" ? "Fluxo Detalhado" : "Performance Detalhada"}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="text-sm text-gray-600">Pico Atual</div>
              <div className="text-2xl font-bold text-green-600">R$ 5.200</div>
              <div className="text-xs text-gray-500">22:00 - 23:00</div>
            </div>
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="text-sm text-gray-600">Crescimento</div>
              <div className="text-2xl font-bold text-blue-600">+23%</div>
              <div className="text-xs text-gray-500">vs. ontem</div>
            </div>
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="text-sm text-gray-600">Projeção</div>
              <div className="text-2xl font-bold text-purple-600">R$ 12.5K</div>
              <div className="text-xs text-gray-500">até 02:00</div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}
