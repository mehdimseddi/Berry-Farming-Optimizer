# core/logger.py

import logging

# Configure logging only once
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a logger for your app
logger = logging.getLogger("farming_app")
