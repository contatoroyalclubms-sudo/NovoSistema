#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from app.database import settings
from app.models import Base

def create_financeiro_tables():
    """Create financial tables"""
    engine = create_engine(settings.database_url)
    
    Base.metadata.create_all(bind=engine)
    print("✅ Financial tables created successfully!")

if __name__ == "__main__":
    create_financeiro_tables()
