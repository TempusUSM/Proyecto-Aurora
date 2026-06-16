from database import engine
from models import Base

# Borra las tablas viejas
# Base.metadata.drop_all(bind=engine)
# Crea las tablas según el models.py actualizado
Base.metadata.create_all(bind=engine)
