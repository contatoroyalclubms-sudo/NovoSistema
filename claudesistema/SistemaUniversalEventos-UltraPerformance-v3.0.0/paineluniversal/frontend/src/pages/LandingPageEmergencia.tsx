import React from 'react'

const LandingPageEmergencia = () => {
  const styles = {
    container: {
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #581c87 0%, #0f172a 50%, #be185d 100%)',
      padding: '2rem',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    },
    header: {
      textAlign: 'center' as 'center',
      marginBottom: '4rem',
      color: 'white'
    },
    title: {
      fontSize: '4rem',
      fontWeight: '900',
      marginBottom: '1.5rem',
      background: 'linear-gradient(45deg, #a855f7, #ec4899, #06b6d4)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      backgroundClip: 'text'
    },
    subtitle: {
      fontSize: '1.5rem',
      color: '#cbd5e1',
      maxWidth: '48rem',
      margin: '0 auto'
    },
    grid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
      gap: '2rem',
      marginBottom: '4rem',
      maxWidth: '75rem',
      margin: '0 auto 4rem auto'
    },
    card: {
      background: 'rgba(30, 41, 59, 0.5)',
      backdropFilter: 'blur(20px)',
      borderRadius: '1.5rem',
      padding: '2rem',
      border: '1px solid rgba(71, 85, 105, 0.5)',
      transition: 'all 0.3s ease'
    },
    cardIcon: {
      width: '4rem',
      height: '4rem',
      borderRadius: '1rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: '2rem',
      marginBottom: '1.5rem'
    },
    cardTitle: {
      fontSize: '1.5rem',
      fontWeight: '700',
      color: 'white',
      marginBottom: '1rem'
    },
    cardText: {
      color: '#cbd5e1',
      lineHeight: '1.6'
    },
    statsContainer: {
      background: 'rgba(30, 41, 59, 0.3)',
      backdropFilter: 'blur(20px)',
      borderRadius: '2rem',
      padding: '3rem',
      border: '1px solid rgba(71, 85, 105, 0.3)',
      marginBottom: '4rem',
      maxWidth: '75rem',
      margin: '0 auto 4rem auto'
    },
    statsGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
      gap: '2rem',
      textAlign: 'center' as 'center'
    },
    statNumber: {
      fontSize: '2.5rem',
      fontWeight: '900',
      marginBottom: '0.5rem'
    },
    statLabel: {
      color: '#cbd5e1'
    },
    ctaContainer: {
      textAlign: 'center' as 'center'
    },
    button: {
      background: 'linear-gradient(45deg, #7c3aed, #ec4899)',
      color: 'white',
      padding: '1rem 3rem',
      borderRadius: '1rem',
      fontSize: '1.25rem',
      fontWeight: '700',
      border: 'none',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      marginBottom: '1rem'
    },
    benefits: {
      color: '#94a3b8',
      marginTop: '1rem'
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>
          🚀 EventosIA
        </h1>
        <p style={styles.subtitle}>
          A próxima geração de gestão de eventos com inteligência artificial
        </p>
      </div>

      <div style={styles.grid}>
        <div style={styles.card}>
          <div style={{...styles.cardIcon, background: 'linear-gradient(45deg, #a855f7, #ec4899)'}}>
            🧠
          </div>
          <h3 style={styles.cardTitle}>IA Integrada</h3>
          <p style={styles.cardText}>
            Inteligência artificial avançada para otimizar cada aspecto do seu evento automaticamente.
          </p>
        </div>

        <div style={styles.card}>
          <div style={{...styles.cardIcon, background: 'linear-gradient(45deg, #10b981, #06b6d4)'}}>
            📱
          </div>
          <h3 style={styles.cardTitle}>Check-in Biométrico</h3>
          <p style={styles.cardText}>
            Reconhecimento facial avançado para entrada segura e instantânea nos eventos.
          </p>
        </div>

        <div style={styles.card}>
          <div style={{...styles.cardIcon, background: 'linear-gradient(45deg, #06b6d4, #3b82f6)'}}>
            💳
          </div>
          <h3 style={styles.cardTitle}>PDV Completo</h3>
          <p style={styles.cardText}>
            Sistema de vendas integrado com controle de estoque e relatórios em tempo real.
          </p>
        </div>
      </div>

      <div style={styles.statsContainer}>
        <div style={styles.statsGrid}>
          <div>
            <div style={{...styles.statNumber, background: 'linear-gradient(45deg, #10b981, #06b6d4)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'}}>
              1000+
            </div>
            <p style={styles.statLabel}>Eventos Realizados</p>
          </div>
          <div>
            <div style={{...styles.statNumber, background: 'linear-gradient(45deg, #a855f7, #ec4899)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'}}>
              50k+
            </div>
            <p style={styles.statLabel}>Participantes</p>
          </div>
          <div>
            <div style={{...styles.statNumber, background: 'linear-gradient(45deg, #06b6d4, #3b82f6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'}}>
              98%
            </div>
            <p style={styles.statLabel}>Satisfação</p>
          </div>
          <div>
            <div style={{...styles.statNumber, background: 'linear-gradient(45deg, #f59e0b, #ef4444)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'}}>
              24/7
            </div>
            <p style={styles.statLabel}>Suporte</p>
          </div>
        </div>
      </div>

      <div style={styles.ctaContainer}>
        <button 
          style={styles.button}
          onMouseOver={(e) => {
            e.currentTarget.style.transform = 'scale(1.05)'
            e.currentTarget.style.boxShadow = '0 25px 50px -12px rgba(139, 92, 246, 0.5)'
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.transform = 'scale(1)'
            e.currentTarget.style.boxShadow = 'none'
          }}
        >
          COMEÇAR AGORA - GRÁTIS
        </button>
        <p style={styles.benefits}>
          ✓ 30 dias grátis ✓ Sem cartão ✓ Setup gratuito
        </p>
      </div>
    </div>
  )
}

export default LandingPageEmergencia
