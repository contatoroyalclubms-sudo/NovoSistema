"use client"

import React, { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { 
  Bell, 
  X, 
  CheckCircle, 
  AlertTriangle, 
  Info, 
  TrendingUp,
  Users,
  DollarSign,
  Activity,
  Settings
} from "lucide-react"

interface Notification {
  id: string
  type: "success" | "warning" | "info" | "error"
  title: string
  description: string
  timestamp: Date
  priority: "high" | "medium" | "low"
  aiGenerated?: boolean
  actions?: Array<{
    label: string
    action: () => void
    primary?: boolean
  }>
  read?: boolean
}

const mockNotifications: Notification[] = [
  {
    id: "1",
    type: "success",
    title: "Meta de Revenue Alcançada!",
    description: "R$ 8.969,41 - 12% acima do esperado para este horário",
    timestamp: new Date(Date.now() - 2 * 60 * 1000),
    priority: "high",
    actions: [
      { label: "Ver Detalhes", action: () => console.log("Ver detalhes"), primary: true },
      { label: "Compartilhar", action: () => console.log("Compartilhar") }
    ]
  },
  {
    id: "2",
    type: "warning",
    title: "IA detectou comportamento anômalo",
    description: "Queda súbita de 15% em bebidas quentes. Investigar causas?",
    timestamp: new Date(Date.now() - 5 * 60 * 1000),
    priority: "medium",
    aiGenerated: true,
    actions: [
      { label: "Investigar", action: () => console.log("Investigar"), primary: true },
      { label: "Ignorar", action: () => console.log("Ignorar") }
    ]
  },
  {
    id: "3",
    type: "info",
    title: "Novo cliente VIP detectado",
    description: "Sérgio Miguel - 10ª visita, R$ 1.137 total gasto",
    timestamp: new Date(Date.now() - 8 * 60 * 1000),
    priority: "low",
    actions: [
      { label: "Ver Perfil", action: () => console.log("Ver perfil") },
      { label: "Oferecer Brinde", action: () => console.log("Oferecer brinde") }
    ]
  },
  {
    id: "4",
    type: "warning",
    title: "Estoque baixo detectado",
    description: "Whisky Premium: apenas 12 unidades restantes",
    timestamp: new Date(Date.now() - 15 * 60 * 1000),
    priority: "medium",
    actions: [
      { label: "Reabastecer", action: () => console.log("Reabastecer"), primary: true },
      { label: "Ver Fornecedores", action: () => console.log("Ver fornecedores") }
    ]
  },
  {
    id: "5",
    type: "success",
    title: "Pico de movimento detectado",
    description: "165 pedidos na última hora - recorde do mês!",
    timestamp: new Date(Date.now() - 20 * 60 * 1000),
    priority: "high",
    aiGenerated: true
  }
]

function NotificationCard({ notification, onClose, onMarkAsRead }: {
  notification: Notification
  onClose: () => void
  onMarkAsRead: () => void
}) {
  const getIcon = () => {
    switch (notification.type) {
      case "success":
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case "warning":
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />
      case "error":
        return <AlertTriangle className="h-5 w-5 text-red-600" />
      default:
        return <Info className="h-5 w-5 text-blue-600" />
    }
  }

  const getBorderColor = () => {
    switch (notification.priority) {
      case "high":
        return "border-l-red-500"
      case "medium":
        return "border-l-yellow-500"
      default:
        return "border-l-blue-500"
    }
  }

  const getTimeAgo = (timestamp: Date) => {
    const now = new Date()
    const diffInMinutes = Math.floor((now.getTime() - timestamp.getTime()) / (1000 * 60))
    
    if (diffInMinutes < 1) return "agora"
    if (diffInMinutes < 60) return `${diffInMinutes} min atrás`
    
    const diffInHours = Math.floor(diffInMinutes / 60)
    if (diffInHours < 24) return `${diffInHours}h atrás`
    
    const diffInDays = Math.floor(diffInHours / 24)
    return `${diffInDays}d atrás`
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 300, scale: 0.9 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 300, scale: 0.9 }}
      transition={{ duration: 0.3, type: "spring", stiffness: 300, damping: 30 }}
      className={`bg-white rounded-lg shadow-lg border-l-4 ${getBorderColor()} p-4 mb-3 max-w-sm ${
        !notification.read ? "ring-2 ring-blue-100" : ""
      }`}
      onClick={onMarkAsRead}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3 flex-1">
          {getIcon()}
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="font-semibold text-gray-900 text-sm">
                {notification.title}
              </h4>
              {notification.aiGenerated && (
                <span className="bg-purple-100 text-purple-700 text-xs px-2 py-0.5 rounded-full font-medium">
                  IA
                </span>
              )}
            </div>
            <p className="text-gray-600 text-sm mb-2">
              {notification.description}
            </p>
            <div className="text-xs text-gray-500 mb-3">
              {getTimeAgo(notification.timestamp)}
            </div>
            
            {notification.actions && (
              <div className="flex gap-2 flex-wrap">
                {notification.actions.map((action, index) => (
                  <button
                    key={index}
                    onClick={(e) => {
                      e.stopPropagation()
                      action.action()
                    }}
                    className={`text-xs px-3 py-1 rounded-full transition-colors ${
                      action.primary
                        ? "bg-blue-600 text-white hover:bg-blue-700"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    {action.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation()
            onClose()
          }}
          className="text-gray-400 hover:text-gray-600 transition-colors ml-2"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </motion.div>
  )
}

function NotificationCenter({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [notifications, setNotifications] = useState<Notification[]>(mockNotifications)
  const [filter, setFilter] = useState<"all" | "unread" | "ai">("all")

  const filteredNotifications = notifications.filter(notification => {
    switch (filter) {
      case "unread":
        return !notification.read
      case "ai":
        return notification.aiGenerated
      default:
        return true
    }
  })

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })))
  }

  const clearAll = () => {
    setNotifications([])
  }

  if (!isOpen) return null

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              Central de Notificações
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex gap-2">
              {["all", "unread", "ai"].map((filterType) => (
                <button
                  key={filterType}
                  onClick={() => setFilter(filterType as any)}
                  className={`px-3 py-1 rounded-full text-sm transition-colors ${
                    filter === filterType
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                  }`}
                >
                  {filterType === "all" ? "Todas" : filterType === "unread" ? "Não lidas" : "IA"}
                </button>
              ))}
            </div>
            
            <div className="flex gap-2 ml-auto">
              <button
                onClick={markAllAsRead}
                className="text-sm text-blue-600 hover:text-blue-700 transition-colors"
              >
                Marcar todas como lidas
              </button>
              <button
                onClick={clearAll}
                className="text-sm text-red-600 hover:text-red-700 transition-colors"
              >
                Limpar todas
              </button>
            </div>
          </div>
        </div>
        
        <div className="p-6 max-h-96 overflow-y-auto">
          {filteredNotifications.length === 0 ? (
            <div className="text-center py-8">
              <Bell className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">Nenhuma notificação encontrada</p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredNotifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`p-4 rounded-lg border transition-colors ${
                    !notification.read ? "bg-blue-50 border-blue-200" : "bg-gray-50 border-gray-200"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      {notification.type === "success" && <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />}
                      {notification.type === "warning" && <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />}
                      {notification.type === "info" && <Info className="h-5 w-5 text-blue-600 mt-0.5" />}
                      
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium text-gray-900">
                            {notification.title}
                          </h4>
                          {notification.aiGenerated && (
                            <span className="bg-purple-100 text-purple-700 text-xs px-2 py-0.5 rounded-full font-medium">
                              IA
                            </span>
                          )}
                        </div>
                        <p className="text-gray-600 text-sm mb-2">
                          {notification.description}
                        </p>
                        <div className="text-xs text-gray-500">
                          {notification.timestamp.toLocaleString("pt-BR")}
                        </div>
                      </div>
                    </div>
                    
                    {!notification.read && (
                      <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
                    )}
                  </div>
                  
                  {notification.actions && (
                    <div className="flex gap-2 mt-3">
                      {notification.actions.map((action, index) => (
                        <button
                          key={index}
                          onClick={action.action}
                          className={`text-sm px-3 py-1 rounded transition-colors ${
                            action.primary
                              ? "bg-blue-600 text-white hover:bg-blue-700"
                              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                          }`}
                        >
                          {action.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  )
}

export default function NotificationSystem() {
  const [notifications, setNotifications] = useState<Notification[]>(mockNotifications.slice(0, 3))
  const [showCenter, setShowCenter] = useState(false)
  const [unreadCount, setUnreadCount] = useState(3)

  useEffect(() => {
    const interval = setInterval(() => {
      if (Math.random() > 0.7) {
        const newNotification: Notification = {
          id: Date.now().toString(),
          type: ["success", "warning", "info"][Math.floor(Math.random() * 3)] as any,
          title: "Nova atualização em tempo real",
          description: "Sistema detectou mudança nos dados",
          timestamp: new Date(),
          priority: "medium",
          aiGenerated: Math.random() > 0.5
        }
        
        setNotifications(prev => [newNotification, ...prev.slice(0, 4)])
        setUnreadCount(prev => prev + 1)
      }
    }, 30000) // Every 30 seconds

    return () => clearInterval(interval)
  }, [])

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  const markAsRead = (id: string) => {
    setNotifications(prev => prev.map(n => 
      n.id === id ? { ...n, read: true } : n
    ))
    setUnreadCount(prev => Math.max(0, prev - 1))
  }

  return (
    <>
      {/* Floating Notifications */}
      <div className="fixed top-4 right-4 z-40 space-y-3">
        <AnimatePresence>
          {notifications.slice(0, 3).map((notification) => (
            <NotificationCard
              key={notification.id}
              notification={notification}
              onClose={() => removeNotification(notification.id)}
              onMarkAsRead={() => markAsRead(notification.id)}
            />
          ))}
        </AnimatePresence>
      </div>

      {/* Notification Bell Button */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setShowCenter(true)}
        className="fixed bottom-6 right-6 bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition-colors z-30"
      >
        <Bell className="h-6 w-6" />
        {unreadCount > 0 && (
          <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-6 w-6 flex items-center justify-center font-medium">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </motion.button>

      {/* Notification Center Modal */}
      <AnimatePresence>
        {showCenter && (
          <NotificationCenter
            isOpen={showCenter}
            onClose={() => setShowCenter(false)}
          />
        )}
      </AnimatePresence>
    </>
  )
}
