import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.session import engine, Base
from app.database import models

print("Criando tabelas do banco de dados...")
Base.metadata.create_all(bind=engine)
print("Tabelas criadas!")