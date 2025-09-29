from sqlalchemy.orm import declarative_base

Base = declarative_base()

# 👇 Importa todos los modelos aquí para que Alembic los vea
from app.models import models
