import { useEffect, useRef } from 'react';

interface UseBarcodeProps {
  onScan: (code: string) => void;
  enabled?: boolean;
}

export const useBarcode = ({ onScan, enabled = true }: UseBarcodeProps) => {
  const bufferRef = useRef<string>('');
  const timeoutRef = useRef<number>();

  useEffect(() => {
    if (!enabled) return;

    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.key === 'Enter') {
        if (bufferRef.current.length > 3) {
          onScan(bufferRef.current);
          bufferRef.current = '';
        }
        return;
      }
      
      if (event.key.length === 1) {
        bufferRef.current += event.key;
        
        if (timeoutRef.current) {
          window.clearTimeout(timeoutRef.current);
        }
        
        timeoutRef.current = window.setTimeout(() => {
          bufferRef.current = '';
        }, 100);
      }
    };

    document.addEventListener('keypress', handleKeyPress);
    
    return () => {
      document.removeEventListener('keypress', handleKeyPress);
      if (timeoutRef.current) {
        window.clearTimeout(timeoutRef.current);
      }
    };
  }, [onScan, enabled]);

  return {
    clearBuffer: () => {
      bufferRef.current = '';
    }
  };
};

export const useQRScanner = ({ onScan, enabled = true }: UseBarcodeProps) => {
  const bufferRef = useRef<string>('');
  const timeoutRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    if (!enabled) return;

    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.key === 'Enter') {
        if (bufferRef.current.length > 5) {
          onScan(bufferRef.current);
          bufferRef.current = '';
        }
        return;
      }
      
      if (event.key.length === 1) {
        bufferRef.current += event.key;
        
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
        }
        
        timeoutRef.current = setTimeout(() => {
          bufferRef.current = '';
        }, 100);
      }
    };

    document.addEventListener('keypress', handleKeyPress);
    
    return () => {
      document.removeEventListener('keypress', handleKeyPress);
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [onScan, enabled]);

  return {
    clearBuffer: () => {
      bufferRef.current = '';
    }
  };
};
