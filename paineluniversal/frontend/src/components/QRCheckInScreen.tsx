import React, { useState, useEffect } from 'react';

interface Event {
  id: string;
  name: string;
  description: string;
  start_time: string;
  end_time: string;
  location: string;
  max_capacity: number;
  status: string;
  check_ins_count: number;
  created_at: string;
}

interface CheckInRecord {
  id: string;
  user_name: string;
  user_email?: string;
  check_in_time: string;
}

interface DashboardData {
  total_events: number;
  active_events: number;
  total_checkins: number;
  today_checkins: number;
  popular_events: Array<{
    event_name: string;
    checkins: number;
    capacity: number;
    occupancy_rate: number;
  }>;
  recent_checkins: Array<{
    user_name: string;
    event_name: string;
    check_in_time: string;
  }>;
}

interface QRCheckInScreenProps {
  isAdmin?: boolean;
}

const QRCheckInScreen: React.FC<QRCheckInScreenProps> = ({ isAdmin = false }) => {
  const [events, setEvents] = useState<Event[]>([]);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'events' | 'create' | 'scanner'>('dashboard');
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [qrCodeImage, setQrCodeImage] = useState<string>('');
  const [attendees, setAttendees] = useState<CheckInRecord[]>([]);

  // Estado para criar evento
  const [newEvent, setNewEvent] = useState({
    name: '',
    description: '',
    start_time: '',
    end_time: '',
    location: '',
    max_capacity: 100
  });

  // Estado para check-in manual
  const [checkInData, setCheckInData] = useState({
    qr_data: '',
    user_name: '',
    user_email: '',
    user_phone: ''
  });

  // Função para buscar dashboard
  const fetchDashboard = async () => {
    try {
      const response = await fetch('/api/qr-checkin/dashboard');
      const result = await response.json();
      if (result.success) {
        setDashboardData(result.data);
      }
    } catch (error) {
      console.error('Erro ao buscar dashboard:', error);
    }
  };

  // Função para buscar eventos
  const fetchEvents = async () => {
    try {
      const response = await fetch('/api/qr-checkin/events');
      const result = await response.json();
      if (result.success) {
        setEvents(result.data);
      }
    } catch (error) {
      console.error('Erro ao buscar eventos:', error);
    } finally {
      setLoading(false);
    }
  };

  // Função para criar evento
  const createEvent = async () => {
    try {
      const response = await fetch('/api/qr-checkin/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newEvent)
      });

      const result = await response.json();
      if (result.success) {
        alert('Evento criado com sucesso!');
        setNewEvent({
          name: '',
          description: '',
          start_time: '',
          end_time: '',
          location: '',
          max_capacity: 100
        });
        fetchEvents();
        setActiveTab('events');
      } else {
        alert('Erro ao criar evento');
      }
    } catch (error) {
      console.error('Erro ao criar evento:', error);
      alert('Erro interno');
    }
  };

  // Função para obter QR code
  const getQRCode = async (eventId: string) => {
    try {
      const response = await fetch(`/api/qr-checkin/events/${eventId}/qr-code`);
      const result = await response.json();
      if (result.success) {
        setQrCodeImage(result.data.qr_code_image);
      }
    } catch (error) {
      console.error('Erro ao obter QR code:', error);
    }
  };

  // Função para obter participantes
  const getAttendees = async (eventId: string) => {
    try {
      const response = await fetch(`/api/qr-checkin/events/${eventId}/attendees`);
      const result = await response.json();
      if (result.success) {
        setAttendees(result.data.attendees);
      }
    } catch (error) {
      console.error('Erro ao obter participantes:', error);
    }
  };

  // Função para processar check-in manual
  const processCheckIn = async () => {
    try {
      const response = await fetch('/api/qr-checkin/checkin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(checkInData)
      });

      const result = await response.json();
      if (result.success) {
        alert(`Check-in realizado com sucesso! ${result.message}`);
        setCheckInData({
          qr_data: '',
          user_name: '',
          user_email: '',
          user_phone: ''
        });
        fetchDashboard();
      } else {
        alert(`Erro: ${result.message}`);
      }
    } catch (error) {
      console.error('Erro no check-in:', error);
      alert('Erro interno');
    }
  };

  // Função para formatar data
  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR');
  };

  // Effects
  useEffect(() => {
    fetchDashboard();
    fetchEvents();
  }, []);

  // Auto-refresh
  useEffect(() => {
    const interval = setInterval(() => {
      if (activeTab === 'dashboard') {
        fetchDashboard();
      }
    }, 30000); // 30 segundos

    return () => clearInterval(interval);
  }, [activeTab]);

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h2>Carregando Sistema de QR Check-in...</h2>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: '#333', marginBottom: '20px' }}>
        🎯 Sistema de QR Check-in
      </h1>

      {/* Navegação */}
      <div style={{ marginBottom: '20px', borderBottom: '1px solid #ddd' }}>
        <nav style={{ display: 'flex', gap: '20px' }}>
          <button
            onClick={() => setActiveTab('dashboard')}
            style={{
              padding: '10px 20px',
              border: 'none',
              background: activeTab === 'dashboard' ? '#007bff' : 'transparent',
              color: activeTab === 'dashboard' ? 'white' : '#007bff',
              cursor: 'pointer',
              borderRadius: '4px',
              fontSize: '14px'
            }}
          >
            Dashboard
          </button>
          <button
            onClick={() => setActiveTab('events')}
            style={{
              padding: '10px 20px',
              border: 'none',
              background: activeTab === 'events' ? '#007bff' : 'transparent',
              color: activeTab === 'events' ? 'white' : '#007bff',
              cursor: 'pointer',
              borderRadius: '4px',
              fontSize: '14px'
            }}
          >
            Eventos
          </button>
          {isAdmin && (
            <button
              onClick={() => setActiveTab('create')}
              style={{
                padding: '10px 20px',
                border: 'none',
                background: activeTab === 'create' ? '#28a745' : 'transparent',
                color: activeTab === 'create' ? 'white' : '#28a745',
                cursor: 'pointer',
                borderRadius: '4px',
                fontSize: '14px'
              }}
            >
              Criar Evento
            </button>
          )}
          <button
            onClick={() => setActiveTab('scanner')}
            style={{
              padding: '10px 20px',
              border: 'none',
              background: activeTab === 'scanner' ? '#ffc107' : 'transparent',
              color: activeTab === 'scanner' ? '#333' : '#ffc107',
              cursor: 'pointer',
              borderRadius: '4px',
              fontSize: '14px'
            }}
          >
            Check-in Manual
          </button>
        </nav>
      </div>

      {/* Dashboard */}
      {activeTab === 'dashboard' && dashboardData && (
        <div>
          <h2>Dashboard Geral</h2>
          
          {/* Estatísticas */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '15px',
            marginBottom: '30px'
          }}>
            <div style={{
              background: 'white',
              padding: '20px',
              borderRadius: '8px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              textAlign: 'center',
              borderLeft: '4px solid #007bff'
            }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#333' }}>
                {dashboardData.total_events}
              </div>
              <div style={{ fontSize: '14px', color: '#666' }}>Total de Eventos</div>
            </div>

            <div style={{
              background: 'white',
              padding: '20px',
              borderRadius: '8px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              textAlign: 'center',
              borderLeft: '4px solid #28a745'
            }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#333' }}>
                {dashboardData.active_events}
              </div>
              <div style={{ fontSize: '14px', color: '#666' }}>Eventos Ativos</div>
            </div>

            <div style={{
              background: 'white',
              padding: '20px',
              borderRadius: '8px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              textAlign: 'center',
              borderLeft: '4px solid #ffc107'
            }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#333' }}>
                {dashboardData.total_checkins}
              </div>
              <div style={{ fontSize: '14px', color: '#666' }}>Total Check-ins</div>
            </div>

            <div style={{
              background: 'white',
              padding: '20px',
              borderRadius: '8px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              textAlign: 'center',
              borderLeft: '4px solid #dc3545'
            }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#333' }}>
                {dashboardData.today_checkins}
              </div>
              <div style={{ fontSize: '14px', color: '#666' }}>Check-ins Hoje</div>
            </div>
          </div>

          {/* Eventos Populares */}
          <div style={{ marginBottom: '30px' }}>
            <h3>Eventos Mais Populares</h3>
            <div style={{
              background: 'white',
              padding: '20px',
              borderRadius: '8px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
              {dashboardData.popular_events.map((event, index) => (
                <div key={index} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '10px 0',
                  borderBottom: index < dashboardData.popular_events.length - 1 ? '1px solid #eee' : 'none'
                }}>
                  <div>
                    <strong>{event.event_name}</strong>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      {event.checkins}/{event.capacity} participantes
                    </div>
                  </div>
                  <div style={{
                    padding: '4px 8px',
                    borderRadius: '4px',
                    background: event.occupancy_rate > 80 ? '#dc3545' : event.occupancy_rate > 50 ? '#ffc107' : '#28a745',
                    color: 'white',
                    fontSize: '12px'
                  }}>
                    {event.occupancy_rate}%
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Check-ins Recentes */}
          <div>
            <h3>Check-ins Recentes</h3>
            <div style={{
              background: 'white',
              padding: '20px',
              borderRadius: '8px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
              {dashboardData.recent_checkins.map((checkin, index) => (
                <div key={index} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '8px 0',
                  borderBottom: index < dashboardData.recent_checkins.length - 1 ? '1px solid #eee' : 'none'
                }}>
                  <div>
                    <strong>{checkin.user_name}</strong>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      {checkin.event_name}
                    </div>
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {formatDateTime(checkin.check_in_time)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Lista de Eventos */}
      {activeTab === 'events' && (
        <div>
          <h2>Eventos</h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '20px'
          }}>
            {events.map(event => (
              <div key={event.id} style={{
                background: 'white',
                padding: '20px',
                borderRadius: '8px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                border: '1px solid #eee'
              }}>
                <h4 style={{ margin: '0 0 10px 0', color: '#333' }}>{event.name}</h4>
                <p style={{ margin: '0 0 10px 0', color: '#666', fontSize: '14px' }}>
                  {event.description}
                </p>
                <div style={{ fontSize: '12px', color: '#666', marginBottom: '10px' }}>
                  <div>📍 {event.location}</div>
                  <div>🕐 {formatDateTime(event.start_time)}</div>
                  <div>👥 {event.check_ins_count}/{event.max_capacity}</div>
                  <div>Status: <span style={{
                    color: event.status === 'active' ? '#28a745' : '#ffc107'
                  }}>{event.status}</span></div>
                </div>
                
                <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                  <button
                    onClick={() => {
                      setSelectedEvent(event);
                      getQRCode(event.id);
                    }}
                    style={{
                      padding: '6px 12px',
                      background: '#007bff',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      fontSize: '12px',
                      cursor: 'pointer'
                    }}
                  >
                    Ver QR Code
                  </button>
                  
                  <button
                    onClick={() => {
                      setSelectedEvent(event);
                      getAttendees(event.id);
                    }}
                    style={{
                      padding: '6px 12px',
                      background: '#28a745',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      fontSize: '12px',
                      cursor: 'pointer'
                    }}
                  >
                    Ver Participantes
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Modal QR Code */}
          {selectedEvent && qrCodeImage && (
            <div style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0,0,0,0.5)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1000
            }}>
              <div style={{
                background: 'white',
                padding: '30px',
                borderRadius: '8px',
                textAlign: 'center',
                maxWidth: '400px'
              }}>
                <h3>{selectedEvent.name}</h3>
                <img src={qrCodeImage} alt="QR Code" style={{ maxWidth: '250px' }} />
                <div style={{ marginTop: '20px' }}>
                  <button
                    onClick={() => {
                      setSelectedEvent(null);
                      setQrCodeImage('');
                    }}
                    style={{
                      padding: '8px 16px',
                      background: '#dc3545',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    Fechar
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Modal Participantes */}
          {selectedEvent && attendees.length > 0 && !qrCodeImage && (
            <div style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0,0,0,0.5)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1000
            }}>
              <div style={{
                background: 'white',
                padding: '30px',
                borderRadius: '8px',
                maxWidth: '600px',
                maxHeight: '80vh',
                overflow: 'auto'
              }}>
                <h3>Participantes - {selectedEvent.name}</h3>
                <div style={{ maxHeight: '400px', overflow: 'auto' }}>
                  {attendees.map((attendee, index) => (
                    <div key={index} style={{
                      padding: '10px',
                      borderBottom: '1px solid #eee',
                      display: 'flex',
                      justifyContent: 'space-between'
                    }}>
                      <div>
                        <strong>{attendee.user_name}</strong>
                        {attendee.user_email && (
                          <div style={{ fontSize: '12px', color: '#666' }}>
                            {attendee.user_email}
                          </div>
                        )}
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>
                        {formatDateTime(attendee.check_in_time)}
                      </div>
                    </div>
                  ))}
                </div>
                <div style={{ marginTop: '20px', textAlign: 'center' }}>
                  <button
                    onClick={() => {
                      setSelectedEvent(null);
                      setAttendees([]);
                    }}
                    style={{
                      padding: '8px 16px',
                      background: '#dc3545',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    Fechar
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Criar Evento */}
      {activeTab === 'create' && isAdmin && (
        <div>
          <h2>Criar Novo Evento</h2>
          <div style={{
            background: 'white',
            padding: '30px',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            maxWidth: '600px'
          }}>
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                Nome do Evento:
              </label>
              <input
                type="text"
                value={newEvent.name}
                onChange={(e) => setNewEvent({...newEvent, name: e.target.value})}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px'
                }}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                Descrição:
              </label>
              <textarea
                value={newEvent.description}
                onChange={(e) => setNewEvent({...newEvent, description: e.target.value})}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  minHeight: '80px'
                }}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '20px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                  Data/Hora Início:
                </label>
                <input
                  type="datetime-local"
                  value={newEvent.start_time}
                  onChange={(e) => setNewEvent({...newEvent, start_time: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                  Data/Hora Fim:
                </label>
                <input
                  type="datetime-local"
                  value={newEvent.end_time}
                  onChange={(e) => setNewEvent({...newEvent, end_time: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px'
                  }}
                />
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                Local:
              </label>
              <input
                type="text"
                value={newEvent.location}
                onChange={(e) => setNewEvent({...newEvent, location: e.target.value})}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px'
                }}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                Capacidade Máxima:
              </label>
              <input
                type="number"
                value={newEvent.max_capacity}
                onChange={(e) => setNewEvent({...newEvent, max_capacity: parseInt(e.target.value)})}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px'
                }}
              />
            </div>

            <button
              onClick={createEvent}
              style={{
                background: '#28a745',
                color: 'white',
                padding: '12px 24px',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '16px'
              }}
            >
              Criar Evento
            </button>
          </div>
        </div>
      )}

      {/* Check-in Manual */}
      {activeTab === 'scanner' && (
        <div>
          <h2>Check-in Manual</h2>
          <div style={{
            background: 'white',
            padding: '30px',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            maxWidth: '600px'
          }}>
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                Dados do QR Code:
              </label>
              <textarea
                value={checkInData.qr_data}
                onChange={(e) => setCheckInData({...checkInData, qr_data: e.target.value})}
                placeholder='{"type":"event_checkin","event_id":"...","timestamp":"...","version":"1.0"}'
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  minHeight: '80px',
                  fontFamily: 'monospace',
                  fontSize: '12px'
                }}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                Nome do Usuário:
              </label>
              <input
                type="text"
                value={checkInData.user_name}
                onChange={(e) => setCheckInData({...checkInData, user_name: e.target.value})}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px'
                }}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                E-mail (opcional):
              </label>
              <input
                type="email"
                value={checkInData.user_email}
                onChange={(e) => setCheckInData({...checkInData, user_email: e.target.value})}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px'
                }}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                Telefone (opcional):
              </label>
              <input
                type="tel"
                value={checkInData.user_phone}
                onChange={(e) => setCheckInData({...checkInData, user_phone: e.target.value})}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px'
                }}
              />
            </div>

            <button
              onClick={processCheckIn}
              style={{
                background: '#ffc107',
                color: '#333',
                padding: '12px 24px',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '16px'
              }}
            >
              Processar Check-in
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default QRCheckInScreen;
