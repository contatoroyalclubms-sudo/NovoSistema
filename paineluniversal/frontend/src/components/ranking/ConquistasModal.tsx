import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Card, CardContent } from '../ui/card';
import { Award, Trophy, Star, Crown, Target, Medal } from 'lucide-react';
import { gamificacaoService } from '../../services/api';
import { useToast } from '../../hooks/use-toast';

interface ConquistasModalProps {
  isOpen: boolean;
  onClose: () => void;
  promoter: any;
}

const ConquistasModal: React.FC<ConquistasModalProps> = ({ isOpen, onClose, promoter }) => {
  const { toast } = useToast();
  const [conquistas, setConquistas] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && promoter) {
      carregarConquistas();
    }
  }, [isOpen, promoter]);

  const carregarConquistas = async () => {
    try {
      setLoading(true);
      const mockConquistas = [
        {
          id: 1,
          conquista_nome: "Vendedor Bronze",
          conquista_descricao: "Realize 10 vendas",
          badge_nivel: "bronze",
          icone: "🥉",
          valor_alcancado: 15,
          data_conquista: new Date().toISOString(),
          evento_nome: "Festa de Ano Novo 2025"
        },
        {
          id: 2,
          conquista_nome: "Presença Garantida",
          conquista_descricao: "Mantenha 80% de presença",
          badge_nivel: "prata",
          icone: "✅",
          valor_alcancado: 85,
          data_conquista: new Date().toISOString(),
          evento_nome: null
        }
      ];
      setConquistas(mockConquistas);
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao carregar conquistas",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const getBadgeIcon = (badge: string) => {
    const icons = {
      'lenda': <Crown className="h-5 w-5 text-purple-600" />,
      'diamante': <Star className="h-5 w-5 text-blue-600" />,
      'platina': <Award className="h-5 w-5 text-gray-400" />,
      'ouro': <Trophy className="h-5 w-5 text-yellow-500" />,
      'prata': <Medal className="h-5 w-5 text-gray-500" />,
      'bronze': <Target className="h-5 w-5 text-orange-600" />
    };
    return icons[badge] || <Target className="h-5 w-5 text-gray-400" />;
  };

  const getBadgeColor = (badge: string) => {
    const colors = {
      'lenda': 'bg-purple-100 text-purple-800 border-purple-200',
      'diamante': 'bg-blue-100 text-blue-800 border-blue-200',
      'platina': 'bg-gray-100 text-gray-800 border-gray-200',
      'ouro': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'prata': 'bg-gray-100 text-gray-600 border-gray-200',
      'bronze': 'bg-orange-100 text-orange-800 border-orange-200'
    };
    return colors[badge] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Award className="h-5 w-5" />
            Conquistas de {promoter?.nome_promoter}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Carregando conquistas...</p>
            </div>
          ) : conquistas.length === 0 ? (
            <div className="text-center py-8">
              <Award className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p className="text-gray-500">Nenhuma conquista encontrada</p>
            </div>
          ) : (
            <div className="space-y-3">
              {conquistas.map((conquista) => (
                <Card key={conquista.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-4">
                      <div className="text-3xl">{conquista.icone}</div>
                      
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold">{conquista.conquista_nome}</h3>
                          <Badge className={`${getBadgeColor(conquista.badge_nivel)} flex items-center gap-1`}>
                            {getBadgeIcon(conquista.badge_nivel)}
                            {conquista.badge_nivel.toUpperCase()}
                          </Badge>
                        </div>
                        
                        <p className="text-sm text-gray-600 mb-2">{conquista.conquista_descricao}</p>
                        
                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <span>Valor alcançado: {conquista.valor_alcancado}</span>
                          <span>
                            {new Date(conquista.data_conquista).toLocaleDateString('pt-BR')}
                          </span>
                        </div>
                        
                        {conquista.evento_nome && (
                          <div className="mt-1">
                            <Badge variant="outline" className="text-xs">
                              {conquista.evento_nome}
                            </Badge>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        <div className="flex justify-end gap-2 pt-4">
          <Button variant="outline" onClick={onClose}>
            Fechar
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ConquistasModal;
