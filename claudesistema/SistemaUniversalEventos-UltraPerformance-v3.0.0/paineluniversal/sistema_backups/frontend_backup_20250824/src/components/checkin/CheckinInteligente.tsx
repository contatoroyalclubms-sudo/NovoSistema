import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { useToast } from '../../hooks/use-toast';
import { eventoService } from '../../services/api';
import { Scan, UserCheck, Users, Clock, AlertTriangle, CheckCircle } from 'lucide-react';

interface CheckinInteligente {
  eventoId?: number;
}

const CheckinInteligente: React.FC<CheckinInteligente> = ({ eventoId = 1 }) => {
  const [eventos, setEventos] = useState<any[]>([]);
  const [eventoSelecionado, setEventoSelecionado] = useState<number>(eventoId);
  const [cpf, setCpf] = useState('');
  const [qrCode, setQrCode] = useState('');
  const [validacaoCpf, setValidacaoCpf] = useState('');
  const [metodoCheckin, setMetodoCheckin] = useState<'cpf' | 'qr'>('cpf');
  const [loading, setLoading] = useState(false);
  const [dashboard, setDashboard] = useState<any>(null);
  const [checkinsRecentes, setCheckinsRecentes] = useState<any[]>([]);
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);
  const { toast } = useToast();
  const qrInputRef = useRef<HTMLInputElement>(null);
  const cpfInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    carregarEventos();
    conectarWebSocket();
    
    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, [eventoSelecionado]);

  const conectarWebSocket = () => {
    if (!eventoSelecionado) return;
    
    const wsUrl = `ws://localhost:8000/api/checkin/ws/${eventoSelecionado}`;
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('WebSocket check-in conectado');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'checkin_update') {
        carregarDashboard();
        carregarCheckinsRecentes();
        
        toast({
          title: "Novo check-in realizado",
          description: `${data.data.checkin.nome} - ${data.data.checkin.metodo}`,
        });
      } else if (data.type === 'dashboard_update') {
        setDashboard(data.data);
      }
    };
    
    ws.onerror = (error) => {
      console.error('Erro WebSocket check-in:', error);
    };
    
    ws.onclose = () => {
      console.log('WebSocket check-in desconectado');
      setTimeout(conectarWebSocket, 3000);
    };
    
    setWebsocket(ws);
  };

  const carregarEventos = async () => {
    try {
      const response = await eventoService.listar();
      setEventos(response.filter((e: any) => e.status === 'ativo'));
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao carregar eventos",
        variant: "destructive"
      });
    }
  };

  const carregarDashboard = async () => {
    if (!eventoSelecionado) return;
    
    try {
      const response = await fetch(`/api/checkins/dashboard/${eventoSelecionado}`);
      const data = await response.json();
      setDashboard(data);
    } catch (error) {
      console.error('Erro ao carregar dashboard:', error);
    }
  };

  const carregarCheckinsRecentes = async () => {
    if (!eventoSelecionado) return;
    
    try {
      const response = await fetch(`/api/checkins/evento/${eventoSelecionado}`);
      const data = await response.json();
      setCheckinsRecentes(data.slice(0, 10));
    } catch (error) {
      console.error('Erro ao carregar check-ins recentes:', error);
    }
  };

  const formatarCPF = (cpf: string) => {
    const numbers = cpf.replace(/\D/g, '');
    return numbers.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  };

  const processarCheckinCPF = async () => {
    if (!cpf || !validacaoCpf || !eventoSelecionado) {
      toast({
        title: "Campos obrigatórios",
        description: "Preencha CPF e código de validação",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    
    try {
      const response = await fetch('/api/checkins/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          cpf: cpf.replace(/\D/g, ''),
          evento_id: eventoSelecionado,
          metodo_checkin: 'cpf',
          validacao_cpf: validacaoCpf
        })
      });

      if (response.ok) {
        const result = await response.json();
        toast({
          title: "Check-in realizado!",
          description: `${result.nome} - CPF: ${formatarCPF(result.cpf)}`,
        });
        
        setCpf('');
        setValidacaoCpf('');
        if (cpfInputRef.current) {
          cpfInputRef.current.focus();
        }
      } else {
        const errorData = await response.json();
        toast({
          title: "Erro no check-in",
          description: errorData.detail || 'Erro ao processar check-in',
          variant: "destructive"
        });
      }
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao processar check-in",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const processarCheckinQR = async () => {
    if (!qrCode || !validacaoCpf) {
      toast({
        title: "Campos obrigatórios",
        description: "Escaneie QR Code e digite validação CPF",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    
    try {
      const response = await fetch('/api/checkins/qr', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          qr_code: qrCode,
          validacao_cpf: validacaoCpf
        })
      });

      if (response.ok) {
        const result = await response.json();
        toast({
          title: "Check-in realizado!",
          description: `${result.nome} - QR Code validado`,
        });
        
        setQrCode('');
        setValidacaoCpf('');
        if (qrInputRef.current) {
          qrInputRef.current.focus();
        }
      } else {
        const errorData = await response.json();
        toast({
          title: "Erro no check-in",
          description: errorData.detail || 'QR Code inválido',
          variant: "destructive"
        });
      }
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao processar check-in",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (eventoSelecionado) {
      carregarDashboard();
      carregarCheckinsRecentes();
    }
  }, [eventoSelecionado]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 p-4 h-screen bg-gray-50">
      <div className="lg:col-span-2 flex flex-col">
        <Card className="mb-4 shadow-lg">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2">
              <UserCheck className="h-5 w-5" />
              Check-in Inteligente
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-2 mb-4">
              <Button
                variant={metodoCheckin === 'cpf' ? 'default' : 'outline'}
                onClick={() => setMetodoCheckin('cpf')}
                className="h-12 text-lg"
              >
                📱 CPF
              </Button>
              <Button
                variant={metodoCheckin === 'qr' ? 'default' : 'outline'}
                onClick={() => setMetodoCheckin('qr')}
                className="h-12 text-lg"
              >
                <Scan className="h-5 w-5 mr-2" />
                QR Code
              </Button>
            </div>

            {metodoCheckin === 'cpf' ? (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="cpf">CPF</Label>
                  <Input
                    ref={cpfInputRef}
                    id="cpf"
                    placeholder="000.000.000-00"
                    value={cpf}
                    onChange={(e) => setCpf(formatarCPF(e.target.value))}
                    className="text-xl h-14"
                    maxLength={14}
                    autoFocus
                  />
                </div>
                <div>
                  <Label htmlFor="validacao-cpf">3 Primeiros Dígitos do CPF</Label>
                  <Input
                    id="validacao-cpf"
                    placeholder="123"
                    value={validacaoCpf}
                    onChange={(e) => setValidacaoCpf(e.target.value.replace(/\D/g, '').slice(0, 3))}
                    className="text-xl h-14"
                    maxLength={3}
                  />
                </div>
                <Button
                  onClick={processarCheckinCPF}
                  disabled={loading}
                  className="w-full h-16 text-xl font-bold"
                  size="lg"
                >
                  {loading ? 'Processando...' : 'Realizar Check-in CPF'}
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="qr-code">QR Code</Label>
                  <Input
                    ref={qrInputRef}
                    id="qr-code"
                    placeholder="Escaneie ou digite o QR Code"
                    value={qrCode}
                    onChange={(e) => setQrCode(e.target.value)}
                    className="text-xl h-14"
                    autoFocus
                  />
                </div>
                <div>
                  <Label htmlFor="validacao-qr">3 Primeiros Dígitos do CPF</Label>
                  <Input
                    id="validacao-qr"
                    placeholder="123"
                    value={validacaoCpf}
                    onChange={(e) => setValidacaoCpf(e.target.value.replace(/\D/g, '').slice(0, 3))}
                    className="text-xl h-14"
                    maxLength={3}
                  />
                </div>
                <Button
                  onClick={processarCheckinQR}
                  disabled={loading}
                  className="w-full h-16 text-xl font-bold"
                  size="lg"
                >
                  {loading ? 'Processando...' : 'Realizar Check-in QR'}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="flex-1 shadow-lg">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Check-ins Recentes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {checkinsRecentes.map((checkin, index) => (
                <div key={index} className="flex justify-between items-center p-3 border rounded-lg bg-white">
                  <div>
                    <div className="font-medium">{checkin.nome}</div>
                    <div className="text-sm text-gray-500">
                      CPF: {formatarCPF(checkin.cpf)} • {checkin.metodo_checkin}
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge variant="default">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Confirmado
                    </Badge>
                    <div className="text-xs text-gray-500 mt-1">
                      {new Date(checkin.checkin_em).toLocaleTimeString('pt-BR')}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="flex flex-col gap-4">
        <Card className="shadow-lg">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Dashboard Tempo Real
            </CardTitle>
          </CardHeader>
          <CardContent>
            {dashboard ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">{dashboard.total_checkins}</div>
                    <div className="text-sm text-green-700">Check-ins</div>
                  </div>
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{dashboard.checkins_ultima_hora}</div>
                    <div className="text-sm text-blue-700">Última Hora</div>
                  </div>
                  <div className="text-center p-3 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">{dashboard.taxa_presenca}%</div>
                    <div className="text-sm text-purple-700">Taxa Presença</div>
                  </div>
                  <div className="text-center p-3 bg-orange-50 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">{dashboard.fila_espera}</div>
                    <div className="text-sm text-orange-700">Fila Espera</div>
                  </div>
                </div>

                {dashboard.fila_espera > 0 && (
                  <Alert>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      <strong>{dashboard.fila_espera} pessoa(s)</strong> com ingresso aprovado aguardando check-in.
                    </AlertDescription>
                  </Alert>
                )}

                <div>
                  <h4 className="font-medium mb-2">Check-ins por Método</h4>
                  <div className="space-y-2">
                    {dashboard.checkins_por_metodo?.map((metodo: any, index: number) => (
                      <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                        <span className="capitalize">{metodo.metodo}</span>
                        <Badge variant="outline">{metodo.total}</Badge>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Users className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                <p>Carregando dashboard...</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default CheckinInteligente;
