import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Alert, AlertDescription } from '../ui/alert';
import { useToast } from '../../hooks/use-toast';
import { Upload, Eye, Download } from 'lucide-react';
import { financeiroService } from '../../services/api';

interface ComprovanteModalProps {
  isOpen: boolean;
  onClose: () => void;
  movimentacao: any;
  onSuccess: () => void;
}

const ComprovanteModal: React.FC<ComprovanteModalProps> = ({
  isOpen,
  onClose,
  movimentacao,
  onSuccess
}) => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
      if (!allowedTypes.includes(file.type)) {
        setError('Tipo de arquivo não permitido. Use JPEG, PNG ou PDF.');
        return;
      }
      
      if (file.size > 10 * 1024 * 1024) {
        setError('Arquivo muito grande. Máximo 10MB.');
        return;
      }
      
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !movimentacao) return;
    
    try {
      setLoading(true);
      setError(null);
      
      await financeiroService.uploadComprovante(movimentacao.id, selectedFile);
      
      toast({
        title: "Sucesso",
        description: "Comprovante enviado com sucesso",
      });
      
      onSuccess();
      onClose();
    } catch (err: any) {
      let errorMessage = 'Erro ao enviar comprovante';
      
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleViewComprovante = () => {
    if (movimentacao?.comprovante_url) {
      window.open(movimentacao.comprovante_url, '_blank');
    }
  };

  const handleDownloadComprovante = () => {
    if (movimentacao?.comprovante_url) {
      const link = document.createElement('a');
      link.href = movimentacao.comprovante_url;
      link.download = `comprovante_${movimentacao.id}`;
      link.click();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>
            {movimentacao?.comprovante_url ? 'Visualizar Comprovante' : 'Enviar Comprovante'}
          </DialogTitle>
        </DialogHeader>

        {error && (
          <Alert className="border-red-200 bg-red-50">
            <AlertDescription className="text-red-800">{error}</AlertDescription>
          </Alert>
        )}

        <div className="space-y-4">
          {movimentacao?.comprovante_url ? (
            <div className="text-center space-y-4">
              <div className="p-4 border rounded-lg bg-green-50">
                <p className="text-green-800 font-medium">Comprovante já enviado</p>
                <p className="text-sm text-green-600 mt-1">
                  Movimentação: {movimentacao.categoria}
                </p>
              </div>
              
              <div className="flex gap-2 justify-center">
                <Button
                  onClick={handleViewComprovante}
                  className="flex items-center gap-2"
                >
                  <Eye className="h-4 w-4" />
                  Visualizar
                </Button>
                
                <Button
                  variant="outline"
                  onClick={handleDownloadComprovante}
                  className="flex items-center gap-2"
                >
                  <Download className="h-4 w-4" />
                  Baixar
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="p-4 border rounded-lg bg-blue-50">
                <p className="text-blue-800 font-medium">
                  {movimentacao?.categoria}
                </p>
                <p className="text-sm text-blue-600 mt-1">
                  Valor: R$ {movimentacao?.valor?.toFixed(2)}
                </p>
              </div>
              
              <div>
                <Label htmlFor="comprovante">Selecionar Arquivo</Label>
                <Input
                  id="comprovante"
                  type="file"
                  accept=".jpg,.jpeg,.png,.pdf"
                  onChange={handleFileSelect}
                  className="mt-1"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Formatos aceitos: JPEG, PNG, PDF (máx. 10MB)
                </p>
              </div>
              
              {selectedFile && (
                <div className="p-3 border rounded-lg bg-gray-50">
                  <p className="text-sm font-medium">Arquivo selecionado:</p>
                  <p className="text-sm text-gray-600">{selectedFile.name}</p>
                  <p className="text-xs text-gray-500">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="flex justify-end space-x-2 pt-4">
          <Button type="button" variant="outline" onClick={onClose}>
            Fechar
          </Button>
          
          {!movimentacao?.comprovante_url && (
            <Button 
              onClick={handleUpload} 
              disabled={!selectedFile || loading}
              className="flex items-center gap-2"
            >
              <Upload className="h-4 w-4" />
              {loading ? 'Enviando...' : 'Enviar'}
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ComprovanteModal;
