/**
 * PaymentLinkCreator - Advanced form with live preview for creating payment links
 * Sistema Universal de Gestão de Eventos
 */

import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft, 
  Eye, 
  Palette, 
  Settings, 
  Link as LinkIcon,
  DollarSign,
  Calendar,
  Users,
  Webhook,
  Smartphone,
  Save,
  AlertCircle,
  CheckCircle2,
  Copy,
  QrCode,
  Split,
  Trash2,
  Plus
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { Progress } from '@/components/ui/progress';

import { 
  PaymentLinkCreate,
  PaymentLinkFormData,
  PaymentType,
  LinkTheme,
  SplitRecipient,
  PreviewSettings,
  THEME_PRESETS
} from '@/types/payment-links';

interface PaymentLinkCreatorProps {
  initialData?: PaymentLinkFormData;
  onSubmit: (data: PaymentLinkFormData) => Promise<void>;
  onCancel: () => void;
  loading?: boolean;
  mode: 'create' | 'edit';
}

const PaymentLinkCreator: React.FC<PaymentLinkCreatorProps> = ({
  initialData,
  onSubmit,
  onCancel,
  loading = false,
  mode
}) => {
  // Form state
  const [formData, setFormData] = useState<PaymentLinkFormData>({
    title: '',
    description: '',
    payment_type: PaymentType.SINGLE,
    currency: 'BRL',
    theme: LinkTheme.DEFAULT,
    collect_customer_info: true,
    send_receipt: true,
    enable_split: false,
    split_recipients: [],
    ...initialData
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [previewMode, setPreviewMode] = useState<'desktop' | 'mobile'>('desktop');
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    { id: 'basic', title: 'Informações Básicas', icon: LinkIcon },
    { id: 'payment', title: 'Configurações de Pagamento', icon: DollarSign },
    { id: 'design', title: 'Personalização', icon: Palette },
    { id: 'advanced', title: 'Configurações Avançadas', icon: Settings }
  ];

  useEffect(() => {
    if (initialData) {
      setFormData({ ...formData, ...initialData });
    }
  }, [initialData]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title?.trim()) {
      newErrors.title = 'Título é obrigatório';
    }

    if (formData.payment_type === PaymentType.SINGLE && !formData.amount) {
      newErrors.amount = 'Valor é obrigatório para pagamento único';
    }

    if (formData.payment_type === PaymentType.FLEXIBLE) {
      if (formData.min_amount && formData.max_amount && formData.min_amount >= formData.max_amount) {
        newErrors.max_amount = 'Valor máximo deve ser maior que o mínimo';
      }
    }

    if (formData.enable_split && (!formData.split_recipients || formData.split_recipients.length === 0)) {
      newErrors.split_recipients = 'Adicione pelo menos um destinatário para split';
    }

    if (formData.webhook_url && !isValidUrl(formData.webhook_url)) {
      newErrors.webhook_url = 'URL do webhook inválida';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const isValidUrl = (url: string): boolean => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      setSubmitError(null);
      
      // Prepare form data
      const submitData: PaymentLinkCreate = {
        ...formData,
        expires_at: formData.expiry_date ? 
          new Date(formData.expiry_date).toISOString() : undefined
      };

      await onSubmit(submitData);
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'Erro ao salvar link');
    }
  };

  const handleFieldChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when field is updated
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const addSplitRecipient = () => {
    const newRecipient: SplitRecipient = {
      recipient_id: '',
      account_id: '',
      name: '',
      document: '',
      split_type: 'percentage',
      percentage: 0
    };

    setFormData(prev => ({
      ...prev,
      split_recipients: [...(prev.split_recipients || []), newRecipient]
    }));
  };

  const updateSplitRecipient = (index: number, field: keyof SplitRecipient, value: any) => {
    setFormData(prev => ({
      ...prev,
      split_recipients: prev.split_recipients?.map((recipient, i) => 
        i === index ? { ...recipient, [field]: value } : recipient
      )
    }));
  };

  const removeSplitRecipient = (index: number) => {
    setFormData(prev => ({
      ...prev,
      split_recipients: prev.split_recipients?.filter((_, i) => i !== index)
    }));
  };

  const getFormProgress = (): number => {
    let completed = 0;
    let total = 0;

    // Basic info (required fields)
    total += 2;
    if (formData.title) completed += 1;
    if (formData.payment_type) completed += 1;

    // Payment settings
    total += 1;
    if (formData.payment_type === PaymentType.SINGLE && formData.amount) completed += 1;
    else if (formData.payment_type === PaymentType.FLEXIBLE) completed += 1;
    else if (formData.payment_type === PaymentType.RECURRING) completed += 1;

    // Optional but common fields
    total += 3;
    if (formData.description) completed += 1;
    if (formData.theme !== LinkTheme.DEFAULT) completed += 1;
    if (formData.webhook_url) completed += 1;

    return Math.round((completed / total) * 100);
  };

  const renderPreview = () => {
    const previewData: PreviewSettings = {
      theme: formData.theme || LinkTheme.DEFAULT,
      title: formData.title || 'Título do Link',
      description: formData.description,
      amount: formData.amount,
      min_amount: formData.min_amount,
      max_amount: formData.max_amount,
      payment_type: formData.payment_type,
      collect_customer_info: formData.collect_customer_info || false,
      allow_installments: formData.allow_installments || false
    };

    const themeStyle = THEME_PRESETS[previewData.theme];

    return (
      <div className={`${previewMode === 'mobile' ? 'max-w-sm' : 'max-w-md'} mx-auto`}>
        <div 
          className="p-6 rounded-lg shadow-lg"
          style={{
            backgroundColor: themeStyle.background_color,
            color: themeStyle.text_color,
            fontFamily: themeStyle.font_family
          }}
        >
          {formData.logo_url && (
            <div className="text-center mb-4">
              <img 
                src={formData.logo_url} 
                alt="Logo" 
                className="h-12 mx-auto rounded"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = 'none';
                }}
              />
            </div>
          )}

          <h2 className="text-xl font-bold text-center mb-2" style={{ color: themeStyle.text_color }}>
            {previewData.title}
          </h2>

          {previewData.description && (
            <p className="text-center text-sm mb-4 opacity-80">
              {previewData.description}
            </p>
          )}

          <div className="bg-white bg-opacity-10 p-4 rounded mb-4">
            {previewData.payment_type === PaymentType.FLEXIBLE ? (
              <div>
                <Label className="text-sm">Valor do pagamento:</Label>
                <Input 
                  type="number" 
                  placeholder={`Min: R$ ${previewData.min_amount || 0} - Max: R$ ${previewData.max_amount || 999999}`}
                  className="mt-1"
                />
              </div>
            ) : (
              <div className="text-center">
                <div className="text-2xl font-bold" style={{ color: themeStyle.primary_color }}>
                  R$ {(previewData.amount || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </div>
              </div>
            )}
          </div>

          {previewData.collect_customer_info && (
            <div className="space-y-3 mb-4">
              <Input placeholder="Nome completo" />
              <Input placeholder="Email" />
            </div>
          )}

          <div className="space-y-2 mb-4">
            <Label className="flex items-center space-x-2">
              <input type="radio" name="payment_method" defaultChecked />
              <span>PIX</span>
            </Label>
            <Label className="flex items-center space-x-2">
              <input type="radio" name="payment_method" />
              <span>Cartão de Crédito/Débito</span>
              {previewData.allow_installments && (
                <Badge variant="secondary" className="text-xs">Parcelável</Badge>
              )}
            </Label>
          </div>

          <Button 
            className="w-full"
            style={{
              backgroundColor: themeStyle.button_color,
              borderRadius: `${themeStyle.border_radius}px`
            }}
          >
            Pagar {previewData.amount ? `R$ ${previewData.amount.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}` : ''}
          </Button>

          <div className="text-center mt-4 text-xs opacity-60">
            🔒 Pagamento 100% seguro
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" onClick={onCancel}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar
          </Button>
          <div>
            <h1 className="text-2xl font-bold">
              {mode === 'create' ? 'Criar' : 'Editar'} Link de Pagamento
            </h1>
            <div className="flex items-center space-x-2 mt-1">
              <Progress value={getFormProgress()} className="w-32 h-2" />
              <span className="text-sm text-gray-500">{getFormProgress()}% completo</span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            onClick={() => setPreviewMode(previewMode === 'desktop' ? 'mobile' : 'desktop')}
          >
            <Smartphone className="h-4 w-4 mr-2" />
            {previewMode === 'desktop' ? 'Ver Mobile' : 'Ver Desktop'}
          </Button>
          <Button onClick={handleSubmit} disabled={loading}>
            <Save className="h-4 w-4 mr-2" />
            {loading ? 'Salvando...' : mode === 'create' ? 'Criar Link' : 'Salvar Alterações'}
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {submitError && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{submitError}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form Panel */}
        <div className="space-y-6">
          <Tabs defaultValue="basic" className="w-full">
            <TabsList className="grid grid-cols-4 w-full">
              {steps.map((step, index) => {
                const Icon = step.icon;
                return (
                  <TabsTrigger key={step.id} value={step.id} className="text-xs">
                    <Icon className="h-4 w-4 mr-1" />
                    <span className="hidden sm:inline">{step.title}</span>
                  </TabsTrigger>
                );
              })}
            </TabsList>

            {/* Basic Information */}
            <TabsContent value="basic" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Informações Básicas</CardTitle>
                  <CardDescription>Configure as informações fundamentais do seu link</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="title">Título do Link *</Label>
                    <Input
                      id="title"
                      value={formData.title || ''}
                      onChange={(e) => handleFieldChange('title', e.target.value)}
                      placeholder="Ex: Ingresso VIP para o evento"
                      className={errors.title ? 'border-red-500' : ''}
                    />
                    {errors.title && <p className="text-sm text-red-500 mt-1">{errors.title}</p>}
                  </div>

                  <div>
                    <Label htmlFor="description">Descrição</Label>
                    <Textarea
                      id="description"
                      value={formData.description || ''}
                      onChange={(e) => handleFieldChange('description', e.target.value)}
                      placeholder="Descreva o que o cliente está pagando"
                      rows={3}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="expires_at">Data de Expiração</Label>
                      <Input
                        id="expires_at"
                        type="datetime-local"
                        value={formData.expiry_date ? 
                          new Date(formData.expiry_date).toISOString().slice(0, 16) : ''}
                        onChange={(e) => handleFieldChange('expiry_date', new Date(e.target.value))}
                      />
                    </div>

                    <div>
                      <Label htmlFor="max_uses">Limite de Usos</Label>
                      <Input
                        id="max_uses"
                        type="number"
                        value={formData.max_uses || ''}
                        onChange={(e) => handleFieldChange('max_uses', parseInt(e.target.value) || undefined)}
                        placeholder="Ilimitado"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Payment Configuration */}
            <TabsContent value="payment" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Configurações de Pagamento</CardTitle>
                  <CardDescription>Defina os valores e tipos de pagamento</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="payment_type">Tipo de Pagamento</Label>
                    <Select
                      value={formData.payment_type}
                      onValueChange={(value) => handleFieldChange('payment_type', value as PaymentType)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value={PaymentType.SINGLE}>Valor Fixo</SelectItem>
                        <SelectItem value={PaymentType.FLEXIBLE}>Valor Flexível</SelectItem>
                        <SelectItem value={PaymentType.RECURRING}>Recorrente</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {formData.payment_type === PaymentType.SINGLE && (
                    <div>
                      <Label htmlFor="amount">Valor (R$) *</Label>
                      <Input
                        id="amount"
                        type="number"
                        step="0.01"
                        value={formData.amount || ''}
                        onChange={(e) => handleFieldChange('amount', parseFloat(e.target.value) || undefined)}
                        placeholder="0,00"
                        className={errors.amount ? 'border-red-500' : ''}
                      />
                      {errors.amount && <p className="text-sm text-red-500 mt-1">{errors.amount}</p>}
                    </div>
                  )}

                  {formData.payment_type === PaymentType.FLEXIBLE && (
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="min_amount">Valor Mínimo (R$)</Label>
                        <Input
                          id="min_amount"
                          type="number"
                          step="0.01"
                          value={formData.min_amount || ''}
                          onChange={(e) => handleFieldChange('min_amount', parseFloat(e.target.value) || undefined)}
                          placeholder="0,00"
                        />
                      </div>
                      <div>
                        <Label htmlFor="max_amount">Valor Máximo (R$)</Label>
                        <Input
                          id="max_amount"
                          type="number"
                          step="0.01"
                          value={formData.max_amount || ''}
                          onChange={(e) => handleFieldChange('max_amount', parseFloat(e.target.value) || undefined)}
                          placeholder="999999,99"
                          className={errors.max_amount ? 'border-red-500' : ''}
                        />
                        {errors.max_amount && <p className="text-sm text-red-500 mt-1">{errors.max_amount}</p>}
                      </div>
                    </div>
                  )}

                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="allow_installments">Permitir Parcelamento</Label>
                      <p className="text-sm text-gray-500">Habilita parcelamento no cartão de crédito</p>
                    </div>
                    <Switch
                      id="allow_installments"
                      checked={formData.allow_installments || false}
                      onCheckedChange={(checked) => handleFieldChange('allow_installments', checked)}
                    />
                  </div>

                  <Separator />

                  {/* Split Payment Section */}
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="enable_split">Split de Pagamentos</Label>
                        <p className="text-sm text-gray-500">Dividir pagamentos entre múltiplas contas</p>
                      </div>
                      <Switch
                        id="enable_split"
                        checked={formData.enable_split || false}
                        onCheckedChange={(checked) => handleFieldChange('enable_split', checked)}
                      />
                    </div>

                    {formData.enable_split && (
                      <div className="space-y-4 p-4 border rounded-lg">
                        <div className="flex items-center justify-between">
                          <h4 className="font-medium">Destinatários do Split</h4>
                          <Button size="sm" onClick={addSplitRecipient}>
                            <Plus className="h-4 w-4 mr-1" />
                            Adicionar
                          </Button>
                        </div>

                        {formData.split_recipients?.map((recipient, index) => (
                          <div key={index} className="grid grid-cols-12 gap-2 items-end">
                            <div className="col-span-3">
                              <Label className="text-xs">Nome</Label>
                              <Input
                                size="sm"
                                value={recipient.name}
                                onChange={(e) => updateSplitRecipient(index, 'name', e.target.value)}
                                placeholder="Nome"
                              />
                            </div>
                            <div className="col-span-3">
                              <Label className="text-xs">Documento</Label>
                              <Input
                                size="sm"
                                value={recipient.document}
                                onChange={(e) => updateSplitRecipient(index, 'document', e.target.value)}
                                placeholder="CPF/CNPJ"
                              />
                            </div>
                            <div className="col-span-2">
                              <Label className="text-xs">Tipo</Label>
                              <Select
                                value={recipient.split_type}
                                onValueChange={(value) => updateSplitRecipient(index, 'split_type', value)}
                              >
                                <SelectTrigger className="h-8">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="percentage">%</SelectItem>
                                  <SelectItem value="fixed">R$</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>
                            <div className="col-span-2">
                              <Label className="text-xs">Valor</Label>
                              <Input
                                size="sm"
                                type="number"
                                step={recipient.split_type === 'percentage' ? '0.01' : '0.01'}
                                value={recipient.split_type === 'percentage' ? recipient.percentage : recipient.fixed_amount}
                                onChange={(e) => updateSplitRecipient(
                                  index, 
                                  recipient.split_type === 'percentage' ? 'percentage' : 'fixed_amount', 
                                  parseFloat(e.target.value)
                                )}
                                placeholder={recipient.split_type === 'percentage' ? '0.00' : '0,00'}
                              />
                            </div>
                            <div className="col-span-2">
                              <Button 
                                size="sm" 
                                variant="ghost" 
                                onClick={() => removeSplitRecipient(index)}
                                className="h-8 px-2"
                              >
                                <Trash2 className="h-3 w-3" />
                              </Button>
                            </div>
                          </div>
                        ))}

                        {errors.split_recipients && (
                          <p className="text-sm text-red-500">{errors.split_recipients}</p>
                        )}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Design Customization */}
            <TabsContent value="design" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Personalização Visual</CardTitle>
                  <CardDescription>Customize a aparência da página de pagamento</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="theme">Tema</Label>
                    <Select
                      value={formData.theme || LinkTheme.DEFAULT}
                      onValueChange={(value) => handleFieldChange('theme', value as LinkTheme)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value={LinkTheme.DEFAULT}>Padrão</SelectItem>
                        <SelectItem value={LinkTheme.DARK}>Escuro</SelectItem>
                        <SelectItem value={LinkTheme.COLORFUL}>Colorido</SelectItem>
                        <SelectItem value={LinkTheme.MINIMAL}>Minimalista</SelectItem>
                        <SelectItem value={LinkTheme.CUSTOM}>Personalizado</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="logo_url">URL do Logo</Label>
                    <Input
                      id="logo_url"
                      value={formData.logo_url || ''}
                      onChange={(e) => handleFieldChange('logo_url', e.target.value)}
                      placeholder="https://exemplo.com/logo.png"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="success_url">URL de Sucesso</Label>
                      <Input
                        id="success_url"
                        value={formData.success_url || ''}
                        onChange={(e) => handleFieldChange('success_url', e.target.value)}
                        placeholder="https://exemplo.com/sucesso"
                      />
                    </div>
                    <div>
                      <Label htmlFor="cancel_url">URL de Cancelamento</Label>
                      <Input
                        id="cancel_url"
                        value={formData.cancel_url || ''}
                        onChange={(e) => handleFieldChange('cancel_url', e.target.value)}
                        placeholder="https://exemplo.com/cancelado"
                      />
                    </div>
                  </div>

                  {formData.theme === LinkTheme.CUSTOM && (
                    <div>
                      <Label htmlFor="custom_css">CSS Customizado</Label>
                      <Textarea
                        id="custom_css"
                        value={formData.custom_css || ''}
                        onChange={(e) => handleFieldChange('custom_css', e.target.value)}
                        placeholder="/* Seu CSS customizado aqui */"
                        rows={6}
                        className="font-mono text-sm"
                      />
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Advanced Settings */}
            <TabsContent value="advanced" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Configurações Avançadas</CardTitle>
                  <CardDescription>Configurações de integração e comportamento</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="collect_customer_info">Coletar Dados do Cliente</Label>
                        <p className="text-sm text-gray-500">Solicitar nome e email do pagador</p>
                      </div>
                      <Switch
                        id="collect_customer_info"
                        checked={formData.collect_customer_info || false}
                        onCheckedChange={(checked) => handleFieldChange('collect_customer_info', checked)}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="send_receipt">Enviar Comprovante</Label>
                        <p className="text-sm text-gray-500">Enviar recibo por email automaticamente</p>
                      </div>
                      <Switch
                        id="send_receipt"
                        checked={formData.send_receipt || false}
                        onCheckedChange={(checked) => handleFieldChange('send_receipt', checked)}
                      />
                    </div>
                  </div>

                  <Separator />

                  <div>
                    <Label htmlFor="webhook_url">URL do Webhook</Label>
                    <Input
                      id="webhook_url"
                      value={formData.webhook_url || ''}
                      onChange={(e) => handleFieldChange('webhook_url', e.target.value)}
                      placeholder="https://exemplo.com/webhook"
                      className={errors.webhook_url ? 'border-red-500' : ''}
                    />
                    {errors.webhook_url && <p className="text-sm text-red-500 mt-1">{errors.webhook_url}</p>}
                    <p className="text-sm text-gray-500 mt-1">
                      Receba notificações em tempo real sobre os pagamentos
                    </p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        {/* Preview Panel */}
        <div className="lg:sticky lg:top-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center space-x-2">
                  <Eye className="h-5 w-5" />
                  <span>Preview</span>
                </CardTitle>
                <div className="flex items-center space-x-2">
                  <Badge variant={previewMode === 'desktop' ? 'default' : 'secondary'}>
                    {previewMode === 'desktop' ? 'Desktop' : 'Mobile'}
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {renderPreview()}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export { PaymentLinkCreator };