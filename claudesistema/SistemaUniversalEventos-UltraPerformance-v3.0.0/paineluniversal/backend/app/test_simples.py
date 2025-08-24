"""
Versão Ultra Simples - Teste Básico
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Sistema Universal - Teste Básico",
    version="1.0.0",
)

# CORS básico
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Sistema funcionando!",
        "status": "OK"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.test_simples:app", host="127.0.0.1", port=8000, reload=True)
