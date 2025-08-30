# MCP AGENTS - ÁREA ISOLADA

Esta pasta contém todos os agentes MCP e não interfere no sistema principal.

## Estrutura:
- agents/ - Agentes específicos (railway-monitor, deploy-manager)
- configs/ - Configurações dos agentes
- scripts/ - Scripts de automação

## Isolamento:
- Não modifica arquivos do sistema principal
- Não interfere em frontend/ ou backend/
- Mantém compatibilidade total com deploy Railway

## Agentes Disponíveis:

### railway-monitor
Monitora o status do deploy no Railway e valida a saúde do sistema.

### deploy-manager
Gerencia o processo de deploy e validação de estrutura.

### system-validator
Valida a integridade do sistema antes e depois do deploy.

## Como Usar:

1. Os agentes são independentes e podem ser executados isoladamente
2. Não requerem modificações no sistema principal
3. Configurações específicas em `configs/`
4. Scripts auxiliares em `scripts/`

## Compatibilidade:
- Railway Deploy ✓
- Sistema existente ✓
- Frontend/Backend intactos ✓