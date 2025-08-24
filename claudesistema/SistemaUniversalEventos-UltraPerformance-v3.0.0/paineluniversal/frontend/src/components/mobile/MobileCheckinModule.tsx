import React, { useState } from 'react';
import { useIsMobile } from '@/hooks/use-mobile';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';

const MobileCheckinModule: React.FC = () => {
  const [cpf, setCpf] = useState('');
  const [validacao, setValidacao] = useState('');
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();
  const isMobile = useIsMobile();

  const formatCPF = (value: string) => {
    const numbers = value.replace(/\D/g, '');
    if (numbers.length <= 11) {
      return numbers.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    }
    return value;
  };

  const handleCpfChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatCPF(e.target.value);
    setCpf(formatted);
  };

  const handleCheckin = async () => {
    if (!cpf || !validacao) {
      toast({
        title: "Erro",
        description: "Preencha CPF e os 3 dígitos de validação",
        variant: "destructive"
      });
      return;
    }

    if (validacao.length !== 3) {
      toast({
        title: "Erro",
        description: "Digite exatamente 3 dígitos de validação",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast({
        title: "Check-in realizado!",
        description: "Bem-vindo ao evento! 🎉"
      });
      
      setCpf('');
      setValidacao('');
    } catch (error) {
      toast({
        title: "Erro no check-in",
        description: "Verifique os dados e tente novamente",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`p-4 ${isMobile ? 'max-w-sm mx-auto' : 'max-w-md mx-auto'}`}>
      <Card>
        <CardHeader>
          <CardTitle className="text-center">Check-in Rápido</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="cpf">CPF</Label>
            <Input
              id="cpf"
              value={cpf}
              onChange={handleCpfChange}
              placeholder="000.000.000-00"
              className="text-lg"
              maxLength={14}
            />
          </div>
          <div>
            <Label htmlFor="validacao">3 Primeiros Dígitos do CPF</Label>
            <Input
              id="validacao"
              value={validacao}
              onChange={(e) => setValidacao(e.target.value.replace(/\D/g, '').slice(0, 3))}
              placeholder="000"
              maxLength={3}
              className="text-lg text-center"
            />
          </div>
          <Button 
            onClick={handleCheckin} 
            disabled={loading}
            className="w-full text-lg py-6"
          >
            {loading ? 'Processando...' : 'Realizar Check-in'}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default MobileCheckinModule;
