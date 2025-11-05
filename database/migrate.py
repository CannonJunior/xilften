"""
Database Migration Runner

Applies SQL migrations to DuckDB database.
"""

import duckdb
import logging
from pathlib import Path
from typing import List, Tuple
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MigrationRunner:
    """Runs database migrations for DuckDB."""

    def __init__(self, db_path: str = None):
        """
        Initialize migration runner.

        Args:
            db_path (str): Path to DuckDB database file
        """
        self.db_path = db_path or settings.duckdb_database_path
        self.migrations_dir = Path(__file__).parent / "migrations"
        self.conn = None

    def connect(self):
        """Connect to DuckDB database."""
        logger.info(f"Connecting to database: {self.db_path}")
        self.conn = duckdb.connect(self.db_path)

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def get_applied_migrations(self) -> List[str]:
        """
        Get list of already applied migrations.

        Returns:
            List[str]: List of applied migration names
        """
        try:
            result = self.conn.execute(
                "SELECT migration_name FROM migrations ORDER BY id"
            ).fetchall()
            return [row[0] for row in result]
        except Exception:
            # Migrations table doesn't exist yet
            return []

    def get_pending_migrations(self) -> List[Tuple[str, Path]]:
        """
        Get list of pending migrations to apply.

        Returns:
            List[Tuple[str, Path]]: List of (migration_name, file_path) tuples
        """
        applied = set(self.get_applied_migrations())

        # Find all .sql files in migrations directory
        migration_files = sorted(self.migrations_dir.glob("*.sql"))

        pending = []
        for file_path in migration_files:
            migration_name = file_path.stem
            if migration_name not in applied:
                pending.append((migration_name, file_path))

        return pending

    def apply_migration(self, migration_name: str, file_path: Path):
        """
        Apply a single migration.

        Args:
            migration_name (str): Name of the migration
            file_path (Path): Path to migration SQL file
        """
        logger.info(f"Applying migration: {migration_name}")

        try:
            # Read migration SQL
            sql = file_path.read_text()

            # Execute migration
            self.conn.execute(sql)

            logger.info(f"✅ Successfully applied: {migration_name}")

        except Exception as e:
            logger.error(f"❌ Failed to apply migration {migration_name}: {e}")
            raise

    def run_migrations(self):
        """Run all pending migrations."""
        logger.info("=" * 80)
        logger.info("🔄 Starting database migration")
        logger.info("=" * 80)

        self.connect()

        try:
            pending = self.get_pending_migrations()

            if not pending:
                logger.info("✅ No pending migrations. Database is up to date.")
                return

            logger.info(f"Found {len(pending)} pending migration(s)")

            for migration_name, file_path in pending:
                self.apply_migration(migration_name, file_path)

            logger.info("=" * 80)
            logger.info("✅ All migrations applied successfully!")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            raise
        finally:
            self.close()

    def rollback_migration(self, migration_name: str):
        """
        Rollback a specific migration.

        Note: This requires a separate rollback SQL file.

        Args:
            migration_name (str): Name of migration to rollback
        """
        logger.warning(f"⚠️  Rollback requested for: {migration_name}")
        logger.warning("⚠️  Manual rollback required - no automatic rollback implemented")

    def show_status(self):
        """Show migration status."""
        self.connect()

        try:
            applied = self.get_applied_migrations()
            pending = self.get_pending_migrations()

            logger.info("=" * 80)
            logger.info("📊 Migration Status")
            logger.info("=" * 80)
            logger.info(f"Applied migrations: {len(applied)}")
            for migration in applied:
                logger.info(f"  ✅ {migration}")

            logger.info(f"\nPending migrations: {len(pending)}")
            for migration_name, _ in pending:
                logger.info(f"  ⏳ {migration_name}")

            logger.info("=" * 80)

        finally:
            self.close()


def main():
    """Main entry point for migration runner."""
    import argparse

    parser = argparse.ArgumentParser(description="Run database migrations")
    parser.add_argument(
        "command",
        choices=["migrate", "status"],
        help="Command to execute"
    )
    parser.add_argument(
        "--db-path",
        help="Path to DuckDB database file",
        default=None
    )

    args = parser.parse_args()

    runner = MigrationRunner(db_path=args.db_path)

    if args.command == "migrate":
        runner.run_migrations()
    elif args.command == "status":
        runner.show_status()


if __name__ == "__main__":
    main()
