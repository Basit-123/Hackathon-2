"""
Backend Configuration
Loads environment variables for FastAPI application
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Authentication Configuration
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

# JWT Configuration
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 7

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# Validation
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable is required")

if len(BETTER_AUTH_SECRET) < 32:
    raise ValueError("BETTER_AUTH_SECRET must be at least 32 characters")
