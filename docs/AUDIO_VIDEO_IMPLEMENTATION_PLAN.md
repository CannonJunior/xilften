# Audio & Video Content Sections - Implementation Plan

**Version:** 1.0
**Date:** 2025-11-14
**Status:** Draft - Awaiting Review
**Project:** XILFTEN Media Scheduling Application

---

## Executive Summary

This implementation plan outlines the phased development of two major content sections for XILFTEN:

1. **Audio Content Section** - Music, soundtracks, podcasts, audiobooks
2. **Short Video Section** - Trailers, music videos, clips, short-form content

The plan builds on existing infrastructure (DuckDB, FastAPI, D3.js) and integrates seamlessly with the current movie recommendation system, creating a unified multi-media discovery platform.

**Key Integration Points:**
- Movies ↔ Soundtracks (already partially implemented)
- Movies ↔ Video Clips (trailers, behind-the-scenes)
- Music ↔ Music Videos
- Cross-content discovery (mood, era, artist connections)

---

## I. Research Summary

### Completed Research Areas

✅ **Audio Content Taxonomy** - Identified 15+ content types including:
- Music (albums, singles, live recordings, remixes)
- Podcasts (8 subcategories)
- Audiobooks, DJ sets, meditation audio, field recordings

✅ **Video Content Taxonomy** - Identified 20+ content types including:
- Music videos (official, lyric, live)
- Movie/TV clips (trailers, scenes, interviews)
- Short-form native (TikTok-style, YouTube Shorts)
- Educational content (tutorials, essays, reviews)

✅ **Data Sources Evaluated** - Prioritized free, reliable APIs:
- **Audio:** MusicBrainz (primary), Spotify (previews), Last.fm (recommendations)
- **Video:** YouTube Data API (primary), TMDB (already integrated)

✅ **Cross-Content Integration Patterns** - Designed 12+ connection types:
- Soundtrack discovery from movies
- Song identification in video clips
- Artist/creator unified profiles
- Mood-based cross-content recommendations

✅ **Database Schema** - Complete schema design with 14 new tables:
- Audio tables (5): `audio_content`, `audio_tracks`, `artists`, `audio_playlists`, etc.
- Video tables (1): `video_content`
- Cross-reference tables (4): `media_audio_links`, `media_video_links`, etc.

✅ **Technical Architecture** - Defined:
- 40+ new API endpoints
- Data ingestion pipelines
- Multi-level caching strategy
- Performance optimization approaches

---

## II. Implementation Phases

### Phase 1: Audio Foundation (Weeks 1-2)
**Goal:** Basic audio content infrastructure with album browsing and playback

#### Database
- [ ] Create `audio_content` table (albums, singles, podcasts)
- [ ] Create `audio_tracks` table (individual tracks with Spotify features)
- [ ] Create `artists` table (unified artist/creator profiles)
- [ ] Create `audio_content_genres` table (music genre taxonomy)
- [ ] Add indexes for performance

#### Backend (FastAPI)
- [ ] Enhance MusicBrainz service for full music catalog (currently soundtrack-only)
- [ ] Create Spotify API client (`backend/services/spotify_service.py`)
  - Authentication (Client Credentials flow)
  - Album search
  - Track audio features (tempo, energy, danceability)
  - Preview URL retrieval
- [ ] Implement `/api/audio/albums` endpoints
  - `GET /` - List albums (pagination, filters)
  - `GET /{id}` - Get album with tracks
  - `POST /sync` - Sync from MusicBrainz + Spotify
- [ ] Implement `/api/audio/tracks` endpoints
  - `GET /{id}` - Get track details
  - `GET /{id}/audio-features` - Get Spotify features
- [ ] Create `/api/audio/search` endpoints

#### Frontend
- [ ] Create album cover carousel (D3.js, similar to movie poster carousel)
  - Horizontal scrolling with mousewheel
  - Drag-to-scroll functionality
  - Hover effects (scale, preview button)
- [ ] Implement audio preview player
  - Use WaveSurfer.js or custom D3.js waveform
  - 30-second preview playback (Spotify URLs)
  - Play/pause controls, volume slider
- [ ] Create album detail view
  - Album artwork, metadata
  - Track listing with durations
  - Genre tags, release info
  - "Featured in movies" badge (if applicable)

#### Success Metrics
- Load 100+ albums into database
- Preview playback functional for 80%+ tracks
- Sub-500ms album detail page load time

---

### Phase 2: Audio Discovery & Playlists (Week 3)
**Goal:** User engagement features and recommendations

#### Database
- [ ] Create `audio_playlists` table
- [ ] Create `audio_playlist_tracks` join table

#### Backend
- [ ] Implement Last.fm API client (`backend/services/lastfm_service.py`)
  - Similar artists recommendations
  - Tag-based discovery
  - Trending charts
- [ ] Create `/api/audio/playlists` endpoints
  - CRUD operations for playlists
  - Add/remove tracks
  - Reorder tracks
- [ ] Implement `/api/audio/recommendations` endpoint
  - Similar albums (Last.fm)
  - Mood-based filtering (Spotify audio features)
  - BPM-based DJ mix suggestions
- [ ] Create smart playlist generator
  - "Soundtracks from watched movies"
  - "High energy workout mix"
  - "Relaxing evening music"

#### Frontend
- [ ] Build playlist creation UI
  - Drag-and-drop tracks into playlist
  - Reorder within playlist
  - Visual feedback during drag
- [ ] Create genre filter sidebar
  - Genre taxonomy tree
  - Multi-select filtering
- [ ] Implement mood-based discovery
  - Mood slider (energy, valence)
  - Filter by tempo range (BPM)
- [ ] Add waveform visualization for tracks
  - Show tempo markers
  - Energy/danceability indicators

#### Success Metrics
- User can create playlists with 10+ tracks
- Recommendations accuracy > 70% (user feedback)
- Genre filtering reduces results by expected amount

---

### Phase 3: Movie-Audio Integration (Week 4)
**Goal:** Seamless navigation between movies and soundtracks

#### Database
- [ ] Enhance `soundtracks` table with `audio_content_id` foreign key
- [ ] Create `media_audio_links` table
  - Link movies to soundtrack albums
  - Link movies to featured songs (with timestamps)
- [ ] Migrate existing soundtrack data to new schema

#### Backend
- [ ] Update `SoundtrackService` to save to `audio_content` table
- [ ] Create `/api/connections/media/{media_id}/soundtrack` endpoint
- [ ] Create `/api/connections/audio/{audio_id}/movies` endpoint
- [ ] Implement song timeline feature
  - Store scene descriptions and timestamps
  - Extract from IMDB soundtrack data
- [ ] Add AcoustID integration (future: song identification from audio)

#### Frontend
- [ ] Add "Listen to Soundtrack" button on movie cards
  - Links to soundtrack album page
  - Shows track count badge
- [ ] Add "Featured in Movies" badge on albums
  - Hover shows movie posters
  - Click navigates to movie detail
- [ ] Create soundtrack detail page enhancement
  - Show linked movie poster
  - "Watch this movie" button
  - Track timeline (when songs appear in movie)
- [ ] Implement song-in-movie visualization
  - Timeline showing song placement in movie runtime
  - Click to jump to scene (future: video player integration)

#### Success Metrics
- 80%+ of existing soundtracks linked to audio_content
- Bidirectional navigation working (movie ↔ soundtrack)
- Song timeline data for 50%+ of soundtracks

---

### Phase 4: Video Foundation (Weeks 5-6)
**Goal:** Video content browsing and playback

#### Database
- [ ] Create `video_content` table
  - Support YouTube, Vimeo, TMDB sources
  - Store thumbnails, metadata, stats
- [ ] Create indexes on platform and content_type

#### Backend
- [ ] Implement YouTube Data API client (`backend/services/youtube_service.py`)
  - Video search
  - Video details retrieval
  - Quota management (10k units/day)
  - Result caching (24 hours)
- [ ] Enhance TMDB service for video endpoints
  - `GET /movie/{id}/videos`
  - Parse trailers, clips, interviews
- [ ] Create `/api/videos/` endpoints
  - `GET /search/youtube` - Search videos
  - `GET /search/tmdb` - Get movie videos
  - `GET /content` - List saved videos
  - `POST /content` - Add video to database
  - `GET /{id}/embed-url` - Get embed URL

#### Frontend
- [ ] Create video thumbnail grid
  - Responsive grid layout (2x3, 3x4)
  - Video duration badge
  - View count, publish date
  - Hover: Preview thumbnail animation
- [ ] Implement video player
  - YouTube iframe embed
  - Custom controls overlay
  - Related videos sidebar
  - "Watch on YouTube" button
- [ ] Create video detail page
  - Video metadata, description
  - Tags, categories
  - Related content section

#### Success Metrics
- Load 200+ video clips from YouTube/TMDB
- Video playback functional in embedded player
- Search returns relevant results

---

### Phase 5: Video Discovery & Integration (Week 7)
**Goal:** Connect videos to movies and music

#### Database
- [ ] Create `media_video_links` table (movies ↔ videos)
- [ ] Create `audio_video_links` table (music ↔ music videos)

#### Backend
- [ ] Create `/api/connections/media/{media_id}/videos` endpoint
- [ ] Create `/api/connections/audio/{track_id}/videos` endpoint
- [ ] Implement automatic trailer discovery
  - On movie add, search YouTube for official trailer
  - Store in video_content + create link
- [ ] Implement music video discovery
  - Search YouTube for "{artist} - {song} official music video"
  - Parse and link to audio_tracks

#### Frontend
- [ ] Add "Watch Trailer" button on movie cards
  - Opens modal with embedded player
  - Shows related clips (interviews, scenes)
- [ ] Add "Watch Music Video" button on track listings
  - Opens modal or inline player
  - Shows official video + live performances
- [ ] Create "All Videos" tab on movie detail page
  - Trailers, clips, interviews organized
- [ ] Create video feed for movie/artist
  - Chronological list of all videos
  - Filter by type (trailer, clip, interview)

#### Success Metrics
- 60%+ of movies have linked trailers
- 40%+ of popular tracks have linked music videos
- Video discovery from movies increases engagement

---

### Phase 6: Cross-Content Discovery (Week 8)
**Goal:** Unified search and advanced recommendations

#### Database
- [ ] Create `content_connections` table (flexible many-to-many)
  - Supports any content type linking
  - Stores connection strength (for graph algorithms)

#### Backend
- [ ] Implement universal search endpoint
  - Search across media, audio_content, video_content simultaneously
  - Unified ranking algorithm
  - Filter by content type
- [ ] Create `/api/discover/by-mood` endpoint
  - Input: Mood descriptors (dark, energetic, nostalgic)
  - Output: Movies + music + videos matching mood
- [ ] Create `/api/discover/by-era` endpoint
  - Input: Year range
  - Output: Cross-content timeline
- [ ] Create `/api/discover/by-artist` endpoint
  - Input: Artist/creator name
  - Output: All content (movies acted in, music albums, videos)
- [ ] Implement connection strength algorithm
  - Graph analysis (centrality, clustering)
  - Recommend based on connection patterns

#### Frontend
- [ ] Create universal search bar
  - Real-time suggestions as you type
  - Tabs: "All", "Movies", "Music", "Videos"
  - Smart filters (has soundtrack, from era, etc.)
- [ ] Build mood discovery page
  - Mood selectors (sliders for energy, darkness, etc.)
  - Results grid showing all content types
  - Filter and sort options
- [ ] Create timeline visualization
  - X-axis: Years (1960-2025)
  - Y-axis: Content types (movies, albums, videos)
  - Interactive: Click year to filter
- [ ] Expand 3D visualization
  - Add audio (gold spheres) and video (silver cubes)
  - Repurpose axes for cross-content dimensions
  - Connection lines between related content

#### Success Metrics
- Universal search finds relevant results across all types
- Mood discovery returns expected content
- 3D visualization renders 100+ items smoothly

---

### Phase 7: Advanced Features (Weeks 9-10)
**Goal:** Polish and unique differentiators

#### Backend
- [ ] Implement podcast RSS feed parser
  - iTunes Podcast Search integration
  - RSS feed parsing for episodes
  - Episode metadata storage
- [ ] Create audio mixing preview (basic)
  - Calculate crossfade points using audio features
  - Preview transition between two tracks
- [ ] Implement trending detection
  - View/play count velocity
  - Recent popularity surge detection
- [ ] Build export functionality
  - Export playlist to Spotify (via OAuth)
  - Export as M3U file
  - Share playlist link

#### Frontend
- [ ] Create podcast subscription interface
  - Search podcasts
  - Subscribe to RSS feed
  - Episode list with playback
- [ ] Build mixtape creator
  - Visual timeline of tracks
  - Drag to adjust crossfade duration
  - Preview transitions
- [ ] Create trending dashboard
  - "Trending Now" sections for each content type
  - "Rising" indicators
  - Popularity charts
- [ ] Add social sharing
  - Share playlist link
  - Share discovery ("Check out this mood mix")
  - Copy link functionality

#### Success Metrics
- Podcast episodes can be played
- Mixtape transitions sound smooth
- Trending algorithm identifies viral content

---

### Phase 8: Testing & Optimization (Week 11)
**Goal:** Production-ready quality

#### Testing
- [ ] Write unit tests for all new services
  - Spotify service tests (mocked API)
  - YouTube service tests
  - Recommendation algorithm tests
- [ ] Write integration tests
  - Cross-content linking
  - Search functionality
  - Playlist creation workflow
- [ ] Test API quota handling
  - YouTube quota limit simulation
  - Spotify rate limit handling
- [ ] Accessibility testing
  - Screen reader compatibility
  - Keyboard navigation
  - Color contrast (WCAG AA)
- [ ] Mobile responsiveness testing
  - Album carousel on mobile
  - Video player on mobile
  - Touch gestures

#### Optimization
- [ ] Implement Redis caching layer
  - API response caching (5-60 min TTL)
  - Search result caching
- [ ] Database query optimization
  - Add missing indexes
  - Analyze slow queries
  - Create materialized views for complex joins
- [ ] Frontend performance
  - Lazy load images (album art, thumbnails)
  - Virtualized scrolling for long lists
  - Code splitting for routes
- [ ] Load testing
  - Simulate 100 concurrent users
  - Identify bottlenecks
  - Optimize slow endpoints

#### Documentation
- [ ] Update README.md
  - New features overview
  - API documentation links
- [ ] Create API documentation
  - Endpoint reference
  - Request/response examples
- [ ] Write user guide
  - How to create playlists
  - How to discover music
  - How to link content

#### Success Metrics
- Test coverage > 80%
- All API endpoints < 500ms response time
- Zero critical accessibility issues
- Documentation complete and accurate

---

## III. Technical Requirements

### API Keys Needed
- **Spotify API** - Client ID and Secret (free)
- **YouTube Data API v3** - API Key (free, 10k quota/day)
- **Last.fm API** - API Key (free)
- **MusicBrainz** - No API key (already implemented)

### New Dependencies
```
# Backend
spotipy==2.23.0           # Spotify API client
google-api-python-client==2.108.0  # YouTube API
python-dotenv==1.0.0      # Already installed
feedparser==6.0.10        # Podcast RSS parsing

# Frontend
wavesurfer.js==6.6.0      # Audio waveform visualization
youtube-player==5.5.2     # YouTube iframe API wrapper (optional)
```

### Infrastructure
- **Database:** DuckDB (existing) - add ~15 new tables
- **Storage:** Estimated 3 GB for 10k albums + 5k videos (metadata + cached images)
- **Caching:** Redis (optional, for performance)
- **CDN:** Local file serving (album art, thumbnails)

---

## IV. Data Sources Strategy

### MusicBrainz (Primary Music Metadata)
- **Usage:** Album/track metadata, artist info, relationships
- **Cost:** Free, open-source
- **Rate Limits:** 1 request/second (respected)
- **Implementation:** Enhance existing `MusicBrainzSource` class

### Spotify (Audio Previews & Features)
- **Usage:** 30-second previews, album art, audio features (BPM, energy)
- **Cost:** Free
- **Rate Limits:** Rolling 30-second window
- **Implementation:** New `SpotifyService` class

### YouTube Data API (Primary Video Source)
- **Usage:** Video search, metadata, thumbnails, embed URLs
- **Cost:** Free (10,000 quota units/day)
- **Quota Management:**
  - Search = 100 units (limit to 100 searches/day)
  - Video details = 1 unit (can fetch 9,900 videos/day)
  - Cache results for 24 hours
- **Implementation:** New `YouTubeService` class

### TMDB (Movie Video Clips)
- **Usage:** Official trailers, clips from movies
- **Cost:** Free (already integrated)
- **Implementation:** Extend existing `TMDBService`

### Last.fm (Recommendations)
- **Usage:** Similar artists, tags, trending data
- **Cost:** Free for non-commercial
- **Implementation:** New `LastFMService` class

---

## V. Database Migration Plan

### Migration 001: Audio Foundation Tables
```sql
-- Create audio_content table
CREATE TABLE audio_content (...);

-- Create audio_tracks table
CREATE TABLE audio_tracks (...);

-- Create artists table
CREATE TABLE artists (...);

-- Create audio_genres table
CREATE TABLE audio_genres (...);

-- Create audio_content_genres join table
CREATE TABLE audio_content_genres (...);

-- Add indexes
CREATE INDEX idx_audio_content_type ON audio_content(content_type);
-- ... (see full schema in research document)
```

### Migration 002: Playlist Tables
```sql
CREATE TABLE audio_playlists (...);
CREATE TABLE audio_playlist_tracks (...);
```

### Migration 003: Cross-Reference Tables
```sql
-- Link soundtracks to audio_content
ALTER TABLE soundtracks ADD COLUMN audio_content_id UUID REFERENCES audio_content(id);

-- Create media_audio_links
CREATE TABLE media_audio_links (...);
```

### Migration 004: Video Tables
```sql
CREATE TABLE video_content (...);
CREATE TABLE media_video_links (...);
CREATE TABLE audio_video_links (...);
```

### Migration 005: Universal Connections
```sql
CREATE TABLE content_connections (...);
```

---

## VI. Risk Assessment & Mitigation

### High Risk
**Risk:** YouTube API quota exhaustion (10k units/day)
**Impact:** Video search/discovery stops working
**Mitigation:**
- Aggressive caching (24-hour TTL)
- Prioritize high-value searches (official trailers)
- Monitor quota usage with dashboard
- Implement request queueing when approaching limit

**Risk:** Spotify preview URLs expire
**Impact:** Audio playback breaks
**Mitigation:**
- Store Spotify track ID, not just URL
- Re-fetch preview URL on 404 error
- Cache preview URLs for 7 days only

### Medium Risk
**Risk:** Album art copyright issues
**Impact:** Legal concerns with displaying album covers
**Mitigation:**
- Use Spotify/MusicBrainz URLs (not hosting locally)
- Display for personal use only (non-commercial)
- Add attribution to data sources

**Risk:** MusicBrainz data quality variance
**Impact:** Incomplete/incorrect metadata
**Mitigation:**
- Combine multiple sources (MusicBrainz + Spotify)
- Allow manual corrections
- Implement data validation

### Low Risk
**Risk:** Database size growth
**Impact:** Performance degradation
**Mitigation:**
- DuckDB handles multi-GB files efficiently
- Implement data archiving for old content
- Use indexes for all queries

---

## VII. Success Criteria

### Phase 1-3 (Audio + Movie Integration)
- [ ] 500+ albums in database
- [ ] 80%+ albums have Spotify previews
- [ ] 70%+ movies have linked soundtracks
- [ ] Album browsing UI loads in < 500ms
- [ ] User can create and save playlists

### Phase 4-5 (Video + Integration)
- [ ] 300+ videos in database
- [ ] 60%+ movies have linked trailers
- [ ] 40%+ popular songs have music videos
- [ ] Video playback works in embedded player

### Phase 6-7 (Cross-Content + Advanced)
- [ ] Universal search returns relevant results across all types
- [ ] Mood-based discovery functional
- [ ] 3D visualization includes all content types
- [ ] Trending detection identifies popular content

### Phase 8 (Testing & Polish)
- [ ] 80%+ test coverage
- [ ] All API endpoints < 500ms
- [ ] Zero critical accessibility issues
- [ ] Complete documentation

---

## VIII. Open Questions for Review

### Technical Decisions
1. **Audio Playback:** Use WaveSurfer.js or custom D3.js waveform?
2. **Video Player:** Embedded iframe or custom player with API?
3. **Caching Layer:** Redis required or optional?
4. **Database:** Stay with DuckDB or consider PostgreSQL for production?

### Feature Scope
5. **Podcast Priority:** Include in Phase 1 or defer to Phase 7?
6. **Short Video Feed:** Build TikTok-style vertical feed or stick with grid?
7. **Social Features:** Include sharing/collaborative playlists or defer?
8. **Export:** Which formats to support (M3U, Spotify, YouTube, all)?

### Design Decisions
9. **UI Consistency:** Match existing movie carousel exactly or innovate?
10. **Color Scheme:** Different colors for audio (gold) vs video (silver)?
11. **3D Visualization:** Expand existing or create separate view?

### Integration Priority
12. **Which integration is most valuable?**
    - A) Movie → Soundtrack (enhances existing feature)
    - B) Music → Music Video (new engagement pattern)
    - C) Cross-content mood discovery (unique differentiator)

---

## IX. Next Steps

### Before Implementation
1. **Review Meeting** - Discuss this plan with stakeholders
2. **Address Open Questions** - Make decisions on technical/design choices
3. **API Key Acquisition** - Register for Spotify, YouTube, Last.fm APIs
4. **Update TASK.md** - Add implementation tasks with priorities
5. **Create Feature Branches** - Set up git workflow

### First Implementation Task
Once approved, start with:
- **Task:** Create `audio_content` database table
- **File:** `scripts/create_audio_tables.py`
- **Duration:** 1 hour
- **Deliverable:** Executable migration script + unit test

---

## X. Timeline Summary

| Phase | Duration | Deliverables | Status |
|-------|----------|--------------|--------|
| Phase 1: Audio Foundation | 2 weeks | Album browsing, preview playback | Not Started |
| Phase 2: Discovery & Playlists | 1 week | Playlists, recommendations | Not Started |
| Phase 3: Movie-Audio Integration | 1 week | Soundtrack linking | Not Started |
| Phase 4: Video Foundation | 2 weeks | Video browsing, playback | Not Started |
| Phase 5: Video Integration | 1 week | Trailers, music videos | Not Started |
| Phase 6: Cross-Content Discovery | 1 week | Universal search, 3D viz | Not Started |
| Phase 7: Advanced Features | 2 weeks | Podcasts, trending, export | Not Started |
| Phase 8: Testing & Polish | 1 week | Tests, optimization, docs | Not Started |
| **Total** | **11 weeks** | **Complete audio/video platform** | **Draft Plan** |

---

## XI. References

- **Research Document:** `docs/AUDIO_VIDEO_RESEARCH_REPORT.md` (detailed findings)
- **Database Schema:** See Research Document Appendix
- **API Documentation:**
  - MusicBrainz: https://musicbrainz.org/doc/Development/XML_Web_Service/Version_2
  - Spotify: https://developer.spotify.com/documentation/web-api
  - YouTube: https://developers.google.com/youtube/v3
  - Last.fm: https://www.last.fm/api

---

**Document Status:** Draft - Awaiting Review
**Next Review:** [To be scheduled]
**Approval Required From:** Project Owner

---

*This implementation plan is based on comprehensive research of audio/video content types, data sources, integration patterns, and technical architecture. All phases are designed to build incrementally on existing XILFTEN infrastructure while maintaining code quality, performance, and user experience standards.*
