import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Alert, AlertDescription } from '../ui/alert';
import { Evento, EventoCreate } from '../../services/api';

interface EventoModalProps {
  evento?: Evento | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (evento: EventoCreate) => void;
}

const EventoModal: React.FC<EventoModalProps> = ({
  evento,
  isOpen,
  onClose,
  onSave
}) => {
  const [formData, setFormData] = useState<EventoCreate>({
    nome: '',
    descricao: '',
    data_evento: '',
    local: '',
    endereco: '',
    limite_idade: 18,
    capacidade_maxima: 100,
    empresa_id: 1
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (evento) {
      setFormData({
        nome: evento.nome,
        descricao: evento.descricao || '',
        data_evento: new Date(evento.data_evento).toISOString().slice(0, 16),
        local: evento.local,
        endereco: evento.endereco || '',
        limite_idade: evento.limite_idade,
        capacidade_maxima: evento.capacidade_maxima,
        empresa_id: evento.empresa_id
      });
    } else {
      setFormData({
        nome: '',
        descricao: '',
        data_evento: '',
        local: '',
        endereco: '',
        limite_idade: 18,
        capacidade_maxima: 100,
        empresa_id: 1
      });
    }
    setErrors({});
  }, [evento, isOpen]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.nome.trim()) {
      newErrors.nome = 'Nome é obrigatório';
    }

    if (!formData.data_evento) {
      newErrors.data_evento = 'Data do evento é obrigatória';
    } else {
      const dataEvento = new Date(formData.data_evento);
      const agora = new Date();
      if (dataEvento <= agora) {
        newErrors.data_evento = 'Data do evento deve ser futura';
      }
    }

    if (!formData.local.trim()) {
      newErrors.local = 'Local é obrigatório';
    }

    if (formData.limite_idade < 0 || formData.limite_idade > 100) {
      newErrors.limite_idade = 'Limite de idade deve estar entre 0 e 100';
    }

    if (formData.capacidade_maxima < 1) {
      newErrors.capacidade_maxima = 'Capacidade deve ser maior que 0';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      const eventoData = {
        ...formData,
        data_evento: new Date(formData.data_evento).toISOString()
      };
      
      await onSave(eventoData);
    } catch (error) {
      console.error('Erro ao salvar evento:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof EventoCreate, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {evento ? 'Editar Evento' : 'Novo Evento'}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <Label htmlFor="nome">Nome do Evento *</Label>
              <Input
                id="nome"
                value={formData.nome}
                onChange={(e) => handleInputChange('nome', e.target.value)}
                placeholder="Ex: Festa de Ano Novo 2025"
                className={errors.nome ? 'border-red-500' : ''}
              />
              {errors.nome && (
                <p className="text-sm text-red-500 mt-1">{errors.nome}</p>
              )}
            </div>

            <div>
              <Label htmlFor="data_evento">Data e Hora *</Label>
              <Input
                id="data_evento"
                type="datetime-local"
                value={formData.data_evento}
                onChange={(e) => handleInputChange('data_evento', e.target.value)}
                className={errors.data_evento ? 'border-red-500' : ''}
              />
              {errors.data_evento && (
                <p className="text-sm text-red-500 mt-1">{errors.data_evento}</p>
              )}
            </div>

            <div>
              <Label htmlFor="local">Local *</Label>
              <Input
                id="local"
                value={formData.local}
                onChange={(e) => handleInputChange('local', e.target.value)}
                placeholder="Ex: Club Premium"
                className={errors.local ? 'border-red-500' : ''}
              />
              {errors.local && (
                <p className="text-sm text-red-500 mt-1">{errors.local}</p>
              )}
            </div>

            <div className="md:col-span-2">
              <Label htmlFor="endereco">Endereço</Label>
              <Input
                id="endereco"
                value={formData.endereco}
                onChange={(e) => handleInputChange('endereco', e.target.value)}
                placeholder="Ex: Rua das Flores, 123 - Centro"
              />
            </div>

            <div>
              <Label htmlFor="limite_idade">Limite de Idade *</Label>
              <Input
                id="limite_idade"
                type="number"
                min="0"
                max="100"
                value={formData.limite_idade}
                onChange={(e) => handleInputChange('limite_idade', parseInt(e.target.value) || 0)}
                className={errors.limite_idade ? 'border-red-500' : ''}
              />
              {errors.limite_idade && (
                <p className="text-sm text-red-500 mt-1">{errors.limite_idade}</p>
              )}
            </div>

            <div>
              <Label htmlFor="capacidade_maxima">Capacidade Máxima *</Label>
              <Input
                id="capacidade_maxima"
                type="number"
                min="1"
                value={formData.capacidade_maxima}
                onChange={(e) => handleInputChange('capacidade_maxima', parseInt(e.target.value) || 0)}
                className={errors.capacidade_maxima ? 'border-red-500' : ''}
              />
              {errors.capacidade_maxima && (
                <p className="text-sm text-red-500 mt-1">{errors.capacidade_maxima}</p>
              )}
            </div>

            <div className="md:col-span-2">
              <Label htmlFor="descricao">Descrição</Label>
              <Textarea
                id="descricao"
                value={formData.descricao}
                onChange={(e) => handleInputChange('descricao', e.target.value)}
                placeholder="Descreva o evento..."
                rows={3}
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={loading}
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              disabled={loading}
            >
              {loading ? 'Salvando...' : (evento ? 'Atualizar' : 'Criar')}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default EventoModal;
