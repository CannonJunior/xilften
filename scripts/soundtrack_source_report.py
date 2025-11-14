#!/usr/bin/env python3
"""
Generate a report on soundtrack sources in the database.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import db_manager

def generate_report():
    """Generate soundtrack source report."""
    print("=" * 80)
    print("SOUNDTRACK SOURCE REPORT")
    print("=" * 80)
    print()

    try:
        conn = db_manager.get_duckdb_connection()

        # Total soundtracks
        total_query = "SELECT COUNT(*) FROM soundtracks"
        total = conn.execute(total_query).fetchone()[0]
        print(f"📊 Total Soundtracks: {total}")
        print()

        # Breakdown by source
        source_query = """
            SELECT
                COALESCE(source, 'null') as source,
                COUNT(*) as count
            FROM soundtracks
            GROUP BY source
            ORDER BY count DESC
        """
        results = conn.execute(source_query).fetchall()

        print("📈 BY SOURCE:")
        for source, count in results:
            percentage = (count / total * 100) if total > 0 else 0
            print(f"   {source.upper():15s}: {count:3d} ({percentage:5.1f}%)")
        print()

        # Sample soundtracks from each source
        print("🎵 SAMPLE SOUNDTRACKS:")
        for source, _ in results:
            sample_query = f"""
                SELECT
                    s.title,
                    m.title as movie_title,
                    s.total_tracks
                FROM soundtracks s
                JOIN media m ON s.media_id = m.id
                WHERE COALESCE(s.source, 'null') = '{source}'
                LIMIT 3
            """
            samples = conn.execute(sample_query).fetchall()

            print(f"\n   {source.upper()}:")
            for soundtrack_title, movie_title, tracks in samples:
                print(f"     • {movie_title}: {soundtrack_title} ({tracks} tracks)")

        print()
        print("=" * 80)
        return True

    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = generate_report()
    sys.exit(0 if success else 1)
