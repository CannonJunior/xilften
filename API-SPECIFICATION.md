# XILFTEN - API Specification
**Version:** 1.0.0
**Base URL:** `http://localhost:7575`
**Last Updated:** 2025-11-03

---

## 🌐 API OVERVIEW

**Framework:** FastAPI (Python 3.11+)
**Authentication:** Not implemented in v1.0 (local-only application)
**Response Format:** JSON
**Character Encoding:** UTF-8
**CORS:** Enabled for localhost frontend

---

## 📋 API CONVENTIONS

### Response Structure
All successful responses follow this structure:

```json
{
    "success": true,
    "data": { ... },
    "message": "Optional success message",
    "timestamp": "2025-11-03T12:00:00Z"
}
```

### Error Response Structure
All error responses follow this structure:

```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable error message",
        "details": { ... }
    },
    "timestamp": "2025-11-03T12:00:00Z"
}
```

### HTTP Status Codes
- `200 OK` - Successful GET, PUT, DELETE
- `201 Created` - Successful POST creating new resource
- `204 No Content` - Successful DELETE with no response body
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server-side error
- `503 Service Unavailable` - External service (TMDB, Ollama) unavailable

### Pagination
For list endpoints:

```json
{
    "items": [...],
    "total": 150,
    "page": 1,
    "page_size": 20,
    "total_pages": 8
}
```

---

## 🎬 MEDIA ENDPOINTS

### 1. Get All Media
**Endpoint:** `GET /api/media`
**Description:** Retrieve paginated list of media with optional filtering

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | integer | No | Page number (default: 1) |
| page_size | integer | No | Items per page (default: 20, max: 100) |
| media_type | string | No | Filter by type: 'movie', 'tv', 'anime', 'documentary' |
| genre | string | No | Filter by genre slug (comma-separated for multiple) |
| min_rating | float | No | Minimum TMDB rating (0.0-10.0) |
| max_rating | float | No | Maximum TMDB rating (0.0-10.0) |
| year_from | integer | No | Minimum release year |
| year_to | integer | No | Maximum release year |
| maturity_rating | string | No | Filter by maturity rating |
| sort_by | string | No | Sort field: 'title', 'release_date', 'rating', 'popularity' (default: 'title') |
| sort_order | string | No | 'asc' or 'desc' (default: 'asc') |
| search | string | No | Full-text search on title |

**Example Request:**
```http
GET /api/media?page=1&page_size=20&genre=sci-fi&min_rating=7.0&sort_by=release_date&sort_order=desc
```

**Example Response:**
```json
{
    "success": true,
    "data": {
        "items": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "tmdb_id": 603,
                "title": "The Matrix",
                "media_type": "movie",
                "release_date": "1999-03-31",
                "runtime": 136,
                "tmdb_rating": 8.7,
                "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
                "genres": ["sci-fi", "action"]
            }
        ],
        "total": 42,
        "page": 1,
        "page_size": 20,
        "total_pages": 3
    }
}
```

---

### 2. Get Media by ID
**Endpoint:** `GET /api/media/{media_id}`
**Description:** Retrieve full details for a specific media item

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| media_id | UUID | Yes | Media unique identifier |

**Example Request:**
```http
GET /api/media/550e8400-e29b-41d4-a716-446655440000
```

**Example Response:**
```json
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "tmdb_id": 603,
        "imdb_id": "tt0133093",
        "title": "The Matrix",
        "original_title": "The Matrix",
        "media_type": "movie",
        "release_date": "1999-03-31",
        "runtime": 136,
        "overview": "Set in the 22nd century, The Matrix tells the story of a computer hacker...",
        "tagline": "Welcome to the Real World.",
        "tmdb_rating": 8.7,
        "tmdb_vote_count": 25847,
        "user_rating": 9.5,
        "popularity_score": 78.42,
        "maturity_rating": "R",
        "recommended_age_min": 17,
        "recommended_age_max": null,
        "original_language": "en",
        "production_countries": ["US"],
        "spoken_languages": ["en"],
        "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
        "backdrop_path": "/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=vKQi3bBA1y8",
        "status": "Released",
        "genres": [
            {"id": "uuid1", "name": "Science Fiction", "slug": "sci-fi"},
            {"id": "uuid2", "name": "Action", "slug": "action"}
        ],
        "cast": [
            {
                "person_id": "uuid3",
                "name": "Keanu Reeves",
                "character_name": "Neo",
                "order_position": 0,
                "profile_path": "/path.jpg"
            }
        ],
        "crew": [
            {
                "person_id": "uuid4",
                "name": "Lana Wachowski",
                "job": "Director",
                "department": "Directing"
            }
        ],
        "custom_fields": {},
        "created_at": "2025-11-03T10:00:00Z",
        "updated_at": "2025-11-03T12:00:00Z"
    }
}
```

---

### 3. Create Media
**Endpoint:** `POST /api/media`
**Description:** Create a new custom media entry

**Request Body:**
```json
{
    "title": "Custom Film Title",
    "media_type": "movie",
    "release_date": "2025-01-15",
    "runtime": 120,
    "overview": "A compelling story about...",
    "maturity_rating": "PG-13",
    "genres": ["drama", "thriller"],
    "custom_fields": {
        "personal_note": "Must watch this!"
    }
}
```

**Example Response:**
```json
{
    "success": true,
    "data": {
        "id": "new-uuid-here",
        "title": "Custom Film Title",
        ...
    },
    "message": "Media created successfully"
}
```

---

### 4. Update Media
**Endpoint:** `PUT /api/media/{media_id}`
**Description:** Update existing media entry

**Request Body:**
```json
{
    "user_rating": 8.5,
    "custom_fields": {
        "personal_note": "Amazing film!",
        "rewatch_value": "high"
    }
}
```

**Example Response:**
```json
{
    "success": true,
    "data": { ... },
    "message": "Media updated successfully"
}
```

---

### 5. Delete Media
**Endpoint:** `DELETE /api/media/{media_id}`
**Description:** Delete a media entry

**Example Response:**
```json
{
    "success": true,
    "message": "Media deleted successfully"
}
```

---

### 6. Fetch Media from TMDB
**Endpoint:** `POST /api/media/fetch-tmdb`
**Description:** Fetch media metadata from TMDB and create/update local entry

**Request Body:**
```json
{
    "tmdb_id": 603,
    "media_type": "movie"
}
```

**Example Response:**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "tmdb_id": 603,
        "title": "The Matrix",
        ...
    },
    "message": "Media fetched from TMDB successfully"
}
```

---

### 7. Search Media
**Endpoint:** `GET /api/media/search`
**Description:** Full-text search across media titles and overviews

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | Yes | Search query |
| page | integer | No | Page number (default: 1) |
| page_size | integer | No | Items per page (default: 20) |

**Example Request:**
```http
GET /api/media/search?q=matrix&page=1
```

---

## 🌟 GENRE ENDPOINTS

### 1. Get All Genres
**Endpoint:** `GET /api/genres`
**Description:** Retrieve genre taxonomy with hierarchy

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| category | string | No | Filter by genre category |
| include_inactive | boolean | No | Include inactive genres (default: false) |

**Example Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid1",
            "name": "Science Fiction",
            "slug": "sci-fi",
            "genre_category": "sci-fi",
            "parent_genre_id": null,
            "sub_genres": [
                {
                    "id": "uuid2",
                    "name": "Cyberpunk",
                    "slug": "cyberpunk",
                    "parent_genre_id": "uuid1"
                },
                {
                    "id": "uuid3",
                    "name": "Hard Sci-Fi",
                    "slug": "hard-sci-fi",
                    "parent_genre_id": "uuid1"
                }
            ]
        }
    ]
}
```

---

### 2. Get Genre by ID
**Endpoint:** `GET /api/genres/{genre_id}`
**Description:** Get detailed genre information with media count

**Example Response:**
```json
{
    "success": true,
    "data": {
        "id": "uuid1",
        "name": "Science Fiction",
        "slug": "sci-fi",
        "description": "Speculative fiction based on scientific concepts...",
        "media_count": 1247,
        "sub_genres": [...]
    }
}
```

---

## 👥 PEOPLE ENDPOINTS

### 1. Get Person by ID
**Endpoint:** `GET /api/people/{person_id}`
**Description:** Get detailed information about a person (actor/director/writer)

**Example Response:**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "tmdb_person_id": 6384,
        "name": "Keanu Reeves",
        "biography": "Keanu Charles Reeves is a Canadian actor...",
        "birthday": "1964-09-02",
        "known_for_department": "Acting",
        "overall_rating": 8.2,
        "total_works": 87,
        "profile_path": "/path.jpg",
        "recent_works": [...]
    }
}
```

---

## ⭐ REVIEW ENDPOINTS

### 1. Get Reviews for Media
**Endpoint:** `GET /api/reviews/media/{media_id}`
**Description:** Get all user reviews for a specific media

**Example Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "media_id": "media-uuid",
            "rating": 9.5,
            "review_text": "An absolute masterpiece...",
            "watched_date": "2025-10-15",
            "tags": ["thought-provoking", "visually-stunning"],
            "created_at": "2025-10-16T10:00:00Z"
        }
    ]
}
```

---

### 2. Create Review
**Endpoint:** `POST /api/reviews`
**Description:** Add a review for media

**Request Body:**
```json
{
    "media_id": "media-uuid",
    "rating": 9.5,
    "review_text": "An absolute masterpiece of sci-fi cinema!",
    "watched_date": "2025-10-15",
    "tags": ["thought-provoking", "visually-stunning"]
}
```

---

### 3. Update Review
**Endpoint:** `PUT /api/reviews/{review_id}`
**Description:** Update existing review

---

### 4. Delete Review
**Endpoint:** `DELETE /api/reviews/{review_id}`
**Description:** Delete a review

---

## 📅 CALENDAR ENDPOINTS

### 1. Get Calendar Events
**Endpoint:** `GET /api/calendar/events`
**Description:** Retrieve calendar events with date range filtering

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| start_date | date | No | Start of date range (ISO 8601: YYYY-MM-DD) |
| end_date | date | No | End of date range |
| event_type | string | No | Filter by type: 'watch', 'release', 'review', 'custom' |
| completed | boolean | No | Filter by completion status |

**Example Request:**
```http
GET /api/calendar/events?start_date=2025-11-01&end_date=2025-11-30
```

**Example Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "media_id": "media-uuid",
            "media_title": "The Matrix",
            "event_type": "watch",
            "event_date": "2025-11-15",
            "event_time": "19:00:00",
            "title": "Movie Night - The Matrix",
            "description": "Watching with friends",
            "location": "Home Theater",
            "icon": "movie",
            "color": "#FF6B6B",
            "completed": false
        }
    ]
}
```

---

### 2. Create Calendar Event
**Endpoint:** `POST /api/calendar/events`
**Description:** Create a new calendar event

**Request Body:**
```json
{
    "media_id": "media-uuid",
    "event_type": "watch",
    "event_date": "2025-11-15",
    "event_time": "19:00:00",
    "title": "Movie Night - The Matrix",
    "location": "Home Theater",
    "icon": "movie",
    "color": "#FF6B6B",
    "reminder_enabled": true,
    "reminder_minutes": 60
}
```

---

### 3. Update Calendar Event
**Endpoint:** `PUT /api/calendar/events/{event_id}`

---

### 4. Delete Calendar Event
**Endpoint:** `DELETE /api/calendar/events/{event_id}`

---

### 5. Mark Event Complete
**Endpoint:** `POST /api/calendar/events/{event_id}/complete`
**Description:** Mark calendar event as completed

**Example Response:**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "completed": true,
        "completed_at": "2025-11-15T20:30:00Z"
    }
}
```

---

## 🎯 RECOMMENDATION ENDPOINTS

### 1. Get Recommendations
**Endpoint:** `POST /api/recommendations/generate`
**Description:** Generate media recommendations based on criteria

**Request Body:**
```json
{
    "criteria_preset_id": "preset-uuid",
    "limit": 20,
    "exclude_watched": true
}
```

**Example Response:**
```json
{
    "success": true,
    "data": {
        "recommendations": [
            {
                "media": { ... },
                "score": 0.92,
                "score_breakdown": {
                    "genre_match": 1.0,
                    "rating_match": 0.95,
                    "maturity_match": 1.0,
                    "screenwriter_score": 0.85,
                    "director_score": 0.90
                },
                "reasoning": "Matches your preference for sci-fi action with high ratings"
            }
        ],
        "criteria_used": { ... },
        "total_matches": 156
    }
}
```

---

### 2. Get Similar Media
**Endpoint:** `GET /api/recommendations/similar/{media_id}`
**Description:** Find media similar to a specific title

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| limit | integer | No | Number of results (default: 10) |
| algorithm | string | No | 'vector', 'collaborative', 'hybrid' (default: 'hybrid') |

**Example Response:**
```json
{
    "success": true,
    "data": {
        "source_media": { ... },
        "similar_media": [
            {
                "media": { ... },
                "similarity_score": 0.87,
                "match_reasons": ["Same genre", "Similar director score", "Matching themes"]
            }
        ]
    }
}
```

---

## 🧠 CRITERIA ENDPOINTS

### 1. Get All Criteria Presets
**Endpoint:** `GET /api/criteria/presets`
**Description:** Retrieve all saved recommendation criteria presets

**Example Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "name": "High-Quality Sci-Fi",
            "description": "Science fiction with excellent ratings",
            "criteria_config": {
                "genre": {"weight": 1.0, "values": ["sci-fi"]},
                "min_rating": {"weight": 0.8, "value": 7.5},
                "director_score": {"weight": 0.7, "min": 8.0}
            },
            "is_default": false,
            "use_count": 15
        }
    ]
}
```

---

### 2. Create Criteria Preset
**Endpoint:** `POST /api/criteria/presets`
**Description:** Create new recommendation criteria preset

**Request Body:**
```json
{
    "name": "Friday Night Action",
    "description": "Fast-paced action movies for weekend viewing",
    "criteria_config": {
        "genre": {"weight": 1.0, "values": ["action"]},
        "runtime": {"weight": 0.5, "min": 90, "max": 140},
        "min_rating": {"weight": 0.6, "value": 7.0},
        "maturity_rating": {"weight": 0.3, "values": ["PG-13", "R"]}
    }
}
```

---

### 3. Update Criteria Preset
**Endpoint:** `PUT /api/criteria/presets/{preset_id}`

---

### 4. Delete Criteria Preset
**Endpoint:** `DELETE /api/criteria/presets/{preset_id}`

---

### 5. Get Available Criteria Fields
**Endpoint:** `GET /api/criteria/available-fields`
**Description:** Get list of all available fields for custom criteria

**Example Response:**
```json
{
    "success": true,
    "data": {
        "standard_fields": [
            {
                "name": "genre",
                "label": "Genre",
                "type": "multi-select",
                "options": ["sci-fi", "action", "drama", ...],
                "supports_weight": true
            },
            {
                "name": "min_rating",
                "label": "Minimum Rating",
                "type": "number",
                "min": 0,
                "max": 10,
                "supports_weight": true
            },
            {
                "name": "runtime",
                "label": "Runtime (minutes)",
                "type": "range",
                "min": 0,
                "max": 300,
                "supports_weight": true
            }
        ],
        "custom_fields": [
            {
                "name": "rewatch_value",
                "label": "Rewatch Value",
                "type": "select",
                "options": ["low", "medium", "high"]
            }
        ]
    }
}
```

---

## 🤖 AI / OLLAMA ENDPOINTS

### 1. Generate Mashup Recommendation
**Endpoint:** `POST /api/ai/mashup`
**Description:** Generate creative mashup recommendation from natural language query

**Request Body:**
```json
{
    "query": "suggest a movie with fantasy action like World of Warcraft but serious drama like Chernobyl",
    "model": "qwen2.5:3b",
    "max_results": 5
}
```

**Example Response:**
```json
{
    "success": true,
    "data": {
        "query": "fantasy action + serious drama",
        "extracted_criteria": {
            "genres": ["fantasy", "action", "drama"],
            "tone": ["serious", "dark"],
            "themes": ["epic-scale", "moral-complexity"]
        },
        "recommendations": [
            {
                "media": {
                    "title": "The Lord of the Rings: The Return of the King",
                    ...
                },
                "match_score": 0.89,
                "reasoning": "Epic fantasy action with serious dramatic themes exploring moral complexity and sacrifice, similar to the scale of World of Warcraft but with the gravitas of Chernobyl's serious tone."
            }
        ],
        "processing_time_ms": 847
    }
}
```

---

### 2. Generate High-Concept Summary
**Endpoint:** `POST /api/ai/high-concept`
**Description:** Create original high-concept summary from reference media

**Request Body:**
```json
{
    "reference_media": [
        {
            "title": "His Girl Friday",
            "extract_attributes": ["dialogue-style"]
        },
        {
            "title": "Game of Thrones",
            "extract_attributes": ["action", "political-intrigue"]
        },
        {
            "title": "Casablanca",
            "extract_attributes": ["plot-structure", "character-development"]
        }
    ],
    "additional_instructions": "Set in a cyberpunk future",
    "model": "llama3.1"
}
```

**Example Response:**
```json
{
    "success": true,
    "data": {
        "high_concept": "In a neon-drenched megacity, a fast-talking cyber-journalist must navigate deadly corporate espionage while rekindling a romance with a revolutionary hacker, as competing AI factions vie for control of humanity's digital consciousness.",

        "plot_points": [
            "Act 1: Introduction to protagonist and inciting incident",
            "Plot Point 1: Discovery of conspiracy that changes everything",
            "Midpoint: Major revelation and relationship turning point",
            "Plot Point 2: All seems lost, darkest moment",
            "Act 3: Climactic confrontation and resolution"
        ],

        "character_archetypes": [
            {
                "name": "The Cyber-Journalist",
                "archetype": "Fast-talking protagonist (His Girl Friday)",
                "development": "Character-driven growth (Casablanca)"
            },
            {
                "name": "The Hacker",
                "archetype": "Love interest with hidden agenda",
                "development": "Morally complex loyalties (Game of Thrones)"
            }
        ],

        "style_notes": {
            "dialogue": "Witty, rapid-fire exchanges inspired by His Girl Friday",
            "action": "Intense, brutal consequences like Game of Thrones",
            "structure": "Tight, plot-driven narrative like Casablanca"
        },

        "processing_time_ms": 3241
    }
}
```

---

### 3. Chat with AI
**Endpoint:** `POST /api/ai/chat`
**Description:** General conversational interface for media questions

**Request Body:**
```json
{
    "message": "What are some underrated Iranian films from the 1970s?",
    "conversation_id": "optional-uuid-for-history",
    "model": "qwen2.5:3b",
    "use_context": true
}
```

**Example Response:**
```json
{
    "success": true,
    "data": {
        "response": "Based on your media library and Iranian New Wave cinema, here are some underrated films from the 1970s:\n\n1. **Tranquility in the Presence of Others** (1972) by Nasser Taghvai...",
        "conversation_id": "uuid",
        "context_used": ["Iranian New Wave", "1970s cinema"],
        "suggested_media": [
            {
                "media_id": "uuid",
                "title": "Tranquility in the Presence of Others"
            }
        ]
    }
}
```

---

### 4. Get AI Model Status
**Endpoint:** `GET /api/ai/status`
**Description:** Check Ollama connection and available models

**Example Response:**
```json
{
    "success": true,
    "data": {
        "ollama_available": true,
        "ollama_url": "http://localhost:11434",
        "models": [
            {
                "name": "qwen2.5:3b",
                "size": "1.9GB",
                "status": "ready"
            },
            {
                "name": "llama3.1",
                "size": "4.7GB",
                "status": "ready"
            }
        ],
        "last_checked": "2025-11-03T12:00:00Z"
    }
}
```

---

## 🔧 CUSTOM FIELDS ENDPOINTS

### 1. Get Custom Field Schema
**Endpoint:** `GET /api/custom-fields/schema`
**Description:** Retrieve all defined custom fields

**Example Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "field_name": "rewatch_value",
            "field_label": "Rewatch Value",
            "field_type": "select",
            "field_options": ["low", "medium", "high"],
            "is_required": false,
            "description": "How likely you are to rewatch this media"
        }
    ]
}
```

---

### 2. Create Custom Field
**Endpoint:** `POST /api/custom-fields/schema`
**Description:** Define a new custom field

**Request Body:**
```json
{
    "field_name": "emotional_impact",
    "field_label": "Emotional Impact",
    "field_type": "number",
    "validation_rules": {
        "min": 1,
        "max": 10
    },
    "description": "Rate the emotional impact of the media",
    "help_text": "1 = Minimal emotional response, 10 = Life-changing impact"
}
```

---

## 📊 STATISTICS ENDPOINTS

### 1. Get Dashboard Statistics
**Endpoint:** `GET /api/stats/dashboard`
**Description:** Retrieve overview statistics for dashboard

**Example Response:**
```json
{
    "success": true,
    "data": {
        "total_media": 1247,
        "by_type": {
            "movie": 856,
            "tv": 245,
            "anime": 112,
            "documentary": 34
        },
        "total_reviews": 423,
        "average_rating": 7.8,
        "total_watch_time_minutes": 142580,
        "upcoming_events": 12,
        "watched_this_month": 8,
        "top_genres": [
            {"genre": "sci-fi", "count": 234},
            {"genre": "action", "count": 189}
        ]
    }
}
```

---

### 2. Get Watch History Stats
**Endpoint:** `GET /api/stats/watch-history`
**Description:** Analyze watch history patterns

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| period | string | No | 'week', 'month', 'year', 'all' (default: 'month') |

**Example Response:**
```json
{
    "success": true,
    "data": {
        "period": "month",
        "total_watched": 8,
        "total_minutes": 1052,
        "average_rating": 8.2,
        "by_genre": { ... },
        "by_day_of_week": { ... },
        "completion_rate": 0.875
    }
}
```

---

## 🔍 HEALTH & UTILITY ENDPOINTS

### 1. Health Check
**Endpoint:** `GET /api/health`
**Description:** Check API and service status

**Example Response:**
```json
{
    "success": true,
    "data": {
        "status": "healthy",
        "version": "1.0.0",
        "uptime_seconds": 3600,
        "services": {
            "database": "connected",
            "ollama": "connected",
            "tmdb": "connected"
        }
    }
}
```

---

### 2. Get API Version
**Endpoint:** `GET /api/version`

---

### 3. Clear Cache
**Endpoint:** `POST /api/admin/clear-cache`
**Description:** Clear API response cache (if implemented)

---

## 🔐 RATE LIMITING

### TMDB API Rate Limits
- Max 40 requests per 10 seconds
- Implement exponential backoff on 429 responses

### Ollama Rate Limits
- Depends on local hardware
- Queue requests if concurrent limit reached

### Internal API Rate Limits
- Not implemented in v1.0 (local-only application)
- Consider implementing for multi-user scenarios

---

## 🧪 TESTING ENDPOINTS

All endpoints should have corresponding test cases covering:
- ✅ Successful request (200/201)
- ✅ Validation errors (422)
- ✅ Not found (404)
- ✅ Server errors (500)
- ✅ Edge cases (empty results, large datasets, etc.)

---

## 📝 CHANGELOG

### v1.0.0 (2025-11-03)
- Initial API specification
- All core endpoints defined
- AI/Ollama integration endpoints
- Custom fields support
- Calendar event management

---

**End of API Specification**
