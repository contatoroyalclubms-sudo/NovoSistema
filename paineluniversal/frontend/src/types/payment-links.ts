/**
 * Types for Payment Links System
 * Sistema Universal de Gestão de Eventos
 */

// Enums
export enum LinkStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  EXPIRED = "expired",
  COMPLETED = "completed"
}

export enum PaymentType {
  SINGLE = "single",        // Pagamento único
  RECURRING = "recurring",   // Recorrente
  FLEXIBLE = "flexible"      // Valor flexível
}

export enum LinkTheme {
  DEFAULT = "default",
  DARK = "dark",
  COLORFUL = "colorful",
  MINIMAL = "minimal",
  CUSTOM = "custom"
}

export enum PaymentStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
  REFUNDED = "refunded"
}

export enum NotificationPriority {
  LOW = "low",
  NORMAL = "normal",
  HIGH = "high",
  URGENT = "urgent"
}

// Base interfaces
export interface SplitRecipient {
  recipient_id: string;
  account_id: string;
  name: string;
  document: string;
  percentage?: number;
  fixed_amount?: number;
  split_type: 'percentage' | 'fixed';
}

export interface PaymentLinkMetadata {
  [key: string]: any;
  created_by?: string;
  campaign?: string;
  source?: string;
  tags?: string[];
}

// Main interfaces
export interface PaymentLinkCreate {
  title: string;
  description?: string;
  amount?: number;
  min_amount?: number;
  max_amount?: number;
  currency?: string;
  payment_type: PaymentType;
  expires_at?: string; // ISO string
  max_uses?: number;
  
  // Personalização
  theme?: LinkTheme;
  custom_css?: string;
  logo_url?: string;
  success_url?: string;
  cancel_url?: string;
  
  // Split de pagamentos
  enable_split?: boolean;
  split_recipients?: SplitRecipient[];
  
  // Configurações
  collect_customer_info?: boolean;
  send_receipt?: boolean;
  allow_installments?: boolean;
  webhook_url?: string;
  
  metadata?: PaymentLinkMetadata;
}

export interface PaymentLink {
  link_id: string;
  url: string;
  qr_code: string; // Base64 encoded
  short_url: string;
  title: string;
  description?: string;
  amount?: number;
  min_amount?: number;
  max_amount?: number;
  currency: string;
  status: LinkStatus;
  payment_type: PaymentType;
  expires_at?: string;
  max_uses?: number;
  uses_count: number;
  views_count: number;
  total_collected: number;
  
  // Personalização
  theme: LinkTheme;
  custom_css?: string;
  logo_url?: string;
  success_url?: string;
  cancel_url?: string;
  
  // Split
  enable_split: boolean;
  split_recipients?: SplitRecipient[];
  
  // Configurações
  collect_customer_info: boolean;
  send_receipt: boolean;
  allow_installments: boolean;
  webhook_url?: string;
  
  metadata?: PaymentLinkMetadata;
  created_at: string;
  updated_at: string;
}

export interface PaymentAttempt {
  attempt_id: string;
  link_id: string;
  amount: number;
  currency: string;
  customer_email?: string;
  customer_name?: string;
  customer_phone?: string;
  customer_document?: string;
  status: PaymentStatus;
  payment_method?: string;
  transaction_id?: string;
  failure_reason?: string;
  created_at: string;
  completed_at?: string;
  processed_at?: string;
  gateway_response?: any;
}

export interface LinkAnalytics {
  link_id: string;
  period_days: number;
  total_views: number;
  total_attempts: number;
  successful_payments: number;
  total_collected: number;
  conversion_rate: number;
  avg_amount: number;
  payment_methods_breakdown: Record<string, number>;
  daily_stats: DailyStats[];
}

export interface DailyStats {
  date: string;
  attempts: number;
  completed_payments: number;
  revenue: number;
  views?: number;
}

// API Response types
export interface PaymentLinksListResponse {
  links: PaymentLink[];
  total_count: number;
  summary: {
    total_links: number;
    total_revenue: number;
    avg_uses: number;
  };
}

export interface PaymentLinkPaymentsResponse {
  payments: PaymentAttempt[];
  total_count: number;
  summary: {
    completed_payments: number;
    total_amount: number;
  };
}

// Form types
export interface PaymentLinkFormData extends PaymentLinkCreate {
  // Additional form-specific fields
  expiry_date?: Date;
  expiry_time?: string;
  split_recipients_config?: {
    recipient: SplitRecipient;
    errors?: Record<string, string>;
  }[];
}

export interface PaymentLinkFilters {
  status?: LinkStatus;
  payment_type?: PaymentType;
  created_after?: string;
  created_before?: string;
  search?: string;
  limit?: number;
  offset?: number;
}

// Public payment page types
export interface PublicPaymentData {
  customer_name?: string;
  customer_email?: string;
  customer_phone?: string;
  customer_document?: string;
  amount?: number;
  payment_method: string;
  ip_address?: string;
  user_agent?: string;
}

export interface PaymentProcessingResult {
  status: 'success' | 'error' | 'pending';
  payment_id?: string;
  redirect_url?: string;
  qr_code?: string;
  message?: string;
  error?: string;
  attempt_id?: string;
}

// Analytics types
export interface AnalyticsMetrics {
  total_revenue: number;
  total_links: number;
  active_links: number;
  total_payments: number;
  conversion_rate: number;
  avg_amount: number;
  growth_rate: number;
  top_performing_links: PaymentLink[];
}

export interface AnalyticsPeriod {
  label: string;
  value: number;
  days: number;
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string;
    borderColor?: string;
    fill?: boolean;
  }[];
}

// Notification types
export interface NotificationSettings {
  email_notifications: boolean;
  webhook_notifications: boolean;
  in_app_notifications: boolean;
  payment_completed: boolean;
  payment_failed: boolean;
  link_expired: boolean;
  daily_summary: boolean;
}

export interface PaymentNotification {
  id: string;
  type: 'payment_completed' | 'payment_failed' | 'link_created' | 'link_expired';
  title: string;
  message: string;
  link_id?: string;
  payment_id?: string;
  amount?: number;
  priority: NotificationPriority;
  read: boolean;
  created_at: string;
  action_url?: string;
}

// Theme customization types
export interface ThemeCustomization {
  primary_color: string;
  secondary_color: string;
  background_color: string;
  text_color: string;
  button_color: string;
  border_radius: number;
  font_family: string;
  logo_url?: string;
  custom_css?: string;
}

export interface PreviewSettings {
  theme: LinkTheme;
  customization?: ThemeCustomization;
  title: string;
  description?: string;
  amount?: number;
  min_amount?: number;
  max_amount?: number;
  payment_type: PaymentType;
  collect_customer_info: boolean;
  allow_installments: boolean;
}

// Export/Import types
export interface ExportOptions {
  format: 'csv' | 'excel' | 'pdf';
  date_range: {
    start: string;
    end: string;
  };
  include_analytics: boolean;
  include_payments: boolean;
  links?: string[]; // Specific link IDs to export
}

// API Error types
export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, any>;
  status?: number;
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

// Utility types
export type PaymentLinkUpdateData = Partial<Omit<PaymentLinkCreate, 'payment_type' | 'amount' | 'min_amount' | 'max_amount'>>;

export type PaymentLinkSummary = Pick<PaymentLink, 
  'link_id' | 'title' | 'status' | 'payment_type' | 'uses_count' | 
  'total_collected' | 'created_at' | 'expires_at'
>;

export type LinkStatusCount = Record<LinkStatus, number>;

export type PaymentMethodStats = Record<string, {
  count: number;
  total_amount: number;
  percentage: number;
}>;

// Component prop types
export interface PaymentLinkCardProps {
  link: PaymentLink;
  onEdit: (link: PaymentLink) => void;
  onDelete: (linkId: string) => void;
  onViewAnalytics: (linkId: string) => void;
  onCopyLink: (url: string) => void;
  onToggleStatus: (linkId: string, status: LinkStatus) => void;
}

export interface PaymentLinkFormProps {
  initialData?: PaymentLinkFormData;
  onSubmit: (data: PaymentLinkFormData) => Promise<void>;
  onCancel: () => void;
  loading?: boolean;
  mode: 'create' | 'edit';
}

export interface AnalyticsDashboardProps {
  linkId?: string;
  period?: AnalyticsPeriod;
  onPeriodChange?: (period: AnalyticsPeriod) => void;
}

export interface PublicPaymentPageProps {
  linkId: string;
  link?: PaymentLink;
  onPaymentSubmit: (data: PublicPaymentData) => Promise<PaymentProcessingResult>;
  loading?: boolean;
}

// Constants
export const DEFAULT_ANALYTICS_PERIODS: AnalyticsPeriod[] = [
  { label: 'Últimos 7 dias', value: 7, days: 7 },
  { label: 'Últimos 30 dias', value: 30, days: 30 },
  { label: 'Últimos 90 dias', value: 90, days: 90 },
  { label: 'Último ano', value: 365, days: 365 }
];

export const THEME_PRESETS: Record<LinkTheme, ThemeCustomization> = {
  [LinkTheme.DEFAULT]: {
    primary_color: '#3b82f6',
    secondary_color: '#64748b',
    background_color: '#ffffff',
    text_color: '#1f2937',
    button_color: '#3b82f6',
    border_radius: 8,
    font_family: 'Inter, sans-serif'
  },
  [LinkTheme.DARK]: {
    primary_color: '#10b981',
    secondary_color: '#6b7280',
    background_color: '#1f2937',
    text_color: '#f9fafb',
    button_color: '#10b981',
    border_radius: 8,
    font_family: 'Inter, sans-serif'
  },
  [LinkTheme.COLORFUL]: {
    primary_color: '#8b5cf6',
    secondary_color: '#f59e0b',
    background_color: '#fef3c7',
    text_color: '#1f2937',
    button_color: '#8b5cf6',
    border_radius: 16,
    font_family: 'Inter, sans-serif'
  },
  [LinkTheme.MINIMAL]: {
    primary_color: '#000000',
    secondary_color: '#6b7280',
    background_color: '#ffffff',
    text_color: '#000000',
    button_color: '#000000',
    border_radius: 0,
    font_family: 'Inter, sans-serif'
  },
  [LinkTheme.CUSTOM]: {
    primary_color: '#3b82f6',
    secondary_color: '#64748b',
    background_color: '#ffffff',
    text_color: '#1f2937',
    button_color: '#3b82f6',
    border_radius: 8,
    font_family: 'Inter, sans-serif'
  }
};

export const PAYMENT_METHODS = [
  { value: 'pix', label: 'PIX', icon: '💰' },
  { value: 'card', label: 'Cartão de Crédito/Débito', icon: '💳' },
  { value: 'boleto', label: 'Boleto Bancário', icon: '📄' },
  { value: 'bank_transfer', label: 'Transferência Bancária', icon: '🏦' }
];

// Type guards
export const isValidPaymentType = (value: string): value is PaymentType => {
  return Object.values(PaymentType).includes(value as PaymentType);
};

export const isValidLinkStatus = (value: string): value is LinkStatus => {
  return Object.values(LinkStatus).includes(value as LinkStatus);
};

export const isValidPaymentStatus = (value: string): value is PaymentStatus => {
  return Object.values(PaymentStatus).includes(value as PaymentStatus);
};