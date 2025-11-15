#!/usr/bin/env python3
"""
Create audio tables for Phase 1 (Audio Foundation) implementation.

This migration creates the database schema for audio content (albums, singles),
audio tracks, artists, and genre taxonomies as specified in the
AUDIO_VIDEO_IMPLEMENTATION_PLAN.md.
"""

import sys
import os
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import db_manager


def create_audio_tables() -> bool:
    """
    Create audio-related tables in DuckDB.

    Returns:
        bool: True if migration successful, False otherwise
    """
    print("=" * 80)
    print("🎵 CREATING AUDIO TABLES - PHASE 1 (Audio Foundation)")
    print("=" * 80)
    print()

    try:
        conn = db_manager.get_duckdb_connection()

        # Check existing tables
        print("1. Checking existing tables...")
        existing_tables = conn.execute("SHOW TABLES").fetchall()
        table_names = {t[0] for t in existing_tables}
        print(f"   Found {len(table_names)} existing tables")
        print()

        tables_to_create = []

        # ============================================================
        # Table 1: audio_genres
        # ============================================================
        if "audio_genres" not in table_names:
            tables_to_create.append("audio_genres")
            print("2. Creating audio_genres table...")
            conn.execute("""
                CREATE TABLE audio_genres (
                    -- Primary Key
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

                    -- Genre Information
                    name VARCHAR(100) NOT NULL UNIQUE,
                    slug VARCHAR(100) NOT NULL UNIQUE,

                    -- Hierarchy
                    parent_genre_id UUID,

                    -- Description
                    description TEXT,

                    -- Metadata
                    color_code VARCHAR(20),  -- For UI visualization
                    icon_name VARCHAR(50),   -- Icon identifier

                    -- Timestamps
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    -- Foreign Key
                    FOREIGN KEY (parent_genre_id) REFERENCES audio_genres(id)
                )
            """)

            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audio_genres_slug ON audio_genres(slug)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audio_genres_parent ON audio_genres(parent_genre_id)")
            print("   ✅ audio_genres table created")
        else:
            print("2. ⚠️  audio_genres table already exists, skipping")

        print()

        # ============================================================
        # Table 2: artists
        # ============================================================
        if "artists" not in table_names:
            tables_to_create.append("artists")
            print("3. Creating artists table...")
            conn.execute("""
                CREATE TABLE artists (
                    -- Primary Key
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

                    -- External IDs
                    musicbrainz_id UUID,
                    spotify_id VARCHAR(100),

                    -- Basic Information
                    name VARCHAR(500) NOT NULL,
                    sort_name VARCHAR(500),  -- For alphabetical sorting

                    -- Type
                    artist_type VARCHAR(50),  -- 'person', 'group', 'orchestra', 'choir', 'character', 'other'

                    -- Metadata
                    bio TEXT,
                    country VARCHAR(10),  -- ISO country code

                    -- Dates
                    begin_date DATE,  -- Birth date or formation date
                    end_date DATE,    -- Death date or disbandment date

                    -- Media Assets
                    image_url VARCHAR(500),

                    -- Spotify Data
                    spotify_followers INTEGER,
                    spotify_popularity INTEGER,  -- 0-100

                    -- Timestamps
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_synced_musicbrainz TIMESTAMP,
                    last_synced_spotify TIMESTAMP
                )
            """)

            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_artists_name ON artists(name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_artists_musicbrainz_id ON artists(musicbrainz_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_artists_spotify_id ON artists(spotify_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_artists_artist_type ON artists(artist_type)")
            print("   ✅ artists table created")
        else:
            print("3. ⚠️  artists table already exists, skipping")

        print()

        # ============================================================
        # Table 3: audio_content
        # ============================================================
        if "audio_content" not in table_names:
            tables_to_create.append("audio_content")
            print("4. Creating audio_content table...")
            conn.execute("""
                CREATE TABLE audio_content (
                    -- Primary Key
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

                    -- External IDs
                    musicbrainz_id UUID,
                    spotify_id VARCHAR(100),

                    -- Basic Information
                    title VARCHAR(500) NOT NULL,
                    content_type VARCHAR(50) NOT NULL,  -- 'album', 'single', 'ep', 'compilation', 'soundtrack'

                    -- Artist Reference
                    primary_artist_id UUID NOT NULL,

                    -- Release Information
                    release_date DATE,
                    release_year INTEGER,

                    -- Metadata
                    total_tracks INTEGER,
                    total_duration_ms BIGINT,  -- Total duration in milliseconds

                    -- Album Art
                    cover_art_url VARCHAR(500),
                    cover_art_small_url VARCHAR(500),
                    cover_art_large_url VARCHAR(500),

                    -- Label & Copyright
                    record_label VARCHAR(200),
                    copyright_text TEXT,

                    -- Spotify Data
                    spotify_popularity INTEGER,  -- 0-100

                    -- Timestamps
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_synced_musicbrainz TIMESTAMP,
                    last_synced_spotify TIMESTAMP,

                    -- Foreign Keys
                    FOREIGN KEY (primary_artist_id) REFERENCES artists(id)
                )
            """)

            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audio_content_type ON audio_content(content_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audio_content_artist ON audio_content(primary_artist_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audio_content_release_date ON audio_content(release_date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audio_content_musicbrainz_id ON audio_content(musicbrainz_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audio_content_spotify_id ON audio_content(spotify_id)")
            print("   ✅ audio_content table created")
        else:
            print("4. ⚠️  audio_content table already exists, skipping")

        print()

        # ============================================================
        # Table 4: audio_tracks
        # ============================================================
        if "audio_tracks" not in table_names:
            tables_to_create.append("audio_tracks")
            print("5. Creating audio_tracks table...")
            conn.execute("""
                CREATE TABLE audio_tracks (
                    -- Primary Key
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

                    -- External IDs
                    musicbrainz_id UUID,
                    spotify_id VARCHAR(100),
                    isrc VARCHAR(20),  -- International Standard Recording Code

                    -- Basic Information
                    title VARCHAR(500) NOT NULL,
                    track_number INTEGER,
                    disc_number INTEGER DEFAULT 1,

                    -- Parent Reference
                    audio_content_id UUID NOT NULL,

                    -- Duration
                    duration_ms INTEGER NOT NULL,  -- Duration in milliseconds

                    -- Spotify Audio Features
                    spotify_preview_url VARCHAR(500),  -- 30-second preview URL
                    acousticness DECIMAL(5,4),  -- 0.0 to 1.0
                    danceability DECIMAL(5,4),  -- 0.0 to 1.0
                    energy DECIMAL(5,4),        -- 0.0 to 1.0
                    instrumentalness DECIMAL(5,4),  -- 0.0 to 1.0
                    liveness DECIMAL(5,4),      -- 0.0 to 1.0
                    loudness DECIMAL(6,3),      -- Typically -60 to 0 dB
                    speechiness DECIMAL(5,4),   -- 0.0 to 1.0
                    valence DECIMAL(5,4),       -- 0.0 to 1.0 (musical positivity)
                    tempo DECIMAL(7,3),         -- BPM
                    time_signature INTEGER,     -- 3, 4, 5, etc.
                    key INTEGER,                -- 0-11 (C, C#, D, ...)
                    mode INTEGER,               -- 0=minor, 1=major

                    -- Explicit Content
                    explicit BOOLEAN DEFAULT FALSE,

                    -- Timestamps
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_synced_musicbrainz TIMESTAMP,
                    last_synced_spotify TIMESTAMP,

                    -- Foreign Keys
                    FOREIGN KEY (audio_content_id) REFERENCES audio_content(id)
                )
            """)

            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audio_tracks_content ON audio_tracks(audio_content_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audio_tracks_track_number ON audio_tracks(track_number)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audio_tracks_spotify_id ON audio_tracks(spotify_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audio_tracks_musicbrainz_id ON audio_tracks(musicbrainz_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audio_tracks_isrc ON audio_tracks(isrc)")
            print("   ✅ audio_tracks table created")
        else:
            print("5. ⚠️  audio_tracks table already exists, skipping")

        print()

        # ============================================================
        # Table 5: audio_content_genres (Junction Table)
        # ============================================================
        if "audio_content_genres" not in table_names:
            tables_to_create.append("audio_content_genres")
            print("6. Creating audio_content_genres table...")
            conn.execute("""
                CREATE TABLE audio_content_genres (
                    -- Composite Primary Key
                    audio_content_id UUID NOT NULL,
                    genre_id UUID NOT NULL,

                    -- Metadata
                    relevance_score DECIMAL(3,2) DEFAULT 1.00,  -- 0.00 to 1.00

                    -- Timestamps
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    -- Primary Key
                    PRIMARY KEY (audio_content_id, genre_id),

                    -- Foreign Keys
                    FOREIGN KEY (audio_content_id) REFERENCES audio_content(id),
                    FOREIGN KEY (genre_id) REFERENCES audio_genres(id)
                )
            """)

            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audio_content_genres_content ON audio_content_genres(audio_content_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audio_content_genres_genre ON audio_content_genres(genre_id)")
            print("   ✅ audio_content_genres table created")
        else:
            print("6. ⚠️  audio_content_genres table already exists, skipping")

        print()

        # ============================================================
        # Table 6: audio_artists (Junction Table for Multiple Artists)
        # ============================================================
        if "audio_artists" not in table_names:
            tables_to_create.append("audio_artists")
            print("7. Creating audio_artists table...")
            conn.execute("""
                CREATE TABLE audio_artists (
                    -- Composite Primary Key
                    audio_content_id UUID NOT NULL,
                    artist_id UUID NOT NULL,

                    -- Role Information
                    role VARCHAR(100) DEFAULT 'artist',  -- 'artist', 'featured', 'composer', 'producer', etc.

                    -- Order
                    display_order INTEGER DEFAULT 0,

                    -- Timestamps
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    -- Primary Key
                    PRIMARY KEY (audio_content_id, artist_id, role),

                    -- Foreign Keys
                    FOREIGN KEY (audio_content_id) REFERENCES audio_content(id),
                    FOREIGN KEY (artist_id) REFERENCES artists(id)
                )
            """)

            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audio_artists_content ON audio_artists(audio_content_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audio_artists_artist ON audio_artists(artist_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audio_artists_role ON audio_artists(role)")
            print("   ✅ audio_artists table created")
        else:
            print("7. ⚠️  audio_artists table already exists, skipping")

        print()

        # Summary
        print("=" * 80)
        print("📊 MIGRATION SUMMARY")
        print("=" * 80)

        if tables_to_create:
            print(f"✅ Created {len(tables_to_create)} new tables:")
            for table in tables_to_create:
                print(f"   - {table}")
        else:
            print("⚠️  No new tables created (all tables already exist)")

        print()

        # Verify all tables exist
        print("🔍 Verifying table creation...")
        final_tables = conn.execute("SHOW TABLES").fetchall()
        final_table_names = {t[0] for t in final_tables}

        required_tables = [
            "audio_genres",
            "artists",
            "audio_content",
            "audio_tracks",
            "audio_content_genres",
            "audio_artists"
        ]

        all_exist = all(table in final_table_names for table in required_tables)

        if all_exist:
            print("✅ All required audio tables verified")
            print()
            print("📋 Audio Tables Created:")
            for table in required_tables:
                print(f"   ✓ {table}")
            return True
        else:
            missing = [t for t in required_tables if t not in final_table_names]
            print(f"❌ Missing tables: {', '.join(missing)}")
            return False

    except Exception as e:
        print(f"❌ Error creating audio tables: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print()
    success = create_audio_tables()
    print()
    print("=" * 80)
    if success:
        print("✅ AUDIO TABLES MIGRATION COMPLETED SUCCESSFULLY!")
        print()
        print("Next steps:")
        print("  1. Implement Spotify API client (backend/services/spotify_service.py)")
        print("  2. Enhance MusicBrainz service for full music catalog")
        print("  3. Build /api/audio/* CRUD endpoints")
        print("  4. Create album cover carousel (D3.js)")
        print("  5. Implement audio preview player (WaveSurfer.js)")
    else:
        print("❌ AUDIO TABLES MIGRATION FAILED!")
    print("=" * 80)
    print()
    sys.exit(0 if success else 1)
