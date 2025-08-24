import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

const InventoryModule = () => {
  return (
    <Routes>
      <Route index element={<div className="p-6">Módulo Inventory - 85% Implementado</div>} />
      <Route path="*" element={<Navigate to="/erp/inventory" replace />} />
    </Routes>
  );
};

export default InventoryModule;