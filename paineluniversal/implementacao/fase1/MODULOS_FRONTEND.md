# 🎯 FASE 1: Finalização dos Módulos Frontend

## 📋 Checklist de Implementação

### 1. Módulo de Usuários
- [ ] **Arquivo Principal:** `src/components/usuarios/UsuariosModule.tsx`
- [ ] **Modal de Criação:** `src/components/usuarios/UsuarioModal.tsx`
- [ ] **Tabela de Usuários:** `src/components/usuarios/UsuariosTable.tsx`
- [ ] **Filtros:** `src/components/usuarios/UsuariosFiltros.tsx`

#### Funcionalidades Requeridas:
- [ ] Listagem com paginação
- [ ] Busca por nome, CPF, email
- [ ] Filtro por tipo de usuário
- [ ] Filtro por empresa
- [ ] Filtro por status (ativo/inativo)
- [ ] Criação de novo usuário
- [ ] Edição de usuário existente
- [ ] Ativação/desativação
- [ ] Reset de senha
- [ ] Gestão de permissões

### 2. Módulo de Empresas
- [ ] **Arquivo Principal:** `src/components/empresas/EmpresasModule.tsx`
- [ ] **Modal de Criação:** `src/components/empresas/EmpresaModal.tsx`
- [ ] **Tabela de Empresas:** `src/components/empresas/EmpresasTable.tsx`
- [ ] **Upload de Logo:** `src/components/empresas/LogoUpload.tsx`

#### Funcionalidades Requeridas:
- [ ] Listagem com paginação
- [ ] Busca por nome, CNPJ
- [ ] Validação de CNPJ
- [ ] Upload de logo da empresa
- [ ] Configurações específicas por empresa
- [ ] Ativação/desativação
- [ ] Relatório de usuários por empresa

### 3. Sistema de Configurações
- [ ] **Arquivo Principal:** `src/components/configuracoes/ConfiguracoesModule.tsx`
- [ ] **Configurações Gerais:** `src/components/configuracoes/ConfigGerias.tsx`
- [ ] **Configurações de Integração:** `src/components/configuracoes/ConfigIntegracoes.tsx`
- [ ] **Temas:** `src/components/configuracoes/ConfigTemas.tsx`

#### Funcionalidades Requeridas:
- [ ] Configurações do sistema
- [ ] Parâmetros de integração (WhatsApp, N8N)
- [ ] Configuração de temas
- [ ] Configuração de notificações
- [ ] Backup e restore de dados
- [ ] Logs do sistema

## 🛠️ Templates de Código

### Template UsuariosModule.tsx
```typescript
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Plus, Search, Filter } from 'lucide-react';
import { usuarioService, Usuario } from '../../services/api';
import UsuarioModal from './UsuarioModal';
import UsuariosTable from './UsuariosTable';

const UsuariosModule: React.FC = () => {
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [usuarioEdicao, setUsuarioEdicao] = useState<Usuario | null>(null);
  const [filtros, setFiltros] = useState({
    busca: '',
    tipo: '',
    empresa: '',
    status: ''
  });

  const carregarUsuarios = async () => {
    try {
      setLoading(true);
      const response = await usuarioService.listar(filtros);
      setUsuarios(response.data);
    } catch (error) {
      console.error('Erro ao carregar usuários:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    carregarUsuarios();
  }, [filtros]);

  const handleNovoUsuario = () => {
    setUsuarioEdicao(null);
    setModalOpen(true);
  };

  const handleEditarUsuario = (usuario: Usuario) => {
    setUsuarioEdicao(usuario);
    setModalOpen(true);
  };

  const handleSalvarUsuario = async (dadosUsuario: any) => {
    try {
      if (usuarioEdicao) {
        await usuarioService.atualizar(usuarioEdicao.id, dadosUsuario);
      } else {
        await usuarioService.criar(dadosUsuario);
      }
      setModalOpen(false);
      carregarUsuarios();
    } catch (error) {
      console.error('Erro ao salvar usuário:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Gestão de Usuários</h1>
        <Button onClick={handleNovoUsuario}>
          <Plus className="w-4 h-4 mr-2" />
          Novo Usuário
        </Button>
      </div>

      {/* Filtros */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Filter className="w-5 h-5 mr-2" />
            Filtros
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <label>Buscar</label>
              <Input
                placeholder="Nome, CPF ou email..."
                value={filtros.busca}
                onChange={(e) => setFiltros({...filtros, busca: e.target.value})}
              />
            </div>
            <div className="space-y-2">
              <label>Tipo</label>
              <Select value={filtros.tipo} onValueChange={(value) => setFiltros({...filtros, tipo: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos os tipos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todos</SelectItem>
                  <SelectItem value="admin">Admin</SelectItem>
                  <SelectItem value="promoter">Promoter</SelectItem>
                  <SelectItem value="operador">Operador</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label>Status</label>
              <Select value={filtros.status} onValueChange={(value) => setFiltros({...filtros, status: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos os status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todos</SelectItem>
                  <SelectItem value="true">Ativo</SelectItem>
                  <SelectItem value="false">Inativo</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de Usuários */}
      <UsuariosTable 
        usuarios={usuarios}
        loading={loading}
        onEditar={handleEditarUsuario}
        onRecarregar={carregarUsuarios}
      />

      {/* Modal de Criação/Edição */}
      <UsuarioModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        usuario={usuarioEdicao}
        onSalvar={handleSalvarUsuario}
      />
    </div>
  );
};

export default UsuariosModule;
```

### Template EmpresasModule.tsx
```typescript
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Plus, Building, Search } from 'lucide-react';
import { empresaService, Empresa } from '../../services/api';
import EmpresaModal from './EmpresaModal';
import EmpresasTable from './EmpresasTable';

const EmpresasModule: React.FC = () => {
  const [empresas, setEmpresas] = useState<Empresa[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [empresaEdicao, setEmpresaEdicao] = useState<Empresa | null>(null);
  const [busca, setBusca] = useState('');

  const carregarEmpresas = async () => {
    try {
      setLoading(true);
      const response = await empresaService.listar({ busca });
      setEmpresas(response.data);
    } catch (error) {
      console.error('Erro ao carregar empresas:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    carregarEmpresas();
  }, [busca]);

  const handleNovaEmpresa = () => {
    setEmpresaEdicao(null);
    setModalOpen(true);
  };

  const handleEditarEmpresa = (empresa: Empresa) => {
    setEmpresaEdicao(empresa);
    setModalOpen(true);
  };

  const handleSalvarEmpresa = async (dadosEmpresa: any) => {
    try {
      if (empresaEdicao) {
        await empresaService.atualizar(empresaEdicao.id, dadosEmpresa);
      } else {
        await empresaService.criar(dadosEmpresa);
      }
      setModalOpen(false);
      carregarEmpresas();
    } catch (error) {
      console.error('Erro ao salvar empresa:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold flex items-center">
          <Building className="w-8 h-8 mr-3" />
          Gestão de Empresas
        </h1>
        <Button onClick={handleNovaEmpresa}>
          <Plus className="w-4 h-4 mr-2" />
          Nova Empresa
        </Button>
      </div>

      {/* Busca */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center space-x-2">
            <Search className="w-5 h-5 text-gray-400" />
            <Input
              placeholder="Buscar por nome ou CNPJ..."
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              className="flex-1"
            />
          </div>
        </CardContent>
      </Card>

      {/* Tabela de Empresas */}
      <EmpresasTable 
        empresas={empresas}
        loading={loading}
        onEditar={handleEditarEmpresa}
        onRecarregar={carregarEmpresas}
      />

      {/* Modal de Criação/Edição */}
      <EmpresaModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        empresa={empresaEdicao}
        onSalvar={handleSalvarEmpresa}
      />
    </div>
  );
};

export default EmpresasModule;
```

## 📊 Cronograma Detalhado

| Tarefa | Estimativa | Responsável | Status |
|--------|------------|-------------|--------|
| UsuariosModule.tsx | 3 dias | Dev Frontend | ⏳ |
| EmpresasModule.tsx | 3 dias | Dev Frontend | ⏳ |
| ConfiguracoesModule.tsx | 2 dias | Dev Frontend | ⏳ |
| Testes dos módulos | 2 dias | Dev Frontend | ⏳ |
| Integração com backend | 1 dia | Dev Fullstack | ⏳ |

**Total:** 11 dias (2.2 semanas)