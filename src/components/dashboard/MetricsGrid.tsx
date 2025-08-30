"use client"

import React from "react"
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TrendingUp, Users, DollarSign, Activity } from "lucide-react"

const metrics = [
  {
    title: "Revenue Total",
    value: "R$ 8.969,41",
    change: "+12%",
    icon: DollarSign,
    color: "from-green-400 to-emerald-600",
    trend: "up"
  },
  {
    title: "Clientes Ativos",
    value: "1.247",
    change: "+8%",
    icon: Users,
    color: "from-blue-400 to-cyan-600",
    trend: "up"
  },
  {
    title: "Eventos Hoje",
    value: "89",
    change: "+23%",
    icon: Activity,
    color: "from-purple-400 to-pink-600",
    trend: "up"
  },
  {
    title: "Performance IA",
    value: "94.2%",
    change: "+2.1%",
    icon: TrendingUp,
    color: "from-orange-400 to-red-600",
    trend: "up"
  }
]

export default function MetricsGrid() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {metrics.map((metric, index) => (
        <motion.div
          key={metric.title}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1, duration: 0.5 }}
        >
          <Card className="relative overflow-hidden border-0 shadow-xl">
            <div className={`absolute inset-0 bg-gradient-to-br ${metric.color} opacity-10`} />
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                {metric.title}
              </CardTitle>
              <div className={`p-2 rounded-lg bg-gradient-to-br ${metric.color}`}>
                <metric.icon className="h-4 w-4 text-white" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900">{metric.value}</div>
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                className="text-xs text-green-600 flex items-center mt-1"
              >
                <TrendingUp className="h-3 w-3 mr-1" />
                {metric.change} vs. mês anterior
              </motion.p>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  )
}
