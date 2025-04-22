# Import all models
from app.models import load_models
from app.db.session import Base

# Load all models to register them with the Base class
load_models()
