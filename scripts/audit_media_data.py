#!/usr/bin/env python3
"""
Media Data Audit Script

Audits all media entries in the database to identify:
1. Entries without poster_path
2. Entries without tmdb_id (not synced with TMDB)
3. Potential media type mismatches (e.g., TV series marked as movies)
4. Missing or inconsistent release dates
5. Entries that need TMDB sync

Usage:
    python scripts/audit_media_data.py [--fix] [--report-only]

Options:
    --fix: Attempt to fix issues by searching TMDB
    --report-only: Only generate report, don't attempt fixes
"""

import sys
import os
import asyncio
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MediaAuditor:
    """Audits media data for issues and inconsistencies."""

    def __init__(self):
        """Initialize the auditor."""
        import duckdb
        self.conn = duckdb.connect(settings.duckdb_database_path)
        self.issues = {
            'no_poster': [],
            'no_tmdb_id': [],
            'type_mismatch': [],
            'missing_date': [],
            'needs_sync': []
        }

    def run_audit(self) -> Dict[str, List[Any]]:
        """
        Run complete audit of media database.

        Returns:
            Dictionary of issues found
        """
        logger.info("🔍 Starting media data audit...")

        # Get all media entries
        query = """
            SELECT
                id, title, media_type, tmdb_id, poster_path,
                backdrop_path, release_date, last_synced_tmdb,
                overview, runtime
            FROM media
            ORDER BY title
        """

        results = self.conn.execute(query).fetchall()
        columns = ['id', 'title', 'media_type', 'tmdb_id', 'poster_path',
                   'backdrop_path', 'release_date', 'last_synced_tmdb',
                   'overview', 'runtime']

        media_entries = [dict(zip(columns, row)) for row in results]

        logger.info(f"📊 Found {len(media_entries)} media entries to audit")

        # Run checks
        for entry in media_entries:
            self._check_poster(entry)
            self._check_tmdb_id(entry)
            self._check_media_type(entry)
            self._check_release_date(entry)
            self._check_needs_sync(entry)

        return self.issues

    def _check_poster(self, entry: Dict[str, Any]):
        """Check if entry has poster_path."""
        if not entry['poster_path']:
            self.issues['no_poster'].append({
                'id': entry['id'],
                'title': entry['title'],
                'media_type': entry['media_type'],
                'tmdb_id': entry['tmdb_id']
            })

    def _check_tmdb_id(self, entry: Dict[str, Any]):
        """Check if entry has TMDB ID."""
        if not entry['tmdb_id']:
            self.issues['no_tmdb_id'].append({
                'id': entry['id'],
                'title': entry['title'],
                'media_type': entry['media_type']
            })

    def _check_media_type(self, entry: Dict[str, Any]):
        """
        Check for potential media type mismatches.

        Heuristics:
        - Has TMDB ID but media_type is 'anime' (TMDB doesn't have anime category)
        - Has runtime but no TMDB ID (movies usually have runtime)
        - Has overview mentioning 'series', 'season', 'episodes' but marked as movie
        """
        overview = (entry['overview'] or '').lower()

        # Check for series indicators in overview
        series_keywords = ['series', 'season', 'episodes', 'tv show']
        if entry['media_type'] == 'movie' and any(kw in overview for kw in series_keywords):
            self.issues['type_mismatch'].append({
                'id': entry['id'],
                'title': entry['title'],
                'media_type': entry['media_type'],
                'tmdb_id': entry['tmdb_id'],
                'reason': 'Overview suggests TV series'
            })

    def _check_release_date(self, entry: Dict[str, Any]):
        """Check if entry has release date."""
        if not entry['release_date']:
            self.issues['missing_date'].append({
                'id': entry['id'],
                'title': entry['title'],
                'media_type': entry['media_type'],
                'tmdb_id': entry['tmdb_id']
            })

    def _check_needs_sync(self, entry: Dict[str, Any]):
        """Check if entry needs TMDB sync."""
        # Has TMDB ID but missing critical data
        if entry['tmdb_id']:
            missing_data = []
            if not entry['poster_path']:
                missing_data.append('poster')
            if not entry['backdrop_path']:
                missing_data.append('backdrop')
            if not entry['overview']:
                missing_data.append('overview')
            if not entry['runtime']:
                missing_data.append('runtime')

            if missing_data:
                self.issues['needs_sync'].append({
                    'id': entry['id'],
                    'title': entry['title'],
                    'tmdb_id': entry['tmdb_id'],
                    'missing': missing_data
                })

    def generate_report(self) -> str:
        """
        Generate human-readable audit report.

        Returns:
            Report string
        """
        report = []
        report.append("=" * 80)
        report.append("MEDIA DATA AUDIT REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")

        # No Poster
        report.append(f"📷 Entries without poster_path: {len(self.issues['no_poster'])}")
        if self.issues['no_poster']:
            for item in self.issues['no_poster'][:5]:
                report.append(f"   - {item['title']} ({item['media_type']}) "
                             f"[TMDB: {item['tmdb_id'] or 'None'}]")
            if len(self.issues['no_poster']) > 5:
                report.append(f"   ... and {len(self.issues['no_poster']) - 5} more")
        report.append("")

        # No TMDB ID
        report.append(f"🔗 Entries without TMDB ID: {len(self.issues['no_tmdb_id'])}")
        if self.issues['no_tmdb_id']:
            for item in self.issues['no_tmdb_id'][:5]:
                report.append(f"   - {item['title']} ({item['media_type']})")
            if len(self.issues['no_tmdb_id']) > 5:
                report.append(f"   ... and {len(self.issues['no_tmdb_id']) - 5} more")
        report.append("")

        # Media Type Mismatches
        report.append(f"⚠️  Potential media type mismatches: {len(self.issues['type_mismatch'])}")
        if self.issues['type_mismatch']:
            for item in self.issues['type_mismatch']:
                report.append(f"   - {item['title']} ({item['media_type']}) "
                             f"- {item['reason']}")
        report.append("")

        # Missing Dates
        report.append(f"📅 Entries without release date: {len(self.issues['missing_date'])}")
        if self.issues['missing_date']:
            for item in self.issues['missing_date'][:5]:
                report.append(f"   - {item['title']} ({item['media_type']})")
            if len(self.issues['missing_date']) > 5:
                report.append(f"   ... and {len(self.issues['missing_date']) - 5} more")
        report.append("")

        # Needs Sync
        report.append(f"🔄 Entries needing TMDB sync: {len(self.issues['needs_sync'])}")
        if self.issues['needs_sync']:
            for item in self.issues['needs_sync'][:5]:
                report.append(f"   - {item['title']} [TMDB: {item['tmdb_id']}] "
                             f"Missing: {', '.join(item['missing'])}")
            if len(self.issues['needs_sync']) > 5:
                report.append(f"   ... and {len(self.issues['needs_sync']) - 5} more")
        report.append("")

        report.append("=" * 80)
        report.append("RECOMMENDATIONS")
        report.append("=" * 80)

        if self.issues['no_tmdb_id']:
            report.append("• Run TMDB search for entries without TMDB ID")
            report.append("  Example: python scripts/link_to_tmdb.py --auto")

        if self.issues['needs_sync']:
            report.append("• Sync entries with TMDB to get missing data")
            report.append("  Example: python scripts/sync_tmdb_data.py --missing-only")

        if self.issues['type_mismatch']:
            report.append("• Review and correct media type mismatches manually")

        report.append("")

        return "\n".join(report)


async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Audit media data for issues')
    parser.add_argument('--fix', action='store_true',
                       help='Attempt to fix issues automatically')
    parser.add_argument('--report-only', action='store_true',
                       help='Only generate report, no fixes')
    args = parser.parse_args()

    auditor = MediaAuditor()

    # Run audit
    issues = auditor.run_audit()

    # Generate and display report
    report = auditor.generate_report()
    print(report)

    # Save report to file
    report_file = 'media_audit_report.txt'
    with open(report_file, 'w') as f:
        f.write(report)

    logger.info(f"📄 Report saved to: {report_file}")

    # Summary
    total_issues = sum(len(v) for v in issues.values())
    if total_issues == 0:
        logger.info("✅ No issues found! Database is in good shape.")
    else:
        logger.info(f"⚠️  Found {total_issues} total issues across {len([k for k, v in issues.items() if v])} categories")

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
