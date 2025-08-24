import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { Alert, AlertDescription } from '../ui/alert';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { useToast } from '../../hooks/use-toast';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { listaService } from '../../services/api';

interface ImportarConvidadosModalProps {
  isOpen: boolean;
  onClose: () => void;
  lista: any;
  onSuccess: () => void;
}

const ImportarConvidadosModal: React.FC<ImportarConvidadosModalProps> = ({
  isOpen,
  onClose,
  lista,
  onSuccess
}) => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [resultado, setResultado] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      const validTypes = [
        'text/csv',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      ];
      
      if (validTypes.includes(selectedFile.type) || 
          selectedFile.name.endsWith('.csv') || 
          selectedFile.name.endsWith('.xlsx') || 
          selectedFile.name.endsWith('.xls')) {
        setFile(selectedFile);
        setError(null);
        setResultado(null);
      } else {
        setError('Formato de arquivo não suportado. Use CSV ou Excel (.xlsx, .xls)');
        setFile(null);
      }
    }
  };

  const handleImport = async () => {
    if (!file || !lista) return;

    try {
      setLoading(true);
      setError(null);
      
      const result = await listaService.importarConvidados(lista.id, file);
      setResultado(result);
      
      if (result.convidados_criados > 0) {
        toast({
          title: "Importação concluída",
          description: `${result.convidados_criados} convidados importados com sucesso`,
        });
        onSuccess();
      }
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao importar convidados');
    } finally {
      setLoading(false);
    }
  };

  const downloadTemplate = () => {
    const csvContent = "cpf,nome,email,telefone\n123.456.789-00,João Silva,joao@email.com,(11) 99999-9999\n987.654.321-00,Maria Santos,maria@email.com,(11) 88888-8888";
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'template_convidados.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const resetModal = () => {
    setFile(null);
    setResultado(null);
    setError(null);
  };

  const handleClose = () => {
    resetModal();
    onClose();
  };

  if (!lista) return null;

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Importar Convidados - {lista.nome}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {error && (
            <Alert className="border-red-200 bg-red-50">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="text-red-800">{error}</AlertDescription>
            </Alert>
          )}

          {!resultado && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Instruções</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm text-gray-600">
                    <p className="mb-2">Para importar convidados, prepare um arquivo CSV ou Excel com as seguintes colunas:</p>
                    <ul className="list-disc list-inside space-y-1">
                      <li><strong>cpf</strong> (obrigatório): CPF do convidado</li>
                      <li><strong>nome</strong> (obrigatório): Nome completo</li>
                      <li><strong>email</strong> (opcional): E-mail do convidado</li>
                      <li><strong>telefone</strong> (opcional): Telefone do convidado</li>
                    </ul>
                  </div>
                  
                  <Button 
                    variant="outline" 
                    onClick={downloadTemplate}
                    className="flex items-center gap-2"
                  >
                    <FileText className="h-4 w-4" />
                    Baixar Template CSV
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Selecionar Arquivo</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="file">Arquivo CSV ou Excel</Label>
                      <input
                        id="file"
                        type="file"
                        accept=".csv,.xlsx,.xls"
                        onChange={handleFileChange}
                        className="w-full mt-1 p-2 border rounded-md"
                      />
                    </div>
                    
                    {file && (
                      <div className="p-3 bg-blue-50 rounded-md">
                        <p className="text-sm text-blue-800">
                          <strong>Arquivo selecionado:</strong> {file.name}
                        </p>
                        <p className="text-sm text-blue-600">
                          Tamanho: {(file.size / 1024).toFixed(2)} KB
                        </p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </>
          )}

          {resultado && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  Resultado da Importação
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-green-50 rounded-md">
                    <p className="text-2xl font-bold text-green-600">{resultado.convidados_criados}</p>
                    <p className="text-sm text-green-800">Convidados Criados</p>
                  </div>
                  <div className="text-center p-4 bg-blue-50 rounded-md">
                    <p className="text-2xl font-bold text-blue-600">{resultado.total_linhas}</p>
                    <p className="text-sm text-blue-800">Total de Linhas</p>
                  </div>
                </div>

                {resultado.erros && resultado.erros.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-red-600 mb-2">
                      Erros encontrados ({resultado.erros.length}):
                    </h4>
                    <div className="max-h-40 overflow-y-auto bg-red-50 p-3 rounded-md">
                      {resultado.erros.map((erro: string, index: number) => (
                        <p key={index} className="text-sm text-red-800 mb-1">
                          {erro}
                        </p>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        <div className="flex justify-end space-x-2 pt-4">
          <Button variant="outline" onClick={handleClose}>
            {resultado ? 'Fechar' : 'Cancelar'}
          </Button>
          
          {!resultado && (
            <Button 
              onClick={handleImport} 
              disabled={!file || loading}
              className="flex items-center gap-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Importando...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4" />
                  Importar
                </>
              )}
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ImportarConvidadosModal;
