import React, { createContext, useContext, useState, ReactNode } from 'react'

interface AppContextType {
  currentEvent: string | null
  setCurrentEvent: (eventId: string | null) => void
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
  notifications: Notification[]
  addNotification: (notification: Notification) => void
  removeNotification: (id: string) => void
}

interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  duration?: number
}

const AppContext = createContext<AppContextType | undefined>(undefined)

export const useApp = () => {
  const context = useContext(AppContext)
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider')
  }
  return context
}

interface AppProviderProps {
  children: ReactNode
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [currentEvent, setCurrentEvent] = useState<string | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [notifications, setNotifications] = useState<Notification[]>([])

  const addNotification = (notification: Notification) => {
    setNotifications(prev => [...prev, notification])
    
    // Auto remove após duration
    if (notification.duration !== 0) {
      setTimeout(() => {
        removeNotification(notification.id)
      }, notification.duration || 5000)
    }
  }

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  const value: AppContextType = {
    currentEvent,
    setCurrentEvent,
    sidebarOpen,
    setSidebarOpen,
    notifications,
    addNotification,
    removeNotification
  }

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  )
}
