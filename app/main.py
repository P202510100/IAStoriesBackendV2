from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router

# Inicializar app
app = FastAPI(
    title="Backend TP202510100",
    description="API para gestión de usuarios, estudiantes, profesores, historias y registros",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE
    allow_headers=["*"],  # Authorization, Content-Type
)

# Incluir rutas de la API
app.include_router(api_router, prefix="/api/v1")

# Endpoint de prueba
@app.get("/")
def root():
    return {"message": "Backend funcionando correctamente 🚀"}
