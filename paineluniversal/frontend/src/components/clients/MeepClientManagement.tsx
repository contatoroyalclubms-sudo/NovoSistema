import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Badge } from '../../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Checkbox } from '../../components/ui/checkbox';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../../components/ui/dialog';
import { useToast } from '../../hooks/use-toast';
import { Search, Plus, Edit, Trash2, Ban, CheckCircle, History, Users } from 'lucide-react';
import { clientService, MeepClient, ClientCategory, ClientBlockHistory, ClientFilters } from '../../services/clientService';

interface ClientModalProps {
  client?: MeepClient;
  categories: ClientCategory[];
  isOpen: boolean;
  onClose: () => void;
  onSave: (client: MeepClient) => void;
}

const ClientModal: React.FC<ClientModalProps> = ({ client, categories, isOpen, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    nome: '',
    cpf: '',
    identificador: '',
    telefone: '',
    email: '',
    data_nascimento: '',
    sexo: '',
    categoria_id: '',
    nome_na_lista: false
  });
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (client) {
      setFormData({
        nome: client.nome || '',
        cpf: client.cpf || '',
        identificador: client.identificador || '',
        telefone: client.telefone || '',
        email: client.email || '',
        data_nascimento: client.data_nascimento || '',
        sexo: client.sexo || '',
        categoria_id: client.categoria_id || '',
        nome_na_lista: client.nome_na_lista || false
      });
    } else {
      setFormData({
        nome: '',
        cpf: '',
        identificador: '',
        telefone: '',
        email: '',
        data_nascimento: '',
        sexo: '',
        categoria_id: '',
        nome_na_lista: false
      });
    }
  }, [client, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.nome.trim()) {
      toast({
        title: "Erro",
        description: "Nome é obrigatório",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      let savedClient;
      if (client) {
        savedClient = await clientService.updateClient(client.id, formData);
        toast({
          title: "Sucesso",
          description: "Cliente atualizado com sucesso!"
        });
      } else {
        savedClient = await clientService.createClient(formData);
        toast({
          title: "Sucesso",
          description: "Cliente criado com sucesso!"
        });
      }
      onSave(savedClient);
      onClose();
    } catch (error: any) {
      toast({
        title: "Erro",
        description: error.response?.data?.detail || "Erro ao salvar cliente",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleBlock = async () => {
    if (!client) return;
    
    const reason = prompt("Motivo do bloqueio:");
    if (reason === null) return;

    try {
      await clientService.toggleClientBlock(client.id, reason);
      toast({
        title: "Sucesso",
        description: "Cliente bloqueado com sucesso!"
      });
      onSave({ ...client, status: 'bloqueado' });
    } catch (error: any) {
      toast({
        title: "Erro",
        description: error.response?.data?.detail || "Erro ao bloquear cliente",
        variant: "destructive"
      });
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{client ? 'Editar Cliente' : 'Novo Cliente'}</DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="nome">Nome *</Label>
              <Input
                id="nome"
                value={formData.nome}
                onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                placeholder="Nome completo"
                required
              />
            </div>
            <div>
              <Label htmlFor="cpf">CPF</Label>
              <Input
                id="cpf"
                value={formData.cpf}
                onChange={(e) => setFormData({ ...formData, cpf: e.target.value })}
                placeholder="000.000.000-00"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="identificador">Identificador</Label>
              <Input
                id="identificador"
                value={formData.identificador}
                onChange={(e) => setFormData({ ...formData, identificador: e.target.value })}
                placeholder="Identificador único"
              />
            </div>
            <div>
              <Label htmlFor="telefone">Telefone</Label>
              <Input
                id="telefone"
                value={formData.telefone}
                onChange={(e) => setFormData({ ...formData, telefone: e.target.value })}
                placeholder="(00) 00000-0000"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="email@exemplo.com"
              />
            </div>
            <div>
              <Label htmlFor="data_nascimento">Data de Nascimento</Label>
              <Input
                id="data_nascimento"
                type="date"
                value={formData.data_nascimento}
                onChange={(e) => setFormData({ ...formData, data_nascimento: e.target.value })}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="sexo">Sexo</Label>
              <Select value={formData.sexo} onValueChange={(value) => setFormData({ ...formData, sexo: value })}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o sexo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="M">Masculino</SelectItem>
                  <SelectItem value="F">Feminino</SelectItem>
                  <SelectItem value="O">Outro</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="categoria">Categoria</Label>
              <Select value={formData.categoria_id} onValueChange={(value) => setFormData({ ...formData, categoria_id: value })}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione uma categoria" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map(cat => (
                    <SelectItem key={cat.id} value={cat.id}>{cat.descricao}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="nome_na_lista"
              checked={formData.nome_na_lista}
              onCheckedChange={(checked) => setFormData({ ...formData, nome_na_lista: !!checked })}
            />
            <Label htmlFor="nome_na_lista">Nome na lista?</Label>
          </div>

          {client && (
            <div className="flex gap-2 pt-4 border-t">
              <Button type="button" variant="destructive" onClick={handleBlock}>
                <Ban className="w-4 h-4 mr-2" />
                Bloquear
              </Button>
            </div>
          )}

          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Salvando...' : 'Salvar'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

interface CategoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (category: ClientCategory) => void;
}

const CategoryModal: React.FC<CategoryModalProps> = ({ isOpen, onClose, onSave }) => {
  const [descricao, setDescricao] = useState('');
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!descricao.trim()) {
      toast({
        title: "Erro",
        description: "Descrição é obrigatória",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const category = await clientService.createCategory({ descricao });
      toast({
        title: "Sucesso",
        description: "Categoria criada com sucesso!"
      });
      onSave(category);
      setDescricao('');
      onClose();
    } catch (error: any) {
      toast({
        title: "Erro",
        description: error.response?.data?.detail || "Erro ao criar categoria",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Nova Categoria</DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="descricao">Descrição</Label>
            <Input
              id="descricao"
              value={descricao}
              onChange={(e) => setDescricao(e.target.value)}
              placeholder="Descrição da categoria"
              required
            />
          </div>

          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Salvando...' : 'Salvar'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

interface HistoryModalProps {
  client: MeepClient;
  isOpen: boolean;
  onClose: () => void;
}

const HistoryModal: React.FC<HistoryModalProps> = ({ client, isOpen, onClose }) => {
  const [history, setHistory] = useState<ClientBlockHistory[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && client) {
      loadHistory();
    }
  }, [isOpen, client]);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await clientService.getClientBlockHistory(client.id);
      setHistory(data);
    } catch (error) {
      console.error('Erro ao carregar histórico:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Histórico de Bloqueios - {client.nome}</DialogTitle>
        </DialogHeader>
        
        <div className="max-h-96 overflow-y-auto">
          {loading ? (
            <div className="text-center py-4">Carregando...</div>
          ) : history.length === 0 ? (
            <div className="text-center py-4 text-gray-500">Nenhum histórico encontrado</div>
          ) : (
            <div className="space-y-2">
              {history.map((item) => (
                <Card key={item.id}>
                  <CardContent className="p-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      {item.data_bloqueio && (
                        <>
                          <div>
                            <strong>Bloqueado por:</strong> {item.bloqueado_por}
                          </div>
                          <div>
                            <strong>Data do bloqueio:</strong> {new Date(item.data_bloqueio).toLocaleString()}
                          </div>
                          <div className="col-span-2">
                            <strong>Razão:</strong> {item.razao_bloqueio}
                          </div>
                        </>
                      )}
                      {item.data_desbloqueio && (
                        <>
                          <div>
                            <strong>Desbloqueado por:</strong> {item.desbloqueado_por}
                          </div>
                          <div>
                            <strong>Data do desbloqueio:</strong> {new Date(item.data_desbloqueio).toLocaleString()}
                          </div>
                          <div className="col-span-2">
                            <strong>Razão:</strong> {item.razao_desbloqueio}
                          </div>
                        </>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

const MeepClientManagement: React.FC = () => {
  const [clients, setClients] = useState<MeepClient[]>([]);
  const [categories, setCategories] = useState<ClientCategory[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<ClientFilters>({});
  const [selectedClient, setSelectedClient] = useState<MeepClient | undefined>();
  const [showClientModal, setShowClientModal] = useState(false);
  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [currentView, setCurrentView] = useState<'clients' | 'categories'>('clients');
  const { toast } = useToast();

  useEffect(() => {
    loadClients();
    loadCategories();
  }, []);

  const loadClients = async () => {
    setLoading(true);
    try {
      const data = await clientService.getClients(filters);
      setClients(data);
    } catch (error: any) {
      toast({
        title: "Erro",
        description: "Erro ao carregar clientes",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const data = await clientService.getCategories();
      setCategories(data);
    } catch (error: any) {
      toast({
        title: "Erro",
        description: "Erro ao carregar categorias",
        variant: "destructive"
      });
    }
  };

  const handleSearch = () => {
    loadClients();
  };

  const handleEditClient = (client: MeepClient) => {
    setSelectedClient(client);
    setShowClientModal(true);
  };

  const handleNewClient = () => {
    setSelectedClient(undefined);
    setShowClientModal(true);
  };

  const handleSaveClient = (client: MeepClient) => {
    if (selectedClient) {
      setClients(clients.map(c => c.id === client.id ? client : c));
    } else {
      setClients([...clients, client]);
    }
  };

  const handleDeleteClient = async (client: MeepClient) => {
    if (!confirm(`Tem certeza que deseja excluir o cliente ${client.nome}?`)) return;

    try {
      await clientService.deleteClient(client.id);
      setClients(clients.filter(c => c.id !== client.id));
      toast({
        title: "Sucesso",
        description: "Cliente excluído com sucesso!"
      });
    } catch (error: any) {
      toast({
        title: "Erro",
        description: error.response?.data?.detail || "Erro ao excluir cliente",
        variant: "destructive"
      });
    }
  };

  const handleToggleBlock = async (client: MeepClient) => {
    const isBlocking = client.status !== 'bloqueado';
    const reason = prompt(isBlocking ? "Motivo do bloqueio:" : "Motivo do desbloqueio:");
    if (reason === null) return;

    try {
      await clientService.toggleClientBlock(client.id, reason);
      const newStatus = isBlocking ? 'bloqueado' : 'ativo';
      setClients(clients.map(c => c.id === client.id ? { ...c, status: newStatus } : c));
      toast({
        title: "Sucesso",
        description: `Cliente ${isBlocking ? 'bloqueado' : 'desbloqueado'} com sucesso!`
      });
    } catch (error: any) {
      toast({
        title: "Erro",
        description: error.response?.data?.detail || "Erro ao alterar status do cliente",
        variant: "destructive"
      });
    }
  };

  const handleShowHistory = (client: MeepClient) => {
    setSelectedClient(client);
    setShowHistoryModal(true);
  };

  const handleSaveCategory = (category: ClientCategory) => {
    setCategories([...categories, category]);
  };

  const handleDeleteCategory = async (category: ClientCategory) => {
    if (!confirm(`Tem certeza que deseja excluir a categoria ${category.descricao}?`)) return;

    try {
      await clientService.deleteCategory(category.id);
      setCategories(categories.filter(c => c.id !== category.id));
      toast({
        title: "Sucesso",
        description: "Categoria excluída com sucesso!"
      });
    } catch (error: any) {
      toast({
        title: "Erro",
        description: error.response?.data?.detail || "Erro ao excluir categoria",
        variant: "destructive"
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Sistema MEEP - Gestão de Clientes</h1>
        <div className="flex gap-2">
          <Button
            variant={currentView === 'clients' ? 'default' : 'outline'}
            onClick={() => setCurrentView('clients')}
          >
            <Users className="w-4 h-4 mr-2" />
            Clientes
          </Button>
          <Button
            variant={currentView === 'categories' ? 'default' : 'outline'}
            onClick={() => setCurrentView('categories')}
          >
            Categorias
          </Button>
        </div>
      </div>

      {currentView === 'clients' ? (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Gestão de Clientes</CardTitle>
              <Button onClick={handleNewClient}>
                <Plus className="w-4 h-4 mr-2" />
                Novo Cliente
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Input
                  placeholder="Buscar por nome"
                  value={filters.nome || ''}
                  onChange={(e) => setFilters({ ...filters, nome: e.target.value })}
                />
                <Input
                  placeholder="Buscar por CPF"
                  value={filters.cpf || ''}
                  onChange={(e) => setFilters({ ...filters, cpf: e.target.value })}
                />
                <Select value={filters.categoria || ''} onValueChange={(value) => setFilters({ ...filters, categoria: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Categoria" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Todas as categorias</SelectItem>
                    {categories.map(cat => (
                      <SelectItem key={cat.id} value={cat.id}>{cat.descricao}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button onClick={handleSearch}>
                  <Search className="w-4 h-4 mr-2" />
                  Buscar
                </Button>
              </div>

              <div className="flex gap-4">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="somente_bloqueados"
                    checked={filters.somente_bloqueados || false}
                    onCheckedChange={(checked) => setFilters({ ...filters, somente_bloqueados: !!checked })}
                  />
                  <Label htmlFor="somente_bloqueados">Somente bloqueados</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="somente_com_alertas"
                    checked={filters.somente_com_alertas || false}
                    onCheckedChange={(checked) => setFilters({ ...filters, somente_com_alertas: !!checked })}
                  />
                  <Label htmlFor="somente_com_alertas">Somente com alertas</Label>
                </div>
              </div>

              {loading ? (
                <div className="text-center py-8">Carregando...</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse border border-gray-200">
                    <thead>
                      <tr className="bg-gray-50">
                        <th className="border border-gray-200 p-2 text-left">Nome</th>
                        <th className="border border-gray-200 p-2 text-left">CPF</th>
                        <th className="border border-gray-200 p-2 text-left">Telefone</th>
                        <th className="border border-gray-200 p-2 text-left">Email</th>
                        <th className="border border-gray-200 p-2 text-left">Status</th>
                        <th className="border border-gray-200 p-2 text-left">Lista</th>
                        <th className="border border-gray-200 p-2 text-left">Ações</th>
                      </tr>
                    </thead>
                    <tbody>
                      {clients.map((client) => (
                        <tr key={client.id} className="hover:bg-gray-50">
                          <td className="border border-gray-200 p-2">{client.nome}</td>
                          <td className="border border-gray-200 p-2">{client.cpf || '-'}</td>
                          <td className="border border-gray-200 p-2">{client.telefone || '-'}</td>
                          <td className="border border-gray-200 p-2">{client.email || '-'}</td>
                          <td className="border border-gray-200 p-2">
                            <Badge variant={client.status === 'ativo' ? 'default' : 'destructive'}>
                              {client.status}
                            </Badge>
                          </td>
                          <td className="border border-gray-200 p-2">
                            {client.nome_na_lista ? 'Sim' : 'Não'}
                          </td>
                          <td className="border border-gray-200 p-2">
                            <div className="flex gap-1">
                              <Button size="sm" variant="outline" onClick={() => handleEditClient(client)}>
                                <Edit className="w-3 h-3" />
                              </Button>
                              <Button 
                                size="sm" 
                                variant={client.status === 'bloqueado' ? 'default' : 'destructive'}
                                onClick={() => handleToggleBlock(client)}
                              >
                                {client.status === 'bloqueado' ? <CheckCircle className="w-3 h-3" /> : <Ban className="w-3 h-3" />}
                              </Button>
                              <Button size="sm" variant="outline" onClick={() => handleShowHistory(client)}>
                                <History className="w-3 h-3" />
                              </Button>
                              <Button size="sm" variant="destructive" onClick={() => handleDeleteClient(client)}>
                                <Trash2 className="w-3 h-3" />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {clients.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      Nenhum cliente encontrado
                    </div>
                  )}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Categoria Cliente Estabelecimento</CardTitle>
              <Button onClick={() => setShowCategoryModal(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Nova Categoria
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {categories.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                Não há categorias cadastradas
              </div>
            ) : (
              <div className="space-y-2">
                {categories.map((category) => (
                  <div key={category.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span>{category.descricao}</span>
                    <Button size="sm" variant="destructive" onClick={() => handleDeleteCategory(category)}>
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <ClientModal
        client={selectedClient}
        categories={categories}
        isOpen={showClientModal}
        onClose={() => setShowClientModal(false)}
        onSave={handleSaveClient}
      />

      <CategoryModal
        isOpen={showCategoryModal}
        onClose={() => setShowCategoryModal(false)}
        onSave={handleSaveCategory}
      />

      {selectedClient && (
        <HistoryModal
          client={selectedClient}
          isOpen={showHistoryModal}
          onClose={() => setShowHistoryModal(false)}
        />
      )}
    </div>
  );
};

export default MeepClientManagement;
