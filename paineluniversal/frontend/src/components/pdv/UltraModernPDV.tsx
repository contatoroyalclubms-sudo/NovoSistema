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
    <div className="fixed inset-0 w-full h-full bg-black overflow-hidden">
      
      {/* Neural Background Avançado */}
      <div className="absolute inset-0 z-0">
        {/* Camada Base Neural */}
        <div 
          className="absolute inset-0"
          style={{
            background: `
              linear-gradient(135deg, #000000 0%, #0a0a0a 25%, #1a1a1a 50%, #0a0a0a 75%, #000000 100%),
              radial-gradient(circle at 20% 20%, rgba(16, 185, 129, 0.15) 0%, transparent 40%),
              radial-gradient(circle at 80% 20%, rgba(59, 130, 246, 0.15) 0%, transparent 40%),
              radial-gradient(circle at 20% 80%, rgba(139, 92, 246, 0.15) 0%, transparent 40%),
              radial-gradient(circle at 80% 80%, rgba(236, 72, 153, 0.15) 0%, transparent 40%),
              radial-gradient(circle at ${mousePosition.x}% ${mousePosition.y}%, rgba(139, 92, 246, 0.1) 0%, transparent 30%)
            `
          }}
        />
        
        {/* Linhas Neurais Animadas */}
        <div className="absolute inset-0">
          <svg className="w-full h-full opacity-20" style={{ filter: 'blur(0.5px)' }}>
            <defs>
              <pattern id="neural-grid" width="100" height="100" patternUnits="userSpaceOnUse">
                <path d="M 100 0 L 0 0 0 100" fill="none" stroke="rgba(139, 92, 246, 0.3)" strokeWidth="0.5"/>
              </pattern>
              <linearGradient id="neural-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="rgba(16, 185, 129, 0.8)" />
                <stop offset="50%" stopColor="rgba(59, 130, 246, 0.8)" />
                <stop offset="100%" stopColor="rgba(139, 92, 246, 0.8)" />
              </linearGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#neural-grid)" />
          </svg>
        </div>

        {/* Partículas Flutuantes */}
        <div className="absolute inset-0 overflow-hidden">
          {[...Array(12)].map((_, i) => (
            <div
              key={i}
              className="absolute rounded-full opacity-30 animate-pulse"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                width: `${Math.random() * 4 + 2}px`,
                height: `${Math.random() * 4 + 2}px`,
                background: ['#10b981', '#3b82f6', '#8b5cf6', '#ec4899'][Math.floor(Math.random() * 4)],
                animationDelay: `${Math.random() * 3}s`,
                animationDuration: `${Math.random() * 3 + 2}s`
              }}
            />
          ))}
        </div>

        {/* Gradiente de Sobreposição */}
        <div className="absolute inset-0 bg-gradient-to-br from-black/50 via-transparent to-black/30" />
      </div>

      <div className="relative z-10 w-full h-full overflow-y-auto p-6" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
        
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
              <div key={index} className="relative backdrop-blur-xl bg-gradient-to-br from-gray-900/80 to-gray-800/60 rounded-xl p-4 text-center min-w-[120px] shadow-2xl border border-gray-700/50 hover:border-purple-500/50 transition-all duration-300">
                <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 via-blue-500/10 to-purple-500/10 rounded-xl" />
                <div className="relative z-10">
                  <div className={`bg-gradient-to-br from-${stat.color}-500/30 to-${stat.color}-600/20 p-2 rounded-lg w-fit mx-auto mb-2 shadow-lg`}>
                    <stat.icon className={`w-5 h-5 text-${stat.color}-300`} />
                  </div>
                  <div className="text-xl font-bold text-white">{stat.value}</div>
                  <div className="text-xs text-gray-300">{stat.label}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="grid lg:grid-cols-4 gap-6">
          
          {/* Product Categories & Items */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Categories */}
            <div className="backdrop-blur-xl bg-gradient-to-br from-gray-900/80 to-gray-800/60 border border-gray-700/50 rounded-2xl p-6 shadow-2xl">
              
              <h2 className="text-xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent mb-6">Categorias</h2>
              
              <div className="grid grid-cols-3 gap-4">
                {categories.map((category) => (
                  <button
                    key={category.id}
                    onClick={() => setSelectedCategory(category.id)}
                    className={`p-4 rounded-xl border-2 transition-all duration-300 ${
                      selectedCategory === category.id
                        ? `border-${category.color}-500/70 bg-gradient-to-br from-${category.color}-500/20 to-${category.color}-600/10 shadow-lg shadow-${category.color}-500/20`
                        : 'border-gray-600/50 bg-gradient-to-br from-gray-800/60 to-gray-900/40 hover:bg-gradient-to-br hover:from-gray-700/60 hover:to-gray-800/40 hover:border-gray-500/50'
                    }`}
                  >
                    <div className="text-3xl mb-2">{category.icon}</div>
                    <div className="text-white font-semibold text-sm">{category.name}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Products Grid */}
            <div className="backdrop-blur-xl bg-gradient-to-br from-gray-900/80 to-gray-800/60 border border-gray-700/50 rounded-2xl p-6 shadow-2xl">
              
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                  {categories.find(c => c.id === selectedCategory)?.name}
                </h2>
                
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Buscar produtos..."
                    className="bg-gray-800/50 border border-gray-600/50 rounded-xl pl-10 pr-4 py-2 text-white placeholder-gray-400 focus:bg-gray-700/50 focus:border-purple-500/50 transition-all"
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4 max-h-96 overflow-y-auto custom-scrollbar">
                {filteredProducts.map((product) => (
                  <div key={product.id} className="group relative backdrop-blur-sm bg-gradient-to-br from-gray-800/60 to-gray-900/40 border border-gray-600/30 rounded-xl p-4 hover:bg-gradient-to-br hover:from-gray-700/60 hover:to-gray-800/40 hover:border-gray-500/50 transition-all duration-300 shadow-lg">
                    
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
            <div className="backdrop-blur-xl bg-gradient-to-br from-gray-900/80 to-gray-800/60 border border-gray-700/50 rounded-2xl p-6 shadow-2xl">
              
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">Carrinho</h2>
                <div className="flex items-center space-x-2 bg-gradient-to-r from-emerald-500/30 to-emerald-600/20 text-emerald-300 px-3 py-1 rounded-full text-sm font-semibold border border-emerald-500/30">
                  <ShoppingCart className="w-4 h-4" />
                  <span>{getTotalItems()}</span>
                </div>
              </div>

              {cart.length === 0 ? (
                <div className="text-center py-8">
                  <ShoppingCart className="w-16 h-16 text-gray-500 mx-auto mb-4" />
                  <p className="text-gray-400">Carrinho vazio</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-64 overflow-y-auto custom-scrollbar">
                  {cart.map((item) => (
                    <div key={item.id} className="flex items-center space-x-3 p-3 bg-gradient-to-br from-gray-800/60 to-gray-900/40 border border-gray-600/30 rounded-xl hover:bg-gradient-to-br hover:from-gray-700/60 hover:to-gray-800/40 transition-all duration-300">
                      
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
              <div className="backdrop-blur-xl bg-gradient-to-br from-gray-900/80 to-gray-800/60 border border-gray-700/50 rounded-2xl p-6 shadow-2xl">
                
                <h2 className="text-lg font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent mb-6">Forma de Pagamento</h2>
                
                <div className="grid grid-cols-2 gap-3 mb-6">
                  {paymentMethods.map((method) => (
                    <button
                      key={method.id}
                      onClick={() => setPaymentMethod(method.id)}
                      className={`p-4 rounded-xl border-2 transition-all duration-300 ${
                        paymentMethod === method.id
                          ? `border-${method.color}-500/70 bg-gradient-to-br from-${method.color}-500/20 to-${method.color}-600/10 shadow-lg shadow-${method.color}-500/20`
                          : 'border-gray-600/50 bg-gradient-to-br from-gray-800/60 to-gray-900/40 hover:bg-gradient-to-br hover:from-gray-700/60 hover:to-gray-800/40 hover:border-gray-500/50'
                      }`}
                    >
                      <method.icon className={`w-6 h-6 text-${method.color}-300 mx-auto mb-2`} />
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
            <div className="backdrop-blur-xl bg-gradient-to-br from-purple-900/60 to-pink-900/40 border border-purple-500/30 rounded-2xl p-6 shadow-2xl shadow-purple-500/10">
              
              <div className="flex items-center space-x-3 mb-6">
                <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-2 rounded-xl shadow-lg">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <h2 className="text-lg font-bold bg-gradient-to-r from-purple-200 to-pink-200 bg-clip-text text-transparent">IA Recomenda</h2>
              </div>

              <div className="space-y-3">
                {aiRecommendations.map((rec, index) => (
                  <div key={index} className="backdrop-blur-sm bg-gradient-to-br from-purple-800/40 to-pink-800/20 border border-purple-600/30 rounded-xl p-4 hover:bg-gradient-to-br hover:from-purple-700/40 hover:to-pink-700/20 transition-all duration-300">
                    
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-white font-semibold text-sm">{rec.product}</h3>
                      <div className="bg-gradient-to-r from-purple-500/30 to-pink-500/20 text-purple-300 px-2 py-1 rounded-lg text-xs font-semibold border border-purple-500/30">
                        {rec.confidence}%
                      </div>
                    </div>

                    <p className="text-gray-300 text-xs mb-3">{rec.reason}</p>

                    <button className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white py-2 rounded-lg text-sm font-semibold transition-all duration-300 shadow-lg">
                      Promover Agora
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Sales */}
            <div className="backdrop-blur-xl bg-gradient-to-br from-gray-900/80 to-gray-800/60 border border-gray-700/50 rounded-2xl p-6 shadow-2xl">
              
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">Vendas Recentes</h2>
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse shadow-lg shadow-green-400/50" />
              </div>

              <div className="space-y-3">
                {recentSales.map((sale) => (
                  <div key={sale.id} className="flex items-center justify-between p-3 bg-gradient-to-br from-gray-800/60 to-gray-900/40 border border-gray-600/30 rounded-xl hover:bg-gradient-to-br hover:from-gray-700/60 hover:to-gray-800/40 transition-all duration-300">
                    
                    <div>
                      <div className="text-white text-sm font-semibold">
                        {sale.items} {sale.items === 1 ? 'item' : 'itens'}
                      </div>
                      <div className="text-gray-300 text-xs">
                        {sale.method} • {sale.time}
                      </div>
                    </div>

                    <div className="text-emerald-300 font-bold">
                      R$ {sale.total}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="backdrop-blur-xl bg-gradient-to-br from-gray-900/80 to-gray-800/60 border border-gray-700/50 rounded-2xl p-6 shadow-2xl">
              
              <h2 className="text-lg font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent mb-6">Ações Rápidas</h2>

              <div className="grid grid-cols-2 gap-3">
                {[
                  { label: 'Imprimir', icon: Printer, color: 'blue' },
                  { label: 'Relatórios', icon: BarChart3, color: 'purple' },
                  { label: 'Configurar', icon: Settings, color: 'gray' },
                  { label: 'Exportar', icon: Download, color: 'emerald' }
                ].map((action, index) => (
                  <button
                    key={index}
                    className={`group p-3 rounded-xl bg-gradient-to-br from-${action.color}-500/20 to-${action.color}-600/10 border border-${action.color}-500/30 text-${action.color}-300 hover:bg-gradient-to-br hover:from-${action.color}-500/30 hover:to-${action.color}-600/20 hover:border-${action.color}-500/50 transition-all duration-300 shadow-lg`}
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
        /* Hide scrollbar for the main container */
        .overflow-y-auto::-webkit-scrollbar {
          display: none;
        }
        
        .overflow-y-auto {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }

        /* Custom scrollbar for product grids and cart */
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(75, 85, 99, 0.3);
          border-radius: 3px;
        }
        
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: linear-gradient(135deg, rgba(139, 92, 246, 0.7), rgba(59, 130, 246, 0.7));
          border-radius: 3px;
          box-shadow: 0 2px 4px rgba(139, 92, 246, 0.3);
        }
        
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: linear-gradient(135deg, rgba(139, 92, 246, 0.9), rgba(59, 130, 246, 0.9));
          box-shadow: 0 4px 8px rgba(139, 92, 246, 0.5);
        }

        /* Neural animation effects */
        @keyframes neural-pulse {
          0%, 100% { opacity: 0.2; }
          50% { opacity: 0.8; }
        }

        .neural-element {
          animation: neural-pulse 4s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
};

export default UltraModernPDV;
