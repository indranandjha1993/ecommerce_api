# Import and configure all models
from app.models import load_models

# Get the Base class with all models registered
Base = load_models()
