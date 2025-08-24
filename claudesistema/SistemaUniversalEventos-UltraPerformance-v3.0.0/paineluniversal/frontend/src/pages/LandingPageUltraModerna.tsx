import React, { useState, useEffect, useRef } from 'react'
import { motion, useAnimation, useInView, AnimatePresence } from 'framer-motion'
import { 
  Brain, 
  Sparkles, 
  QrCode, 
  Fingerprint, 
  ShoppingCart, 
  CreditCard, 
  Trophy, 
  Target, 
  BarChart3, 
  Activity, 
  Bot, 
  Cpu, 
  CheckCircle,
  Star,
  ArrowRight,
  Zap,
  Shield,
  Users,
  Globe,
  Clock,
  Eye,
  TrendingUp,
  Play,
  X,
  ChevronDown,
  Menu,
  ChevronRight,
  Calendar
} from 'lucide-react'

// Componente de partículas flutuantes avançado
const AdvancedFloatingParticles = () => {
  const [particles, setParticles] = useState([])

  useEffect(() => {
    const newParticles = [...Array(60)].map((_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 6 + 2,
      duration: Math.random() * 20 + 15,
      delay: Math.random() * 5
    }))
    setParticles(newParticles)
  }, [])

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          className="absolute rounded-full"
          style={{
            background: `linear-gradient(45deg, 
              rgba(139, 92, 246, 0.4), 
              rgba(236, 72, 153, 0.4), 
              rgba(6, 182, 212, 0.4)
            )`,
            width: `${particle.size}px`,
            height: `${particle.size}px`,
            left: `${particle.x}%`,
            top: `${particle.y}%`,
          }}
          animate={{
            x: [0, Math.random() * 200 - 100, 0],
            y: [0, Math.random() * 200 - 100, 0],
            scale: [0.5, 1.2, 0.5],
            opacity: [0.2, 0.8, 0.2],
          }}
          transition={{
            duration: particle.duration,
            delay: particle.delay,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      ))}
    </div>
  )
}

// Componente de contador animado melhorado
const AnimatedCounter = ({ end, duration = 2, suffix = "", prefix = "" }) => {
  const [count, setCount] = useState(0)
  const ref = useRef(null)
  const inView = useInView(ref, { once: true })

  useEffect(() => {
    if (inView) {
      let startTime
      const animateCount = (timestamp) => {
        if (!startTime) startTime = timestamp
        const progress = Math.min((timestamp - startTime) / (duration * 1000), 1)
        
        const easeOutQuart = 1 - Math.pow(1 - progress, 4)
        setCount(Math.floor(easeOutQuart * end))
        
        if (progress < 1) {
          requestAnimationFrame(animateCount)
        }
      }
      requestAnimationFrame(animateCount)
    }
  }, [inView, end, duration])

  return (
    <span ref={ref} className="font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400">
      {prefix}{count.toLocaleString()}{suffix}
    </span>
  )
}

// Componente de badge pulsante melhorado
const EnhancedPulseBadge = () => (
  <motion.div
    className="inline-flex items-center px-6 py-3 rounded-full bg-gradient-to-r from-emerald-500/20 to-green-500/20 border border-emerald-500/40 backdrop-blur-sm"
    animate={{ 
      scale: [1, 1.05, 1],
      boxShadow: [
        "0 0 20px rgba(16, 185, 129, 0.3)",
        "0 0 40px rgba(16, 185, 129, 0.5)",
        "0 0 20px rgba(16, 185, 129, 0.3)"
      ]
    }}
    transition={{ duration: 2, repeat: Infinity }}
  >
    <motion.div 
      className="w-3 h-3 bg-emerald-400 rounded-full mr-3" 
      animate={{ opacity: [0.5, 1, 0.5] }}
      transition={{ duration: 1.5, repeat: Infinity }}
    />
    <span className="text-emerald-400 font-bold text-sm tracking-wide">SISTEMA EM FUNCIONAMENTO</span>
  </motion.div>
)

// Navigation aprimorada
const Navigation = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <motion.nav 
      className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        scrolled 
          ? 'bg-slate-900/90 backdrop-blur-xl border-b border-slate-800/50 shadow-2xl' 
          : 'bg-transparent'
      }`}
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          <motion.div 
            className="flex items-center space-x-3"
            whileHover={{ scale: 1.05 }}
          >
            <div className="relative">
              <motion.div 
                className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl blur-lg opacity-50"
                animate={{ opacity: [0.3, 0.7, 0.3] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
              <div className="relative bg-gradient-to-r from-purple-500 to-pink-500 p-3 rounded-xl">
                <Calendar className="w-8 h-8 text-white" />
              </div>
            </div>
            <span className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400">
              EventosIA
            </span>
          </motion.div>
          
          <div className="hidden md:flex items-center space-x-8">
            {['Funcionalidades', 'Demo', 'Depoimentos', 'Preços'].map((item, index) => (
              <motion.a
                key={item}
                href={`#${item.toLowerCase()}`}
                className="text-slate-300 hover:text-white px-4 py-2 rounded-lg font-medium transition-all duration-300 hover:bg-white/10"
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.95 }}
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                {item}
              </motion.a>
            ))}
          </div>

          <div className="hidden md:block">
            <motion.button
              className="relative group bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-3 rounded-xl font-bold overflow-hidden"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
            >
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0"
                animate={{ x: [-100, 300] }}
                transition={{ duration: 1.5, repeat: Infinity, repeatDelay: 1 }}
              />
              <span className="relative">TESTE GRÁTIS</span>
            </motion.button>
          </div>

          <motion.button 
            className="md:hidden relative z-10"
            onClick={() => setIsOpen(!isOpen)}
            whileTap={{ scale: 0.9 }}
          >
            <motion.div
              animate={{ rotate: isOpen ? 180 : 0 }}
              transition={{ duration: 0.3 }}
            >
              {isOpen ? <X className="h-6 w-6 text-white" /> : <Menu className="h-6 w-6 text-white" />}
            </motion.div>
          </motion.button>
        </div>
      </div>

      <AnimatePresence>
        {isOpen && (
          <motion.div 
            className="md:hidden absolute top-full left-0 right-0 bg-slate-900/95 backdrop-blur-xl border-b border-slate-800"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="px-4 py-6 space-y-4">
              {['Funcionalidades', 'Demo', 'Depoimentos', 'Preços'].map((item, index) => (
                <motion.a
                  key={item}
                  href={`#${item.toLowerCase()}`}
                  className="block text-slate-300 hover:text-white px-4 py-3 rounded-lg font-medium transition-colors hover:bg-white/10"
                  onClick={() => setIsOpen(false)}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  {item}
                </motion.a>
              ))}
              <motion.button
                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-xl font-bold"
                whileTap={{ scale: 0.95 }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.4 }}
              >
                TESTE GRÁTIS
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  )
}

// Hero Section ultra-moderna
const HeroSection = () => {
  const [currentWord, setCurrentWord] = useState(0)
  const words = ['Inteligentes', 'Inovadores', 'Automatizados', 'Futuristas']

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentWord((prev) => (prev + 1) % words.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background gradiente animado */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900/20 to-pink-900/20">
        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-purple-600/10 via-transparent to-pink-600/10"
          animate={{
            background: [
              "linear-gradient(45deg, rgba(139, 92, 246, 0.1), transparent, rgba(236, 72, 153, 0.1))",
              "linear-gradient(225deg, rgba(236, 72, 153, 0.1), transparent, rgba(6, 182, 212, 0.1))",
              "linear-gradient(45deg, rgba(139, 92, 246, 0.1), transparent, rgba(236, 72, 153, 0.1))"
            ]
          }}
          transition={{ duration: 8, repeat: Infinity }}
        />
      </div>
      
      <AdvancedFloatingParticles />
      
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-32">
        <div className="text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="mb-8"
          >
            <EnhancedPulseBadge />
          </motion.div>

          <motion.h1
            className="text-6xl md:text-8xl font-black text-white mb-8 leading-tight"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.2 }}
          >
            <span className="block">
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400">
                Eventos
              </span>
            </span>
            <span className="block relative">
              <AnimatePresence mode="wait">
                <motion.span
                  key={currentWord}
                  className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400"
                  initial={{ opacity: 0, y: 20, rotateX: -90 }}
                  animate={{ opacity: 1, y: 0, rotateX: 0 }}
                  exit={{ opacity: 0, y: -20, rotateX: 90 }}
                  transition={{ duration: 0.5 }}
                >
                  {words[currentWord]}
                </motion.span>
              </AnimatePresence>
            </span>
            <span className="block">
              <span className="text-white">com IA</span>
            </span>
          </motion.h1>

          <motion.p
            className="text-2xl md:text-3xl text-slate-300 mb-12 max-w-5xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            Plataforma revolucionária que transforma eventos em 
            <motion.span 
              className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 font-bold"
              animate={{ 
                backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"]
              }}
              transition={{ duration: 3, repeat: Infinity }}
            >
              {" "}experiências inesquecíveis
            </motion.span>
          </motion.p>

          <motion.div
            className="flex flex-col sm:flex-row gap-8 justify-center items-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
          >
            <motion.button
              className="group relative overflow-hidden bg-gradient-to-r from-purple-600 to-pink-600 text-white px-12 py-6 rounded-2xl font-bold text-xl shadow-2xl"
              whileHover={{ 
                scale: 1.05,
                boxShadow: "0 25px 50px -12px rgba(139, 92, 246, 0.5)"
              }}
              whileTap={{ scale: 0.95 }}
            >
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/30 to-white/0"
                animate={{ x: [-300, 300] }}
                transition={{ duration: 2, repeat: Infinity, repeatDelay: 1 }}
              />
              <span className="relative flex items-center">
                TESTE GRÁTIS POR 30 DIAS
                <motion.div
                  className="ml-3"
                  animate={{ x: [0, 5, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  <ArrowRight className="w-6 h-6" />
                </motion.div>
              </span>
            </motion.button>

            <motion.button
              className="group border-2 border-purple-500 text-purple-400 px-12 py-6 rounded-2xl font-bold text-xl hover:bg-purple-500/10 transition-all backdrop-blur-sm"
              whileHover={{ scale: 1.05, borderColor: "#EC4899" }}
              whileTap={{ scale: 0.95 }}
            >
              <span className="flex items-center">
                <motion.div
                  className="mr-3"
                  whileHover={{ scale: 1.2, rotate: 360 }}
                  transition={{ duration: 0.5 }}
                >
                  <Play className="w-6 h-6" />
                </motion.div>
                VER DEMO AO VIVO
              </span>
            </motion.button>
          </motion.div>

          <motion.div
            className="grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-4xl mx-auto"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1 }}
          >
            {[
              { icon: CheckCircle, text: "Sem cartão de crédito" },
              { icon: Zap, text: "Setup em 5 minutos" },
              { icon: Shield, text: "Suporte 24/7" }
            ].map((item, index) => (
              <motion.div
                key={index}
                className="flex items-center justify-center space-x-3 p-4 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10"
                whileHover={{ scale: 1.05, backgroundColor: "rgba(255, 255, 255, 0.1)" }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 1.2 + index * 0.1 }}
              >
                <item.icon className="w-6 h-6 text-emerald-400" />
                <span className="text-slate-300 font-medium">{item.text}</span>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>

      <motion.div
        className="absolute bottom-10 left-1/2 transform -translate-x-1/2"
        animate={{ y: [0, 15, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <ChevronDown className="w-10 h-10 text-slate-400" />
      </motion.div>
    </section>
  )
}

// Features Section ultra-avançada
const FeaturesSection = () => {
  const features = [
    {
      icon: Brain,
      title: "Gestão de Eventos com IA",
      description: "Crie eventos em segundos com nossa IA avançada",
      details: ["Descrições automáticas", "Copy de marketing", "Análise de feedback"],
      gradient: "from-purple-500 via-purple-600 to-indigo-600",
      delay: 0
    },
    {
      icon: Fingerprint,
      title: "Check-in Inteligente",
      description: "Check-in por CPF, QR Code ou biometria facial",
      details: ["Reconhecimento facial", "Validação instantânea", "Controle de presença"],
      gradient: "from-pink-500 via-rose-600 to-red-600",
      delay: 0.1
    },
    {
      icon: ShoppingCart,
      title: "PDV Completo Integrado",
      description: "Venda produtos direto no evento",
      details: ["Estoque em tempo real", "Pagamentos múltiplos", "Relatórios"],
      gradient: "from-cyan-500 via-blue-600 to-indigo-600",
      delay: 0.2
    },
    {
      icon: Trophy,
      title: "Gamificação para Promoters",
      description: "Sistema de ranking e recompensas",
      details: ["XP e badges", "Competições", "Métricas"],
      gradient: "from-emerald-500 via-green-600 to-teal-600",
      delay: 0.3
    },
    {
      icon: BarChart3,
      title: "Dashboard em Tempo Real",
      description: "Acompanhe tudo ao vivo",
      details: ["Métricas live", "Relatórios", "Analytics"],
      gradient: "from-orange-500 via-red-600 to-pink-600",
      delay: 0.4
    },
    {
      icon: Bot,
      title: "Inteligência Artificial Integrada",
      description: "IA que entende seus eventos",
      details: ["Ideias de eventos", "Otimização", "Análises preditivas"],
      gradient: "from-violet-500 via-purple-600 to-indigo-600",
      delay: 0.5
    }
  ]

  return (
    <section id="funcionalidades" className="py-32 bg-slate-900 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900/5 via-transparent to-pink-900/5"></div>
      
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          className="text-center mb-24"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
        >
          <motion.h2 
            className="text-5xl md:text-7xl font-black text-white mb-8"
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            viewport={{ once: true }}
          >
            Funcionalidades
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400">
              Revolucionárias
            </span>
          </motion.h2>
          <motion.p 
            className="text-2xl text-slate-300 max-w-4xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            viewport={{ once: true }}
          >
            Tecnologia de ponta que transforma eventos simples em experiências extraordinárias
          </motion.p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              className="group relative"
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: feature.delay }}
              viewport={{ once: true }}
              whileHover={{ scale: 1.05 }}
            >
              {/* Glow effect */}
              <motion.div
                className={`absolute inset-0 bg-gradient-to-r ${feature.gradient} rounded-3xl blur-xl opacity-0 group-hover:opacity-30 transition-opacity duration-500`}
                whileHover={{ scale: 1.1 }}
              />
              
              <div className="relative bg-slate-800/40 backdrop-blur-xl rounded-3xl p-8 border border-slate-700/50 group-hover:border-slate-600/50 transition-all duration-500 h-full">
                {/* Icon container */}
                <motion.div
                  className={`w-20 h-20 rounded-2xl bg-gradient-to-r ${feature.gradient} flex items-center justify-center mb-8 group-hover:scale-110 transition-transform duration-300`}
                  whileHover={{ rotate: 360 }}
                  transition={{ duration: 0.6 }}
                >
                  <feature.icon className="w-10 h-10 text-white" />
                </motion.div>

                <motion.h3 
                  className="text-2xl font-bold text-white mb-4 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-purple-400 group-hover:to-pink-400 transition-all duration-300"
                  whileHover={{ scale: 1.05 }}
                >
                  {feature.title}
                </motion.h3>

                <p className="text-slate-300 mb-8 text-lg leading-relaxed">
                  {feature.description}
                </p>

                <ul className="space-y-3">
                  {feature.details.map((detail, i) => (
                    <motion.li 
                      key={i} 
                      className="flex items-center text-slate-400"
                      initial={{ opacity: 0, x: -20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.5, delay: 0.6 + i * 0.1 }}
                      viewport={{ once: true }}
                    >
                      <CheckCircle className="w-5 h-5 text-emerald-400 mr-3 flex-shrink-0" />
                      <span className="group-hover:text-slate-300 transition-colors">{detail}</span>
                    </motion.li>
                  ))}
                </ul>

                {/* Hover overlay */}
                <motion.div
                  className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-5 rounded-3xl transition-opacity duration-500`}
                />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

// Stats Section impressionante
const StatsSection = () => {
  const stats = [
    { number: 10000, suffix: "+", label: "Eventos Realizados", icon: Calendar, prefix: "" },
    { number: 500000, suffix: "+", label: "Check-ins Processados", icon: Users, prefix: "" },
    { number: 2.5, suffix: "M+", label: "em Vendas Processadas", prefix: "R$ ", icon: TrendingUp },
    { number: 98, suffix: "%", label: "Satisfação dos Clientes", icon: Trophy, prefix: "" },
    { number: 2, suffix: "s", label: "Tempo de Check-in", prefix: "< ", icon: Clock },
    { number: 24, suffix: "/7", label: "Uptime Garantido", icon: Shield, prefix: "" }
  ]

  return (
    <section className="py-32 relative overflow-hidden">
      {/* Background gradiente dinâmico */}
      <motion.div 
        className="absolute inset-0 bg-gradient-to-br from-slate-800 via-slate-900 to-slate-800"
        animate={{
          background: [
            "linear-gradient(to bottom right, #1e293b, #0f172a, #1e293b)",
            "linear-gradient(to bottom right, #1e293b, #7c3aed20, #0f172a)",
            "linear-gradient(to bottom right, #1e293b, #0f172a, #1e293b)"
          ]
        }}
        transition={{ duration: 8, repeat: Infinity }}
      />
      
      {/* Partículas flutuantes */}
      <div className="absolute inset-0">
        {[...Array(30)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-purple-400/20 rounded-full"
            animate={{
              scale: [0, 1.5, 0],
              opacity: [0, 0.8, 0]
            }}
            transition={{
              duration: Math.random() * 4 + 3,
              repeat: Infinity,
              delay: Math.random() * 3
            }}
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
          />
        ))}
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          className="text-center mb-20"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
        >
          <h2 className="text-5xl md:text-7xl font-black text-white mb-8">
            Números que
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400">
              Impressionam
            </span>
          </h2>
          <p className="text-2xl text-slate-300 max-w-4xl mx-auto">
            Resultados reais de clientes que já transformaram seus eventos
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              className="group text-center"
              initial={{ opacity: 0, scale: 0.5, y: 50 }}
              whileInView={{ opacity: 1, scale: 1, y: 0 }}
              transition={{ 
                duration: 0.8, 
                delay: index * 0.1,
                type: "spring",
                stiffness: 100 
              }}
              viewport={{ once: true }}
              whileHover={{ scale: 1.05 }}
            >
              <motion.div
                className="relative bg-slate-800/40 backdrop-blur-xl rounded-3xl p-8 border border-slate-700/50 group-hover:border-purple-500/50 transition-all duration-500"
                whileHover={{
                  boxShadow: "0 25px 50px -12px rgba(139, 92, 246, 0.3)"
                }}
              >
                {/* Icon com efeito glow */}
                <motion.div
                  className="w-20 h-20 mx-auto mb-6 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300 relative"
                  whileHover={{ rotate: 360 }}
                  transition={{ duration: 0.8 }}
                >
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl blur-xl opacity-0 group-hover:opacity-50 transition-opacity duration-300"
                  />
                  <stat.icon className="w-10 h-10 text-white relative z-10" />
                </motion.div>
                
                {/* Número com animação */}
                <div className="text-5xl md:text-6xl font-black mb-3">
                  {stat.prefix && <span className="text-slate-300">{stat.prefix}</span>}
                  <motion.span
                    className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400"
                    whileInView={{ scale: [0.5, 1.2, 1] }}
                    transition={{ duration: 0.8, delay: index * 0.1 + 0.5 }}
                    viewport={{ once: true }}
                  >
                    <AnimatedCounter end={stat.number} suffix={stat.suffix} />
                  </motion.span>
                </div>
                
                <p className="text-slate-300 text-xl font-medium">{stat.label}</p>

                {/* Overlay gradiente */}
                <motion.div
                  className="absolute inset-0 bg-gradient-to-br from-purple-600/0 to-pink-600/0 group-hover:from-purple-600/5 group-hover:to-pink-600/5 rounded-3xl transition-all duration-500"
                />
              </motion.div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

// Demo Visual Section
const DemoVisualSection = () => {
  const [activeDemo, setActiveDemo] = useState(0)
  
  const demos = [
    {
      title: "Dashboard em Ação",
      description: "Acompanhe métricas em tempo real",
      image: "📊",
      features: ["Dados ao vivo", "Gráficos interativos", "Alertas inteligentes"]
    },
    {
      title: "Check-in Biométrico",
      description: "Reconhecimento facial instantâneo",
      image: "👁️",
      features: ["Sem contato", "2 segundos", "99.9% precisão"]
    },
    {
      title: "PDV Integrado",
      description: "Vendas processadas automaticamente",
      image: "💳",
      features: ["Estoque sync", "Multi-pagamento", "Relatórios"]
    },
    {
      title: "Gamificação Live",
      description: "Rankings atualizados em tempo real",
      image: "🏆",
      features: ["XP ao vivo", "Competições", "Badges"]
    }
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveDemo((prev) => (prev + 1) % demos.length)
    }, 4000)
    return () => clearInterval(interval)
  }, [])

  return (
    <section className="py-32 bg-slate-900 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/10 to-purple-900/10"></div>
      
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          className="text-center mb-20"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
        >
          <h2 className="text-5xl md:text-7xl font-black text-white mb-8">
            Veja o Sistema
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400">
              em Funcionamento
            </span>
          </h2>
          <p className="text-2xl text-slate-300 max-w-4xl mx-auto">
            Demonstrações reais das funcionalidades que revolucionam eventos
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left - Demo Preview */}
          <motion.div
            className="relative"
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 1 }}
            viewport={{ once: true }}
          >
            <div className="relative bg-slate-800/40 backdrop-blur-xl rounded-3xl p-8 border border-slate-700/50">
              <motion.div
                className="text-8xl text-center mb-6"
                key={activeDemo}
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ duration: 0.8, type: "spring" }}
              >
                {demos[activeDemo].image}
              </motion.div>
              
              <motion.h3
                className="text-3xl font-bold text-white text-center mb-4"
                key={`title-${activeDemo}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                {demos[activeDemo].title}
              </motion.h3>
              
              <motion.p
                className="text-slate-300 text-center text-lg mb-8"
                key={`desc-${activeDemo}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 }}
              >
                {demos[activeDemo].description}
              </motion.p>

              <motion.div
                className="space-y-3"
                key={`features-${activeDemo}`}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5, delay: 0.4 }}
              >
                {demos[activeDemo].features.map((feature, index) => (
                  <motion.div
                    key={index}
                    className="flex items-center justify-center space-x-3 p-3 bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-xl"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: 0.5 + index * 0.1 }}
                  >
                    <CheckCircle className="w-5 h-5 text-emerald-400" />
                    <span className="text-slate-300 font-medium">{feature}</span>
                  </motion.div>
                ))}
              </motion.div>
            </div>
          </motion.div>

          {/* Right - Demo Navigation */}
          <motion.div
            className="space-y-6"
            initial={{ opacity: 0, x: 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 1 }}
            viewport={{ once: true }}
          >
            {demos.map((demo, index) => (
              <motion.button
                key={index}
                className={`w-full text-left p-6 rounded-2xl border transition-all duration-300 ${
                  activeDemo === index 
                    ? 'bg-gradient-to-r from-purple-600/20 to-pink-600/20 border-purple-500/50' 
                    : 'bg-slate-800/40 border-slate-700/50 hover:border-slate-600/50'
                }`}
                onClick={() => setActiveDemo(index)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="flex items-center space-x-4">
                  <div className={`text-4xl transition-transform duration-300 ${
                    activeDemo === index ? 'scale-110' : ''
                  }`}>
                    {demo.image}
                  </div>
                  <div>
                    <h4 className={`text-xl font-bold mb-2 transition-colors ${
                      activeDemo === index 
                        ? 'text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400' 
                        : 'text-white'
                    }`}>
                      {demo.title}
                    </h4>
                    <p className="text-slate-400">{demo.description}</p>
                  </div>
                </div>
              </motion.button>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  )
}

// Testimonials Section melhorada
const TestimonialsSection = () => {
  const testimonials = [
    {
      name: "Maria Silva",
      company: "Eventos Premium",
      role: "CEO",
      text: "Revolucionou completamente nossos eventos! O check-in biométrico eliminou filas e a IA nos ajuda a criar descrições perfeitas. Aumentamos a eficiência em 300%.",
      rating: 5,
      avatar: "MS",
      results: "300% + eficiência"
    },
    {
      name: "João Santos",
      company: "Mega Produções",
      role: "Diretor",
      text: "O PDV integrado foi um game-changer. Vendas aumentaram 150% e o controle de estoque em tempo real eliminou perdas. Suporte excepcional 24/7!",
      rating: 5,
      avatar: "JS",
      results: "150% + vendas"
    },
    {
      name: "Ana Costa",
      company: "Eventos Corporativos",
      role: "Gerente",
      text: "A gamificação motivou nossa equipe como nunca. Rankings em tempo real criaram uma competição saudável. Relatórios automáticos poupam horas!",
      rating: 5,
      avatar: "AC",
      results: "50% + produtividade"
    }
  ]

  return (
    <section id="depoimentos" className="py-32 bg-gradient-to-br from-slate-800 to-slate-900 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900/5 to-pink-900/5"></div>
      
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          className="text-center mb-24"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
        >
          <h2 className="text-5xl md:text-7xl font-black text-white mb-8">
            Histórias de
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400">
              Sucesso Real
            </span>
          </h2>
          <p className="text-2xl text-slate-300 max-w-4xl mx-auto">
            Veja como nossos clientes transformaram seus eventos e aumentaram resultados
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              className="group relative"
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: index * 0.2 }}
              viewport={{ once: true }}
              whileHover={{ scale: 1.05 }}
            >
              {/* Glow effect */}
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
              />
              
              <div className="relative bg-slate-800/40 backdrop-blur-xl rounded-3xl p-8 border border-slate-700/50 group-hover:border-purple-500/50 transition-all duration-500 h-full">
                {/* Rating stars */}
                <div className="flex items-center space-x-1 mb-6">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, scale: 0 }}
                      whileInView={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.3, delay: 0.6 + i * 0.1 }}
                      viewport={{ once: true }}
                    >
                      <Star className="w-6 h-6 text-yellow-400 fill-current" />
                    </motion.div>
                  ))}
                </div>

                {/* Results badge */}
                <motion.div
                  className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-emerald-500/20 to-green-500/20 border border-emerald-500/30 rounded-full mb-6"
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5, delay: 0.4 }}
                  viewport={{ once: true }}
                >
                  <TrendingUp className="w-4 h-4 text-emerald-400 mr-2" />
                  <span className="text-emerald-400 font-bold text-sm">{testimonial.results}</span>
                </motion.div>
                
                <motion.p
                  className="text-slate-300 mb-8 italic leading-relaxed text-lg"
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  transition={{ duration: 0.8, delay: 0.6 }}
                  viewport={{ once: true }}
                >
                  "{testimonial.text}"
                </motion.p>
                
                <motion.div
                  className="flex items-center space-x-4"
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.8 }}
                  viewport={{ once: true }}
                >
                  <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
                    {testimonial.avatar}
                  </div>
                  <div>
                    <p className="font-bold text-white text-lg">{testimonial.name}</p>
                    <p className="text-slate-400">{testimonial.role}</p>
                    <p className="text-purple-400 font-semibold">{testimonial.company}</p>
                  </div>
                </motion.div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

// Comparison Section ultra-avançada
const ComparisonSection = () => {
  const comparisons = [
    { feature: "IA Integrada", us: "Completa", competitors: "Não possui", icon: Brain },
    { feature: "Check-in Biométrico", us: "Facial + CPF", competitors: "Apenas QR", icon: Fingerprint },
    { feature: "PDV Completo", us: "Integrado", competitors: "Separado", icon: ShoppingCart },
    { feature: "Gamificação", us: "Avançada", competitors: "Não possui", icon: Trophy },
    { feature: "Tempo Real", us: "Total", competitors: "Limitado", icon: Activity },
    { feature: "Suporte", us: "24/7", competitors: "Comercial", icon: Shield }
  ]

  return (
    <section className="py-32 bg-slate-900 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900/5 to-pink-900/5"></div>
      
      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          className="text-center mb-20"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
        >
          <h2 className="text-5xl md:text-7xl font-black text-white mb-8">
            Por que Escolher
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400">
              Nossa Plataforma?
            </span>
          </h2>
          <p className="text-2xl text-slate-300 max-w-4xl mx-auto">
            Compare e veja por que somos a escolha inteligente
          </p>
        </motion.div>

        <motion.div
          className="bg-slate-800/40 backdrop-blur-xl rounded-3xl p-8 border border-slate-700/50"
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          {/* Header */}
          <div className="grid grid-cols-3 gap-8 mb-8 pb-6 border-b border-slate-700">
            <div className="text-center">
              <h3 className="text-2xl font-bold text-white">Funcionalidade</h3>
            </div>
            <div className="text-center">
              <h3 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
                EventosIA
              </h3>
            </div>
            <div className="text-center">
              <h3 className="text-2xl font-bold text-slate-400">Concorrentes</h3>
            </div>
          </div>

          {/* Comparison rows */}
          <div className="space-y-4">
            {comparisons.map((item, index) => (
              <motion.div
                key={index}
                className="grid grid-cols-3 gap-8 py-6 rounded-xl hover:bg-slate-700/20 transition-colors"
                initial={{ opacity: 0, x: -30 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-to-r from-slate-600 to-slate-700 rounded-xl flex items-center justify-center">
                    <item.icon className="w-6 h-6 text-slate-300" />
                  </div>
                  <span className="text-white font-semibold text-lg">{item.feature}</span>
                </div>
                
                <div className="flex items-center justify-center">
                  <motion.div
                    className="flex items-center space-x-3 bg-gradient-to-r from-emerald-500/10 to-green-500/10 px-4 py-2 rounded-xl border border-emerald-500/20"
                    whileHover={{ scale: 1.05 }}
                  >
                    <CheckCircle className="w-6 h-6 text-emerald-400" />
                    <span className="text-emerald-400 font-bold">{item.us}</span>
                  </motion.div>
                </div>
                
                <div className="flex items-center justify-center">
                  <div className="flex items-center space-x-3 bg-red-500/10 px-4 py-2 rounded-xl border border-red-500/20">
                    <X className="w-6 h-6 text-red-400" />
                    <span className="text-red-400 font-bold">{item.competitors}</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}

// CTA Section final épica
const CTASection = () => {
  return (
    <section className="py-32 relative overflow-hidden">
      {/* Background gradiente animado */}
      <motion.div 
        className="absolute inset-0 bg-gradient-to-br from-purple-900 via-slate-900 to-pink-900"
        animate={{
          background: [
            "linear-gradient(to bottom right, #581c87, #0f172a, #be185d)",
            "linear-gradient(to bottom right, #be185d, #581c87, #0f172a)",
            "linear-gradient(to bottom right, #0f172a, #be185d, #581c87)",
            "linear-gradient(to bottom right, #581c87, #0f172a, #be185d)"
          ]
        }}
        transition={{ duration: 8, repeat: Infinity }}
      />
      
      <AdvancedFloatingParticles />
      
      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
        >
          <motion.h2 
            className="text-6xl md:text-8xl font-black text-white mb-8"
            animate={{ 
              textShadow: [
                "0 0 20px rgba(139, 92, 246, 0.5)",
                "0 0 40px rgba(236, 72, 153, 0.5)",
                "0 0 60px rgba(6, 182, 212, 0.5)",
                "0 0 40px rgba(236, 72, 153, 0.5)",
                "0 0 20px rgba(139, 92, 246, 0.5)"
              ]
            }}
            transition={{ duration: 4, repeat: Infinity }}
          >
            Transforme seus
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400">
              eventos hoje
            </span>
          </motion.h2>

          <motion.p
            className="text-2xl text-slate-300 mb-12 max-w-4xl mx-auto"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            viewport={{ once: true }}
          >
            Junte-se a mais de <span className="text-purple-400 font-bold">1000 organizadores</span> que já revolucionaram seus eventos
          </motion.p>

          {/* Benefits grid */}
          <motion.div
            className="grid md:grid-cols-3 gap-8 mb-16 max-w-5xl mx-auto"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            viewport={{ once: true }}
          >
            {[
              { icon: Shield, title: "30 dias grátis", subtitle: "sem compromisso", color: "emerald" },
              { icon: Zap, title: "Setup gratuito", subtitle: "+ treinamento incluso", color: "purple" },
              { icon: Users, title: "Suporte 24/7", subtitle: "especializado", color: "cyan" }
            ].map((benefit, index) => (
              <motion.div
                key={index}
                className={`bg-slate-800/40 backdrop-blur-xl rounded-2xl p-8 border border-slate-700/50 hover:border-${benefit.color}-500/50 transition-all`}
                whileHover={{ scale: 1.05, y: -10 }}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.7 + index * 0.1 }}
                viewport={{ once: true }}
              >
                <benefit.icon className={`w-16 h-16 text-${benefit.color}-400 mx-auto mb-4`} />
                <p className="text-white font-bold text-xl mb-2">{benefit.title}</p>
                <p className="text-slate-400">{benefit.subtitle}</p>
              </motion.div>
            ))}
          </motion.div>

          {/* CTA buttons */}
          <motion.div
            className="flex flex-col sm:flex-row gap-8 justify-center items-center"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
            viewport={{ once: true }}
          >
            <motion.button
              className="group relative overflow-hidden bg-gradient-to-r from-purple-600 to-pink-600 text-white px-16 py-6 rounded-2xl font-bold text-2xl shadow-2xl"
              whileHover={{ 
                scale: 1.05,
                boxShadow: "0 25px 50px -12px rgba(139, 92, 246, 0.5)"
              }}
              whileTap={{ scale: 0.95 }}
            >
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/30 to-white/0"
                animate={{ x: [-400, 400] }}
                transition={{ duration: 2, repeat: Infinity, repeatDelay: 1.5 }}
              />
              <span className="relative flex items-center">
                COMEÇAR AGORA
                <motion.div
                  className="ml-4"
                  animate={{ x: [0, 10, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  <ArrowRight className="w-8 h-8" />
                </motion.div>
              </span>
            </motion.button>

            <motion.button
              className="border-2 border-white text-white px-16 py-6 rounded-2xl font-bold text-2xl hover:bg-white hover:text-slate-900 transition-all backdrop-blur-sm"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              FALAR COM ESPECIALISTA
            </motion.button>
          </motion.div>

          <motion.div
            className="mt-12 text-slate-400 text-lg"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 1 }}
            viewport={{ once: true }}
          >
            ✓ Sem cartão de crédito ✓ Ativação instantânea ✓ Garantia de satisfação
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}

// FAQ Section interativa
const FAQSection = () => {
  const [openFAQ, setOpenFAQ] = useState(null)

  const faqs = [
    {
      question: "Como funciona a integração com outros sistemas?",
      answer: "Nossa plataforma oferece APIs REST completas e webhooks para integração com qualquer sistema. Suportamos integrações nativas com CRMs, ERPs, sistemas de pagamento e plataformas de email marketing. Nossa equipe técnica oferece suporte completo durante a integração.",
      icon: Globe
    },
    {
      question: "O check-in biométrico é seguro e confiável?",
      answer: "Sim! Utilizamos tecnologia de reconhecimento facial de última geração com criptografia de ponta a ponta. Os dados biométricos são processados localmente e nunca armazenados em nossos servidores. Temos certificações ISO 27001 e LGPD.",
      icon: Shield
    },
    {
      question: "Quanto tempo leva para configurar o sistema?",
      answer: "A configuração básica leva apenas 5 minutos através do nosso setup wizard intuitivo. Para configurações avançadas e treinamento da equipe, nossa equipe oferece suporte completo gratuito que pode ser concluído em até 24 horas.",
      icon: Clock
    },
    {
      question: "Há limite de eventos ou participantes?",
      answer: "Não! Nossa infraestrutura em nuvem escala automaticamente. Já gerenciamos eventos com mais de 100.000 participantes simultâneos sem problemas de performance. Você paga apenas pelo que usar.",
      icon: Users
    },
    {
      question: "Como funciona o suporte técnico?",
      answer: "Oferecemos suporte 24/7 via chat ao vivo, email e telefone. Nossa equipe de especialistas tem tempo médio de resposta de 2 minutos durante horário comercial e 15 minutos fora do horário. Inclui também treinamento gratuito.",
      icon: Zap
    }
  ]

  return (
    <section className="py-32 bg-slate-900">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          className="text-center mb-20"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
        >
          <h2 className="text-5xl md:text-7xl font-black text-white mb-8">
            Dúvidas
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400">
              Frequentes
            </span>
          </h2>
          <p className="text-2xl text-slate-300">
            Tudo que você precisa saber sobre nossa plataforma
          </p>
        </motion.div>

        <div className="space-y-6">
          {faqs.map((faq, index) => (
            <motion.div
              key={index}
              className="bg-slate-800/40 backdrop-blur-xl rounded-2xl border border-slate-700/50"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <motion.button
                className="w-full px-8 py-6 text-left flex justify-between items-center hover:bg-slate-700/20 transition-colors rounded-2xl"
                onClick={() => setOpenFAQ(openFAQ === index ? null : index)}
                whileHover={{ scale: 1.02 }}
              >
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                    <faq.icon className="w-6 h-6 text-white" />
                  </div>
                  <span className="text-white font-bold text-xl">{faq.question}</span>
                </div>
                <motion.div
                  animate={{ rotate: openFAQ === index ? 180 : 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <ChevronDown className="w-8 h-8 text-slate-400" />
                </motion.div>
              </motion.button>
              
              <AnimatePresence>
                {openFAQ === index && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden"
                  >
                    <div className="px-8 pb-6">
                      <p className="text-slate-300 leading-relaxed text-lg ml-16">
                        {faq.answer}
                      </p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

// Footer épico
const Footer = () => {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-4 gap-12 mb-12">
          {/* Brand */}
          <motion.div 
            className="space-y-6"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <div className="flex items-center space-x-3">
              <div className="relative">
                <motion.div 
                  className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl blur-lg opacity-50"
                  animate={{ opacity: [0.3, 0.7, 0.3] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
                <div className="relative bg-gradient-to-r from-purple-500 to-pink-500 p-3 rounded-xl">
                  <Calendar className="w-8 h-8 text-white" />
                </div>
              </div>
              <span className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
                EventosIA
              </span>
            </div>
            <p className="text-slate-400 leading-relaxed">
              A próxima geração de gestão de eventos com inteligência artificial e tecnologia de ponta.
            </p>
          </motion.div>

          {/* Links columns */}
          {[
            {
              title: "Produto",
              links: ["Funcionalidades", "Integrações", "API", "Preços", "Demo"]
            },
            {
              title: "Empresa", 
              links: ["Sobre nós", "Blog", "Carreiras", "Imprensa", "Contato"]
            },
            {
              title: "Suporte",
              links: ["Central de Ajuda", "Documentação", "Status", "Segurança", "Comunidade"]
            }
          ].map((column, index) => (
            <motion.div
              key={index}
              className="space-y-6"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: (index + 1) * 0.1 }}
              viewport={{ once: true }}
            >
              <h4 className="font-bold text-white text-lg">{column.title}</h4>
              <div className="space-y-3">
                {column.links.map((link) => (
                  <motion.a
                    key={link}
                    href="#"
                    className="block text-slate-400 hover:text-white transition-colors"
                    whileHover={{ x: 5 }}
                  >
                    {link}
                  </motion.a>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
        
        <motion.div 
          className="border-t border-slate-800 pt-8 text-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          viewport={{ once: true }}
        >
          <p className="text-slate-400">
            &copy; 2025 EventosIA. Todos os direitos reservados. Transformando eventos com tecnologia.
          </p>
        </motion.div>
      </div>
    </footer>
  )
}

// Componente principal
const LandingPageUltraModerna = () => {
  return (
    <div className="min-h-screen bg-slate-900 text-white overflow-x-hidden">
      <Navigation />
      <HeroSection />
      <StatsSection />
      <FeaturesSection />
      <DemoVisualSection />
      <TestimonialsSection />
      <ComparisonSection />
      <CTASection />
      <FAQSection />
      <Footer />
    </div>
  )
}

export default LandingPageUltraModerna
