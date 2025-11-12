-- Migration: Add Soundtrack and Music Tables
-- Created: 2025-11-11
-- Description: Adds tables for storing movie soundtracks and music metadata

-- Table: soundtracks
CREATE TABLE IF NOT EXISTS soundtracks (
    id VARCHAR PRIMARY KEY,
    media_id VARCHAR NOT NULL,
    title VARCHAR(500) NOT NULL,
    release_date DATE,
    label VARCHAR(200),
    musicbrainz_id VARCHAR(100),
    spotify_album_id VARCHAR(100),
    lastfm_url VARCHAR(500),
    album_art_url VARCHAR(500),
    total_tracks INTEGER,
    duration_ms INTEGER,
    description TEXT,
    album_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_synced TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_soundtracks_media ON soundtracks(media_id);
CREATE INDEX IF NOT EXISTS idx_soundtracks_musicbrainz ON soundtracks(musicbrainz_id);
CREATE INDEX IF NOT EXISTS idx_soundtracks_spotify ON soundtracks(spotify_album_id);

-- Table: soundtrack_tracks
CREATE TABLE IF NOT EXISTS soundtrack_tracks (
    id VARCHAR PRIMARY KEY,
    soundtrack_id VARCHAR NOT NULL,
    track_number INTEGER NOT NULL,
    disc_number INTEGER DEFAULT 1,
    title VARCHAR(500) NOT NULL,
    artist VARCHAR(300),
    composer VARCHAR(300),
    duration_ms INTEGER,
    musicbrainz_recording_id VARCHAR(100),
    spotify_track_id VARCHAR(100),
    isrc VARCHAR(20),
    preview_url VARCHAR(500),
    spotify_uri VARCHAR(200),
    explicit BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tracks_soundtrack ON soundtrack_tracks(soundtrack_id);
CREATE INDEX IF NOT EXISTS idx_tracks_spotify ON soundtrack_tracks(spotify_track_id);
CREATE INDEX IF NOT EXISTS idx_tracks_musicbrainz ON soundtrack_tracks(musicbrainz_recording_id);

-- Table: music_artists
CREATE TABLE IF NOT EXISTS music_artists (
    id VARCHAR PRIMARY KEY,
    name VARCHAR(300) NOT NULL UNIQUE,
    musicbrainz_artist_id VARCHAR(100),
    spotify_artist_id VARCHAR(100),
    image_url VARCHAR(500),
    genres JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_artists_name ON music_artists(name);
CREATE INDEX IF NOT EXISTS idx_artists_musicbrainz ON music_artists(musicbrainz_artist_id);
CREATE INDEX IF NOT EXISTS idx_artists_spotify ON music_artists(spotify_artist_id);

-- Table: track_artists
CREATE TABLE IF NOT EXISTS track_artists (
    track_id VARCHAR NOT NULL,
    artist_id VARCHAR NOT NULL,
    role VARCHAR(100),
    PRIMARY KEY (track_id, artist_id, role)
);

CREATE INDEX IF NOT EXISTS idx_track_artists_track ON track_artists(track_id);
CREATE INDEX IF NOT EXISTS idx_track_artists_artist ON track_artists(artist_id);
