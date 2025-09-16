# vector_db/init_qdrant.py (Final Fixed Version)
import sys
import os
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.http import models
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("qdrant_init")

# Add parent directory to Python path
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

try:
    from config import QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME
    logger.info("✅ Config imported successfully")
except ImportError as e:
    logger.error(f"❌ Config import error: {str(e)}")
    logger.error("Please make sure config.py exists and has the required variables")
    sys.exit(1)

# Default embedding dimension
EMBEDDING_DIM = 384  # Default for all-MiniLM-L6-v2
try:
    from config import EMBEDDING_DIM
    logger.info(f"ℹ️ Using EMBEDDING_DIM from config: {EMBEDDING_DIM}")
except ImportError:
    logger.warning(f"⚠️ Using default EMBEDDING_DIM: {EMBEDDING_DIM}")

def initialize_qdrant():
    logger.info("\n🔧 Initializing Qdrant...")
    try:
        logger.info(f"Connecting to: {QDRANT_URL}")
        logger.info(f"Using collection: {COLLECTION_NAME}")
        
        client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            prefer_grpc=True,
            timeout=10.0  # Add timeout
        )
        
        # Test connection - safest method
        try:
            # This should work for all versions
            health = client.health_check()
            logger.info(f"✅ Health check passed: {health}")
        except Exception as e:
            logger.error(f"❌ Health check failed: {str(e)}")
            return False
        
        # Check if collection exists
        try:
            collection_info = client.get_collection(COLLECTION_NAME)
            logger.info(f"ℹ️ Collection '{COLLECTION_NAME}' already exists")
            logger.info(f"   - Vectors count: {collection_info.vectors_count}")
            return True
        except Exception as e:
            logger.info(f"🆕 Creating new collection: '{COLLECTION_NAME}'")
        
        # Create collection
        try:
            client.recreate_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=EMBEDDING_DIM,
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"✅ Collection '{COLLECTION_NAME}' created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Collection creation failed: {str(e)}")
            return False
        
    except Exception as e:
        logger.exception(f"❌ Initialization failed")
        return False

if __name__ == "__main__":
    logger.info(f"QDRANT_URL: {QDRANT_URL}")
    logger.info(f"COLLECTION_NAME: {COLLECTION_NAME}")
    logger.info(f"EMBEDDING_DIM: {EMBEDDING_DIM}")
    
    if initialize_qdrant():
        logger.info("\n🎉 Qdrant initialization complete!")
    else:
        logger.error("\n❌ Qdrant initialization failed")