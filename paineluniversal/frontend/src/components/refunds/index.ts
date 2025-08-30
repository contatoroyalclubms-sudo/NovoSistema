/**
 * Refunds Components - Sistema de Gestão de Estornos
 * Sistema Universal de Gestão de Eventos
 * 
 * Exportações centralizadas de todos os componentes relacionados a estornos
 */

// Main Dashboard
export { default as RefundManagementDashboard } from './RefundManagementDashboard';

// Request and Status Components
export { default as RefundRequestForm } from './RefundRequestForm';
export { default as RefundStatusTracker } from './RefundStatusTracker';

// Analytics and Reporting
export { default as RefundAnalyticsDashboard } from './RefundAnalyticsDashboard';

// Additional specialized components would be exported here:
// export { default as ChargebackManager } from './ChargebackManager';
// export { default as RefundApprovalQueue } from './RefundApprovalQueue';
// export { default as FraudDetectionDashboard } from './FraudDetectionDashboard';
// export { default as RefundWorkflowDesigner } from './RefundWorkflowDesigner';

// Types and interfaces
export type {
  RefundCase,
  RefundMetrics,
  RefundTrendData,
  RefundCategoryData,
  FraudAnalytics,
  AIInsights
} from './RefundAnalyticsDashboard';

// Component props types
export type {
  RefundRequestFormProps
} from './RefundRequestForm';

export type {
  RefundTrackerProps
} from './RefundStatusTracker';

export type {
  RefundAnalyticsDashboardProps
} from './RefundAnalyticsDashboard';