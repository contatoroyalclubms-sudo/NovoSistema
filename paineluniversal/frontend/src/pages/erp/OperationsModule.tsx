import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

const OperationsModule = () => {
  return (
    <Routes>
      <Route index element={<div className="p-6">Módulo Operações - 20% Implementado - Sprint 3</div>} />
      <Route path="*" element={<Navigate to="/erp/operations" replace />} />
    </Routes>
  );
};

export default OperationsModule;