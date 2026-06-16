import logging
import os
import sys

from waitress import serve

from app import app

# Configure logging for the WSGI server
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [WSGI] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("waitress")
logger.setLevel(logging.INFO)

def run_server():
    """
    Start the production WSGI server.
    This configuration strictly bounds the thread pool size to prevent
    unbounded memory growth and threading exhaustion under heavy concurrent loads.
    """
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    # Thread pool bounds to prevent memory leaks and threading exhaustion
    threads = int(os.environ.get("WSGI_THREADS", 4))
    
    # Connection bounds to prevent resource starvation
    connection_limit = int(os.environ.get("WSGI_CONNECTION_LIMIT", 100))
    
    logger.info(f"Starting production WSGI server on {host}:{port}")
    logger.info(f"Thread pool size bounded to: {threads}")
    logger.info(f"Max concurrent connections bounded to: {connection_limit}")
    
    try:
        serve(
            app,
            host=host,
            port=port,
            threads=threads,
            connection_limit=connection_limit,
            channel_timeout=30,  # Drop inactive connections after 30s
            cleanup_interval=30,  # Run GC on channels
            ident="PsycheCare Server/1.0",  # Obfuscate actual server details
        )
    except Exception as e:
        logger.critical(f"Server crashed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_server()
