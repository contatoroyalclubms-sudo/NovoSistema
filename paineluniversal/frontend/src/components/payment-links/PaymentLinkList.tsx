/**
 * PaymentLinkList - Advanced list component with filters and search
 * Sistema Universal de Gestão de Eventos
 */

import React, { useState } from 'react';
import { 
  MoreVertical, 
  Edit3, 
  Trash2, 
  Copy, 
  ExternalLink, 
  BarChart3, 
  QrCode, 
  Share2,
  Eye,
  EyeOff,
  Calendar,
  DollarSign,
  Users,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  Clock,
  XCircle,
  Pause,
  Play
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

import { 
  PaymentLink,
  LinkStatus,
  PaymentType,
  PaymentLinkCardProps
} from '@/types/payment-links';

interface PaymentLinkListProps {
  links: PaymentLink[];
  selectedLinks: string[];
  onSelectionChange: (selectedIds: string[]) => void;
  onEdit: (link: PaymentLink) => void;
  onDelete: (linkId: string) => void;
  onToggleStatus: (linkId: string, status: LinkStatus) => void;
  onViewAnalytics: (linkId: string) => void;
  viewMode?: 'table' | 'cards';
}

const PaymentLinkList: React.FC<PaymentLinkListProps> = ({
  links,
  selectedLinks,
  onSelectionChange,
  onEdit,
  onDelete,
  onToggleStatus,
  onViewAnalytics,
  viewMode = 'table'
}) => {
  const [qrCodeModal, setQrCodeModal] = useState<{ open: boolean; link: PaymentLink | null }>({
    open: false,
    link: null
  });

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      onSelectionChange(links.map(link => link.link_id));
    } else {
      onSelectionChange([]);
    }
  };

  const handleSelectLink = (linkId: string, checked: boolean) => {
    if (checked) {
      onSelectionChange([...selectedLinks, linkId]);
    } else {
      onSelectionChange(selectedLinks.filter(id => id !== linkId));
    }
  };

  const copyLinkUrl = (link: PaymentLink) => {
    const url = `${window.location.origin}/pay/${link.link_id}`;
    navigator.clipboard.writeText(url);
    // Show toast notification
  };

  const shareLink = async (link: PaymentLink) => {
    const url = `${window.location.origin}/pay/${link.link_id}`;
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: link.title,
          text: link.description || '',
          url: url,
        });
      } catch (err) {
        copyLinkUrl(link);
      }
    } else {
      copyLinkUrl(link);
    }
  };

  const getStatusIcon = (status: LinkStatus) => {
    switch (status) {
      case LinkStatus.ACTIVE:
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case LinkStatus.INACTIVE:
        return <XCircle className="h-4 w-4 text-red-500" />;
      case LinkStatus.EXPIRED:
        return <Clock className="h-4 w-4 text-orange-500" />;
      case LinkStatus.COMPLETED:
        return <CheckCircle2 className="h-4 w-4 text-blue-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: LinkStatus) => {
    switch (status) {
      case LinkStatus.ACTIVE:
        return 'bg-green-100 text-green-800 border-green-200';
      case LinkStatus.INACTIVE:
        return 'bg-red-100 text-red-800 border-red-200';
      case LinkStatus.EXPIRED:
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case LinkStatus.COMPLETED:
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPaymentTypeLabel = (type: PaymentType) => {
    switch (type) {
      case PaymentType.SINGLE:
        return 'Único';
      case PaymentType.FLEXIBLE:
        return 'Flexível';
      case PaymentType.RECURRING:
        return 'Recorrente';
      default:
        return type;
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const isExpiringSoon = (expiresAt?: string) => {
    if (!expiresAt) return false;
    const expiry = new Date(expiresAt);
    const now = new Date();
    const diff = expiry.getTime() - now.getTime();
    const days = diff / (1000 * 3600 * 24);
    return days <= 7 && days > 0;
  };

  const isNearMaxUses = (link: PaymentLink) => {
    if (!link.max_uses) return false;
    const usage = (link.uses_count / link.max_uses) * 100;
    return usage >= 80;
  };

  // QR Code Modal component
  const QRCodeModal = () => (
    <Dialog open={qrCodeModal.open} onOpenChange={(open) => setQrCodeModal({ open, link: null })}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>QR Code do Link</DialogTitle>
          <DialogDescription>
            Compartilhe este QR Code para pagamentos rápidos
          </DialogDescription>
        </DialogHeader>
        <div className="text-center space-y-4">
          {qrCodeModal.link && (
            <>
              <div className="inline-block p-4 bg-white border rounded-lg">
                <img 
                  src={qrCodeModal.link.qr_code} 
                  alt="QR Code" 
                  className="w-48 h-48 mx-auto"
                />
              </div>
              <div>
                <p className="font-medium">{qrCodeModal.link.title}</p>
                {qrCodeModal.link.amount && (
                  <p className="text-lg font-bold text-green-600">
                    {formatCurrency(qrCodeModal.link.amount)}
                  </p>
                )}
              </div>
              <Button onClick={() => copyLinkUrl(qrCodeModal.link!)} className="w-full">
                <Copy className="h-4 w-4 mr-2" />
                Copiar Link
              </Button>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );

  // Cards view
  if (viewMode === 'cards') {
    return (
      <div className="space-y-4">
        {links.map((link) => (
          <PaymentLinkCard
            key={link.link_id}
            link={link}
            selected={selectedLinks.includes(link.link_id)}
            onSelect={(checked) => handleSelectLink(link.link_id, checked)}
            onEdit={() => onEdit(link)}
            onDelete={() => onDelete(link.link_id)}
            onToggleStatus={(status) => onToggleStatus(link.link_id, status)}
            onViewAnalytics={() => onViewAnalytics(link.link_id)}
            onCopyLink={() => copyLinkUrl(link)}
            onShowQR={() => setQrCodeModal({ open: true, link })}
            onShare={() => shareLink(link)}
          />
        ))}
        <QRCodeModal />
      </div>
    );
  }

  // Table view
  return (
    <div className="space-y-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-12">
              <Checkbox
                checked={selectedLinks.length === links.length && links.length > 0}
                onCheckedChange={handleSelectAll}
              />
            </TableHead>
            <TableHead>Link</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Tipo</TableHead>
            <TableHead className="text-right">Valor</TableHead>
            <TableHead className="text-right">Usos</TableHead>
            <TableHead className="text-right">Receita</TableHead>
            <TableHead>Criado</TableHead>
            <TableHead className="w-12"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {links.map((link) => (
            <TableRow key={link.link_id} className="hover:bg-gray-50">
              <TableCell>
                <Checkbox
                  checked={selectedLinks.includes(link.link_id)}
                  onCheckedChange={(checked) => handleSelectLink(link.link_id, checked as boolean)}
                />
              </TableCell>
              
              <TableCell className="max-w-xs">
                <div>
                  <div className="font-medium truncate">{link.title}</div>
                  {link.description && (
                    <div className="text-sm text-gray-500 truncate">{link.description}</div>
                  )}
                  <div className="flex items-center space-x-2 mt-1">
                    {isExpiringSoon(link.expires_at) && (
                      <Badge variant="outline" className="text-orange-600 border-orange-200">
                        <Clock className="h-3 w-3 mr-1" />
                        Expira em breve
                      </Badge>
                    )}
                    {isNearMaxUses(link) && (
                      <Badge variant="outline" className="text-red-600 border-red-200">
                        <AlertCircle className="h-3 w-3 mr-1" />
                        Limite próximo
                      </Badge>
                    )}
                  </div>
                </div>
              </TableCell>
              
              <TableCell>
                <Badge variant="outline" className={getStatusColor(link.status)}>
                  {getStatusIcon(link.status)}
                  <span className="ml-1">{link.status}</span>
                </Badge>
              </TableCell>
              
              <TableCell>
                <Badge variant="secondary">
                  {getPaymentTypeLabel(link.payment_type)}
                </Badge>
              </TableCell>
              
              <TableCell className="text-right">
                {link.payment_type === PaymentType.FLEXIBLE ? (
                  <div className="text-sm">
                    <div>{formatCurrency(link.min_amount || 0)}</div>
                    <div className="text-gray-500">até {formatCurrency(link.max_amount || 0)}</div>
                  </div>
                ) : (
                  <div className="font-medium">{formatCurrency(link.amount || 0)}</div>
                )}
              </TableCell>
              
              <TableCell className="text-right">
                <div className="text-sm">
                  <div className="font-medium">{link.uses_count}</div>
                  {link.max_uses && (
                    <div className="text-gray-500">/ {link.max_uses}</div>
                  )}
                </div>
              </TableCell>
              
              <TableCell className="text-right">
                <div className="font-medium text-green-600">
                  {formatCurrency(link.total_collected)}
                </div>
                <div className="text-xs text-gray-500">
                  {link.views_count} visualizações
                </div>
              </TableCell>
              
              <TableCell>
                <div className="text-sm">
                  {formatDate(link.created_at)}
                </div>
                {link.expires_at && (
                  <div className="text-xs text-gray-500">
                    Expira: {formatDate(link.expires_at)}
                  </div>
                )}
              </TableCell>
              
              <TableCell>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="h-8 w-8 p-0">
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuLabel>Ações</DropdownMenuLabel>
                    <DropdownMenuItem onClick={() => copyLinkUrl(link)}>
                      <Copy className="h-4 w-4 mr-2" />
                      Copiar Link
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => setQrCodeModal({ open: true, link })}>
                      <QrCode className="h-4 w-4 mr-2" />
                      Ver QR Code
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => shareLink(link)}>
                      <Share2 className="h-4 w-4 mr-2" />
                      Compartilhar
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={() => onViewAnalytics(link.link_id)}>
                      <BarChart3 className="h-4 w-4 mr-2" />
                      Analytics
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => onEdit(link)}>
                      <Edit3 className="h-4 w-4 mr-2" />
                      Editar
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem 
                      onClick={() => onToggleStatus(
                        link.link_id, 
                        link.status === LinkStatus.ACTIVE ? LinkStatus.INACTIVE : LinkStatus.ACTIVE
                      )}
                    >
                      {link.status === LinkStatus.ACTIVE ? (
                        <>
                          <Pause className="h-4 w-4 mr-2" />
                          Desativar
                        </>
                      ) : (
                        <>
                          <Play className="h-4 w-4 mr-2" />
                          Ativar
                        </>
                      )}
                    </DropdownMenuItem>
                    <DropdownMenuItem 
                      onClick={() => onDelete(link.link_id)}
                      className="text-red-600 focus:text-red-600"
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Excluir
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      
      <QRCodeModal />
    </div>
  );
};

// Card component for individual payment links
const PaymentLinkCard: React.FC<{
  link: PaymentLink;
  selected: boolean;
  onSelect: (checked: boolean) => void;
  onEdit: () => void;
  onDelete: () => void;
  onToggleStatus: (status: LinkStatus) => void;
  onViewAnalytics: () => void;
  onCopyLink: () => void;
  onShowQR: () => void;
  onShare: () => void;
}> = ({
  link,
  selected,
  onSelect,
  onEdit,
  onDelete,
  onToggleStatus,
  onViewAnalytics,
  onCopyLink,
  onShowQR,
  onShare
}) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(amount);
  };

  const getStatusColor = (status: LinkStatus) => {
    switch (status) {
      case LinkStatus.ACTIVE:
        return 'bg-green-100 text-green-800 border-green-200';
      case LinkStatus.INACTIVE:
        return 'bg-red-100 text-red-800 border-red-200';
      case LinkStatus.EXPIRED:
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case LinkStatus.COMPLETED:
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: LinkStatus) => {
    switch (status) {
      case LinkStatus.ACTIVE:
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case LinkStatus.INACTIVE:
        return <XCircle className="h-4 w-4 text-red-500" />;
      case LinkStatus.EXPIRED:
        return <Clock className="h-4 w-4 text-orange-500" />;
      case LinkStatus.COMPLETED:
        return <CheckCircle2 className="h-4 w-4 text-blue-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <Card className={`transition-all duration-200 ${selected ? 'ring-2 ring-blue-500 border-blue-200' : 'hover:shadow-md'}`}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3">
            <Checkbox
              checked={selected}
              onCheckedChange={onSelect}
              className="mt-1"
            />
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2">
                <h3 className="font-semibold text-lg truncate">{link.title}</h3>
                <Badge variant="outline" className={getStatusColor(link.status)}>
                  {getStatusIcon(link.status)}
                  <span className="ml-1">{link.status}</span>
                </Badge>
              </div>
              
              {link.description && (
                <p className="text-gray-600 text-sm mt-1 line-clamp-2">{link.description}</p>
              )}
              
              <div className="flex items-center space-x-4 mt-3 text-sm text-gray-500">
                <div className="flex items-center space-x-1">
                  <DollarSign className="h-4 w-4" />
                  <span>
                    {link.payment_type === PaymentType.FLEXIBLE 
                      ? `${formatCurrency(link.min_amount || 0)} - ${formatCurrency(link.max_amount || 0)}`
                      : formatCurrency(link.amount || 0)
                    }
                  </span>
                </div>
                <div className="flex items-center space-x-1">
                  <Users className="h-4 w-4" />
                  <span>{link.uses_count} usos</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Eye className="h-4 w-4" />
                  <span>{link.views_count} views</span>
                </div>
              </div>
              
              {link.expires_at && (
                <div className="flex items-center space-x-1 mt-2 text-sm text-orange-600">
                  <Calendar className="h-4 w-4" />
                  <span>Expira: {new Date(link.expires_at).toLocaleDateString('pt-BR')}</span>
                </div>
              )}
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="text-right">
              <div className="text-lg font-bold text-green-600">
                {formatCurrency(link.total_collected)}
              </div>
              <div className="text-sm text-gray-500">receita total</div>
            </div>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-8 w-8 p-0">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>Ações</DropdownMenuLabel>
                <DropdownMenuItem onClick={onCopyLink}>
                  <Copy className="h-4 w-4 mr-2" />
                  Copiar Link
                </DropdownMenuItem>
                <DropdownMenuItem onClick={onShowQR}>
                  <QrCode className="h-4 w-4 mr-2" />
                  Ver QR Code
                </DropdownMenuItem>
                <DropdownMenuItem onClick={onShare}>
                  <Share2 className="h-4 w-4 mr-2" />
                  Compartilhar
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={onViewAnalytics}>
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Analytics
                </DropdownMenuItem>
                <DropdownMenuItem onClick={onEdit}>
                  <Edit3 className="h-4 w-4 mr-2" />
                  Editar
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem 
                  onClick={() => onToggleStatus(
                    link.status === LinkStatus.ACTIVE ? LinkStatus.INACTIVE : LinkStatus.ACTIVE
                  )}
                >
                  {link.status === LinkStatus.ACTIVE ? (
                    <>
                      <EyeOff className="h-4 w-4 mr-2" />
                      Desativar
                    </>
                  ) : (
                    <>
                      <Eye className="h-4 w-4 mr-2" />
                      Ativar
                    </>
                  )}
                </DropdownMenuItem>
                <DropdownMenuItem 
                  onClick={onDelete}
                  className="text-red-600 focus:text-red-600"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Excluir
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
        
        {/* Quick Actions */}
        <div className="flex items-center justify-between mt-4 pt-4 border-t">
          <div className="flex items-center space-x-2">
            <Button size="sm" variant="outline" onClick={onCopyLink}>
              <Copy className="h-3 w-3 mr-1" />
              Copiar
            </Button>
            <Button size="sm" variant="outline" onClick={onShare}>
              <Share2 className="h-3 w-3 mr-1" />
              Compartilhar
            </Button>
            <Button size="sm" variant="outline" onClick={onViewAnalytics}>
              <BarChart3 className="h-3 w-3 mr-1" />
              Analytics
            </Button>
          </div>
          
          <div className="flex items-center space-x-1 text-xs text-gray-500">
            <TrendingUp className="h-3 w-3" />
            <span>
              {link.uses_count > 0 ? ((link.uses_count / (link.views_count || 1)) * 100).toFixed(1) : '0'}% conversão
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export { PaymentLinkList };