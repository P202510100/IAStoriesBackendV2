from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router

# Inicializar app
app = FastAPI(
    title="Backend TP202510100",
    description="API para gestión de usuarios, estudiantes, profesores, historias y registros",
    version="1.0.0"
)

# Configurar CORS
origins = [
    "http://localhost:3000",   # frontend local
    "http://127.0.0.1:3000",
    # agregar dominios de producción aquí
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
