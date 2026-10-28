"""
SAP HANA Cloud connection management.

Loads credentials from environment variables (via .env file) and provides
a reusable connection factory and connectivity test helper.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv

# Load .env from ai-career-engine root directory
load_dotenv()


def get_hana_connection():
    """Creates and returns a new SAP HANA Cloud database connection.

    Reads connection parameters from environment variables:
        HANA_HOST, HANA_PORT, HANA_USER, HANA_PASSWORD, HANA_ENCRYPT

    Returns:
        dbapi.Connection: An active HANA database connection.

    Raises:
        RuntimeError: If required environment variables are missing.
        ImportError: If hdbcli is not installed.
    """
    try:
        from hdbcli import dbapi
    except ImportError:
        raise ImportError(
            "hdbcli is not installed. Run: pip install hdbcli"
        )

    host = os.getenv("HANA_HOST")
    port = int(os.getenv("HANA_PORT", "443"))
    user = os.getenv("HANA_USER")
    password = os.getenv("HANA_PASSWORD")
    encrypt = os.getenv("HANA_ENCRYPT", "true").lower() in ("true", "1")
    ssl_validate = os.getenv("HANA_SSL_VALIDATE", "true").lower() in ("true", "1", "t")

    if not all([host, user, password]):
        raise RuntimeError(
            "Missing HANA_HOST, HANA_USER, or HANA_PASSWORD in environment. "
            "Copy .env.example to .env and fill in your SAP HANA Cloud credentials."
        )

    conn_kwargs = {
        "encrypt": encrypt,
        "sslValidateCertificate": ssl_validate,
        "sslCryptoProvider": "openssl",
    }
    
    return dbapi.connect(
        address=host,
        port=port,
        user=user,
        password=password,
        **conn_kwargs
    )


def test_connection() -> Dict[str, Any]:
    """Tests SAP HANA Cloud connectivity and returns connection metadata.

    Returns:
        dict: Contains 'status', 'current_user', 'current_schema', and
              optionally 'hana_version'.

    Raises:
        RuntimeError: If connection fails.
    """
    conn = get_hana_connection()
    try:
        cursor = conn.cursor()

        # Basic connectivity check
        cursor.execute("SELECT CURRENT_USER, CURRENT_SCHEMA FROM DUMMY")
        row = cursor.fetchone()

        # Get HANA version
        cursor.execute("SELECT VERSION FROM SYS.M_DATABASE")
        version_row = cursor.fetchone()

        return {
            "status": "connected",
            "current_user": row[0],
            "current_schema": row[1],
            "hana_version": version_row[0] if version_row else "unknown",
        }
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc),
        }
    finally:
        conn.close()


def is_hana_available() -> bool:
    """Quick check whether HANA credentials are configured in the environment.

    Does NOT attempt an actual connection — this is a cheap config-level check
    used to determine whether HANA-dependent tests should be skipped.
    """
    return all([
        os.getenv("HANA_HOST"),
        os.getenv("HANA_USER"),
        os.getenv("HANA_PASSWORD"),
    ])
