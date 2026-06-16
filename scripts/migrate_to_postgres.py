#!/usr/bin/env python
"""
Migrate SQLite data to PostgreSQL.

Usage:
    python scripts/migrate_to_postgres.py

Requires:
    - DATABASE_URL env var set (e.g. postgresql://user:pass@host:5432/dbname).
    - For self-hosted: DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT env vars.
    - PostgreSQL database already created.
"""
import os
import subprocess
import sys


def run(cmd, cwd=None, env=None):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        sys.exit(result.returncode)
    return result.stdout


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Step 1: Dump data from SQLite (current DJANGO_SETTINGS_MODULE)
    print("Dumping data from SQLite...")
    run([sys.executable, "manage.py", "dumpdata", "--natural-foreign", "--natural-primary",
         "-o", "data_dump.json"], cwd=project_root)

    # Step 2: Switch to production settings and apply migrations
    print("Applying migrations on PostgreSQL...")
    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = "config.settings.production"
    run([sys.executable, "manage.py", "migrate"], cwd=project_root, env=env)

    # Step 3: Load data into PostgreSQL
    print("Loading data into PostgreSQL...")
    run([sys.executable, "manage.py", "loaddata", "data_dump.json"], cwd=project_root, env=env)

    # Step 4: Verify
    print("Verifying row counts...")
    run([sys.executable, "manage.py", "check", "--deploy"], cwd=project_root, env=env)

    print("\nMigration complete! Data exported from SQLite and loaded into PostgreSQL.")
    print("To switch to PostgreSQL, set: DJANGO_SETTINGS_MODULE=config.settings.production")


if __name__ == "__main__":
    main()
