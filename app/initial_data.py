import logging
import sys

import typer

from app.db.init_db import init_db
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
    try:
        db = SessionLocal()
        init_db(db)
        logger.info("Initial data created")
    except Exception as e:
        logger.error(f"Error creating initial data: {e}")
        sys.exit(1)


@app.command()
def create_demo_data():
    """
    Create demo data for development purposes.
    """
    logger.info("Creating demo data")
    try:
        db = SessionLocal()
        from app.db.init_db import create_initial_data
        create_initial_data(db)
        logger.info("Demo data created")
    except Exception as e:
        logger.error(f"Error creating demo data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    app()
