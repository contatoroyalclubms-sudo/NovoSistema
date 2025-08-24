// Tipos de usuário
export interface User {
  id: string
  email: string
  name: string
  role: UserRole
  avatar?: string
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export enum UserRole {
  ADMIN = 'admin',
  MANAGER = 'manager',
  USER = 'user'
}

// Tipos de autenticação
export interface LoginCredentials {
  email: string
  password: string
}

export interface AuthResponse {
  user: User
  token: string
  refreshToken: string
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
}

// Tipos de API
export interface ApiResponse<T = any> {
  data: T
  message: string
  success: boolean
}

export interface ApiError {
  message: string
  code: string
  details?: any
}

// Tipos de eventos
export interface Event {
  id: string
  title: string
  description: string
  startDate: string
  endDate: string
  location: string
  maxParticipants: number
  currentParticipants: number
  status: EventStatus
  createdBy: string
  createdAt: string
  updatedAt: string
}

export enum EventStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  ONGOING = 'ongoing',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

// Tipos de participantes
export interface Participant {
  id: string
  eventId: string
  userId: string
  name: string
  email: string
  phone?: string
  status: ParticipantStatus
  registeredAt: string
}

export enum ParticipantStatus {
  REGISTERED = 'registered',
  CONFIRMED = 'confirmed',
  ATTENDED = 'attended',
  CANCELLED = 'cancelled'
}
