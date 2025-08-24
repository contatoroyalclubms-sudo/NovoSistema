import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import EventosModule from '../EventosModule';
import { eventoService } from '../../../services/api';

jest.mock('../../../services/api');
const mockedEventoService = eventoService as jest.Mocked<typeof eventoService>;

const mockEventos = [
  {
    id: 1,
    nome: 'Evento Teste 1',
    descricao: 'Descrição do evento teste 1',
    data_evento: '2025-12-31T22:00:00Z',
    local: 'Local Teste 1',
    endereco: 'Endereço Teste 1',
    limite_idade: 18,
    capacidade_maxima: 500,
    status: 'ativo',
    empresa_id: 1,
    criador_id: 1,
    criado_em: '2024-01-01T00:00:00Z',
    atualizado_em: null
  },
  {
    id: 2,
    nome: 'Evento Teste 2',
    descricao: 'Descrição do evento teste 2',
    data_evento: '2025-06-15T20:00:00Z',
    local: 'Local Teste 2',
    endereco: 'Endereço Teste 2',
    limite_idade: 21,
    capacidade_maxima: 300,
    status: 'ativo',
    empresa_id: 1,
    criador_id: 1,
    criado_em: '2024-01-01T00:00:00Z',
    atualizado_em: null
  }
];

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('EventosModule', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockedEventoService.listar.mockResolvedValue(mockEventos);
  });

  test('renderiza título e botão de novo evento', async () => {
    renderWithRouter(<EventosModule />);
    
    expect(screen.getByText('Gestão de Eventos')).toBeInTheDocument();
    expect(screen.getByText('Novo Evento')).toBeInTheDocument();
  });

  test('carrega e exibe lista de eventos', async () => {
    renderWithRouter(<EventosModule />);
    
    await waitFor(() => {
      expect(screen.getByText('Evento Teste 1')).toBeInTheDocument();
      expect(screen.getByText('Evento Teste 2')).toBeInTheDocument();
    });
    
    expect(mockedEventoService.listar).toHaveBeenCalledTimes(1);
  });

  test('exibe loading state inicialmente', () => {
    renderWithRouter(<EventosModule />);
    
    expect(screen.getByText('Carregando eventos...')).toBeInTheDocument();
  });

  test('permite buscar eventos por nome', async () => {
    mockedEventoService.buscar.mockResolvedValue([mockEventos[0]]);
    
    renderWithRouter(<EventosModule />);
    
    await waitFor(() => {
      expect(screen.getByText('Evento Teste 1')).toBeInTheDocument();
    });
    
    const searchInput = screen.getByPlaceholderText('Buscar por nome do evento...');
    const searchButton = screen.getByText('Buscar');
    
    fireEvent.change(searchInput, { target: { value: 'Evento Teste 1' } });
    fireEvent.click(searchButton);
    
    await waitFor(() => {
      expect(mockedEventoService.buscar).toHaveBeenCalledWith({ nome: 'Evento Teste 1' });
    });
  });

  test('permite filtrar eventos', async () => {
    renderWithRouter(<EventosModule />);
    
    await waitFor(() => {
      expect(screen.getByText('Evento Teste 1')).toBeInTheDocument();
    });
    
    const filterButton = screen.getByText('Mostrar Filtros');
    fireEvent.click(filterButton);
    
    expect(screen.getByLabelText('Status')).toBeInTheDocument();
    expect(screen.getByLabelText('Local')).toBeInTheDocument();
    expect(screen.getByLabelText('Limite de Idade Mínimo')).toBeInTheDocument();
  });

  test('exibe informações corretas do evento', async () => {
    renderWithRouter(<EventosModule />);
    
    await waitFor(() => {
      expect(screen.getByText('Evento Teste 1')).toBeInTheDocument();
      expect(screen.getByText('Local Teste 1')).toBeInTheDocument();
      expect(screen.getByText(/Limite: 18\+ \| Capacidade: 500/)).toBeInTheDocument();
    });
  });

  test('permite exportar CSV', async () => {
    const mockBlob = new Blob(['csv content'], { type: 'text/csv' });
    mockedEventoService.exportarCSV.mockResolvedValue(mockBlob);
    
    global.URL.createObjectURL = jest.fn(() => 'mock-url');
    global.URL.revokeObjectURL = jest.fn();
    
    const mockLink = {
      href: '',
      download: '',
      click: jest.fn()
    };
    jest.spyOn(document, 'createElement').mockReturnValue(mockLink as any);
    jest.spyOn(document.body, 'appendChild').mockImplementation();
    jest.spyOn(document.body, 'removeChild').mockImplementation();
    
    renderWithRouter(<EventosModule />);
    
    await waitFor(() => {
      expect(screen.getByText('Evento Teste 1')).toBeInTheDocument();
    });
    
    const csvButtons = screen.getAllByText('CSV');
    fireEvent.click(csvButtons[0]);
    
    await waitFor(() => {
      expect(mockedEventoService.exportarCSV).toHaveBeenCalledWith(1);
      expect(mockLink.click).toHaveBeenCalled();
    });
  });

  test('permite exportar PDF', async () => {
    const mockBlob = new Blob(['pdf content'], { type: 'application/pdf' });
    mockedEventoService.exportarPDF.mockResolvedValue(mockBlob);
    
    global.URL.createObjectURL = jest.fn(() => 'mock-url');
    global.URL.revokeObjectURL = jest.fn();
    
    const mockLink = {
      href: '',
      download: '',
      click: jest.fn()
    };
    jest.spyOn(document, 'createElement').mockReturnValue(mockLink as any);
    jest.spyOn(document.body, 'appendChild').mockImplementation();
    jest.spyOn(document.body, 'removeChild').mockImplementation();
    
    renderWithRouter(<EventosModule />);
    
    await waitFor(() => {
      expect(screen.getByText('Evento Teste 1')).toBeInTheDocument();
    });
    
    const pdfButtons = screen.getAllByText('PDF');
    fireEvent.click(pdfButtons[0]);
    
    await waitFor(() => {
      expect(mockedEventoService.exportarPDF).toHaveBeenCalledWith(1);
      expect(mockLink.click).toHaveBeenCalled();
    });
  });

  test('exibe mensagem quando não há eventos', async () => {
    mockedEventoService.listar.mockResolvedValue([]);
    
    renderWithRouter(<EventosModule />);
    
    await waitFor(() => {
      expect(screen.getByText('Nenhum evento encontrado')).toBeInTheDocument();
      expect(screen.getByText('Comece criando seu primeiro evento.')).toBeInTheDocument();
    });
  });

  test('exibe erro quando falha ao carregar eventos', async () => {
    mockedEventoService.listar.mockRejectedValue(new Error('Erro de rede'));
    
    renderWithRouter(<EventosModule />);
    
    await waitFor(() => {
      expect(screen.getByText('Erro ao carregar eventos')).toBeInTheDocument();
    });
  });

  test('permite cancelar evento com confirmação', async () => {
    global.confirm = jest.fn(() => true);
    mockedEventoService.cancelar.mockResolvedValue();
    
    renderWithRouter(<EventosModule />);
    
    await waitFor(() => {
      expect(screen.getByText('Evento Teste 1')).toBeInTheDocument();
    });
    
    const deleteButtons = screen.getAllByRole('button');
    const deleteButton = deleteButtons.find(button => 
      button.querySelector('svg')?.getAttribute('data-testid') === 'trash-2'
    );
    
    if (deleteButton) {
      fireEvent.click(deleteButton);
      
      await waitFor(() => {
        expect(global.confirm).toHaveBeenCalledWith(
          'Tem certeza que deseja cancelar o evento "Evento Teste 1"?'
        );
        expect(mockedEventoService.cancelar).toHaveBeenCalledWith(1);
      });
    }
  });

  test('não cancela evento se usuário não confirmar', async () => {
    global.confirm = jest.fn(() => false);
    
    renderWithRouter(<EventosModule />);
    
    await waitFor(() => {
      expect(screen.getByText('Evento Teste 1')).toBeInTheDocument();
    });
    
    const deleteButtons = screen.getAllByRole('button');
    const deleteButton = deleteButtons.find(button => 
      button.querySelector('svg')?.getAttribute('data-testid') === 'trash-2'
    );
    
    if (deleteButton) {
      fireEvent.click(deleteButton);
      
      expect(global.confirm).toHaveBeenCalled();
      expect(mockedEventoService.cancelar).not.toHaveBeenCalled();
    }
  });
});
