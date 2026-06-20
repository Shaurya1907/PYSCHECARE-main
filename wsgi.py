"""
WSGI entry point for production deployment.
"""

import logging
import os
import sys

from waitress import serve

from app import app, CHAT_API_SECRET

# Security verification check for production environments
if not CHAT_API_SECRET or len(CHAT_API_SECRET) < 32:
    logging.warning(
        "CRITICAL SECURITY WARNING: CHAT_API_SECRET is unset or dangerously short (< 32 chars). "
        "This may lead to cryptographic authentication bypass vulnerabilities. "
        "Please enforce strong cryptographic secrets immediately."
    )

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
    unbounded memory growth and threading exhaustion under heavy loads.
    """
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")

    # Thread pool bounds to prevent memory leaks
    threads = int(os.environ.get("WSGI_THREADS", 4))

    # Connection bounds to prevent resource starvation
    connection_limit = int(os.environ.get("WSGI_CONNECTION_LIMIT", 100))

    logger.info("Starting production WSGI server on %s:%s", host, port)
    logger.info("Thread pool size bounded to: %s", threads)
    logger.info("Max concurrent connections bounded to: %s", connection_limit)

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
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.critical("Server crashed with error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    run_server()
