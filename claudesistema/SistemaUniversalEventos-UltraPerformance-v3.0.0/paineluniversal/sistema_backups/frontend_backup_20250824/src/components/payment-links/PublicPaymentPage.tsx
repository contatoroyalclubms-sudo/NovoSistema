/**
 * PublicPaymentPage - Responsive public payment page for payment links
 * Sistema Universal de Gestão de Eventos
 */

import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { 
  CreditCard, 
  Smartphone, 
  QrCode, 
  Shield, 
  Clock, 
  CheckCircle2, 
  AlertCircle, 
  Loader2,
  User,
  Mail,
  Phone,
  FileText,
  Copy,
  ExternalLink,
  ArrowRight,
  Zap
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';

import { 
  PaymentLink,
  PublicPaymentData,
  PaymentProcessingResult,
  PaymentType,
  LinkTheme,
  THEME_PRESETS,
  PAYMENT_METHODS
} from '@/types/payment-links';

import paymentLinksService from '@/services/payment-links-service';

interface PublicPaymentPageProps {
  linkId?: string;
}

const PublicPaymentPage: React.FC<PublicPaymentPageProps> = ({ linkId: propLinkId }) => {
  const { linkId: paramLinkId } = useParams<{ linkId: string }>();
  const [searchParams] = useSearchParams();
  const linkId = propLinkId || paramLinkId;

  // State
  const [link, setLink] = useState<PaymentLink | null>(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<PaymentProcessingResult | null>(null);
  const [step, setStep] = useState<'form' | 'processing' | 'success' | 'error'>('form');

  // Form data
  const [formData, setFormData] = useState<PublicPaymentData>({
    payment_method: 'pix'
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [agreesToTerms, setAgreesToTerms] = useState(false);

  // UI state
  const [selectedInstallments, setSelectedInstallments] = useState(1);
  const [showQRCode, setShowQRCode] = useState(false);

  // Load payment link data
  useEffect(() => {
    if (linkId) {
      loadPaymentLink();
    }
  }, [linkId]);

  // Pre-fill form from URL params
  useEffect(() => {
    const amount = searchParams.get('amount');
    const email = searchParams.get('email');
    const name = searchParams.get('name');

    if (amount) setFormData(prev => ({ ...prev, amount: parseFloat(amount) }));
    if (email) setFormData(prev => ({ ...prev, customer_email: email }));
    if (name) setFormData(prev => ({ ...prev, customer_name: name }));
  }, [searchParams]);

  const loadPaymentLink = async () => {
    if (!linkId) return;

    try {
      setLoading(true);
      setError(null);
      
      const linkData = await paymentLinksService.getPublicPaymentLink(linkId);
      setLink(linkData);

      // Pre-fill amount for single payment type
      if (linkData.payment_type === PaymentType.SINGLE && linkData.amount) {
        setFormData(prev => ({ ...prev, amount: linkData.amount }));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Link de pagamento não encontrado');
      setStep('error');
    } finally {
      setLoading(false);
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.payment_method) {
      errors.payment_method = 'Selecione um método de pagamento';
    }

    if (link?.payment_type === PaymentType.FLEXIBLE) {
      if (!formData.amount || formData.amount <= 0) {
        errors.amount = 'Valor é obrigatório';
      } else {
        if (link.min_amount && formData.amount < link.min_amount) {
          errors.amount = `Valor mínimo: R$ ${link.min_amount.toFixed(2)}`;
        }
        if (link.max_amount && formData.amount > link.max_amount) {
          errors.amount = `Valor máximo: R$ ${link.max_amount.toFixed(2)}`;
        }
      }
    }

    if (link?.collect_customer_info) {
      if (!formData.customer_name?.trim()) {
        errors.customer_name = 'Nome é obrigatório';
      }
      if (!formData.customer_email?.trim()) {
        errors.customer_email = 'Email é obrigatório';
      } else if (!/\S+@\S+\.\S+/.test(formData.customer_email)) {
        errors.customer_email = 'Email inválido';
      }
    }

    if (!agreesToTerms) {
      errors.terms = 'Você deve aceitar os termos para continuar';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm() || !link) return;

    try {
      setProcessing(true);
      setStep('processing');

      const paymentData: PublicPaymentData = {
        ...formData,
        amount: link.payment_type === PaymentType.SINGLE ? link.amount : formData.amount,
        ip_address: await getClientIP(),
        user_agent: navigator.userAgent
      };

      const result = await paymentLinksService.processPayment(linkId!, paymentData);
      
      setSuccess(result);
      
      if (result.status === 'success') {
        setStep('success');
        
        // Redirect if provided
        if (result.redirect_url) {
          setTimeout(() => {
            window.location.href = result.redirect_url!;
          }, 3000);
        }
      } else {
        setStep('error');
        setError(result.error || 'Erro no processamento do pagamento');
      }
    } catch (err) {
      setStep('error');
      setError(err instanceof Error ? err.message : 'Erro ao processar pagamento');
    } finally {
      setProcessing(false);
    }
  };

  const getClientIP = async (): Promise<string> => {
    try {
      const response = await fetch('https://api.ipify.org?format=json');
      const data = await response.json();
      return data.ip;
    } catch {
      return '';
    }
  };

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(amount);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // You might want to show a toast notification here
  };

  const getThemeStyles = () => {
    if (!link) return THEME_PRESETS.default;
    return THEME_PRESETS[link.theme] || THEME_PRESETS.default;
  };

  const themeStyles = getThemeStyles();

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Carregando...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (step === 'error' || !link) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mb-4">
              <AlertCircle className="h-6 w-6 text-red-600" />
            </div>
            <CardTitle className="text-red-600">Erro no Pagamento</CardTitle>
          </CardHeader>
          <CardContent className="text-center space-y-4">
            <p className="text-gray-600">{error}</p>
            <Button onClick={() => window.location.reload()}>
              Tentar Novamente
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Success state
  if (step === 'success') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-4">
              <CheckCircle2 className="h-6 w-6 text-green-600" />
            </div>
            <CardTitle className="text-green-600">Pagamento Confirmado!</CardTitle>
          </CardHeader>
          <CardContent className="text-center space-y-4">
            <p className="text-gray-600">
              Seu pagamento foi processado com sucesso.
            </p>
            {success?.payment_id && (
              <div className="p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500">ID da Transação</p>
                <p className="font-mono text-sm">{success.payment_id}</p>
              </div>
            )}
            {success?.redirect_url && (
              <div className="text-sm text-gray-500">
                Redirecionando em alguns segundos...
              </div>
            )}
            {link.success_url && (
              <Button asChild>
                <a href={link.success_url}>
                  Continuar
                  <ArrowRight className="h-4 w-4 ml-2" />
                </a>
              </Button>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  // Processing state
  if (step === 'processing') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-4">
              <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
            </div>
            <CardTitle>Processando Pagamento...</CardTitle>
          </CardHeader>
          <CardContent className="text-center space-y-4">
            <Progress value={75} className="w-full" />
            <p className="text-gray-600">
              Não feche esta página. Seu pagamento está sendo processado.
            </p>
            {success?.qr_code && formData.payment_method === 'pix' && (
              <div className="space-y-4">
                <Separator />
                <div className="text-center">
                  <h3 className="font-semibold mb-2">Escaneie o QR Code</h3>
                  <div className="inline-block p-4 bg-white rounded-lg border">
                    <img 
                      src={success.qr_code} 
                      alt="QR Code PIX" 
                      className="w-48 h-48 mx-auto"
                    />
                  </div>
                  <p className="text-sm text-gray-500 mt-2">
                    Abra o aplicativo do seu banco e escaneie o código
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  // Main payment form
  return (
    <div 
      className="min-h-screen py-8 px-4"
      style={{ 
        backgroundColor: themeStyles.background_color,
        fontFamily: themeStyles.font_family 
      }}
    >
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          {link.logo_url && (
            <div className="mb-4">
              <img 
                src={link.logo_url} 
                alt="Logo" 
                className="h-16 mx-auto rounded-lg"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = 'none';
                }}
              />
            </div>
          )}
          
          <h1 
            className="text-3xl font-bold mb-2"
            style={{ color: themeStyles.text_color }}
          >
            {link.title}
          </h1>
          
          {link.description && (
            <p 
              className="text-lg opacity-80"
              style={{ color: themeStyles.text_color }}
            >
              {link.description}
            </p>
          )}
          
          {link.expires_at && (
            <div className="mt-4 inline-flex items-center space-x-2 px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm">
              <Clock className="h-4 w-4" />
              <span>
                Válido até {new Date(link.expires_at).toLocaleDateString('pt-BR')}
              </span>
            </div>
          )}
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Payment Form */}
          <div className="md:col-span-2">
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <CreditCard className="h-5 w-5" />
                  <span>Informações de Pagamento</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* Amount Section */}
                  <div className="p-4 bg-gray-50 rounded-lg">
                    {link.payment_type === PaymentType.FLEXIBLE ? (
                      <div>
                        <Label htmlFor="amount" className="text-sm font-medium">
                          Valor do Pagamento (R$)
                        </Label>
                        <Input
                          id="amount"
                          type="number"
                          step="0.01"
                          min={link.min_amount || 0}
                          max={link.max_amount || 999999}
                          value={formData.amount || ''}
                          onChange={(e) => setFormData(prev => ({ 
                            ...prev, 
                            amount: parseFloat(e.target.value) || undefined 
                          }))}
                          placeholder="0,00"
                          className={`text-lg mt-1 ${formErrors.amount ? 'border-red-500' : ''}`}
                        />
                        {formErrors.amount && (
                          <p className="text-sm text-red-500 mt-1">{formErrors.amount}</p>
                        )}
                        <div className="flex justify-between text-sm text-gray-500 mt-1">
                          {link.min_amount && <span>Mín: {formatCurrency(link.min_amount)}</span>}
                          {link.max_amount && <span>Máx: {formatCurrency(link.max_amount)}</span>}
                        </div>
                      </div>
                    ) : (
                      <div className="text-center">
                        <p className="text-sm text-gray-600 mb-2">Valor a pagar:</p>
                        <p 
                          className="text-3xl font-bold"
                          style={{ color: themeStyles.primary_color }}
                        >
                          {formatCurrency(link.amount || 0)}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Customer Information */}
                  {link.collect_customer_info && (
                    <div className="space-y-4">
                      <h3 className="font-semibold flex items-center space-x-2">
                        <User className="h-4 w-4" />
                        <span>Seus Dados</span>
                      </h3>
                      
                      <div className="grid md:grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="customer_name">Nome Completo *</Label>
                          <Input
                            id="customer_name"
                            value={formData.customer_name || ''}
                            onChange={(e) => setFormData(prev => ({ 
                              ...prev, 
                              customer_name: e.target.value 
                            }))}
                            placeholder="Seu nome completo"
                            className={formErrors.customer_name ? 'border-red-500' : ''}
                          />
                          {formErrors.customer_name && (
                            <p className="text-sm text-red-500 mt-1">{formErrors.customer_name}</p>
                          )}
                        </div>
                        
                        <div>
                          <Label htmlFor="customer_email">Email *</Label>
                          <Input
                            id="customer_email"
                            type="email"
                            value={formData.customer_email || ''}
                            onChange={(e) => setFormData(prev => ({ 
                              ...prev, 
                              customer_email: e.target.value 
                            }))}
                            placeholder="seu@email.com"
                            className={formErrors.customer_email ? 'border-red-500' : ''}
                          />
                          {formErrors.customer_email && (
                            <p className="text-sm text-red-500 mt-1">{formErrors.customer_email}</p>
                          )}
                        </div>
                      </div>
                      
                      <div>
                        <Label htmlFor="customer_phone">Telefone (opcional)</Label>
                        <Input
                          id="customer_phone"
                          value={formData.customer_phone || ''}
                          onChange={(e) => setFormData(prev => ({ 
                            ...prev, 
                            customer_phone: e.target.value 
                          }))}
                          placeholder="(11) 99999-9999"
                        />
                      </div>
                    </div>
                  )}

                  {/* Payment Methods */}
                  <div className="space-y-4">
                    <h3 className="font-semibold flex items-center space-x-2">
                      <CreditCard className="h-4 w-4" />
                      <span>Método de Pagamento</span>
                    </h3>
                    
                    <RadioGroup
                      value={formData.payment_method}
                      onValueChange={(value) => setFormData(prev => ({ 
                        ...prev, 
                        payment_method: value 
                      }))}
                      className="space-y-3"
                    >
                      {PAYMENT_METHODS.map((method) => (
                        <div key={method.value} className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                          <RadioGroupItem value={method.value} id={method.value} />
                          <Label 
                            htmlFor={method.value} 
                            className="flex-1 cursor-pointer flex items-center space-x-3"
                          >
                            <span className="text-xl">{method.icon}</span>
                            <div>
                              <div className="font-medium">{method.label}</div>
                              {method.value === 'pix' && (
                                <div className="text-sm text-green-600">Aprovação instantânea</div>
                              )}
                              {method.value === 'card' && link.allow_installments && (
                                <div className="text-sm text-blue-600">Até 12x sem juros</div>
                              )}
                            </div>
                          </Label>
                        </div>
                      ))}
                    </RadioGroup>
                    
                    {formErrors.payment_method && (
                      <p className="text-sm text-red-500">{formErrors.payment_method}</p>
                    )}
                  </div>

                  {/* Installments for card payment */}
                  {formData.payment_method === 'card' && link.allow_installments && (
                    <div>
                      <Label>Parcelas</Label>
                      <select
                        value={selectedInstallments}
                        onChange={(e) => setSelectedInstallments(parseInt(e.target.value))}
                        className="w-full mt-1 p-2 border rounded-md"
                      >
                        {[...Array(12)].map((_, i) => {
                          const installments = i + 1;
                          const installmentValue = (formData.amount || link.amount || 0) / installments;
                          return (
                            <option key={installments} value={installments}>
                              {installments}x de {formatCurrency(installmentValue)}
                              {installments === 1 ? ' à vista' : ` (Total: ${formatCurrency((formData.amount || link.amount || 0))})`}
                            </option>
                          );
                        })}
                      </select>
                    </div>
                  )}

                  {/* Terms and Conditions */}
                  <div className="space-y-4">
                    <div className="flex items-start space-x-2">
                      <Checkbox
                        id="terms"
                        checked={agreesToTerms}
                        onCheckedChange={(checked) => setAgreesToTerms(checked as boolean)}
                      />
                      <Label 
                        htmlFor="terms" 
                        className="text-sm leading-relaxed cursor-pointer"
                      >
                        Concordo com os{' '}
                        <a href="#" className="text-blue-600 hover:underline">
                          termos de uso
                        </a>
                        {' '}e{' '}
                        <a href="#" className="text-blue-600 hover:underline">
                          política de privacidade
                        </a>
                      </Label>
                    </div>
                    {formErrors.terms && (
                      <p className="text-sm text-red-500">{formErrors.terms}</p>
                    )}
                  </div>

                  {/* Submit Button */}
                  <Button
                    type="submit"
                    disabled={processing}
                    className="w-full py-3 text-lg"
                    style={{
                      backgroundColor: themeStyles.button_color,
                      borderRadius: `${themeStyles.border_radius}px`
                    }}
                  >
                    {processing ? (
                      <Loader2 className="h-5 w-5 animate-spin mr-2" />
                    ) : (
                      <Zap className="h-5 w-5 mr-2" />
                    )}
                    Pagar {formData.amount || link.amount ? formatCurrency(formData.amount || link.amount || 0) : ''}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Summary Sidebar */}
          <div>
            <Card className="shadow-lg sticky top-4">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <FileText className="h-4 w-4" />
                  <span>Resumo</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Produto:</span>
                    <span className="font-medium">{link.title}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Valor:</span>
                    <span className="font-bold text-green-600">
                      {formatCurrency(formData.amount || link.amount || 0)}
                    </span>
                  </div>
                  {formData.payment_method === 'card' && selectedInstallments > 1 && (
                    <div className="flex justify-between text-sm text-gray-600">
                      <span>Parcelas:</span>
                      <span>{selectedInstallments}x de {formatCurrency((formData.amount || link.amount || 0) / selectedInstallments)}</span>
                    </div>
                  )}
                </div>

                <Separator />

                {/* Security Features */}
                <div className="space-y-2">
                  <h4 className="font-semibold text-sm">Segurança</h4>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Shield className="h-4 w-4 text-green-500" />
                    <span>Pagamento 100% seguro</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                    <span>Dados criptografados</span>
                  </div>
                  {link.send_receipt && (
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Mail className="h-4 w-4 text-blue-500" />
                      <span>Recibo por email</span>
                    </div>
                  )}
                </div>

                <Separator />

                {/* Support Info */}
                <div className="text-center">
                  <p className="text-xs text-gray-500">
                    Algum problema? 
                    <a href="#" className="text-blue-600 hover:underline ml-1">
                      Entre em contato
                    </a>
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export { PublicPaymentPage };