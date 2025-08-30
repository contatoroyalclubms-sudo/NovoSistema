import { useContext } from 'react';
import AuthContext from '../contexts/AuthContext-new';
import { AuthContextType } from '../types/auth-types';

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  
  return context;
};

export default useAuth;
