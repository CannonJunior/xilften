# Soundtrack Sources Documentation

## Overview

This document describes the soundtrack data sources used in the application, their priorities, and the research conducted to find the best available options.

## Current Implementation

### Source Priority System

Sources are prioritized by integer values where **lower number = higher priority**:
- Priority 5-9: Primary sources (tried first)
- Priority 10-15: Secondary sources
- Priority 20+: Fallback sources (tried last)

### Active Sources

#### 1. MusicBrainz (Priority: 10)
- **Type**: API-based
- **Status**: Primary source
- **Cost**: Free, open-source
- **License**: CC0 (public domain for core data)
- **Reliability**: High
- **Coverage**: Excellent for major releases
- **API Limits**: No hard limits for non-commercial use
- **Implementation**: `backend/services/soundtrack_sources/musicbrainz_source.py`

**Pros**:
- Free and open-source
- Comprehensive music metadata
- Stable API
- No bot detection issues
- Community-maintained

**Cons**:
- May not have soundtracks for very new or niche releases
- Requires accurate movie title matching

#### 2. IMDB (Priority: 20)
- **Type**: Web scraping
- **Status**: Fallback source
- **Cost**: Free
- **Reliability**: Low (bot detection)
- **Coverage**: High when accessible
- **Implementation**: `backend/services/soundtrack_sources/imdb_source.py`

**Pros**:
- Comprehensive coverage
- No API key required
- Large database

**Cons**:
- **Bot detection returns HTTP 202** instead of 200
- Unreliable for automated access
- May break with HTML structure changes
- Scraping-based (fragile)

**Note**: IMDB was initially set as primary source (priority 5) but was demoted to priority 20 (fallback) due to bot detection issues discovered in 2025-11-13.

## Research Findings

### Investigated Sources

#### Tunefind API
- **Evaluation**: Promising but not free
- **Type**: REST API
- **Cost**: Tiered pricing (Starter through Enterprise)
- **Coverage**: Excellent for TV and movie soundtracks
- **Decision**: Not implemented due to cost requirements

#### Wikipedia API
- **Evaluation**: Technically possible but not ideal
- **Type**: API + HTML scraping
- **Cost**: Free
- **Issues**:
  - Requires HTML scraping (similar to IMDB)
  - Inconsistent data formatting
  - Not all movies have soundtrack information
  - Would face similar fragility issues as IMDB scraping
- **Decision**: Not implemented

#### OMDb API
- **Evaluation**: Not suitable
- **Coverage**: General movie metadata, not soundtrack-specific
- **Decision**: Not applicable for soundtrack data

## Current Status

### Coverage Statistics
- **Total Movies**: 20
- **With Soundtracks**: 14 (70%)
- **Without Soundtracks**: 6 (30%)

### Movies Without Soundtracks
1. Deadpool & Wolverine (2024)
2. Demon Slayer: Kimetsu no Yaiba Infinity Castle (2025)
3. Mufasa: The Lion King (2024)
4. Ne Zha 2 (2025)
5. Star Wars (1977)
6. The Fantastic 4: First Steps (2025)

**Note**: These movies may not have soundtrack data available in any free databases, not due to technical limitations.

## Recommendations

### For Adding New Sources

When considering new soundtrack sources, evaluate:

1. **API vs Scraping**: Prefer API-based sources over scraping
2. **Cost**: Free/open-source preferred for this project
3. **Reliability**: Check for rate limits, bot detection
4. **Coverage**: Test with sample movies
5. **Maintenance**: Consider long-term stability

### Priority Guidelines

- **5-9**: Reserve for paid/premium APIs with guaranteed uptime
- **10-15**: Free APIs with good reliability (current: MusicBrainz at 10)
- **20+**: Scraping-based fallback sources (current: IMDB at 20)

## Configuration

### Changing Source Priority

Edit the `get_priority()` method in each source file:

```python
def get_priority(self) -> int:
    """
    Get source priority.

    Returns:
        int: Priority value (lower = higher priority)
    """
    return 10  # Adjust this value
```

### Adding a New Source

1. Create new source file in `backend/services/soundtrack_sources/`
2. Extend `SoundtrackSource` base class
3. Implement required methods:
   - `search_soundtrack()`
   - `is_available()`
   - `get_priority()`
4. Register in `backend/services/soundtrack_service.py`

## Investigation History

### 2025-11-13: IMDB Bot Detection Issue

**Problem**: IMDB started returning HTTP 202 (Accepted) for automated requests instead of HTTP 200, indicating bot detection.

**Investigation**:
- Created debug script: `scripts/debug_imdb_soundtrack.py`
- Confirmed HTTP 202 responses for all test cases
- Researched alternative sources

**Resolution**:
- Demoted IMDB from priority 5 to priority 20
- Confirmed MusicBrainz as reliable primary source
- Documented findings in this file

**Files Modified**:
- `backend/services/soundtrack_sources/imdb_source.py:222` (priority change)

## Future Considerations

### Potential Improvements

1. **Spotify API**: Could provide track previews and streaming links
   - Requires API key
   - Good coverage for popular soundtracks
   - Commercial use restrictions

2. **Last.fm API**: Music metadata and listening data
   - Free tier available
   - Good for album metadata
   - May require API key

3. **Discogs API**: Comprehensive music database
   - Free tier available
   - Excellent for physical releases
   - May have coverage gaps for digital-only releases

4. **Custom Aggregation**: Combine multiple sources
   - Use MusicBrainz for primary data
   - Fall back to other sources for missing entries
   - Merge and deduplicate results

### Monitoring

Regularly check:
- Source availability and response times
- Changes in API terms or rate limits
- New soundtrack data sources
- Coverage gaps in current sources

## References

- MusicBrainz: https://musicbrainz.org/doc/MusicBrainz_API
- Tunefind: https://www.tunefind.com/api
- IMDB: https://www.imdb.com (note: no official API)

---

Last Updated: 2025-11-13
