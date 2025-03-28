from app import app, db
import models
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    with app.app_context():
        # Check if tables already exist
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if 'user' in existing_tables:
            logger.info("Tables already exist in the database.")
        else:
            db.create_all()
            logger.info("Database tables created successfully.")
            
        # Validate tables have been created
        tables = inspector.get_table_names()
        logger.info(f"Available tables: {', '.join(tables)}")
        
except Exception as e:
    logger.error(f"Error creating database tables: {str(e)}")
    raise