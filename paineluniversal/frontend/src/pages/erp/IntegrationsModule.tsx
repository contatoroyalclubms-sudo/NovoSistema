import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

const IntegrationsModule = () => {
  return (
    <Routes>
      <Route index element={<div className="p-6">Módulo Integrações - 80% Implementado</div>} />
      <Route path="*" element={<Navigate to="/erp/integrations" replace />} />
    </Routes>
  );
};

export default IntegrationsModule;