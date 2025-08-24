const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');

const app = express();
const PORT = 8000;
const SECRET_KEY = 'test-secret-key-123';

// Middleware
app.use(cors({
  origin: ['http://localhost:5173', 'http://127.0.0.1:5173'],
  credentials: true
}));
app.use(express.json());

// Base de dados em memória
const USERS_DB = {
  'admin@teste.com': {
    id: '1',
    email: 'admin@teste.com',
    password: '123456',
    name: 'Administrador',
    role: 'admin',
    is_active: true,
    created_at: '2024-01-01T10:00:00Z',
    updated_at: '2024-01-01T10:00:00Z'
  }
};

// Utilitários JWT
function createAccessToken(data) {
  return jwt.sign(
    { ...data, type: 'access' },
    SECRET_KEY,
    { expiresIn: '30m' }
  );
}

function createRefreshToken(data) {
  return jwt.sign(
    { ...data, type: 'refresh' },
    SECRET_KEY,
    { expiresIn: '30d' }
  );
}

function verifyToken(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ detail: 'Token não fornecido' });
  }

  const token = authHeader.substring(7);
  try {
    const payload = jwt.verify(token, SECRET_KEY);
    const user = USERS_DB[payload.sub];
    if (!user) {
      return res.status(401).json({ detail: 'Usuário não encontrado' });
    }
    req.user = user;
    next();
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ detail: 'Token expirado' });
    }
    return res.status(401).json({ detail: 'Token inválido' });
  }
}

// Rotas
app.get('/', (req, res) => {
  res.json({ message: 'Mock Auth API', status: 'running' });
});

app.post('/api/v1/auth/login', (req, res) => {
  const { email, password } = req.body;
  
  const user = USERS_DB[email];
  
  if (!user || user.password !== password) {
    return res.status(401).json({
      detail: 'Email ou senha incorretos'
    });
  }
  
  if (!user.is_active) {
    return res.status(401).json({
      detail: 'Usuário inativo'
    });
  }
  
  const access_token = createAccessToken({ sub: user.email });
  const refresh_token = createRefreshToken({ sub: user.email });
  
  res.json({
    access_token,
    refresh_token,
    token_type: 'bearer'
  });
});

app.get('/api/v1/auth/me', verifyToken, (req, res) => {
  const { password, ...userWithoutPassword } = req.user;
  res.json(userWithoutPassword);
});

app.post('/api/v1/auth/refresh', (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ detail: 'Token de refresh não fornecido' });
  }

  const token = authHeader.substring(7);
  try {
    const payload = jwt.verify(token, SECRET_KEY);
    
    if (payload.type !== 'refresh') {
      return res.status(401).json({ detail: 'Token de refresh inválido' });
    }
    
    const user = USERS_DB[payload.sub];
    if (!user) {
      return res.status(401).json({ detail: 'Usuário não encontrado' });
    }
    
    const access_token = createAccessToken({ sub: user.email });
    const refresh_token = createRefreshToken({ sub: user.email });
    
    res.json({
      access_token,
      refresh_token,
      token_type: 'bearer'
    });
    
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ detail: 'Token de refresh expirado' });
    }
    return res.status(401).json({ detail: 'Token de refresh inválido' });
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Mock backend running on http://localhost:${PORT}`);
  console.log('Test credentials: admin@teste.com / 123456');
});
