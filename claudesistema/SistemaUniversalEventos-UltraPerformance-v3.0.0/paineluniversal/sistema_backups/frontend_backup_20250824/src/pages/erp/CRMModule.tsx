import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

const CRMModule = () => {
  return (
    <Routes>
      <Route index element={<div className="p-6">Módulo CRM - 55% Implementado - Sprint 4</div>} />
      <Route path="*" element={<Navigate to="/erp/crm" replace />} />
    </Routes>
  );
};

export default CRMModule;