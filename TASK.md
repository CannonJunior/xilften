# XILFTEN - Media Multi-Use Scheduling Application
## Task Tracking Document

**Project Started:** 2025-11-03
**Last Updated:** 2025-11-03
**Architecture:** CAG (Context-Augmented Generation) - Not RAG
**Port:** 7575 (CRITICAL - Never change without permission)

---

## 🎯 PROJECT OVERVIEW

**Purpose:** A modern web application for scheduling consumption of movies, TV shows, and streaming media, with future expansion to music, games, food/recipes, events, and projects.

**Core Technology Stack:**
- Frontend: HTML5, CSS3, Vanilla JavaScript, D3.js (Observable)
- Backend: Python/FastAPI (port 7575)
- Database: ChromaDB + DuckDB (local vector database)
- AI/ML: Ollama (local LLM on port 11434)
- APIs: TMDB (The Movie Database) for media metadata
- Future: Flutter web compilation for cross-platform deployment

---

## 📊 GENRE TAXONOMY & SUB-GENRES

### 1. **Film Noir**
Primary Genre Categories:
- **Neo-Noir** (1970s-present): Modern subversion of classic noir tropes
- **Tech-Noir**: Sci-fi elements (Blade Runner, The Terminator)
- **Neon-Noir**: Vibrant neon palettes, hyper-stylized aesthetics (Taxi Driver, Good Time)
- **Superhero-Noir**: Contemporary noir themes (Watchmen, Jessica Jones)
- **Noir Western**: Hybrid genre blending noir with western settings
- **Classic Noir**: 1940s-1950s American film noir

**Key Characteristics:**
- Morally ambiguous protagonists
- High-contrast visual style
- Urban settings
- Paranoia and psychological complexity
- Non-linear narratives

---

### 2. **Science Fiction**

Primary Sub-Genres:
- **Cyberpunk**: Dystopian near-futures, AI, cyberware, societal collapse (low-life + high-tech)
- **Hard Sci-Fi**: Technology-focused, scientific realism, concept-heavy
- **Soft Sci-Fi**: Character-focused, emotional/sociological impacts of technology
- **Space Opera**: Pure adventure, common space travel, galaxy-spanning narratives
- **Military Sci-Fi**: Futuristic warfare, advanced battle technology
- **Steampunk**: Victorian-era technology aesthetics
- **Post-Apocalyptic**: Survival after civilization collapse
- **Dystopian**: Oppressive societal control, totalitarian futures
- **Time Travel**: Temporal paradoxes and alternate timelines

**Key Themes:**
- Artificial intelligence
- Space exploration
- Technological singularity
- Human augmentation
- First contact scenarios

---

### 3. **Documentary**

Documentary Modes (Bill Nichols Classification):
- **Observational**: Fly-on-the-wall, cinema verité, unobtrusive camera (Hoop Dreams)
- **Expository**: Educational, "voice of God" narration, heavily researched (Ken Burns style)
- **Poetic**: Abstract, experimental, mood-focused over factual truth
- **Participatory**: Filmmaker actively engages subjects through interviews
- **Reflexive**: Self-aware, meta-commentary on documentary-making process
- **Performative**: Filmmaker's personal experience, subjective truth

**Content Categories:**
- Nature/Wildlife
- True Crime
- Historical
- Political/Social Justice
- Biographical
- Scientific
- Music/Arts

---

### 4. **Comedy**

Primary Sub-Genres:
- **Slapstick**: Exaggerated physical stunts and gags (Chaplin, Keaton, Three Stooges)
- **Romantic Comedy (Rom-Com)**: Love + humor, unrealistic situations leading to happy endings
- **Dark Comedy**: Humor from taboo subjects (death, war, illness)
- **Screwball Comedy**: 1930s-1940s depression-era style, fast-paced witty dialogue
- **Parody/Spoof**: Satirizes other film genres or classic films
- **Action Comedy**: Blockbuster style, fast-paced action with comedic elements
- **Mockumentary**: Faux-documentary format
- **Satire**: Social/political commentary through humor

**Tone Categories:**
- Lighthearted
- Witty/Intellectual
- Absurdist
- Crude/Raunchy
- Wholesome/Family

---

### 5. **Anime**

**Demographic Categories:**
- **Shonen**: Teen boys (12-18), male protagonist, action/adventure/drama (Naruto, Dragon Ball)
- **Seinen**: Young men (18-40), mature themes, psychological/gore/violence
- **Shoujo**: Teen girls, romance-focused, female protagonist
- **Josei**: Adult women, realistic romance and drama
- **Kodomomuke**: Children, simple stories and themes

**Theme/Sub-Genre Categories:**
- **Isekai**: Reincarnation/transportation to another world (Re: Zero, That Time I Got Reincarnated as a Slime)
- **Mecha**: Giant robots piloted by humans (Gundam, Neon Genesis Evangelion)
- **Slice of Life**: Everyday activities and relationships
- **Fantasy**: Magic, mythical creatures, alternate worlds
- **Sports**: Competition and athletic achievement
- **Romance**: Love stories and relationships
- **Psychological**: Mental/emotional exploration
- **Horror**: Supernatural or psychological terror

---

### 6. **Action**

Primary Sub-Genres:
- **Martial Arts**: Hand-to-hand combat, melee weapons
  - Kung Fu
  - Wuxia (Chinese martial arts fantasy)
  - Karate Films
  - Martial Arts Comedy (Jackie Chan style)
- **Superhero**: Characters with supernatural abilities (MCU, DC)
- **Spy/Espionage**: Secret missions, special gadgets (James Bond, Mission Impossible)
- **Action Thriller**: Suspense combined with action sequences
- **Disaster Films**: Natural catastrophes, survival scenarios
- **Action Comedy**: Humor integrated with action (Deadpool, Rush Hour)
- **Military Action**: War scenarios, tactical combat
- **Western Action**: Frontier/Old West settings

**Style Categories:**
- Choreographed fight sequences
- Vehicular chase scenes
- Gunfights/shootouts
- Explosive set pieces

---

### 7. **International: Iranian Cinema**

**Movement Categories:**
- **Iranian New Wave (Cinema-ye Motafavet)**: 1960s-1970s grassroots movement
  - First Wave (1964-1968): Experimental beginnings
  - Second Wave (1968-1979): Most internationally recognized (The Cow, Qeysar)
  - Third Wave: Post-revolution continuation
- **Popular Art Cinema**: Broader audience appeal beyond educated elite
- **Neorealist Cinema**: Italian Neorealism influence, everyday life focus
- **Minimalist Art Cinema**: Poetry in everyday life, fiction/reality blur

**Key Characteristics:**
- Blurred boundaries between fiction and documentary
- Focus on ordinary people
- Poetic visual language
- Social commentary within constraints
- Humanist themes

**Notable Directors:**
- Abbas Kiarostami
- Asghar Farhadi
- Jafar Panahi
- Majid Majidi
- Dariush Mehrjui

---

### 8. **Multi-Genre**

**Hybrid Genre Combinations:**
- Horror + Noir (Psycho)
- Sci-Fi + Noir (Blade Runner) [Tech-Noir]
- Comedy + Noir (Fargo) [Dark Comedy]
- Western + Noir (Mystery Road)
- Action + Comedy (Rush Hour, Deadpool)
- Horror + Comedy (Shaun of the Dead)
- Sci-Fi + Horror (Alien, The Thing)
- Romance + Sci-Fi (Eternal Sunshine of the Spotless Mind)
- Documentary + Animation (Waltz with Bashir)

**Classification Strategy:**
- Tag with all applicable primary genres
- Calculate weighted score across all genre preferences
- Allow filtering by "must contain" vs "can contain" genres

---

## 🎨 DESIRED FEATURES

### ✅ PHASE 1: FOUNDATION (Week 1)
**Status:** Not Started
**Target Completion:** TBD

#### Backend Infrastructure
- [ ] Initialize project structure with UV package manager
- [ ] Set up FastAPI server on port 7575
- [ ] Configure ChromaDB + DuckDB for local vector storage
- [ ] Create Pydantic models for media entities
- [ ] Set up environment variables with python-dotenv
- [ ] Configure CORS for frontend-backend communication

#### TMDB API Integration
- [ ] Register for TMDB API key
- [ ] Create TMDB client service module
- [ ] Implement media metadata fetching endpoints
- [ ] Implement poster/image retrieval
- [ ] Add rate limiting and caching layer
- [ ] Create fallback error handling

#### Database Schema
- [ ] Design media table structure (movies, TV shows, anime)
- [ ] Design user reviews table
- [ ] Design custom criteria fields table
- [ ] Design calendar events table (reviews, releases, watch dates)
- [ ] Create database migration scripts
- [ ] Seed initial genre taxonomy data

#### Basic Frontend
- [ ] Create HTML5 semantic structure
- [ ] Set up CSS architecture (variables, reset, utilities)
- [ ] Configure D3.js Observable imports
- [ ] Create basic responsive layout
- [ ] Implement API client wrapper (fetch)

---

### ✅ PHASE 2: CORE FEATURES (Week 2)
**Status:** Not Started
**Target Completion:** TBD

#### Feature 1: D3.js Carousel with Mousewheel Scrolling
- [ ] Research CSS Scroll Snap vs JavaScript implementation
- [ ] Create carousel container with D3.js data binding
- [ ] Implement horizontal mousewheel event handlers
- [ ] Add touch/swipe support for mobile
- [ ] Create thumbnail navigation strip
- [ ] Implement lazy loading for images
- [ ] Add keyboard navigation (arrow keys)
- [ ] Create smooth scroll animations
- [ ] Add active state indicators
- [ ] Performance optimization for large datasets

**Technical Requirements:**
- Bidirectional scrolling (left/right with mousewheel)
- Smooth transitions between items
- Support for 100+ media items
- Responsive design (mobile, tablet, desktop)

#### Feature 2: Minimalistic D3.js Calendar
- [ ] Implement d3-time module for calendar grid
- [ ] Create month/year navigation controls
- [ ] Design color coding system for event types:
  - Reviews (blue)
  - New releases (green)
  - Scheduled watch dates (orange)
  - Custom events (purple)
- [ ] Add SVG icon overlay system for categories
- [ ] Implement click-to-expand day detail view
- [ ] Create smooth month transition animations
- [ ] Add event creation modal
- [ ] Implement calendar heatmap view option
- [ ] Create mini-calendar date picker component

**Technical Requirements:**
- Responsive month view
- Support for multiple events per day
- Icon + color categorization
- Quick add/edit/delete functionality

---

### ✅ PHASE 3: RECOMMENDATION ENGINE (Week 3)
**Status:** Not Started
**Target Completion:** TBD

#### Feature 3: Multi-Criteria Recommendation Engine
- [ ] Design scoring algorithm architecture
- [ ] Implement criteria normalization (0-1 scale)
- [ ] Create weighted sum calculation system
- [ ] Build criteria configuration storage
- [ ] Implement recommendation ranking endpoint
- [ ] Add collaborative filtering layer (optional)
- [ ] Create recommendation caching system
- [ ] Add A/B testing framework for algorithm tuning

**Default Criteria Fields:**
- Maturity Rating (with recommended ages)
- Review Rating (TMDB, user reviews)
- Length/Runtime
- Genre (multi-select)
- Release Year
- Screenwriter Score (average rating of credited writers)
- Director Score
- Cast Score (average rating of main actors)
- Popularity (trending factor)
- Personal watch history similarity

#### Feature 4: Custom Criteria Interface
- [ ] Create dynamic form builder UI
- [ ] Fetch available TMDB schema fields
- [ ] Implement drag-and-drop weight sliders (0-100%)
- [ ] Add criteria preset save/load functionality
- [ ] Create visual preview of matching media count
- [ ] Implement criteria validation logic
- [ ] Add preset sharing/export (JSON)
- [ ] Create criteria comparison view
- [ ] Add "smart suggestions" for common combinations

**User Workflow:**
1. Select base criteria from TMDB fields
2. Adjust weight importance (slider 0-100%)
3. Preview number of matching results
4. Save as named preset
5. Apply to recommendation engine

---

### ✅ PHASE 4: API & DATA MANAGEMENT (Week 3-4)
**Status:** Not Started
**Target Completion:** TBD

#### Feature 5: Media API Endpoints
- [ ] **POST /api/media/create** - Create new custom media entry
- [ ] **GET /api/media/{id}** - Fetch single media details
- [ ] **PUT /api/media/{id}** - Update media entry
- [ ] **DELETE /api/media/{id}** - Remove media entry
- [ ] **GET /api/media/search** - Search media by criteria
- [ ] **POST /api/media/fetch-tmdb** - Fetch and merge TMDB data
- [ ] **POST /api/media/review** - Add user review to media
- [ ] **GET /api/media/reviews/{id}** - Get all reviews for media
- [ ] **GET /api/media/recommendations** - Get personalized recommendations

**Data Flow:**
1. User creates custom media entry (manual input)
2. System attempts to match with TMDB
3. If found, merge metadata automatically
4. If not found, store custom entry only
5. User can add personal review/rating

---

### ✅ PHASE 5: AI/AGENTIC FEATURES (Week 4-5)
**Status:** Not Started
**Target Completion:** TBD

#### Feature 6: Ollama Local LLM Integration
- [ ] Install Ollama on localhost:11434
- [ ] Configure qwen2.5:3b model
- [ ] Configure llama3.1 model (fallback)
- [ ] Create Ollama client service module
- [ ] Implement streaming response handling
- [ ] Create prompt template library
- [ ] Add conversation history management
- [ ] Implement RAG/CAG pipeline for media context
- [ ] Create embedding generation for semantic search
- [ ] Add error handling and fallback logic

#### Feature 7: Agentic AI Mashup & Recommendations
- [ ] **Content Mashup Generator**
  - [ ] Parse user natural language queries
  - [ ] Extract genre/tone/style criteria from query
  - [ ] Query ChromaDB for similar embeddings
  - [ ] Generate mashup concept with Ollama
  - [ ] Return synthesized recommendation with reasoning
  - [ ] Example: "fantasy action like World of Warcraft + serious drama like Chernobyl"

- [ ] **High-Concept Summary Writer**
  - [ ] Accept multiple reference media inputs
  - [ ] Extract key attributes (dialogue style, action, plot structure)
  - [ ] Generate original high-concept summary
  - [ ] Create plot point outline
  - [ ] Return formatted creative document
  - [ ] Example: "witty dialogue like His Girl Friday + action like Game of Thrones + plot like Casablanca"

- [ ] **AI Chat Interface**
  - [ ] Create chat UI component
  - [ ] Implement message history display
  - [ ] Add streaming response animations
  - [ ] Create preset query buttons
  - [ ] Add feedback mechanism (thumbs up/down)

**CAG Architecture (Context-Augmented Generation):**
```
User Query → Parse Intent → Extract Criteria → Query ChromaDB
→ Retrieve Context → Augment Prompt → Ollama Generation → Response
```

**Key Differences from RAG:**
- Focus on creative synthesis vs factual retrieval
- Emphasis on mashup/combination generation
- Contextual augmentation for creative outputs

---

## 🗓️ TASK TIMELINE

### Week 1: Foundation
- Backend setup (FastAPI, ChromaDB, TMDB)
- Database schema design
- Basic frontend structure
- API client configuration

### Week 2: Visual Components
- D3.js carousel implementation
- D3.js calendar visualization
- Responsive UI polish
- Media detail views

### Week 3: Intelligence Layer
- Multi-criteria recommendation engine
- Custom criteria builder UI
- Scoring algorithm implementation
- Preset management system

### Week 4: AI Integration
- Ollama setup and configuration
- CAG pipeline implementation
- Mashup generator
- High-concept writer

### Week 5: Testing & Polish
- Unit tests (pytest)
- UI/UX refinement
- Performance optimization
- Documentation

### Future: Flutter Migration
- Flutter web wrapper
- Cross-platform compilation
- iOS/Android builds via Xcode/Android Studio

---

## 🔧 TECHNICAL DEBT & IMPROVEMENTS

### Performance Optimizations
- [ ] Implement request caching layer (Redis optional)
- [ ] Optimize D3.js rendering for large datasets
- [ ] Add pagination for recommendation results
- [ ] Implement virtual scrolling for carousel
- [ ] Compress and lazy-load images

### Security Enhancements
- [ ] Add API rate limiting
- [ ] Implement CSRF protection
- [ ] Sanitize user inputs
- [ ] Add authentication system (future phase)
- [ ] Encrypt sensitive data in database

### User Experience
- [ ] Add loading states and skeleton screens
- [ ] Implement error boundary components
- [ ] Create onboarding tutorial
- [ ] Add keyboard shortcuts guide
- [ ] Implement dark mode toggle

---

## 📚 RESEARCH REFERENCES

### Carousel Best Practices
- Source: Smashing Magazine, Chrome Developers Blog (2025)
- Key Insight: CSS Scroll Snap API for native browser support
- Avoid: Auto-rotation, especially on mobile devices

### D3.js Calendar Visualizations
- Source: Observable D3 Gallery, RisingStack Engineering
- Key Insight: d3-time module for calendar layouts
- Pattern: Calendar heatmap for time-series data

### Recommendation Systems
- Source: Eugene Yan, Towards Data Science
- Architecture: Offline batch processing + online ranking
- Pattern: Multi-stage filtering (retrieval → ranking → re-ranking)

### Ollama Integration
- Source: Ollama Official Blog, Cohorte Projects
- Best Practice: REST API on port 11434
- Use Case: Privacy-first local LLM for creative tasks

### Genre Research
- Film Noir: Film School Rejects, MasterClass
- Sci-Fi: Pan Macmillan, SciFi Ideas
- Documentary: MasterClass, Bill Nichols taxonomy
- Comedy: WeVideo, Premium Beat
- Anime: Beebom, Dopomyn
- Action: NYFA, Screen Rant
- Iranian Cinema: Association for Iranian Studies, Wikipedia

---

## 🐛 DISCOVERED ISSUES / BLOCKERS

**None yet - Project just started**

---

## ✅ COMPLETED TASKS

- [x] Initial project research and architecture design (2025-11-03)
- [x] Genre taxonomy research and sub-genre identification (2025-11-03)
- [x] Web research on D3.js best practices (2025-11-03)
- [x] Web research on recommendation engine patterns (2025-11-03)
- [x] Web research on Ollama integration (2025-11-03)
- [x] TASK.md creation (2025-11-03)

---

## 📝 NOTES & CONTEXT

### CAG vs RAG
- **RAG (Retrieval-Augmented Generation)**: Fact-based retrieval from documents
- **CAG (Context-Augmented Generation)**: Creative synthesis with contextual prompts
- This project uses CAG for creative media recommendations and mashup generation

### Port Configuration
- **Web App Port:** 7575 (CRITICAL - Never change without explicit permission)
- **Ollama Port:** 11434 (Standard local LLM endpoint)

### Future Expansion Roadmap
1. Music library and playlist management
2. Video game tracking and recommendations
3. Food/recipe scheduling and meal planning
4. Event calendar integration
5. Project management features
6. Cross-platform mobile apps (Flutter → iOS/Android)

### Design Philosophy
- **Minimalism:** Clean, uncluttered UI
- **Performance:** Fast, responsive interactions
- **Privacy:** All data stored locally, zero external tracking
- **Flexibility:** Extensible to multiple content types
- **Intelligence:** AI-augmented discovery and creativity

---

**End of TASK.md**
