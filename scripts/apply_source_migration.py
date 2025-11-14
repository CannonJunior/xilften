#!/usr/bin/env python3
"""
Apply the source column migration directly to the database.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import db_manager

def apply_migration():
    """Apply the source column migration."""
    print("=" * 80)
    print("Applying source column migration to soundtracks table")
    print("=" * 80)

    try:
        conn = db_manager.get_duckdb_connection()

        # Check if column already exists
        print("\n1. Checking if source column exists...")
        check_query = """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'soundtracks'
            AND column_name = 'source'
        """
        result = conn.execute(check_query).fetchone()

        if result:
            print("✅ Column 'source' already exists!")
            return True

        print("📝 Column 'source' does not exist, adding it...")

        # Add the column
        print("\n2. Adding source column...")
        alter_query = """
            ALTER TABLE soundtracks
            ADD COLUMN source VARCHAR DEFAULT 'unknown'
        """
        conn.execute(alter_query)
        print("✅ Column added successfully")

        # Update existing rows
        print("\n3. Updating existing rows...")
        update_query = """
            UPDATE soundtracks
            SET source = 'musicbrainz'
            WHERE source = 'unknown' AND musicbrainz_id IS NOT NULL
        """
        conn.execute(update_query)

        # Check how many rows were updated
        count_query = "SELECT COUNT(*) FROM soundtracks WHERE source = 'musicbrainz'"
        count = conn.execute(count_query).fetchone()[0]
        print(f"✅ Updated {count} existing rows to 'musicbrainz' source")

        # Verify the column exists now
        print("\n4. Verifying migration...")
        result = conn.execute(check_query).fetchone()
        if result:
            print("✅ Migration verified successfully!")

            # Show column details
            desc_query = """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'soundtracks'
                AND column_name = 'source'
            """
            details = conn.execute(desc_query).fetchone()
            if details:
                print(f"\nColumn details:")
                print(f"  Name: {details[0]}")
                print(f"  Type: {details[1]}")
                print(f"  Nullable: {details[2]}")

            return True
        else:
            print("❌ Migration verification failed!")
            return False

    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print()
    success = apply_migration()
    print()
    print("=" * 80)
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
    print("=" * 80)
    print()
    sys.exit(0 if success else 1)
