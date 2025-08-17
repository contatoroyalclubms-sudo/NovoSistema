/// <reference types="vite/client" />

// Vite environment variables types
interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_WS_URL: string
  readonly VITE_APP_NAME: string
  readonly VITE_APP_VERSION: string
  readonly VITE_ENVIRONMENT: 'development' | 'production' | 'test'
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// Global types
declare global {
  interface Window {
    // Para integração com ferramentas de analytics
    gtag?: (...args: any[]) => void
    // Para debug em desenvolvimento
    __APP_DEBUG__?: boolean
  }
}

// React Hook Form types
declare module 'react-hook-form' {
  interface FieldValues {
    [key: string]: any
  }
}

// Styled components theme
declare module 'styled-components' {
  interface DefaultTheme {
    colors: {
      primary: string
      secondary: string
      success: string
      warning: string
      error: string
      info: string
      background: string
      surface: string
      text: string
    }
    spacing: {
      xs: string
      sm: string
      md: string
      lg: string
      xl: string
    }
    borderRadius: {
      sm: string
      md: string
      lg: string
    }
  }
}

export {}
