import React, { useState, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ChevronRightIcon, 
  ChevronLeftIcon, 
  CalendarIcon,
  MapPinIcon,
  PhotoIcon,
  CogIcon,
  PaintBrushIcon,
  BoltIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';

interface EventFormData {
  // Dados básicos
  nome: string;
  descricao: string;
  tipo_evento: string;
  status: string;
  
  // Dados temporais
  data_inicio: string;
  data_fim: string;
  data_inicio_checkin: string;
  data_fim_checkin: string;
  
  // Localização
  local_nome: string;
  local_endereco: string;
  local_coordenadas?: { lat: number; lng: number };
  capacidade_maxima?: number;
  
  // Configurações visuais
  cor_primaria: string;
  cor_secundaria: string;
  cor_accent: string;
  logo_url?: string;
  banner_url?: string;
  background_url?: string;
  template_layout: string;
  custom_css?: string;
  brand_fonts?: any;
  
  // Sistema de templates
  template_id?: string;
  template_customizations?: any;
  
  // Configurações funcionais
  permite_checkin_antecipado: boolean;
  requer_confirmacao: boolean;
  requer_aprovacao: boolean;
  limite_participantes?: number;
  valor_entrada: number;
  moeda: string;
  
  // Configurações de acesso
  visibilidade: string;
  senha_acesso?: string;
  dominios_permitidos?: string[];
  
  // Gamificação
  sistema_pontuacao_ativo: boolean;
  pontos_checkin: number;
  pontos_participacao: number;
  badges_personalizadas?: any[];
  
  // QR Code
  qr_code_style?: any;
  qr_code_expires_at?: string;
  
  // Webhooks
  webhook_checkin?: string;
  webhook_checkout?: string;
  webhook_pagamento?: string;
  webhook_cancelamento?: string;
  webhook_headers?: any;
  
  // Email templates
  email_confirmacao_template?: string;
  email_lembrete_template?: string;
  email_checkin_template?: string;
  email_pos_evento_template?: string;
  email_cancelamento_template?: string;
  email_sender_name?: string;
  email_sender_email?: string;
  
  // Integrações
  integracao_google_calendar?: any;
  integracao_facebook_event?: any;
  integracao_eventbrite?: any;
  integracao_zoom?: any;
  integracao_youtube?: any;
  
  // Analytics
  analytics_config?: any;
  metricas_personalizadas?: any[];
  
  // SEO
  metadados_seo?: any;
  dados_estruturados?: any;
  
  // Configurações de API
  api_rate_limit: number;
  
  // Metadados
  tags?: string[];
  configuracoes_extras?: any;
  notas_internas?: string;
}

interface Step {
  id: string;
  title: string;
  description: string;
  icon: React.ElementType;
  component: React.ComponentType<any>;
}

const EventCreationWizard: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState<EventFormData>({
    // Valores padrão
    nome: '',
    descricao: '',
    tipo_evento: 'festa',
    status: 'planejamento',
    data_inicio: '',
    data_fim: '',
    data_inicio_checkin: '',
    data_fim_checkin: '',
    local_nome: '',
    local_endereco: '',
    capacidade_maxima: undefined,
    cor_primaria: '#0EA5E9',
    cor_secundaria: '#64748B',
    cor_accent: '#10B981',
    template_layout: 'default',
    permite_checkin_antecipado: false,
    requer_confirmacao: true,
    requer_aprovacao: false,
    valor_entrada: 0,
    moeda: 'BRL',
    visibilidade: 'publico',
    sistema_pontuacao_ativo: false,
    pontos_checkin: 10,
    pontos_participacao: 5,
    api_rate_limit: 1000,
    tags: []
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Componente para Dados Básicos
  const BasicInfoStep: React.FC<any> = ({ formData, setFormData, errors }) => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Nome do Evento *
          </label>
          <input
            type="text"
            value={formData.nome}
            onChange={(e) => setFormData({...formData, nome: e.target.value})}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.nome ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Digite o nome do evento"
          />
          {errors.nome && <p className="text-red-500 text-sm mt-1">{errors.nome}</p>}
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tipo de Evento *
          </label>
          <select
            value={formData.tipo_evento}
            onChange={(e) => setFormData({...formData, tipo_evento: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="festa">Festa</option>
            <option value="show">Show</option>
            <option value="conferencia">Conferência</option>
            <option value="workshop">Workshop</option>
            <option value="networking">Networking</option>
            <option value="corporativo">Corporativo</option>
            <option value="casamento">Casamento</option>
            <option value="aniversario">Aniversário</option>
            <option value="outro">Outro</option>
          </select>
        </div>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Descrição do Evento
        </label>
        <ReactQuill
          theme="snow"
          value={formData.descricao}
          onChange={(value) => setFormData({...formData, descricao: value})}
          modules={{
            toolbar: [
              [{ 'header': [1, 2, false] }],
              ['bold', 'italic', 'underline', 'strike'],
              [{'list': 'ordered'}, {'list': 'bullet'}],
              ['link', 'image'],
              ['clean']
            ],
          }}
          className="bg-white"
        />
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Capacidade Máxima
          </label>
          <input
            type="number"
            value={formData.capacidade_maxima || ''}
            onChange={(e) => setFormData({...formData, capacidade_maxima: e.target.value ? parseInt(e.target.value) : undefined})}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Ex: 500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Valor da Entrada
          </label>
          <div className="flex">
            <span className="inline-flex items-center px-3 rounded-l-lg border border-r-0 border-gray-300 bg-gray-50 text-gray-500">
              R$
            </span>
            <input
              type="number"
              step="0.01"
              value={formData.valor_entrada}
              onChange={(e) => setFormData({...formData, valor_entrada: parseFloat(e.target.value) || 0})}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-r-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="0.00"
            />
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Visibilidade
          </label>
          <select
            value={formData.visibilidade}
            onChange={(e) => setFormData({...formData, visibilidade: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="publico">Público</option>
            <option value="privado">Privado</option>
            <option value="restrito">Restrito</option>
          </select>
        </div>
      </div>
      
      <div className="space-y-4">
        <h4 className="font-medium text-gray-900">Configurações</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.permite_checkin_antecipado}
              onChange={(e) => setFormData({...formData, permite_checkin_antecipado: e.target.checked})}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span className="text-sm text-gray-700">Permitir check-in antecipado</span>
          </label>
          
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.requer_confirmacao}
              onChange={(e) => setFormData({...formData, requer_confirmacao: e.target.checked})}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span className="text-sm text-gray-700">Requer confirmação</span>
          </label>
          
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.requer_aprovacao}
              onChange={(e) => setFormData({...formData, requer_aprovacao: e.target.checked})}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span className="text-sm text-gray-700">Requer aprovação</span>
          </label>
          
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.sistema_pontuacao_ativo}
              onChange={(e) => setFormData({...formData, sistema_pontuacao_ativo: e.target.checked})}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span className="text-sm text-gray-700">Sistema de pontuação</span>
          </label>
        </div>
      </div>
    </div>
  );

  // Componente para Data e Local
  const DateLocationStep: React.FC<any> = ({ formData, setFormData, errors }) => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Data e Hora de Início *
          </label>
          <input
            type="datetime-local"
            value={formData.data_inicio}
            onChange={(e) => setFormData({...formData, data_inicio: e.target.value})}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.data_inicio ? 'border-red-500' : 'border-gray-300'
            }`}
          />
          {errors.data_inicio && <p className="text-red-500 text-sm mt-1">{errors.data_inicio}</p>}
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Data e Hora de Fim *
          </label>
          <input
            type="datetime-local"
            value={formData.data_fim}
            onChange={(e) => setFormData({...formData, data_fim: e.target.value})}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.data_fim ? 'border-red-500' : 'border-gray-300'
            }`}
          />
          {errors.data_fim && <p className="text-red-500 text-sm mt-1">{errors.data_fim}</p>}
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Início do Check-in
          </label>
          <input
            type="datetime-local"
            value={formData.data_inicio_checkin}
            onChange={(e) => setFormData({...formData, data_inicio_checkin: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Fim do Check-in
          </label>
          <input
            type="datetime-local"
            value={formData.data_fim_checkin}
            onChange={(e) => setFormData({...formData, data_fim_checkin: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Nome do Local *
        </label>
        <input
          type="text"
          value={formData.local_nome}
          onChange={(e) => setFormData({...formData, local_nome: e.target.value})}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.local_nome ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="Ex: Centro de Convenções ABC"
        />
        {errors.local_nome && <p className="text-red-500 text-sm mt-1">{errors.local_nome}</p>}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Endereço Completo *
        </label>
        <textarea
          value={formData.local_endereco}
          onChange={(e) => setFormData({...formData, local_endereco: e.target.value})}
          rows={3}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.local_endereco ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="Rua, número, bairro, cidade, CEP"
        />
        {errors.local_endereco && <p className="text-red-500 text-sm mt-1">{errors.local_endereco}</p>}
      </div>
    </div>
  );

  // Componente para Branding Visual
  const BrandingStep: React.FC<any> = ({ formData, setFormData, uploadedFiles, setUploadedFiles, fileInputRef }) => {
    const handleFileUpload = useCallback(async (files: FileList | null, category: string) => {
      if (!files || files.length === 0) return;
      
      const formData = new FormData();
      Array.from(files).forEach(file => {
        formData.append('files', file);
      });
      formData.append('category', category);
      
      try {
        // Simular upload - implementar chamada real para API
        const newFiles = Array.from(files).map(file => ({
          name: file.name,
          size: file.size,
          type: file.type,
          category,
          url: URL.createObjectURL(file),
          uploaded: false
        }));
        
        setUploadedFiles(prev => [...prev, ...newFiles]);
        
        // Atualizar URLs no formData baseado na categoria
        if (category === 'logo' && newFiles.length > 0) {
          setFormData(prev => ({...prev, logo_url: newFiles[0].url}));
        } else if (category === 'banner' && newFiles.length > 0) {
          setFormData(prev => ({...prev, banner_url: newFiles[0].url}));
        }
        
      } catch (error) {
        console.error('Erro no upload:', error);
      }
    }, [setFormData, setUploadedFiles]);
    
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Cor Primária
            </label>
            <div className="flex space-x-2">
              <input
                type="color"
                value={formData.cor_primaria}
                onChange={(e) => setFormData({...formData, cor_primaria: e.target.value})}
                className="h-10 w-20 border border-gray-300 rounded-lg cursor-pointer"
              />
              <input
                type="text"
                value={formData.cor_primaria}
                onChange={(e) => setFormData({...formData, cor_primaria: e.target.value})}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="#0EA5E9"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Cor Secundária
            </label>
            <div className="flex space-x-2">
              <input
                type="color"
                value={formData.cor_secundaria}
                onChange={(e) => setFormData({...formData, cor_secundaria: e.target.value})}
                className="h-10 w-20 border border-gray-300 rounded-lg cursor-pointer"
              />
              <input
                type="text"
                value={formData.cor_secundaria}
                onChange={(e) => setFormData({...formData, cor_secundaria: e.target.value})}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="#64748B"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Cor de Destaque
            </label>
            <div className="flex space-x-2">
              <input
                type="color"
                value={formData.cor_accent}
                onChange={(e) => setFormData({...formData, cor_accent: e.target.value})}
                className="h-10 w-20 border border-gray-300 rounded-lg cursor-pointer"
              />
              <input
                type="text"
                value={formData.cor_accent}
                onChange={(e) => setFormData({...formData, cor_accent: e.target.value})}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="#10B981"
              />
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Logo do Evento
            </label>
            <div 
              className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:border-blue-400 transition-colors"
              onClick={() => {
                const input = document.createElement('input');
                input.type = 'file';
                input.accept = 'image/*';
                input.onchange = (e) => handleFileUpload((e.target as HTMLInputElement).files, 'logo');
                input.click();
              }}
            >
              {formData.logo_url ? (
                <div>
                  <img src={formData.logo_url} alt="Logo" className="max-h-20 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">Clique para alterar</p>
                </div>
              ) : (
                <div>
                  <PhotoIcon className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">Clique para fazer upload do logo</p>
                </div>
              )}
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Banner do Evento
            </label>
            <div 
              className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:border-blue-400 transition-colors"
              onClick={() => {
                const input = document.createElement('input');
                input.type = 'file';
                input.accept = 'image/*';
                input.onchange = (e) => handleFileUpload((e.target as HTMLInputElement).files, 'banner');
                input.click();
              }}
            >
              {formData.banner_url ? (
                <div>
                  <img src={formData.banner_url} alt="Banner" className="max-h-20 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">Clique para alterar</p>
                </div>
              ) : (
                <div>
                  <PhotoIcon className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">Clique para fazer upload do banner</p>
                </div>
              )}
            </div>
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Template Layout
          </label>
          <select
            value={formData.template_layout}
            onChange={(e) => setFormData({...formData, template_layout: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="default">Padrão</option>
            <option value="modern">Moderno</option>
            <option value="elegant">Elegante</option>
            <option value="corporate">Corporativo</option>
            <option value="creative">Criativo</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            CSS Personalizado
          </label>
          <textarea
            value={formData.custom_css || ''}
            onChange={(e) => setFormData({...formData, custom_css: e.target.value})}
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
            placeholder="/* Adicione seu CSS personalizado aqui */"
          />
          <p className="text-sm text-gray-500 mt-1">
            Use CSS válido para personalizar a aparência do seu evento
          </p>
        </div>
      </div>
    );
  };

  // Componente de Revisão e Configurações Finais
  const ReviewStep: React.FC<any> = ({ formData, setFormData }) => (
    <div className="space-y-6">
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Resumo do Evento</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Informações Básicas</h4>
            <div className="space-y-2 text-sm">
              <p><span className="font-medium">Nome:</span> {formData.nome}</p>
              <p><span className="font-medium">Tipo:</span> {formData.tipo_evento}</p>
              <p><span className="font-medium">Capacidade:</span> {formData.capacidade_maxima || 'Ilimitada'}</p>
              <p><span className="font-medium">Valor:</span> R$ {formData.valor_entrada.toFixed(2)}</p>
            </div>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Data e Local</h4>
            <div className="space-y-2 text-sm">
              <p><span className="font-medium">Início:</span> {new Date(formData.data_inicio).toLocaleString('pt-BR')}</p>
              <p><span className="font-medium">Fim:</span> {new Date(formData.data_fim).toLocaleString('pt-BR')}</p>
              <p><span className="font-medium">Local:</span> {formData.local_nome}</p>
            </div>
          </div>
        </div>
        
        {formData.descricao && (
          <div className="mt-4">
            <h4 className="font-medium text-gray-900 mb-2">Descrição</h4>
            <div 
              className="text-sm text-gray-600"
              dangerouslySetInnerHTML={{__html: formData.descricao}}
            />
          </div>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Tags do Evento
        </label>
        <input
          type="text"
          value={formData.tags?.join(', ') || ''}
          onChange={(e) => setFormData({
            ...formData, 
            tags: e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag)
          })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="festa, música, networking (separadas por vírgula)"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Notas Internas
        </label>
        <textarea
          value={formData.notas_internas || ''}
          onChange={(e) => setFormData({...formData, notas_internas: e.target.value})}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Notas internas para a equipe organizadora..."
        />
      </div>
    </div>
  );

  const steps: Step[] = [
    {
      id: 'basic',
      title: 'Dados Básicos',
      description: 'Nome, tipo e configurações iniciais',
      icon: CogIcon,
      component: BasicInfoStep
    },
    {
      id: 'datetime',
      title: 'Data e Local',
      description: 'Quando e onde será o evento',
      icon: CalendarIcon,
      component: DateLocationStep
    },
    {
      id: 'branding',
      title: 'Visual e Branding',
      description: 'Cores, logo e personalização visual',
      icon: PaintBrushIcon,
      component: BrandingStep
    },
    {
      id: 'review',
      title: 'Revisão',
      description: 'Conferir e finalizar configurações',
      icon: CheckCircleIcon,
      component: ReviewStep
    }
  ];

  const validateStep = (stepIndex: number): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (stepIndex === 0) {
      // Validar dados básicos
      if (!formData.nome.trim()) {
        newErrors.nome = 'Nome do evento é obrigatório';
      }
    } else if (stepIndex === 1) {
      // Validar data e local
      if (!formData.data_inicio) {
        newErrors.data_inicio = 'Data de início é obrigatória';
      }
      if (!formData.data_fim) {
        newErrors.data_fim = 'Data de fim é obrigatória';
      }
      if (formData.data_inicio && formData.data_fim && formData.data_fim <= formData.data_inicio) {
        newErrors.data_fim = 'Data de fim deve ser posterior à data de início';
      }
      if (!formData.local_nome.trim()) {
        newErrors.local_nome = 'Nome do local é obrigatório';
      }
      if (!formData.local_endereco.trim()) {
        newErrors.local_endereco = 'Endereço é obrigatório';
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
    }
  };

  const handlePrevious = () => {
    setCurrentStep(prev => Math.max(prev - 1, 0));
  };

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) return;
    
    setIsLoading(true);
    try {
      // Implementar submissão para API
      console.log('Dados do evento:', formData);
      
      // Simular delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Redirecionar ou mostrar sucesso
      alert('Evento criado com sucesso!');
      
    } catch (error) {
      console.error('Erro ao criar evento:', error);
      alert('Erro ao criar evento. Tente novamente.');
    } finally {
      setIsLoading(false);
    }
  };

  const CurrentStepComponent = steps[currentStep].component;

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-lg overflow-hidden">
      {/* Header com progresso */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
        <h1 className="text-2xl font-bold mb-4">Criar Novo Evento</h1>
        
        {/* Progress bar */}
        <div className="flex items-center space-x-4">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={step.id} className="flex items-center">
                <div className={`
                  flex items-center justify-center w-8 h-8 rounded-full border-2 transition-colors
                  ${index <= currentStep 
                    ? 'bg-white text-blue-600 border-white' 
                    : 'border-white/50 text-white/50'
                  }
                `}>
                  {index < currentStep ? (
                    <CheckCircleIcon className="w-5 h-5" />
                  ) : (
                    <Icon className="w-4 h-4" />
                  )}
                </div>
                {index < steps.length - 1 && (
                  <div className={`
                    w-12 h-0.5 mx-2 transition-colors
                    ${index < currentStep ? 'bg-white' : 'bg-white/30'}
                  `} />
                )}
              </div>
            );
          })}
        </div>
        
        <div className="mt-4">
          <h2 className="text-lg font-semibold">{steps[currentStep].title}</h2>
          <p className="text-blue-100">{steps[currentStep].description}</p>
        </div>
      </div>

      {/* Conteúdo do step atual */}
      <div className="p-6">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            <CurrentStepComponent
              formData={formData}
              setFormData={setFormData}
              errors={errors}
              uploadedFiles={uploadedFiles}
              setUploadedFiles={setUploadedFiles}
              fileInputRef={fileInputRef}
            />
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Botões de navegação */}
      <div className="flex justify-between items-center p-6 bg-gray-50 border-t">
        <button
          onClick={handlePrevious}
          disabled={currentStep === 0}
          className={`
            flex items-center px-4 py-2 rounded-lg font-medium transition-colors
            ${currentStep === 0
              ? 'text-gray-400 cursor-not-allowed'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200'
            }
          `}
        >
          <ChevronLeftIcon className="w-4 h-4 mr-1" />
          Anterior
        </button>
        
        {currentStep < steps.length - 1 ? (
          <button
            onClick={handleNext}
            className="flex items-center px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Próximo
            <ChevronRightIcon className="w-4 h-4 ml-1" />
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={isLoading}
            className={`
              flex items-center px-6 py-2 rounded-lg font-medium transition-colors
              ${isLoading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700'
              } text-white
            `}
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Criando...
              </>
            ) : (
              <>
                <BoltIcon className="w-4 h-4 mr-1" />
                Criar Evento
              </>
            )}
          </button>
        )}
      </div>
      
      <input
        type="file"
        ref={fileInputRef}
        className="hidden"
        multiple
        accept="image/*"
      />
    </div>
  );
};

export default EventCreationWizard;