from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sistema Neural Backend", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "Sistema Neural Backend Ativo", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok", "backend": "FastAPI", "message": "Backend funcionando perfeitamente!"}

@app.get("/api/dashboard")
async def get_dashboard():
    return {
        "vendas_hoje": 2450.80,
        "produtos_vendidos": 127,
        "clientes_ativos": 89,
        "ia_score": 96.5,
        "neural_status": {
            "backend_api": "connected",
            "websocket": "active", 
            "ia_engine": "processing"
        }
    }

@app.get("/api/pdv/produtos")
async def get_produtos():
    return [
        {"id": 1, "nome": "Cerveja IPA", "preco": 12.50, "emoji": "🍺"},
        {"id": 2, "nome": "Hambúrguer", "preco": 25.90, "emoji": "🍔"},
        {"id": 3, "nome": "Água 500ml", "preco": 3.50, "emoji": "💧"},
        {"id": 4, "nome": "Batata Frita", "preco": 15.00, "emoji": "🍟"},
        {"id": 5, "nome": "Refrigerante", "preco": 6.00, "emoji": "🥤"},
        {"id": 6, "nome": "Pizza Margherita", "preco": 35.00, "emoji": "🍕"}
    ]

@app.get("/api/pdv/recomendacoes")
async def get_recomendacoes():
    return [
        {
            "produto": "Cerveja + Hambúrguer",
            "score": 95,
            "tipo": "combo",
            "descricao": "🍺 Cerveja combina com 🍔 Hambúrguer"
        },
        {
            "produto": "Batata Frita", 
            "score": 88,
            "tipo": "tendencia",
            "descricao": "🍟 Batata é o mais vendido hoje"
        }
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
