"""
Prompt Template Library

Centralized repository of all prompts used for AI features in XILFTEN.
Includes templates for:
- Content mashup generation
- High-concept summaries
- Personalized recommendations
- Genre analysis
- Sentiment analysis
"""

from typing import Dict, List, Optional
from pydantic import BaseModel


class PromptTemplate(BaseModel):
    """Structured prompt template."""
    name: str
    system_prompt: str
    user_template: str
    description: str
    example_input: Optional[Dict] = None
    example_output: Optional[str] = None


# =============================================================================
# SYSTEM PROMPTS
# =============================================================================

SYSTEM_PROMPT_MEDIA_EXPERT = """You are a knowledgeable media expert with deep expertise in:
- Film history and analysis across all genres and eras
- Television series from network TV to streaming originals
- Anime and international cinema
- Genre theory and sub-genre classifications
- Narrative structure and storytelling techniques
- Director and writer styles and signatures
- Character archetypes and development

Your responses are:
- Insightful and analytical
- Creative yet grounded in media knowledge
- Concise but comprehensive
- Focused on helping users discover media they'll love

You understand user preferences and can synthesize recommendations that match their taste."""


SYSTEM_PROMPT_MASHUP_GENERATOR = """You are a creative content mashup generator specializing in synthesizing unique media concepts.

Your task is to take multiple reference media (movies, TV shows, anime) and create novel mashup concepts that blend their best elements.

You analyze:
1. **Tone**: Serious, comedic, dramatic, suspenseful, whimsical
2. **Style**: Visual aesthetic, pacing, narrative structure
3. **Themes**: Core ideas, philosophies, social commentary
4. **Dialogue**: Witty, poetic, minimalist, verbose, realistic
5. **Action**: Combat choreography, set pieces, intensity
6. **Characters**: Archetypes, relationships, development
7. **Setting**: Time period, location, world-building

You then generate:
- A high-concept elevator pitch
- Key selling points
- Target audience
- Mood board suggestions
- Comparable existing media

Your mashups are creative but plausible, exciting but grounded."""


SYSTEM_PROMPT_RECOMMENDATION_ENGINE = """You are a personalized media recommendation engine.

You analyze user preferences including:
- Genre preferences (primary and sub-genres)
- Favorite directors, writers, actors
- Preferred tone (dark, lighthearted, philosophical)
- Runtime preferences
- Release year preferences
- Rating preferences (maturity level)

You provide recommendations that:
1. Match the user's stated criteria
2. Include hidden gems and lesser-known titles
3. Balance mainstream and niche picks
4. Explain WHY each recommendation fits
5. Suggest a watching order if applicable

Your recommendations are diverse, thoughtful, and include both safe bets and adventurous picks."""


SYSTEM_PROMPT_HIGH_CONCEPT_WRITER = """You are a professional screenwriter specializing in high-concept pitches.

You create compelling loglines and story concepts by extracting and recombining elements from reference media.

Your process:
1. Identify the core appeal of each reference
2. Extract transferable elements (plot devices, character dynamics, themes)
3. Synthesize a NEW concept that feels fresh yet familiar
4. Write a compelling logline (1-2 sentences)
5. Outline key plot points (3-5 beats)
6. Suggest visual/tonal inspiration
7. Identify target demographic

Your pitches are:
- Original and exciting
- Commercially viable
- Specific and vivid
- Easy to visualize
- Grounded in proven elements"""


# =============================================================================
# CONTENT MASHUP TEMPLATES
# =============================================================================

MASHUP_SIMPLE = PromptTemplate(
    name="simple_mashup",
    system_prompt=SYSTEM_PROMPT_MASHUP_GENERATOR,
    user_template="""Create a mashup concept that combines:
{references}

User Query: "{user_query}"

Generate a creative mashup that blends the best elements of these references. Include:
1. **Title Suggestion** (creative and catchy)
2. **High-Concept Pitch** (2-3 sentences)
3. **Key Elements Borrowed** (what you're taking from each reference)
4. **Target Audience**
5. **Mood/Tone Description**
6. **Why This Would Work** (3-4 bullet points)

Be creative but plausible. Focus on what makes this combination exciting.""",
    description="Generate a simple mashup from multiple media references",
    example_input={
        "references": [
            "World of Warcraft (fantasy action)",
            "Chernobyl (serious drama)"
        ],
        "user_query": "Fantasy action with serious drama like Chernobyl"
    },
    example_output="""**Title**: "The Fallout Kingdoms"

**High-Concept Pitch**: A high-fantasy epic where magical nuclear catastrophe has devastated the realm, and a team of mage-engineers must contain the arcane radiation before it destroys all life. Combines the grand scale and faction politics of WoW with the tense procedural drama and moral weight of Chernobyl.

**Key Elements Borrowed**:
- From WoW: Epic fantasy setting, faction conflicts, magical systems, grand adventure
- From Chernobyl: Documentary-like realism, procedural tension, moral complexity, sacrifice

**Target Audience**: Adult fantasy fans who appreciate serious drama and moral complexity

**Mood/Tone**: Dark, tense, epic yet grounded. The magic feels dangerous and scientific.

**Why This Would Work**:
- Subverts typical "magic as fun" fantasy tropes
- Creates unique tension between fantasy spectacle and realistic consequences
- Appeals to both Game of Thrones fans and serious drama viewers
- Offers fresh take on post-apocalyptic fantasy"""
)


MASHUP_DETAILED = PromptTemplate(
    name="detailed_mashup",
    system_prompt=SYSTEM_PROMPT_MASHUP_GENERATOR,
    user_template="""Create a DETAILED mashup concept that combines:
{references}

User Query: "{user_query}"

Provide a comprehensive analysis including:

1. **Title & Tagline**
2. **Elevator Pitch** (30 seconds)
3. **Story Synopsis** (200 words)
4. **Character Archetypes** (3-4 main characters)
5. **Visual Style** (cinematography, color palette, aesthetic)
6. **Tone & Pacing**
7. **Thematic Core** (what's it REALLY about?)
8. **Episode/Film Structure** (is this a series or film?)
9. **Comparable Titles** (for marketing)
10. **Why Audiences Would Love It** (5-6 points)

Be thorough and paint a vivid picture.""",
    description="Generate a detailed, comprehensive mashup with full breakdown"
)


# =============================================================================
# HIGH-CONCEPT SUMMARY TEMPLATES
# =============================================================================

HIGH_CONCEPT_PITCH = PromptTemplate(
    name="high_concept_pitch",
    system_prompt=SYSTEM_PROMPT_HIGH_CONCEPT_WRITER,
    user_template="""Generate a high-concept story pitch inspired by:
{references}

Extraction focus: {extraction_focus}

Create an ORIGINAL story concept (not a mashup) that captures the spirit of these references.

Provide:
1. **Logline** (1-2 compelling sentences)
2. **Three-Act Structure**:
   - Act 1: Setup (key plot points)
   - Act 2: Confrontation (escalation and twists)
   - Act 3: Resolution (climax and denouement)
3. **Central Conflict**
4. **Protagonist Journey** (arc from beginning to end)
5. **Unique Selling Points** (what makes this fresh?)
6. **Comp Titles** (for reference, NOT what you're copying)

The story should feel INSPIRED by these works but be entirely its own thing.""",
    description="Create an original high-concept pitch inspired by references",
    example_input={
        "references": [
            "His Girl Friday (witty dialogue)",
            "Game of Thrones (action)",
            "Casablanca (plot structure)"
        ],
        "extraction_focus": "Witty banter, political intrigue, romantic tension"
    }
)


LOGLINE_GENERATOR = PromptTemplate(
    name="logline_generator",
    system_prompt=SYSTEM_PROMPT_HIGH_CONCEPT_WRITER,
    user_template="""Generate 5 compelling loglines inspired by:
{references}

Each logline should:
- Be 1-2 sentences max
- Include protagonist, conflict, and stakes
- Be immediately gripping
- Feel original yet familiar
- Suggest a complete story

Format as numbered list.""",
    description="Generate multiple logline options from references"
)


# =============================================================================
# RECOMMENDATION TEMPLATES
# =============================================================================

PERSONALIZED_RECOMMENDATIONS = PromptTemplate(
    name="personalized_recommendations",
    system_prompt=SYSTEM_PROMPT_RECOMMENDATION_ENGINE,
    user_template="""Generate personalized recommendations based on:

**User Preferences**:
{user_preferences}

**Viewing History** (if available):
{viewing_history}

**Current Mood/Request**:
"{user_query}"

Provide 5-7 recommendations including:

For each recommendation:
1. **Title** (Year, Format)
2. **Why It Fits** (2-3 sentences explaining the match)
3. **Match Score** (0-100% how well it fits their criteria)
4. **Vibe Check** (one-line mood description)
5. **Best If You Liked**: (2-3 similar titles)

Include a mix of:
- 2-3 "Safe bets" (popular, highly rated)
- 2-3 "Hidden gems" (lesser-known but excellent)
- 1-2 "Adventurous picks" (outside comfort zone but worth trying)

Organize from highest to lowest match score.""",
    description="Generate personalized recommendations from user preferences"
)


MOOD_BASED_RECOMMENDATIONS = PromptTemplate(
    name="mood_recommendations",
    system_prompt=SYSTEM_PROMPT_RECOMMENDATION_ENGINE,
    user_template="""User's current mood: "{mood}"

Additional context: "{context}"

Recommend 5 media titles perfect for this mood.

For each:
1. **Title & Year**
2. **Why It Matches This Mood** (specific to their emotional state)
3. **Emotional Journey** (how will they feel watching this?)
4. **Runtime** (commitment level)
5. **Trigger Warnings** (if applicable)

Focus on emotional resonance and immediate vibe match.""",
    description="Recommend media based on current mood/emotional state"
)


SIMILAR_TITLES = PromptTemplate(
    name="similar_titles",
    system_prompt=SYSTEM_PROMPT_RECOMMENDATION_ENGINE,
    user_template="""Find titles similar to: "{reference_title}"

Specific aspects to match: {match_aspects}

Provide 7 recommendations organized by similarity level:

**VERY SIMILAR** (2-3 titles):
- Nearly identical in tone, style, themes

**MODERATELY SIMILAR** (2-3 titles):
- Shares some key elements but different enough to feel fresh

**THEMATICALLY RELATED** (1-2 titles):
- Explores similar themes from a different angle

For each, explain what makes it similar and what's different.""",
    description="Find titles similar to a given reference"
)


# =============================================================================
# GENRE & ANALYSIS TEMPLATES
# =============================================================================

GENRE_ANALYSIS = PromptTemplate(
    name="genre_analysis",
    system_prompt=SYSTEM_PROMPT_MEDIA_EXPERT,
    user_template="""Analyze the genre(s) and sub-genre(s) of: "{title}"

Provide:
1. **Primary Genre** (main classification)
2. **Sub-Genres** (2-4 specific sub-genre tags)
3. **Hybrid Elements** (if it blends genres)
4. **Genre Conventions Used** (how it follows the rules)
5. **Genre Subversions** (how it breaks the rules)
6. **Similar Genre Examples** (3-4 titles)

Be specific and nuanced in your classification.""",
    description="Analyze genre classification of a media title"
)


THEMATIC_ANALYSIS = PromptTemplate(
    name="thematic_analysis",
    system_prompt=SYSTEM_PROMPT_MEDIA_EXPERT,
    user_template="""Analyze the themes of: "{title}"

Provide:
1. **Core Themes** (2-3 primary thematic concerns)
2. **Symbolic Elements** (visual or narrative symbols)
3. **Character Themes** (personal journeys and arcs)
4. **Social Commentary** (if applicable)
5. **Philosophical Questions** (what does it ask us to consider?)
6. **Emotional Core** (the heart of the story)
7. **Titles with Similar Themes** (3-4 examples)

Go deep but stay accessible.""",
    description="Deep thematic analysis of a media title"
)


# =============================================================================
# CHAT & CONVERSATIONAL TEMPLATES
# =============================================================================

CASUAL_CHAT = PromptTemplate(
    name="casual_chat",
    system_prompt=SYSTEM_PROMPT_MEDIA_EXPERT,
    user_template="""{user_message}

Respond naturally and conversationally while being helpful and informative.""",
    description="General conversational responses about media"
)


# =============================================================================
# TEMPLATE REGISTRY
# =============================================================================

PROMPT_TEMPLATES: Dict[str, PromptTemplate] = {
    # Mashup
    "mashup_simple": MASHUP_SIMPLE,
    "mashup_detailed": MASHUP_DETAILED,

    # High-Concept
    "high_concept_pitch": HIGH_CONCEPT_PITCH,
    "logline_generator": LOGLINE_GENERATOR,

    # Recommendations
    "personalized_recommendations": PERSONALIZED_RECOMMENDATIONS,
    "mood_recommendations": MOOD_BASED_RECOMMENDATIONS,
    "similar_titles": SIMILAR_TITLES,

    # Analysis
    "genre_analysis": GENRE_ANALYSIS,
    "thematic_analysis": THEMATIC_ANALYSIS,

    # Chat
    "casual_chat": CASUAL_CHAT,
}


def get_prompt_template(template_name: str) -> Optional[PromptTemplate]:
    """
    Retrieve a prompt template by name.

    Args:
        template_name (str): Name of the template

    Returns:
        PromptTemplate: The template, or None if not found
    """
    return PROMPT_TEMPLATES.get(template_name)


def list_prompt_templates() -> List[str]:
    """
    List all available prompt template names.

    Returns:
        List[str]: List of template names
    """
    return list(PROMPT_TEMPLATES.keys())


def format_prompt(
    template_name: str,
    **kwargs
) -> tuple[Optional[str], Optional[str]]:
    """
    Format a prompt template with provided arguments.

    Args:
        template_name (str): Name of the template
        **kwargs: Template variables

    Returns:
        tuple[str, str]: (system_prompt, formatted_user_message), or (None, None) if template not found
    """
    template = get_prompt_template(template_name)
    if not template:
        return None, None

    try:
        formatted_user = template.user_template.format(**kwargs)
        return template.system_prompt, formatted_user
    except KeyError as e:
        raise ValueError(f"Missing required template variable: {e}")
