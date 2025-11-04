# XILFTEN - Database Schema Documentation
**Last Updated:** 2025-11-03
**Database:** ChromaDB + DuckDB (Vector Database)

---

## 🗄️ DATABASE ARCHITECTURE

This application uses a **hybrid database approach**:
- **ChromaDB**: Vector embeddings for semantic search and AI recommendations
- **DuckDB**: Relational data for structured media metadata, user data, and criteria
- **Local Storage**: Frontend state management and user preferences

---

## 📊 RELATIONAL SCHEMA (DuckDB)

### Table: `media`
Stores all media entries (movies, TV shows, anime, etc.)

```sql
CREATE TABLE media (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

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
    production_countries JSON, -- Array of country codes
    spoken_languages JSON, -- Array of language objects

    -- Media Assets
    poster_path VARCHAR(500),
    backdrop_path VARCHAR(500),
    trailer_url VARCHAR(500),

    -- Status
    status VARCHAR(50), -- 'Released', 'In Production', 'Planned', 'Canceled'

    -- Custom Fields Support
    custom_fields JSON, -- Flexible storage for user-defined criteria

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_synced_tmdb TIMESTAMP, -- Last TMDB data fetch

    -- Indexes
    INDEX idx_media_type (media_type),
    INDEX idx_release_date (release_date),
    INDEX idx_tmdb_id (tmdb_id),
    INDEX idx_maturity_rating (maturity_rating)
);
```

---

### Table: `genres`
Genre taxonomy and classification

```sql
CREATE TABLE genres (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Genre Information
    tmdb_genre_id INTEGER UNIQUE,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE, -- URL-friendly identifier

    -- Hierarchy
    parent_genre_id UUID REFERENCES genres(id), -- For sub-genres
    genre_category VARCHAR(100), -- 'film-noir', 'sci-fi', 'documentary', etc.

    -- Description
    description TEXT,

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    INDEX idx_parent_genre (parent_genre_id),
    INDEX idx_category (genre_category)
);
```

---

### Table: `media_genres`
Many-to-many relationship between media and genres

```sql
CREATE TABLE media_genres (
    media_id UUID REFERENCES media(id) ON DELETE CASCADE,
    genre_id UUID REFERENCES genres(id) ON DELETE CASCADE,

    -- Optional: Weight for multi-genre films
    weight DECIMAL(3,2) DEFAULT 1.0, -- 0.0 to 1.0, primary vs secondary genre

    PRIMARY KEY (media_id, genre_id),
    INDEX idx_media (media_id),
    INDEX idx_genre (genre_id)
);
```

---

### Table: `people`
Actors, directors, writers, crew

```sql
CREATE TABLE people (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    INDEX idx_tmdb_person (tmdb_person_id),
    INDEX idx_known_for (known_for_department)
);
```

---

### Table: `media_credits`
Cast and crew credits for media

```sql
CREATE TABLE media_credits (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationships
    media_id UUID REFERENCES media(id) ON DELETE CASCADE,
    person_id UUID REFERENCES people(id) ON DELETE CASCADE,

    -- Credit Information
    credit_type VARCHAR(50) NOT NULL, -- 'cast', 'crew'
    department VARCHAR(100), -- 'Acting', 'Directing', 'Writing', 'Production', etc.
    job VARCHAR(100), -- 'Director', 'Screenplay', 'Producer', etc.
    character_name VARCHAR(200), -- For cast members

    -- Ordering
    order_position INTEGER, -- For cast: billing order, 0 = lead

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    PRIMARY KEY (media_id, person_id, credit_type, department),
    INDEX idx_media (media_id),
    INDEX idx_person (person_id),
    INDEX idx_credit_type (credit_type)
);
```

---

### Table: `user_reviews`
User's personal reviews and ratings

```sql
CREATE TABLE user_reviews (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationships
    media_id UUID REFERENCES media(id) ON DELETE CASCADE,

    -- Review Content
    rating DECIMAL(3,1) NOT NULL, -- 0.0 to 10.0
    review_text TEXT,

    -- Review Metadata
    watched_date DATE,
    rewatch_count INTEGER DEFAULT 0,

    -- Emotional Response (optional tags)
    tags JSON, -- ['thought-provoking', 'emotional', 'entertaining', etc.]

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    INDEX idx_media (media_id),
    INDEX idx_rating (rating),
    INDEX idx_watched_date (watched_date)
);
```

---

### Table: `calendar_events`
Calendar entries for scheduled watches, releases, and reviews

```sql
CREATE TABLE calendar_events (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationships
    media_id UUID REFERENCES media(id) ON DELETE CASCADE,

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

    -- Indexes
    INDEX idx_media (media_id),
    INDEX idx_event_date (event_date),
    INDEX idx_event_type (event_type),
    INDEX idx_completed (completed)
);
```

---

### Table: `recommendation_criteria`
User-defined multi-criteria recommendation presets

```sql
CREATE TABLE recommendation_criteria (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Preset Information
    name VARCHAR(200) NOT NULL,
    description TEXT,

    -- Criteria Configuration (JSON)
    criteria_config JSON NOT NULL,
    /* Example structure:
    {
        "maturity_rating": {"weight": 0.8, "values": ["PG-13", "R"]},
        "genre": {"weight": 1.0, "values": ["sci-fi", "action"]},
        "min_rating": {"weight": 0.6, "value": 7.0},
        "runtime": {"weight": 0.3, "min": 90, "max": 150},
        "release_year": {"weight": 0.2, "min": 2010, "max": 2025},
        "screenwriter_score": {"weight": 0.7, "min": 7.5},
        "director_score": {"weight": 0.9, "min": 8.0},
        "custom_field_xyz": {"weight": 0.5, "value": "some_value"}
    }
    */

    -- Metadata
    is_default BOOLEAN DEFAULT FALSE,
    use_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    INDEX idx_name (name),
    INDEX idx_is_default (is_default)
);
```

---

### Table: `custom_fields_schema`
Defines user-created custom fields for media

```sql
CREATE TABLE custom_fields_schema (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Field Definition
    field_name VARCHAR(100) NOT NULL UNIQUE,
    field_label VARCHAR(200) NOT NULL,
    field_type VARCHAR(50) NOT NULL, -- 'text', 'number', 'boolean', 'select', 'multi-select', 'date'

    -- Field Configuration
    field_options JSON, -- For select/multi-select: ["option1", "option2"]
    field_default_value VARCHAR(500),
    is_required BOOLEAN DEFAULT FALSE,

    -- Validation Rules
    validation_rules JSON,
    /* Example:
    {
        "min": 0,
        "max": 100,
        "pattern": "^[A-Z]",
        "allowed_values": ["value1", "value2"]
    }
    */

    -- Metadata
    description TEXT,
    help_text VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    INDEX idx_field_name (field_name),
    INDEX idx_is_active (is_active)
);
```

---

### Table: `watch_history`
Track viewing history for recommendation algorithms

```sql
CREATE TABLE watch_history (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationships
    media_id UUID REFERENCES media(id) ON DELETE CASCADE,

    -- Watch Information
    watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    watch_duration INTEGER, -- Minutes watched (for partial watches)
    completed BOOLEAN DEFAULT TRUE,

    -- Context
    watch_source VARCHAR(100), -- 'Netflix', 'Theater', 'Blu-ray', etc.
    watch_context VARCHAR(100), -- 'Solo', 'With Friends', 'Date Night', etc.

    -- Engagement Metrics
    paused_count INTEGER DEFAULT 0,
    rewind_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    INDEX idx_media (media_id),
    INDEX idx_watched_at (watched_at),
    INDEX idx_completed (completed)
);
```

---

## 🧬 VECTOR DATABASE SCHEMA (ChromaDB)

### Collection: `media_embeddings`
Semantic embeddings for AI-powered recommendations

```python
# ChromaDB Collection Configuration
collection_name = "media_embeddings"

# Metadata stored with each embedding:
{
    "media_id": "uuid-string",
    "media_type": "movie|tv|anime|documentary",
    "title": "Media Title",
    "genres": ["genre1", "genre2"],
    "embedding_type": "overview|plot|themes|combined",
    "embedding_model": "ollama/qwen2.5:3b",
    "created_at": "2025-11-03T12:00:00Z"
}

# Document stored (for context retrieval):
# Full text: overview + plot + themes + user reviews
```

### Collection: `mashup_concepts`
Generated mashup concepts and high-concept summaries

```python
collection_name = "mashup_concepts"

# Metadata:
{
    "mashup_id": "uuid-string",
    "source_media_ids": ["uuid1", "uuid2", "uuid3"],
    "user_query": "original user request",
    "generated_at": "2025-11-03T12:00:00Z",
    "model_used": "ollama/qwen2.5:3b",
    "user_rating": 0-10  # Feedback mechanism
}

# Document:
# Generated high-concept summary and plot points
```

---

## 🔗 RELATIONSHIPS DIAGRAM

```
┌─────────────┐
│    media    │◄──────┐
└──────┬──────┘       │
       │              │
       │              │
       ▼              │
┌──────────────┐      │
│ media_genres │      │
└──────┬───────┘      │
       │              │
       ▼              │
┌─────────────┐       │
│   genres    │       │
└─────────────┘       │
                      │
┌──────────────┐      │
│media_credits │──────┘
└──────┬───────┘
       │
       ▼
┌─────────────┐
│   people    │
└─────────────┘

┌─────────────┐
│    media    │◄────┬────────────────┐
└──────┬──────┘     │                │
       │            │                │
       ├────────────┼────────────┐   │
       │            │            │   │
       ▼            ▼            ▼   ▼
┌──────────────┐ ┌─────────────┐ ┌──────────────┐
│user_reviews  │ │calendar_    │ │watch_        │
│              │ │events       │ │history       │
└──────────────┘ └─────────────┘ └──────────────┘
```

---

## 📈 DATA SEEDING PLAN

### Initial Genre Taxonomy Seed
Based on research, populate the `genres` table with:

1. **Film Noir** (6 sub-genres)
2. **Science Fiction** (9 sub-genres)
3. **Documentary** (6 modes)
4. **Comedy** (8 sub-genres)
5. **Anime** (5 demographics + 8 themes)
6. **Action** (8 sub-genres)
7. **Iranian Cinema** (4 movements)
8. **Multi-Genre** (hybrid combinations)

### Sample Media Data
Populate with 50-100 iconic films across all genres for testing:
- The Matrix (sci-fi, action)
- Blade Runner (tech-noir, sci-fi)
- Spirited Away (anime, fantasy)
- A Separation (Iranian, drama)
- His Girl Friday (screwball comedy)
- Game of Thrones (fantasy, drama) [TV]

---

## 🔍 INDEXES & PERFORMANCE

### Recommended Indexes
```sql
-- Full-text search on media titles
CREATE INDEX idx_media_title_fts ON media USING GIN(to_tsvector('english', title));

-- Composite index for filtering
CREATE INDEX idx_media_filter ON media(media_type, maturity_rating, release_date DESC);

-- Calendar date range queries
CREATE INDEX idx_calendar_date_range ON calendar_events(event_date, event_type);

-- Recommendation criteria usage
CREATE INDEX idx_criteria_usage ON recommendation_criteria(use_count DESC, created_at DESC);
```

### Query Optimization Notes
- Use prepared statements for repeated queries
- Implement query result caching for common filters
- Partition `watch_history` by year if dataset grows large
- Use DuckDB's columnar format for analytical queries

---

## 🔒 DATA INTEGRITY RULES

### Constraints
1. **media.tmdb_id** must be unique when not null
2. **user_reviews.rating** must be between 0.0 and 10.0
3. **calendar_events.event_date** cannot be more than 5 years in past (configurable)
4. **recommendation_criteria.criteria_config** must be valid JSON
5. **custom_fields_schema.field_name** must be alphanumeric + underscores only

### Cascading Deletes
- Deleting media → cascade to: media_genres, media_credits, user_reviews, calendar_events, watch_history
- Deleting people → cascade to: media_credits
- Deleting genres → cascade to: media_genres

### Triggers (Future Enhancement)
```sql
-- Auto-update media.updated_at on any change
CREATE TRIGGER update_media_timestamp
BEFORE UPDATE ON media
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Increment recommendation_criteria.use_count when used
CREATE TRIGGER increment_criteria_usage
AFTER INSERT ON recommendation_results  -- hypothetical table
FOR EACH ROW
EXECUTE FUNCTION increment_criteria_use_count();
```

---

## 🧪 MIGRATION STRATEGY

### Version Control
Use Alembic or custom migration scripts:

```
database/migrations/
├── 001_initial_schema.sql
├── 002_add_custom_fields.sql
├── 003_add_watch_history.sql
└── 004_add_indexes.sql
```

### Migration Checklist
- [ ] Create migration script
- [ ] Test on development database copy
- [ ] Document breaking changes
- [ ] Create rollback script
- [ ] Run migration
- [ ] Verify data integrity
- [ ] Update application models

---

**End of Database Schema Documentation**
