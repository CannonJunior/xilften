-- XILFTEN Initial Database Schema
-- Migration: 001
-- Created: 2025-11-04
-- Description: Create all initial tables for XILFTEN media scheduling application

-- ============================================================================
-- TABLE: media
-- Stores all media entries (movies, TV shows, anime, etc.)
-- ============================================================================
CREATE TABLE IF NOT EXISTS media (
    -- Primary Key
    id VARCHAR PRIMARY KEY,

    -- External IDs
    tmdb_id INTEGER UNIQUE,
    imdb_id VARCHAR(20),

    -- Basic Information
    title VARCHAR(500) NOT NULL,
    original_title VARCHAR(500),
    media_type VARCHAR(50) NOT NULL, -- 'movie', 'tv', 'anime', 'documentary'

    -- Metadata
    release_date DATE,
    runtime INTEGER, -- in minutes
    overview TEXT,
    tagline VARCHAR(500),

    -- Ratings & Popularity
    tmdb_rating DECIMAL(3,1), -- 0.0 to 10.0
    tmdb_vote_count INTEGER,
    user_rating DECIMAL(3,1), -- User's personal rating
    popularity_score DECIMAL(10,2),

    -- Content Classification
    maturity_rating VARCHAR(20), -- 'G', 'PG', 'PG-13', 'R', 'NC-17', 'TV-MA', etc.
    recommended_age_min INTEGER,
    recommended_age_max INTEGER,

    -- Language & Country
    original_language VARCHAR(10),
    production_countries VARCHAR, -- JSON array as text
    spoken_languages VARCHAR, -- JSON array as text

    -- Media Assets
    poster_path VARCHAR(500),
    backdrop_path VARCHAR(500),
    trailer_url VARCHAR(500),

    -- Status
    status VARCHAR(50), -- 'Released', 'In Production', 'Planned', 'Canceled'

    -- Custom Fields Support
    custom_fields VARCHAR, -- JSON object as text

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_synced_tmdb TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_media_type ON media(media_type);
CREATE INDEX IF NOT EXISTS idx_release_date ON media(release_date);
CREATE INDEX IF NOT EXISTS idx_tmdb_id ON media(tmdb_id);
CREATE INDEX IF NOT EXISTS idx_maturity_rating ON media(maturity_rating);
CREATE INDEX IF NOT EXISTS idx_title ON media(title);

-- ============================================================================
-- TABLE: genres
-- Genre taxonomy and classification
-- ============================================================================
CREATE TABLE IF NOT EXISTS genres (
    -- Primary Key
    id VARCHAR PRIMARY KEY,

    -- Genre Information
    tmdb_genre_id INTEGER UNIQUE,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE, -- URL-friendly identifier

    -- Hierarchy
    parent_genre_id VARCHAR, -- For sub-genres
    genre_category VARCHAR(100), -- 'film-noir', 'sci-fi', 'documentary', etc.

    -- Description
    description TEXT,

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

);

CREATE INDEX IF NOT EXISTS idx_parent_genre ON genres(parent_genre_id);
CREATE INDEX IF NOT EXISTS idx_category ON genres(genre_category);
CREATE INDEX IF NOT EXISTS idx_genre_slug ON genres(slug);

-- ============================================================================
-- TABLE: media_genres
-- Many-to-many relationship between media and genres
-- ============================================================================
CREATE TABLE IF NOT EXISTS media_genres (
    media_id VARCHAR NOT NULL,
    genre_id VARCHAR NOT NULL,

    -- Optional: Weight for multi-genre films
    weight DECIMAL(3,2) DEFAULT 1.0, -- 0.0 to 1.0, primary vs secondary genre

    PRIMARY KEY (media_id, genre_id),
);

CREATE INDEX IF NOT EXISTS idx_media_genres_media ON media_genres(media_id);
CREATE INDEX IF NOT EXISTS idx_media_genres_genre ON media_genres(genre_id);

-- ============================================================================
-- TABLE: people
-- Actors, directors, writers, crew
-- ============================================================================
CREATE TABLE IF NOT EXISTS people (
    -- Primary Key
    id VARCHAR PRIMARY KEY,

    -- External IDs
    tmdb_person_id INTEGER UNIQUE,
    imdb_id VARCHAR(20),

    -- Personal Information
    name VARCHAR(200) NOT NULL,
    biography TEXT,
    birthday DATE,
    deathday DATE,

    -- Professional
    known_for_department VARCHAR(100), -- 'Acting', 'Directing', 'Writing', etc.

    -- Media Assets
    profile_path VARCHAR(500),

    -- Calculated Scores
    overall_rating DECIMAL(3,1), -- Average rating across all works
    total_works INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tmdb_person ON people(tmdb_person_id);
CREATE INDEX IF NOT EXISTS idx_known_for ON people(known_for_department);
CREATE INDEX IF NOT EXISTS idx_person_name ON people(name);

-- ============================================================================
-- TABLE: media_credits
-- Cast and crew credits for media
-- ============================================================================
CREATE TABLE IF NOT EXISTS media_credits (
    -- Primary Key
    id VARCHAR PRIMARY KEY,

    -- Relationships
    media_id VARCHAR NOT NULL,
    person_id VARCHAR NOT NULL,

    -- Credit Information
    credit_type VARCHAR(50) NOT NULL, -- 'cast', 'crew'
    department VARCHAR(100), -- 'Acting', 'Directing', 'Writing', 'Production', etc.
    job VARCHAR(100), -- 'Director', 'Screenplay', 'Producer', etc.
    character_name VARCHAR(200), -- For cast members

    -- Ordering
    order_position INTEGER, -- For cast: billing order, 0 = lead

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

);

CREATE INDEX IF NOT EXISTS idx_credits_media ON media_credits(media_id);
CREATE INDEX IF NOT EXISTS idx_credits_person ON media_credits(person_id);
CREATE INDEX IF NOT EXISTS idx_credits_type ON media_credits(credit_type);

-- ============================================================================
-- TABLE: user_reviews
-- User's personal reviews and ratings
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_reviews (
    -- Primary Key
    id VARCHAR PRIMARY KEY,

    -- Relationships
    media_id VARCHAR NOT NULL,

    -- Review Content
    rating DECIMAL(3,1) NOT NULL, -- 0.0 to 10.0
    review_text TEXT,

    -- Review Metadata
    watched_date DATE,
    rewatch_count INTEGER DEFAULT 0,

    -- Emotional Response (optional tags)
    tags VARCHAR, -- JSON array as text: ['thought-provoking', 'emotional', etc.]

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

);

CREATE INDEX IF NOT EXISTS idx_reviews_media ON user_reviews(media_id);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON user_reviews(rating);
CREATE INDEX IF NOT EXISTS idx_reviews_watched_date ON user_reviews(watched_date);

-- ============================================================================
-- TABLE: calendar_events
-- Calendar entries for scheduled watches, releases, and reviews
-- ============================================================================
CREATE TABLE IF NOT EXISTS calendar_events (
    -- Primary Key
    id VARCHAR PRIMARY KEY,

    -- Relationships
    media_id VARCHAR,

    -- Event Details
    event_type VARCHAR(50) NOT NULL, -- 'watch', 'release', 'review', 'custom'
    event_date DATE NOT NULL,
    event_time TIME,

    -- Event Information
    title VARCHAR(200),
    description TEXT,
    location VARCHAR(200), -- 'Netflix', 'Theater', 'Home', etc.

    -- Visual Categorization
    icon VARCHAR(50), -- Icon identifier for UI
    color VARCHAR(7), -- Hex color code (#RRGGBB)

    -- Reminder Settings
    reminder_enabled BOOLEAN DEFAULT FALSE,
    reminder_minutes INTEGER, -- Minutes before event

    -- Status
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

);

CREATE INDEX IF NOT EXISTS idx_events_media ON calendar_events(media_id);
CREATE INDEX IF NOT EXISTS idx_events_date ON calendar_events(event_date);
CREATE INDEX IF NOT EXISTS idx_events_type ON calendar_events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_completed ON calendar_events(completed);

-- ============================================================================
-- TABLE: recommendation_criteria
-- User-defined multi-criteria recommendation presets
-- ============================================================================
CREATE TABLE IF NOT EXISTS recommendation_criteria (
    -- Primary Key
    id VARCHAR PRIMARY KEY,

    -- Preset Information
    name VARCHAR(200) NOT NULL,
    description TEXT,

    -- Criteria Configuration (JSON as text)
    criteria_config VARCHAR NOT NULL,

    -- Metadata
    is_default BOOLEAN DEFAULT FALSE,
    use_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_criteria_name ON recommendation_criteria(name);
CREATE INDEX IF NOT EXISTS idx_criteria_default ON recommendation_criteria(is_default);

-- ============================================================================
-- TABLE: custom_fields_schema
-- Defines user-created custom fields for media
-- ============================================================================
CREATE TABLE IF NOT EXISTS custom_fields_schema (
    -- Primary Key
    id VARCHAR PRIMARY KEY,

    -- Field Definition
    field_name VARCHAR(100) NOT NULL UNIQUE,
    field_label VARCHAR(200) NOT NULL,
    field_type VARCHAR(50) NOT NULL, -- 'text', 'number', 'boolean', 'select', 'multi-select', 'date'

    -- Field Configuration
    field_options VARCHAR, -- JSON for select/multi-select
    field_default_value VARCHAR(500),
    is_required BOOLEAN DEFAULT FALSE,

    -- Validation Rules
    validation_rules VARCHAR, -- JSON

    -- Metadata
    description TEXT,
    help_text VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_custom_fields_name ON custom_fields_schema(field_name);
CREATE INDEX IF NOT EXISTS idx_custom_fields_active ON custom_fields_schema(is_active);

-- ============================================================================
-- TABLE: watch_history
-- Track viewing history for recommendation algorithms
-- ============================================================================
CREATE TABLE IF NOT EXISTS watch_history (
    -- Primary Key
    id VARCHAR PRIMARY KEY,

    -- Relationships
    media_id VARCHAR NOT NULL,

    -- Watch Details
    watched_at TIMESTAMP NOT NULL,
    watch_duration INTEGER, -- Minutes actually watched
    completion_percentage DECIMAL(5,2), -- 0.00 to 100.00

    -- Context
    watch_source VARCHAR(100), -- 'Netflix', 'Amazon Prime', 'Theater', 'Physical', etc.
    watch_method VARCHAR(50), -- 'streaming', 'download', 'physical', 'theater'

    -- Engagement Metrics
    paused_count INTEGER DEFAULT 0,
    rewind_count INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

);

CREATE INDEX IF NOT EXISTS idx_watch_history_media ON watch_history(media_id);
CREATE INDEX IF NOT EXISTS idx_watch_history_watched_at ON watch_history(watched_at);

-- ============================================================================
-- TABLE: migrations
-- Track applied database migrations
-- ============================================================================
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY,
    migration_name VARCHAR(255) NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Record this migration
INSERT INTO migrations (id, migration_name) VALUES (1, '001_initial_schema');
