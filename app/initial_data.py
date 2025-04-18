import logging

import typer

from app.db.init_db import init_db, create_initial_data
from app.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = typer.Typer()


@app.command()
def init():
    """
    Initialize the database with required initial data.
    """
    logger.info("Creating initial data")
    db = SessionLocal()
    init_db(db)
    logger.info("Initial data created")


@app.command()
def create_demo_data():
    """
    Create demo data for development purposes.
    """
    logger.info("Creating demo data")
    db = SessionLocal()
    create_initial_data(db)
    logger.info("Demo data created")


if __name__ == "__main__":
    app()
