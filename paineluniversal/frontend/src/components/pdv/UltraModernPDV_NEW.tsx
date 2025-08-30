import { useState, useEffect } from 'react';
import { 
  ShoppingCart, CreditCard, DollarSign, Plus, Minus, X, 
  Search, QrCode, Receipt, Printer, Brain,
  TrendingUp, Star, 
  NfcIcon, Settings,
  ArrowRight, BarChart3, Download
} from 'lucide-react';

interface Product {
  id: number;
  name: string;
  price: number;
  category: string;
  image: string;
  stock: number;
  popular: boolean;
}

interface CartItem extends Product {
  quantity: number;
}

const UltraModernPDV = () => {
  const [cart, setCart] = useState<CartItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('bebidas');
  const [paymentMethod, setPaymentMethod] = useState('card');
  const [isProcessing, setIsProcessing] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [aiRecommendations, setAiRecommendations] = useState<{product: string; reason: string; confidence: number}[]>([]);
  const [recentSales, setRecentSales] = useState<{id: number; items: number; total: string; method: string; time: string}[]>([]);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ 
        x: (e.clientX / window.innerWidth) * 100, 
        y: (e.clientY / window.innerHeight) * 100 
      });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Produtos do evento
  const products = [
    {
      id: 1,
      name: 'Água Mineral',
      price: 3.50,
      category: 'bebidas',
      image: 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=300&h=300&fit=crop',
      stock: 150,
      popular: true
    },
    {
      id: 2,
      name: 'Refrigerante',
      price: 5.00,
      category: 'bebidas',
      image: 'https://images.unsplash.com/photo-1581636625402-29b2a704ef13?w=300&h=300&fit=crop',
      stock: 89,
      popular: false
    },
    {
      id: 3,
      name: 'Café Premium',
      price: 7.50,
      category: 'bebidas',
      image: 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=300&h=300&fit=crop',
      stock: 45,
      popular: true
    },
    {
      id: 4,
      name: 'Sanduíche Natural',
      price: 12.90,
      category: 'comidas',
      image: 'https://images.unsplash.com/photo-1553909489-cd47e0ef937f?w=300&h=300&fit=crop',
      stock: 23,
      popular: true
    },
    {
      id: 5,
      name: 'Bolo de Chocolate',
      price: 8.50,
      category: 'comidas',
      image: 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=300&h=300&fit=crop',
      stock: 15,
      popular: false
    },
    {
      id: 6,
      name: 'Camiseta do Evento',
      price: 45.00,
      category: 'souvenirs',
      image: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300&h=300&fit=crop',
      stock: 67,
      popular: true
    },
    {
      id: 7,
      name: 'Caneca Personalizada',
      price: 25.00,
      category: 'souvenirs',
      image: 'https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=300&h=300&fit=crop',
      stock: 34,
      popular: false
    }
  ];

  const categories = [
    { id: 'bebidas', name: 'Bebidas', icon: '🥤', color: 'blue' },
    { id: 'comidas', name: 'Comidas', icon: '🍕', color: 'emerald' },
    { id: 'souvenirs', name: 'Souvenirs', icon: '🎁', color: 'purple' }
  ];

  const paymentMethods = [
    { id: 'card', name: 'Cartão', icon: CreditCard, color: 'blue' },
    { id: 'pix', name: 'PIX', icon: QrCode, color: 'emerald' },
    { id: 'cash', name: 'Dinheiro', icon: DollarSign, color: 'yellow' },
    { id: 'nfc', name: 'NFC', icon: NfcIcon, color: 'purple' }
  ];

  // Simulação de IA para recomendações
  useEffect(() => {
    const recommendations = [
      { product: 'Água Mineral', reason: '73% dos clientes compram junto com café', confidence: 94 },
      { product: 'Camiseta do Evento', reason: 'Pico de vendas detectado agora', confidence: 87 },
      { product: 'Sanduíche Natural', reason: 'Horário ideal para alimentos', confidence: 91 }
    ];
    setAiRecommendations(recommendations);
  }, [cart]);

  // Simular vendas em tempo real
  useEffect(() => {
    const interval = setInterval(() => {
      const newSale = {
        id: Date.now(),
        items: Math.floor(Math.random() * 3) + 1,
        total: (Math.random() * 50 + 10).toFixed(2),
        method: ['Cartão', 'PIX', 'Dinheiro'][Math.floor(Math.random() * 3)],
        time: new Date().toLocaleTimeString()
      };
      setRecentSales(prev => [newSale, ...prev.slice(0, 4)]);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const addToCart = (product: Product) => {
    const existingItem = cart.find(item => item.id === product.id);
    if (existingItem) {
      setCart(cart.map(item => 
        item.id === product.id 
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
  };

  const removeFromCart = (productId: number) => {
    setCart(cart.filter(item => item.id !== productId));
  };

  const updateQuantity = (productId: number, newQuantity: number) => {
    if (newQuantity <= 0) {
      removeFromCart(productId);
    } else {
      setCart(cart.map(item => 
        item.id === productId 
          ? { ...item, quantity: newQuantity }
          : item
      ));
    }
  };

  const getTotalPrice = () => {
    return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  const getTotalItems = () => {
    return cart.reduce((total, item) => total + item.quantity, 0);
  };

  const processPayment = () => {
    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
      setCart([]);
      // Adicionar à lista de vendas recentes
      const newSale = {
        id: Date.now(),
        items: getTotalItems(),
        total: getTotalPrice().toFixed(2),
        method: paymentMethods.find(p => p.id === paymentMethod)?.name || 'Cartão',
        time: new Date().toLocaleTimeString()
      };
      setRecentSales(prev => [newSale, ...prev.slice(0, 4)]);
    }, 3000);
  };

  const filteredProducts = products.filter(product => product.category === selectedCategory);

  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      
      {/* Neural Background */}
      <div className="fixed inset-0 z-0">
        <div 
          className="absolute inset-0 opacity-30"
          style={{
            background: `
              radial-gradient(circle at 25% 25%, rgba(16, 185, 129, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 75% 75%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
              radial-gradient(circle at ${mousePosition.x}% ${mousePosition.y}%, rgba(139, 92, 246, 0.05) 0%, transparent 30%)
            `
          }}
        />
      </div>

      <div className="relative z-10 min-h-screen p-6">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-black bg-gradient-to-r from-white via-emerald-200 to-blue-200 bg-clip-text text-transparent">
              PDV Inteligente
            </h1>
            <p className="text-gray-400 mt-2">Sistema de vendas com IA e análise preditiva</p>
          </div>

          {/* Quick Stats */}
          <div className="flex items-center space-x-6">
            {[
              { label: 'Vendas Hoje', value: 'R$ 12.5K', icon: DollarSign, color: 'emerald' },
              { label: 'Transações', value: '247', icon: Receipt, color: 'blue' },
              { label: 'Ticket Médio', value: 'R$ 28.50', icon: TrendingUp, color: 'purple' }
            ].map((stat, index) => (
              <div key={index} className="backdrop-blur-xl bg-white/[0.08] border border-white/10 rounded-xl p-4 text-center min-w-[120px]">
                <div className={`bg-${stat.color}-500/20 p-2 rounded-lg w-fit mx-auto mb-2`}>
                  <stat.icon className={`w-5 h-5 text-${stat.color}-400`} />
                </div>
                <div className="text-xl font-bold text-white">{stat.value}</div>
                <div className="text-xs text-gray-400">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="grid lg:grid-cols-4 gap-6">
          
          {/* Product Categories & Items */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Categories */}
            <div className="backdrop-blur-xl bg-gradient-to-br from-white/[0.08] to-white/[0.02] border border-white/10 rounded-2xl p-6">
              
              <h2 className="text-xl font-bold text-white mb-6">Categorias</h2>
              
              <div className="grid grid-cols-3 gap-4">
                {categories.map((category) => (
                  <button
                    key={category.id}
                    onClick={() => setSelectedCategory(category.id)}
                    className={`p-4 rounded-xl border-2 transition-all duration-300 ${
                      selectedCategory === category.id
                        ? `border-${category.color}-500/50 bg-${category.color}-500/10`
                        : 'border-white/10 bg-white/[0.03] hover:bg-white/[0.08]'
                    }`}
                  >
                    <div className="text-3xl mb-2">{category.icon}</div>
                    <div className="text-white font-semibold text-sm">{category.name}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Products Grid */}
            <div className="backdrop-blur-xl bg-gradient-to-br from-white/[0.08] to-white/[0.02] border border-white/10 rounded-2xl p-6">
              
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-white">
                  {categories.find(c => c.id === selectedCategory)?.name}
                </h2>
                
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Buscar produtos..."
                    className="bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 py-2 text-white placeholder-gray-400 focus:bg-white/10 focus:border-purple-500/50 transition-all"
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4 max-h-96 overflow-y-auto custom-scrollbar">
                {filteredProducts.map((product) => (
                  <div key={product.id} className="group relative backdrop-blur-sm bg-white/[0.03] border border-white/[0.08] rounded-xl p-4 hover:bg-white/[0.08] transition-all duration-300">
                    
                    {/* Popular Badge */}
                    {product.popular && (
                      <div className="absolute top-3 right-3 bg-yellow-500/20 text-yellow-400 px-2 py-1 rounded-full text-xs font-semibold flex items-center space-x-1">
                        <Star className="w-3 h-3 fill-current" />
                        <span>Popular</span>
                      </div>
                    )}

                    {/* Product Image */}
                    <div className="relative mb-4">
                      <img 
                        src={product.image} 
                        alt={product.name}
                        className="w-full h-24 object-cover rounded-lg"
                      />
                      {product.stock < 20 && (
                        <div className="absolute bottom-2 left-2 bg-red-500/20 text-red-400 px-2 py-1 rounded text-xs font-semibold">
                          Baixo Estoque
                        </div>
                      )}
                    </div>

                    {/* Product Info */}
                    <div className="space-y-2">
                      <h3 className="text-white font-semibold">{product.name}</h3>
                      <div className="flex items-center justify-between">
                        <span className="text-emerald-400 font-bold text-lg">
                          R$ {product.price.toFixed(2)}
                        </span>
                        <span className="text-gray-400 text-sm">
                          {product.stock} unidades
                        </span>
                      </div>
                    </div>

                    {/* Add Button */}
                    <button
                      onClick={() => addToCart(product)}
                      className="w-full mt-4 bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-500 hover:to-blue-500 text-white py-2 rounded-lg font-semibold transition-all duration-300 transform group-hover:scale-105 flex items-center justify-center space-x-2"
                    >
                      <Plus className="w-4 h-4" />
                      <span>Adicionar</span>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Cart & Payment */}
          <div className="space-y-6">
            
            {/* Shopping Cart */}
            <div className="backdrop-blur-xl bg-gradient-to-br from-white/[0.08] to-white/[0.02] border border-white/10 rounded-2xl p-6">
              
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-bold text-white">Carrinho</h2>
                <div className="flex items-center space-x-2 bg-emerald-500/20 text-emerald-400 px-3 py-1 rounded-full text-sm font-semibold">
                  <ShoppingCart className="w-4 h-4" />
                  <span>{getTotalItems()}</span>
                </div>
              </div>

              {cart.length === 0 ? (
                <div className="text-center py-8">
                  <ShoppingCart className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">Carrinho vazio</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-64 overflow-y-auto custom-scrollbar">
                  {cart.map((item) => (
                    <div key={item.id} className="flex items-center space-x-3 p-3 bg-white/[0.03] border border-white/[0.08] rounded-xl">
                      
                      <img 
                        src={item.image} 
                        alt={item.name}
                        className="w-12 h-12 object-cover rounded-lg"
                      />

                      <div className="flex-1 min-w-0">
                        <h3 className="text-white text-sm font-semibold truncate">{item.name}</h3>
                        <p className="text-emerald-400 text-sm font-bold">R$ {item.price.toFixed(2)}</p>
                      </div>

                      {/* Quantity Controls */}
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity - 1)}
                          className="w-6 h-6 bg-red-500/20 text-red-400 rounded-full flex items-center justify-center hover:bg-red-500/30 transition-colors"
                        >
                          <Minus className="w-3 h-3" />
                        </button>
                        
                        <span className="text-white font-semibold min-w-[20px] text-center">
                          {item.quantity}
                        </span>
                        
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity + 1)}
                          className="w-6 h-6 bg-emerald-500/20 text-emerald-400 rounded-full flex items-center justify-center hover:bg-emerald-500/30 transition-colors"
                        >
                          <Plus className="w-3 h-3" />
                        </button>
                      </div>

                      <button
                        onClick={() => removeFromCart(item.id)}
                        className="text-gray-400 hover:text-red-400 transition-colors"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {/* Total */}
              {cart.length > 0 && (
                <div className="mt-6 pt-4 border-t border-white/10">
                  <div className="flex items-center justify-between text-lg font-bold">
                    <span className="text-white">Total:</span>
                    <span className="text-emerald-400">R$ {getTotalPrice().toFixed(2)}</span>
                  </div>
                </div>
              )}
            </div>

            {/* Payment Methods */}
            {cart.length > 0 && (
              <div className="backdrop-blur-xl bg-gradient-to-br from-white/[0.08] to-white/[0.02] border border-white/10 rounded-2xl p-6">
                
                <h2 className="text-lg font-bold text-white mb-6">Forma de Pagamento</h2>
                
                <div className="grid grid-cols-2 gap-3 mb-6">
                  {paymentMethods.map((method) => (
                    <button
                      key={method.id}
                      onClick={() => setPaymentMethod(method.id)}
                      className={`p-4 rounded-xl border-2 transition-all duration-300 ${
                        paymentMethod === method.id
                          ? `border-${method.color}-500/50 bg-${method.color}-500/10`
                          : 'border-white/10 bg-white/[0.03] hover:bg-white/[0.08]'
                      }`}
                    >
                      <method.icon className={`w-6 h-6 text-${method.color}-400 mx-auto mb-2`} />
                      <div className="text-white text-sm font-semibold">{method.name}</div>
                    </button>
                  ))}
                </div>

                {/* Process Payment Button */}
                <button
                  onClick={processPayment}
                  disabled={isProcessing}
                  className="w-full group relative overflow-hidden bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-500 hover:to-blue-500 text-white py-4 px-6 rounded-xl font-bold text-lg transition-all duration-500 transform hover:scale-105 disabled:opacity-70 disabled:cursor-not-allowed shadow-2xl"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                  
                  {isProcessing ? (
                    <div className="flex items-center justify-center space-x-3">
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      <span>Processando...</span>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center space-x-3">
                      <CreditCard className="w-5 h-5" />
                      <span>Finalizar Pagamento</span>
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </div>
                  )}
                </button>
              </div>
            )}
          </div>

          {/* AI Insights & Recent Sales */}
          <div className="space-y-6">
            
            {/* AI Recommendations */}
            <div className="backdrop-blur-xl bg-gradient-to-br from-purple-500/[0.08] to-pink-500/[0.02] border border-purple-500/20 rounded-2xl p-6">
              
              <div className="flex items-center space-x-3 mb-6">
                <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-2 rounded-xl">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <h2 className="text-lg font-bold text-white">IA Recomenda</h2>
              </div>

              <div className="space-y-3">
                {aiRecommendations.map((rec, index) => (
                  <div key={index} className="backdrop-blur-sm bg-white/[0.05] border border-white/[0.08] rounded-xl p-4">
                    
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-white font-semibold text-sm">{rec.product}</h3>
                      <div className="bg-purple-500/20 text-purple-400 px-2 py-1 rounded-lg text-xs font-semibold">
                        {rec.confidence}%
                      </div>
                    </div>

                    <p className="text-gray-400 text-xs mb-3">{rec.reason}</p>

                    <button className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white py-2 rounded-lg text-sm font-semibold transition-all duration-300">
                      Promover Agora
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Sales */}
            <div className="backdrop-blur-xl bg-gradient-to-br from-white/[0.08] to-white/[0.02] border border-white/10 rounded-2xl p-6">
              
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-bold text-white">Vendas Recentes</h2>
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              </div>

              <div className="space-y-3">
                {recentSales.map((sale) => (
                  <div key={sale.id} className="flex items-center justify-between p-3 bg-white/[0.03] border border-white/[0.08] rounded-xl">
                    
                    <div>
                      <div className="text-white text-sm font-semibold">
                        {sale.items} {sale.items === 1 ? 'item' : 'itens'}
                      </div>
                      <div className="text-gray-400 text-xs">
                        {sale.method} • {sale.time}
                      </div>
                    </div>

                    <div className="text-emerald-400 font-bold">
                      R$ {sale.total}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="backdrop-blur-xl bg-gradient-to-br from-white/[0.08] to-white/[0.02] border border-white/10 rounded-2xl p-6">
              
              <h2 className="text-lg font-bold text-white mb-6">Ações Rápidas</h2>

              <div className="grid grid-cols-2 gap-3">
                {[
                  { label: 'Imprimir', icon: Printer, color: 'blue' },
                  { label: 'Relatórios', icon: BarChart3, color: 'purple' },
                  { label: 'Configurar', icon: Settings, color: 'gray' },
                  { label: 'Exportar', icon: Download, color: 'emerald' }
                ].map((action, index) => (
                  <button
                    key={index}
                    className={`group p-3 rounded-xl bg-${action.color}-500/10 border border-${action.color}-500/20 text-${action.color}-400 hover:bg-${action.color}-500/20 hover:border-${action.color}-500/40 transition-all duration-300`}
                  >
                    <action.icon className="w-5 h-5 mx-auto mb-2 group-hover:scale-110 transition-transform" />
                    <div className="text-xs font-semibold">{action.label}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 2px;
        }
        
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(139, 92, 246, 0.5);
          border-radius: 2px;
        }
        
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(139, 92, 246, 0.7);
        }
      `}</style>
    </div>
  );
};

export default UltraModernPDV;
