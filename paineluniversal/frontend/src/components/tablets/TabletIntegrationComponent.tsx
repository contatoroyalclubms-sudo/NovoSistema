import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';


class MeepSystemConfig {
    public config: any;
    
    constructor() {
        this.config = {
            local: {
                imprimirFichaCortada: true,
                carregarFotoLogo: null,
                logoAtual: 'meep_logo_default',
                alterarNomeFicha: 'UNICA CLUB',
                zerarSaldoCartoesCashless: false,
                codigoUnico: '30NS',
            },
            
            textos: {
                fichaParteBaixa: 'Proibido a venda de bebidas alcoólicas para menores de 18 anos',
                botaoVendaCashless: 'Texto exibido no botão de venda cashless.',
                botaoLimparCompra: 'Texto exibido no botão de limpar a compra.',
                tempoInatividade: 'Tempo de inatividade para voltar a tela inicial no totem.',
                tempoOciosidadeComanda: 'Tempo de ociosidade da Comanda Eletrônica.',
                impressoraPadrao: 'BAR Royal0000'
            },
            
            funcionalidades: {
                obrigatorioSincronizarPedido: true,
                temCashback: false,
                exibirCalculoTroco: true,
                solicitarCPF: true,
                trabalhaPrePagoCashlessOnline: true,
                desativarCartaoZerarSaldo: false,
                desativarComandaTransferencia: true,
                imprimirPedidoCompleto: true,
                duplicarImpressao: true,
                desativarCancelamento: true,
                habilitarExtrato: false,
                bloquearConsumo: false,
                possuiLimiteSangria: false,
                possuiSaidaCaixaEgo: false,
                consumoMinimoCashless: true,
                permitirRecargaConsumo: true,
                bloquearConsumoFechamento: false,
                deveChamarAcaoPagar: false,
                deveConfirmarPagamento: false,
                podeVincularCartao: false,
                informarNumeroPessoas: false,
                habilitarMailing: false,
                fecharCaixaAutomatico: true,
                permitirFechamentoAberto: false,
                enviarSMSAlterarStatus: false,
                permitirPagarContas: false,
                transacionaMEEP: true,
                exibirPagamentoCashless: true,
                integrarTablet: true
            },
            
            sistema: {
                identificadorSistema: '0 - Portal Geral',
                tipoComandaEletronica: '2 - Individual',
                comandaIndividualNFC: true,
                reembolsoSaldoRemanescente: '1 - Desabilitado',
                localVendaSplit: 'Selecione o local',
                controleVersaoPOS: 'Controle Versão POS',
                tipoEstabelecimento: 'Boate / Casas Noturnas'
            },
            
            identificacaoCliente: {
                prepagoFicha: {
                    nome: { obrigatorio: false, enabled: true },
                    cpf: { obrigatorio: false, enabled: true },
                    identificador: { obrigatorio: false, enabled: true },
                    email: { obrigatorio: false, enabled: true },
                    telefone: { obrigatorio: false, enabled: true },
                    dataNascimento: { obrigatorio: false, enabled: true },
                    etiqueta: { obrigatorio: false, enabled: true }
                },
                prepagoContaMila: {
                    nome: { obrigatorio: true, enabled: true },
                    cpf: { obrigatorio: true, enabled: true },
                    identificador: { obrigatorio: false, enabled: true },
                    email: { obrigatorio: false, enabled: true },
                    telefone: { obrigatorio: true, enabled: true },
                    dataNascimento: { obrigatorio: false, enabled: true },
                    etiqueta: { obrigatorio: false, enabled: true }
                },
                pospagoComanda: {
                    nome: { obrigatorio: true, enabled: true },
                    cpf: { obrigatorio: true, enabled: true },
                    identificador: { obrigatorio: false, enabled: true },
                    email: { obrigatorio: false, enabled: true },
                    telefone: { obrigatorio: true, enabled: true },
                    dataNascimento: { obrigatorio: false, enabled: true },
                    etiqueta: { obrigatorio: false, enabled: true }
                }
            },
            
            wallet: {
                deveUtilizarWallet: false,
                deveUtilizarModoFranquias: false
            },
            
            validacao: {
                habilitarCheckValidador: true,
                imprimirMultiplosRelatorios: false
            },
            
            verificacoes: {
                deveVerificarContaAberta: true,
                habilitarGerenciamentoPedidos: false
            }
        };
    }
    
    
    async integrarTablet(tabletConfig: any) {
        const integrationData = {
            ...this.config,
            tablet: {
                id: tabletConfig.id,
                nome: tabletConfig.nome,
                ip: tabletConfig.ip,
                porta: tabletConfig.porta || 8080,
                tipo: tabletConfig.tipo || 'pos',
                configuracoes: {
                    ...this.config.funcionalidades,
                    integrarTablet: true,
                    sincronizacaoAutomatica: true,
                    monitoramentoStatus: true
                }
            }
        };
        
        try {
            const response = await axios.post('/api/tablets/integrate', integrationData);
            return {
                success: true,
                message: 'Tablet integrado com sucesso!',
                data: response.data
            };
        } catch (error: any) {
            console.error('Erro na integração do tablet:', error);
            return {
                success: false,
                message: 'Erro ao integrar tablet',
                error: error?.message || 'Erro desconhecido'
            };
        }
    }
}


const useTabletManager = () => {
    const [tablets, setTablets] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const addTablet = async (tabletData: any) => {
        setLoading(true);
        setError(null);
        
        try {
            const newTablet = {
                ...tabletData,
                id: `tablet_${Date.now()}`,
                status: 'conectando',
                createdAt: new Date().toISOString()
            };

            const testResponse = await fetch(`http://${tabletData.ip}:${tabletData.porta}/health`);
            
            if (testResponse.ok) {
                newTablet.status = 'conectado';
                setTablets(prev => [...prev, newTablet]);
                return { success: true, tablet: newTablet };
            } else {
                throw new Error('Tablet não responde');
            }
        } catch (err: any) {
            setError('Erro ao conectar com o tablet');
            return { success: false, error: err?.message || 'Erro desconhecido' };
        }finally {
            setLoading(false);
        }
    };

    const removeTablet = (tabletId: string) => {
        setTablets(prev => prev.filter(t => t.id !== tabletId));
    };

    const updateTabletStatus = async () => {
        if (tablets.length === 0) return;
        
        const statusPromises = tablets.map(async (tablet: any) => {
            try {
                const response = await fetch(`http://${tablet.ip}:${tablet.porta}/health`, {
                    method: 'GET',
                    signal: AbortSignal.timeout(5000)
                });
                
                return {
                    ...tablet,
                    status: response.ok ? 'conectado' : 'desconectado',
                    lastCheck: new Date().toISOString()
                };
            } catch (error) {
                return {
                    ...tablet,
                    status: 'desconectado',
                    lastCheck: new Date().toISOString()
                };
            }
        });

        const updatedTablets = await Promise.all(statusPromises);
        setTablets(updatedTablets);
    };

    useEffect(() => {
        const interval = setInterval(updateTabletStatus, 30000);
        return () => clearInterval(interval);
    }, [tablets]);

    return {
        tablets,
        loading,
        error,
        addTablet,
        removeTablet,
        updateTabletStatus
    };
};


const TabletIntegrationComponent: React.FC = () => {
    const [config, setConfig] = useState<MeepSystemConfig>(new MeepSystemConfig());
    const [novoTablet, setNovoTablet] = useState({
        nome: '',
        ip: '',
        porta: 8080,
        tipo: 'pos'
    });
    const { toast } = useToast();

    const { tablets, loading, error, addTablet, removeTablet, updateTabletStatus } = useTabletManager();


    const adicionarTablet = async () => {
        if (!novoTablet.nome || !novoTablet.ip) {
            toast({
                title: "Erro",
                description: "Nome e IP são obrigatórios!",
                variant: "destructive"
            });
            return;
        }

        try {
            const result = await addTablet(novoTablet);
            
            if (result.success) {
                const integrationResult = await config.integrarTablet(result.tablet);
                
                if (integrationResult.success) {
                    setNovoTablet({ nome: '', ip: '', porta: 8080, tipo: 'pos' });
                    toast({
                        title: "Sucesso",
                        description: "Tablet adicionado e integrado com sucesso!",
                    });
                } else {
                    toast({
                        title: "Aviso",
                        description: "Tablet adicionado mas falha na integração MEEP",
                        variant: "destructive"
                    });
                }
            } else {
                toast({
                    title: "Erro",
                    description: result.error || "Erro ao adicionar tablet",
                    variant: "destructive"
                });
            }
        } catch (error) {
            toast({
                title: "Erro",
                description: "Erro ao adicionar tablet",
                variant: "destructive"
            });
            console.error(error);
        }
    };

    const testarConexaoTablet = async (tablet: any) => {
        try {
            const response = await fetch(`http://${tablet.ip}:${tablet.porta}/health`, {
                method: 'GET',
                signal: AbortSignal.timeout(5000)
            });
            
            if (response.ok) {
                toast({
                    title: "Conexão OK",
                    description: `Tablet ${tablet.nome} está online!`,
                });
            } else {
                toast({
                    title: "Conexão Falhou",
                    description: `Tablet ${tablet.nome} não responde!`,
                    variant: "destructive"
                });
            }
        } catch (error) {
            toast({
                title: "Erro de Conexão",
                description: `Tablet ${tablet.nome} está offline!`,
                variant: "destructive"
            });
        }
        
        await updateTabletStatus();
    };

    const sincronizarConfiguracao = async () => {
        if (tablets.length === 0) {
            toast({
                title: "Aviso",
                description: "Nenhum tablet conectado para sincronizar",
                variant: "destructive"
            });
            return;
        }

        try {
            for (const tablet of tablets) {
                await fetch(`http://${tablet.ip}:${tablet.porta}/api/sync-config`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    },
                    body: JSON.stringify({
                        config: config.config,
                        timestamp: new Date().toISOString()
                    })
                });
            }
            
            toast({
                title: "Sucesso",
                description: "Configuração sincronizada em todos os tablets!",
            });
        } catch (error) {
            toast({
                title: "Erro",
                description: "Erro ao sincronizar configuração",
                variant: "destructive"
            });
        }
    };


    return (
        <div className="space-y-6 p-6">
            <div className="text-center">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                    🔄 Integração com Tablets - Sistema MEEP
                </h2>
                <p className="text-gray-600">Configure e gerencie tablets conectados ao sistema</p>
            </div>

            {/* Formulário para adicionar novo tablet */}
            <Card>
                <CardHeader>
                    <CardTitle>➕ Adicionar Novo Tablet</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div>
                            <Label htmlFor="nome">Nome do Tablet</Label>
                            <Input
                                id="nome"
                                placeholder="Nome do Tablet"
                                value={novoTablet.nome}
                                onChange={(e) => setNovoTablet({...novoTablet, nome: e.target.value})}
                            />
                        </div>
                        <div>
                            <Label htmlFor="ip">IP do Tablet</Label>
                            <Input
                                id="ip"
                                placeholder="192.168.1.100"
                                value={novoTablet.ip}
                                onChange={(e) => setNovoTablet({...novoTablet, ip: e.target.value})}
                            />
                        </div>
                        <div>
                            <Label htmlFor="porta">Porta</Label>
                            <Input
                                id="porta"
                                type="number"
                                placeholder="8080"
                                value={novoTablet.porta}
                                onChange={(e) => setNovoTablet({...novoTablet, porta: parseInt(e.target.value)})}
                            />
                        </div>
                        <div>
                            <Label htmlFor="tipo">Tipo</Label>
                            <select
                                id="tipo"
                                className="w-full p-2 border border-gray-300 rounded-md"
                                value={novoTablet.tipo}
                                onChange={(e) => setNovoTablet({...novoTablet, tipo: e.target.value})}
                            >
                                <option value="pos">POS Terminal</option>
                                <option value="kiosk">Totem Autoatendimento</option>
                                <option value="waiter">Tablet Garçom</option>
                                <option value="kitchen">Cozinha/Bar</option>
                            </select>
                        </div>
                    </div>
                    <Button onClick={adicionarTablet} disabled={loading} className="w-full">
                        {loading ? 'Integrando...' : 'Adicionar Tablet'}
                    </Button>
                </CardContent>
            </Card>

            {/* Lista de tablets conectados */}
            <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                    <CardTitle>📱 Tablets Conectados ({tablets.length})</CardTitle>
                    <Button onClick={sincronizarConfiguracao} disabled={loading} variant="outline">
                        🔄 Sincronizar Todos
                    </Button>
                </CardHeader>
                <CardContent>
                    {tablets.length === 0 ? (
                        <p className="text-center text-gray-500 py-8">Nenhum tablet conectado</p>
                    ) : (
                        <div className="space-y-4">
                            {tablets.map((tablet: any) => (
                                <div key={tablet.id} className="flex items-center justify-between p-4 border rounded-lg">
                                    <div className="flex-1">
                                        <h4 className="font-semibold">{tablet.nome}</h4>
                                        <p className="text-sm text-gray-600">IP: {tablet.ip}:{tablet.porta}</p>
                                        <p className="text-sm text-gray-600">Tipo: {tablet.tipo}</p>
                                        <Badge variant={tablet.status === 'conectado' ? 'default' : 'destructive'}>
                                            {tablet.status === 'conectado' ? '🟢' : '🔴'} {tablet.status}
                                        </Badge>
                                    </div>
                                    <div className="flex gap-2">
                                        <Button 
                                            size="sm" 
                                            variant="outline"
                                            onClick={() => testarConexaoTablet(tablet)}
                                        >
                                            🔍 Testar
                                        </Button>
                                        <Button 
                                            size="sm" 
                                            variant="destructive"
                                            onClick={() => removeTablet(tablet.id)}
                                        >
                                            🗑️ Remover
                                        </Button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Configurações avançadas */}
            <Card>
                <CardHeader>
                    <CardTitle>⚙️ Configurações Avançadas</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <label className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
                            <input
                                type="checkbox"
                                checked={config.config.funcionalidades.integrarTablet}
                                onChange={(e) => {
                                    const newConfig = new MeepSystemConfig();
                                    newConfig.config = { ...config.config };
                                    newConfig.config.funcionalidades.integrarTablet = e.target.checked;
                                    setConfig(newConfig);
                                }}
                                className="w-4 h-4"
                            />
                            <span className="text-sm">Habilitar Integração com Tablets</span>
                        </label>
                        <label className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
                            <input
                                type="checkbox"
                                checked={config.config.funcionalidades.transacionaMEEP}
                                onChange={(e) => {
                                    const newConfig = new MeepSystemConfig();
                                    newConfig.config = { ...config.config };
                                    newConfig.config.funcionalidades.transacionaMEEP = e.target.checked;
                                    setConfig(newConfig);
                                }}
                                className="w-4 h-4"
                            />
                            <span className="text-sm">Transacionar com MEEP</span>
                        </label>
                        <label className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
                            <input
                                type="checkbox"
                                checked={config.config.funcionalidades.exibirPagamentoCashless}
                                onChange={(e) => {
                                    const newConfig = new MeepSystemConfig();
                                    newConfig.config = { ...config.config };
                                    newConfig.config.funcionalidades.exibirPagamentoCashless = e.target.checked;
                                    setConfig(newConfig);
                                }}
                                className="w-4 h-4"
                            />
                            <span className="text-sm">Exibir Pagamento Cashless nos Tablets</span>
                        </label>
                    </div>
                </CardContent>
            </Card>

            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                    {error}
                </div>
            )}
        </div>
    );
};

export default TabletIntegrationComponent;
export { MeepSystemConfig, useTabletManager };
