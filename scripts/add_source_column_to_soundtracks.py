#!/usr/bin/env python3
"""
Add source column to soundtracks table.

This migration adds a 'source' column to track which data source
provided the soundtrack data (musicbrainz, imdb, spotify, etc.).
"""

import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def add_source_column():
    """Add source column to soundtracks table."""
    try:
        logger.info("🔧 Adding 'source' column to soundtracks table...")

        conn = db_manager.get_duckdb_connection()

        # Check if column already exists
        check_query = """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'soundtracks'
            AND column_name = 'source'
        """

        result = conn.execute(check_query).fetchone()

        if result:
            logger.info("✅ Column 'source' already exists!")
            return

        # Add the column with default value
        alter_query = """
            ALTER TABLE soundtracks
            ADD COLUMN source VARCHAR DEFAULT 'unknown'
        """

        conn.execute(alter_query)

        # Update existing rows to have 'musicbrainz' as source (since all current soundtracks are from MusicBrainz)
        update_query = """
            UPDATE soundtracks
            SET source = 'musicbrainz'
            WHERE source = 'unknown' AND musicbrainz_id IS NOT NULL
        """

        rows_updated = conn.execute(update_query).fetchone()[0]

        logger.info(f"✅ Successfully added 'source' column to soundtracks table")
        logger.info(f"✅ Updated {rows_updated} existing rows to source='musicbrainz'")

    except Exception as e:
        logger.error(f"❌ Error adding source column: {e}")
        raise


def main():
    """Main execution."""
    try:
        add_source_column()
        logger.info("🎉 Migration complete!")
        return 0
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
