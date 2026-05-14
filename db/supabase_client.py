import logging
import os

from dotenv import load_dotenv
from supabase import Client, create_client

logger = logging.getLogger(__name__)


def get_supabase() -> Client:
    load_dotenv()

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")

    try:
        return create_client(url, key)
    except Exception:
        logger.error("Supabase client initialization failed")
        raise
