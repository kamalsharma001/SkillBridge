"""
Standalone HANA connectivity test.

Usage:
    cd ai-career-engine
    python test_hana.py

Expected output when connected:
    {
        'status': 'connected',
        'current_user': 'DBADMIN',
        'current_schema': '...',
        'hana_version': '...'
    }
"""

from __future__ import annotations

import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import test_connection, is_hana_available


def main():
    print("=" * 60)
    print("  SAP HANA Cloud Connectivity Test")
    print("=" * 60)

    if not is_hana_available():
        print("\n[!] HANA credentials not found in environment.")
        print("    Copy .env.example to .env and fill in:")
        print("      HANA_HOST=your-hana-host.hanacloud.ondemand.com")
        print("      HANA_PORT=443")
        print("      HANA_USER=DBADMIN")
        print("      HANA_PASSWORD=your-password")
        print("\n    Then re-run: python test_hana.py")
        return

    print("\n[*] Testing SAP HANA Cloud connection...")

    result = test_connection()

    if result.get("status") == "connected":
        print(f"\n[OK] Connected successfully!")
        print(f"     User:    {result['current_user']}")
        print(f"     Schema:  {result['current_schema']}")
        print(f"     Version: {result['hana_version']}")

        # Test schema access
        print("\n[*] Testing schema access...")
        _test_schema_access()

    else:
        print(f"\n[FAIL] Connection failed: {result.get('error', 'Unknown error')}")

    print("\n" + "=" * 60)


def _test_schema_access():
    """Quick check that ONET, ESCO, and SYNTHETIC schemas have data."""
    from database.connection import get_hana_connection

    conn = get_hana_connection()
    try:
        cursor = conn.cursor()

        schemas = [
            ("ONET", "ONET_OCCUPATIONS"),
            ("ESCO", "ESCO_SKILLS_EN"),
            ("SKILLBRIDGE", "CANDIDATES"),
        ]

        for schema, table in schemas:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM "{schema}"."{table}"')
                count = cursor.fetchone()[0]
                print(f"     {schema}.{table}: {count} rows")
            except Exception as exc:
                print(f"     {schema}.{table}: ERROR - {exc}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
