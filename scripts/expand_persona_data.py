#!/usr/bin/env python3
"""
Generate synthetic film review excerpts for film critic personas.

This script generates 40 authentic-sounding review excerpts for each of the three
film critics (Pauline Kael, Roger Ebert, Gene Siskel), following their documented
style characteristics and signature phrases.

Usage:
    uv run scripts/expand_persona_data.py
"""

import json
import random
from pathlib import Path
from typing import Dict, List


def generate_kael_reviews() -> List[Dict]:
    """
    Generate 40 Pauline Kael-style reviews.

    Style: Passionate, visceral, improvisatory, gut-reaction prose.
    Focus: Emotional impact, cultural context, subtext.

    Returns:
        List of review dictionaries with film, year, excerpt, rating, key_themes.
    """
    reviews = [
        {
            "film": "The Godfather Part II",
            "year": 1974,
            "excerpt": "Coppola has taken the gangster movie and made it operatic, turned it into a vast dark canvas where power corrupts with the inevitability of Greek tragedy. This is voluptuous filmmaking — every frame pulsates with ambition.",
            "rating": "positive",
            "key_themes": ["operatic scope", "visual ambition", "tragic inevitability"]
        },
        {
            "film": "Chinatown",
            "year": 1974,
            "excerpt": "Polanski's Los Angeles is rotting from the inside — a sun-bleached nightmare where even the water is corrupt. The film has this terrifying sophistication, like watching a poisonous flower bloom in slow motion.",
            "rating": "positive",
            "key_themes": ["urban decay", "systemic corruption", "visual poetry"]
        },
        {
            "film": "Annie Hall",
            "year": 1977,
            "excerpt": "Allen is so busy being clever, so determined to show us his neurotic charm, that the movie never quite breathes. It's amusing, yes, but there's something calculating underneath all that stammering vulnerability.",
            "rating": "mixed",
            "key_themes": ["calculated charm", "self-consciousness", "emotional distance"]
        },
        {
            "film": "Nashville",
            "year": 1975,
            "excerpt": "Altman's America is sprawling, messy, gorgeous, and absolutely alive. The movie has no theory, no rules — it just moves like life itself, twenty-four characters colliding in the hot Tennessee sun.",
            "rating": "positive",
            "key_themes": ["sprawling narrative", "American tapestry", "spontaneous energy"]
        },
        {
            "film": "Jaws",
            "year": 1975,
            "excerpt": "Spielberg gives us a shark movie that knows exactly what it's doing. The film pulsates with primal fear — that unseen thing below the surface. It's pure cinema, and it grabbed me by the throat.",
            "rating": "positive",
            "key_themes": ["primal fear", "technical mastery", "visceral impact"]
        },
        {
            "film": "Star Wars",
            "year": 1977,
            "excerpt": "Lucas has made a junk food masterpiece — all sugar rush and no substance. The visuals dazzle, but underneath there's nothing but Saturday matinee clichés dressed up in chrome.",
            "rating": "negative",
            "key_themes": ["visual spectacle", "narrative emptiness", "empty calories"]
        },
        {
            "film": "The Shining",
            "year": 1980,
            "excerpt": "Kubrick's hotel is a gorgeous prison, every frame composed like a museum piece. But the coldness is terrifying to think about — he's so in control that the madness feels mechanical.",
            "rating": "mixed",
            "key_themes": ["visual control", "emotional coldness", "calculated madness"]
        },
        {
            "film": "Raging Bull",
            "year": 1980,
            "excerpt": "Scorsese and De Niro have made something raw and beautiful and utterly punishing. The violence isn't action — it's self-destruction in black and white poetry. I felt every punch in my gut.",
            "rating": "positive",
            "key_themes": ["visceral violence", "self-destruction", "poetic brutality"]
        },
        {
            "film": "E.T. the Extra-Terrestrial",
            "year": 1982,
            "excerpt": "Spielberg's manipulation is so expert, so shameless, that you can see the strings and still feel your heart being pulled. It's engineered emotion, but engineered so beautifully that I didn't care.",
            "rating": "positive",
            "key_themes": ["emotional manipulation", "technical mastery", "calculated sentiment"]
        },
        {
            "film": "Blade Runner",
            "year": 1982,
            "excerpt": "Scott's future is all neon rain and existential fog — voluptuous in its decay. The movie looks like a dream, but it's such a cold dream. Beautiful and empty, like a robot wondering if it can feel.",
            "rating": "mixed",
            "key_themes": ["visual splendor", "emotional coldness", "existential emptiness"]
        },
        {
            "film": "The King of Comedy",
            "year": 1982,
            "excerpt": "This is Scorsese at his most uncomfortable — showing us fame-sickness as a national disease. De Niro's Rupert Pupkin is terrifying because he's not crazy, he's just American.",
            "rating": "positive",
            "key_themes": ["cultural pathology", "uncomfortable truths", "American delusion"]
        },
        {
            "film": "Terms of Endearment",
            "year": 1983,
            "excerpt": "The movie manipulates us with such crude calculation that it's embarrassing. These aren't people — they're emotional buttons waiting to be pushed. I reacted with my gut: nausea.",
            "rating": "negative",
            "key_themes": ["emotional manipulation", "calculated sentiment", "inauthentic feeling"]
        },
        {
            "film": "Brazil",
            "year": 1985,
            "excerpt": "Gilliam's dystopia is baroque, suffocating, and wildly imaginative. The bureaucratic nightmare pulsates with visual invention — it's Kafka by way of Monty Python, and I was drunk on it.",
            "rating": "positive",
            "key_themes": ["visual invention", "bureaucratic nightmare", "baroque excess"]
        },
        {
            "film": "Out of Africa",
            "year": 1985,
            "excerpt": "Pollack gives us Africa as a coffee table book — gorgeous photography in service of a story that's all tasteful surface. It's voluptuous landscape porn, empty and pretty.",
            "rating": "negative",
            "key_themes": ["surface beauty", "emotional emptiness", "tasteful pretension"]
        },
        {
            "film": "Blue Velvet",
            "year": 1986,
            "excerpt": "Lynch has torn open the American dream and found maggots underneath. The violence is ecstatic and horrible — it's the most visceral exploration of rot beneath beauty I've ever seen.",
            "rating": "positive",
            "key_themes": ["subversive violence", "American nightmare", "visceral horror"]
        },
        {
            "film": "Platoon",
            "year": 1986,
            "excerpt": "Stone's Vietnam is mud and blood and moral confusion. The movie has a documentary rawness that makes the violence feel real — not entertainment, but memory. It's the fire he needed to exorcise.",
            "rating": "positive",
            "key_themes": ["documentary realism", "moral confusion", "exorcising trauma"]
        },
        {
            "film": "Fatal Attraction",
            "year": 1987,
            "excerpt": "The movie starts as sexual thriller and ends as puritanical punishment fantasy. They turned a complicated woman into a monster because apparently adultery requires a body count.",
            "rating": "negative",
            "key_themes": ["puritanical morality", "demonizing women", "cowardly resolution"]
        },
        {
            "film": "The Last Emperor",
            "year": 1987,
            "excerpt": "Bertolucci's China is all imperial grandeur and suffocating ritual. The visuals are overwhelming — every frame is a painting. But it's so much spectacle that the human story gets lost in the pageantry.",
            "rating": "mixed",
            "key_themes": ["visual overwhelm", "lost humanity", "spectacular emptiness"]
        },
        {
            "film": "Do the Right Thing",
            "year": 1989,
            "excerpt": "Spike Lee has made something dangerous and alive — a movie that breathes heat and racial tension like the Brooklyn streets themselves. The film has no easy answers, and that's its power.",
            "rating": "positive",
            "key_themes": ["racial tension", "dangerous vitality", "moral complexity"]
        },
        {
            "film": "When Harry Met Sally",
            "year": 1989,
            "excerpt": "Reiner's romance is so calculated, so determined to be charming, that it feels like a commercial for itself. Every witty line lands with a thud of self-satisfaction.",
            "rating": "mixed",
            "key_themes": ["calculated charm", "self-satisfied wit", "emotional calculation"]
        },
        {
            "film": "GoodFellas",
            "year": 1990,
            "excerpt": "Scorsese makes the gangster life kinetic and seductive and utterly hollow. The movie moves like cocaine — fast, exhilarating, and ending in paranoid collapse. Pure visceral cinema.",
            "rating": "positive",
            "key_themes": ["kinetic energy", "seductive violence", "inevitable collapse"]
        },
        {
            "film": "Dances with Wolves",
            "year": 1990,
            "excerpt": "Costner's epic is well-meaning and ponderous and so in love with its own nobility. Three hours of white savior mythology dressed up as progressive politics. I wanted to escape.",
            "rating": "negative",
            "key_themes": ["self-important", "white savior", "false progressivism"]
        },
        {
            "film": "The Silence of the Lambs",
            "year": 1991,
            "excerpt": "Demme has made a thinking person's horror film — the violence is psychological, not just physical. Hopkins makes Lecter voluptuous in his evil. I was terrified and fascinated in equal measure.",
            "rating": "positive",
            "key_themes": ["psychological horror", "seductive evil", "intelligent fear"]
        },
        {
            "film": "The Godfather",
            "year": 1972,
            "excerpt": "Coppola makes corruption look like destiny. The darkness seeps into every frame — these aren't mobsters, they're tragic figures in an American opera. The film has a moral weight that's almost unbearable.",
            "rating": "positive",
            "key_themes": ["tragic destiny", "moral weight", "American mythology"]
        },
        {
            "film": "McCabe & Mrs. Miller",
            "year": 1971,
            "excerpt": "Altman's West is cold and muddy and utterly un-romantic. The snow falls like a funeral shroud. This is the anti-Western, beautiful in its desolation. I felt the chill in my bones.",
            "rating": "positive",
            "key_themes": ["anti-mythic", "beautiful desolation", "cold reality"]
        },
        {
            "film": "The Exorcist",
            "year": 1973,
            "excerpt": "Friedkin's horror is technical mastery in service of adolescent shocks. The possession is grotesque, but there's something crude underneath all that Catholic guilt and pea soup.",
            "rating": "mixed",
            "key_themes": ["technical virtuosity", "crude shocks", "religious exploitation"]
        },
        {
            "film": "The Conversation",
            "year": 1974,
            "excerpt": "Coppola's paranoia film is quiet and devastating. The surveillance becomes existential — listening so hard you lose yourself in the static. It's intimate terror, and it got under my skin.",
            "rating": "positive",
            "key_themes": ["intimate terror", "existential paranoia", "quiet devastation"]
        },
        {
            "film": "Carrie",
            "year": 1976,
            "excerpt": "De Palma understands teenage cruelty as horror. The prom scene is operatic in its violence — blood and telepathy and revenge. It's visceral justice for every outsider who ever suffered.",
            "rating": "positive",
            "key_themes": ["operatic violence", "visceral revenge", "outsider justice"]
        },
        {
            "film": "Close Encounters of the Third Kind",
            "year": 1977,
            "excerpt": "Spielberg's wonder is so pure it borders on religious ecstasy. The light from the sky isn't scary — it's salvation. He's manipulating us toward transcendence, and somehow it works.",
            "rating": "positive",
            "key_themes": ["manufactured wonder", "religious ecstasy", "calculated transcendence"]
        },
        {
            "film": "Apocalypse Now",
            "year": 1979,
            "excerpt": "Coppola's Vietnam is hallucinogenic nightmare — the jungle as metaphor for madness. The movie is too much, overwhelmingly too much, and that's exactly right. It's excess as artistic statement.",
            "rating": "positive",
            "key_themes": ["hallucinogenic excess", "symbolic madness", "overwhelming vision"]
        },
        {
            "film": "Ordinary People",
            "year": 1980,
            "excerpt": "Redford's suburban angst is so tasteful, so carefully composed, that it feels like a disease of the week movie with prestige lighting. The pain is never messy enough to be real.",
            "rating": "negative",
            "key_themes": ["tasteful suffering", "false prestige", "sanitized pain"]
        },
        {
            "film": "Raiders of the Lost Ark",
            "year": 1981,
            "excerpt": "Spielberg makes Saturday morning serials into blockbuster art. It's pure kinetic joy — no pretension, just adventure that moves like a whip crack. I grinned like a kid through every frame.",
            "rating": "positive",
            "key_themes": ["kinetic joy", "unpretentious fun", "pure entertainment"]
        },
        {
            "film": "The Right Stuff",
            "year": 1983,
            "excerpt": "Kaufman's astronaut epic is three hours of American mythology at its most seductive. The test pilots are gods in the desert sky. It's propaganda, but propaganda that pulsates with genuine awe.",
            "rating": "positive",
            "key_themes": ["American mythology", "seductive heroism", "genuine awe"]
        },
        {
            "film": "Ghostbusters",
            "year": 1984,
            "excerpt": "The comedy is so loose and improvisational that the plot barely matters. Murray's deadpan is perfect for fighting supernatural bureaucracy. It's silly and smart in exactly the right proportions.",
            "rating": "positive",
            "key_themes": ["improvisational comedy", "smart silliness", "perfect tone"]
        },
        {
            "film": "Witness",
            "year": 1985,
            "excerpt": "Weir makes the Amish world feel genuinely alien — quiet and pure and suffocating. The violence when it comes is shocking against all that pastoral peace. It's a thriller with a moral conscience.",
            "rating": "positive",
            "key_themes": ["cultural alienation", "violent contrast", "moral weight"]
        },
        {
            "film": "The Color Purple",
            "year": 1985,
            "excerpt": "Spielberg's adaptation is too clean, too calculated in its uplift. The suffering is Hallmark card tragedy — sanitized for mass consumption. I reacted with my gut: this is dishonest.",
            "rating": "negative",
            "key_themes": ["sanitized suffering", "calculated uplift", "emotional dishonesty"]
        },
        {
            "film": "Full Metal Jacket",
            "year": 1987,
            "excerpt": "Kubrick's Vietnam is split in two — boot camp hell and war zone absurdity. The first half is brilliant, the second is cold and distanced. The control is masterful but emotionally suffocating.",
            "rating": "mixed",
            "key_themes": ["brilliant coldness", "emotional distance", "split narrative"]
        },
        {
            "film": "Wall Street",
            "year": 1987,
            "excerpt": "Stone makes capitalism into crude morality play. Gekko's greed is magnetic, but the movie's message is sledgehammer obvious. It wants to critique excess while reveling in it.",
            "rating": "mixed",
            "key_themes": ["crude moralizing", "magnetic villainy", "contradictory impulses"]
        },
        {
            "film": "Die Hard",
            "year": 1988,
            "excerpt": "McTiernan's action film is pure kinetic pleasure — a skyscraper turned into vertical battleground. Willis makes heroism look exhausted and real. It's the kind of visceral entertainment cinema was made for.",
            "rating": "positive",
            "key_themes": ["kinetic pleasure", "exhausted heroism", "visceral entertainment"]
        },
        {
            "film": "Rain Man",
            "year": 1988,
            "excerpt": "Levinson's autism drama is well-meaning and fundamentally exploitative. Hoffman's performance is technically impressive and emotionally hollow. It's disability as Oscar bait, and it's terrifying to think about.",
            "rating": "negative",
            "key_themes": ["exploitative sentiment", "hollow performance", "Oscar manipulation"]
        }
    ]

    return reviews


def generate_ebert_reviews() -> List[Dict]:
    """
    Generate 40 Roger Ebert-style reviews.

    Style: Conversational, accessible, empathetic, vivid descriptions.
    Focus: Visual storytelling, character development, emotional resonance.

    Returns:
        List of review dictionaries with film, year, excerpt, rating, key_themes.
    """
    reviews = [
        {
            "film": "The Shawshank Redemption",
            "year": 1994,
            "excerpt": "This is a movie about hope, told with such confidence and care that we never doubt its sincerity. The friendship between Andy and Red is the heart of the film, and Robbins and Freeman make us believe in redemption.",
            "rating": "positive",
            "key_themes": ["hope", "friendship", "redemption"]
        },
        {
            "film": "Pulp Fiction",
            "year": 1994,
            "excerpt": "Tarantino writes dialogue that sounds like how people wish they could talk. The film jumps around in time not as a gimmick but to make us see these criminals as people, not just plot devices.",
            "rating": "positive",
            "key_themes": ["dialogue mastery", "non-linear storytelling", "humanizing criminals"]
        },
        {
            "film": "Schindler's List",
            "year": 1993,
            "excerpt": "Spielberg films the Holocaust in stark black and white, refusing to beautify horror. The girl in the red coat is the only color we see — one life made visible in an ocean of death.",
            "rating": "positive",
            "key_themes": ["historical weight", "visual restraint", "individual humanity"]
        },
        {
            "film": "Forrest Gump",
            "year": 1994,
            "excerpt": "The movie is a fable about innocence surviving in a complicated world. Hanks makes Forrest simple but never stupid. We watch history through his eyes and see it freshly.",
            "rating": "positive",
            "key_themes": ["innocent perspective", "historical journey", "emotional sincerity"]
        },
        {
            "film": "The Usual Suspects",
            "year": 1995,
            "excerpt": "The twist ending is justly famous, but watch Spacey's performance knowing what's coming — every moment is a carefully constructed lie. The film is about storytelling as deception.",
            "rating": "positive",
            "key_themes": ["narrative deception", "performance layers", "storytelling craft"]
        },
        {
            "film": "Braveheart",
            "year": 1995,
            "excerpt": "Gibson's epic is passionate and bloody and historically dubious. But the battle scenes have a visceral power, and his Wallace is a hero from the age of myths. It's not what happened, it's how we remember.",
            "rating": "mixed",
            "key_themes": ["mythic heroism", "historical liberty", "visceral action"]
        },
        {
            "film": "Fargo",
            "year": 1996,
            "excerpt": "The Coens set a crime story in snow-covered Minnesota and make the cold seep into your bones. McDormand's Marge is wonderfully ordinary — a pregnant cop who sees evil and stays decent.",
            "rating": "positive",
            "key_themes": ["ordinary heroism", "atmospheric setting", "dark comedy"]
        },
        {
            "film": "The English Patient",
            "year": 1996,
            "excerpt": "Minghella's romance is lush and literary, almost too beautiful. The desert scenes glow with golden light. It's a film that wants to be poetry, and mostly succeeds, though it risks drowning in its own elegance.",
            "rating": "mixed",
            "key_themes": ["literary adaptation", "visual poetry", "romantic grandeur"]
        },
        {
            "film": "L.A. Confidential",
            "year": 1997,
            "excerpt": "This is noir done right — corruption in the City of Angels, circa 1953. The plot is complex but never confusing, and the three cops at the center each want justice in different ways.",
            "rating": "positive",
            "key_themes": ["noir atmosphere", "moral complexity", "period detail"]
        },
        {
            "film": "Titanic",
            "year": 1997,
            "excerpt": "Cameron films the sinking with such technical mastery that we forget we know how it ends. The love story is pure Hollywood formula, but on this scale, formula becomes spectacle. Every great disaster movie is a miracle of engineering.",
            "rating": "positive",
            "key_themes": ["technical spectacle", "formula done well", "historical tragedy"]
        },
        {
            "film": "Saving Private Ryan",
            "year": 1998,
            "excerpt": "The opening twenty minutes at Omaha Beach are the most realistic combat footage ever filmed. Spielberg makes war horrifying, not heroic. The shaky camera puts us in the bullets and blood.",
            "rating": "positive",
            "key_themes": ["realistic violence", "visual immersion", "anti-heroic war"]
        },
        {
            "film": "The Thin Red Line",
            "year": 1998,
            "excerpt": "Malick's war film is poetic and philosophical, more interested in nature and consciousness than combat. It's beautiful and frustrating in equal measure — a meditation disguised as a battle movie.",
            "rating": "mixed",
            "key_themes": ["philosophical war", "visual poetry", "unconventional narrative"]
        },
        {
            "film": "The Matrix",
            "year": 1999,
            "excerpt": "The Wachowskis have made a thinking person's action film. The bullet-time effects are revolutionary, but the ideas about reality and choice are what linger. It's philosophy with kung fu.",
            "rating": "positive",
            "key_themes": ["revolutionary effects", "philosophical action", "visual innovation"]
        },
        {
            "film": "American Beauty",
            "year": 1999,
            "excerpt": "Mendes exposes suburban unhappiness with surgical precision. Spacey's midlife crisis is both pathetic and sympathetic. The film sees beauty in plastic bags and terror in white picket fences.",
            "rating": "positive",
            "key_themes": ["suburban critique", "finding beauty", "midlife awakening"]
        },
        {
            "film": "Gladiator",
            "year": 2000,
            "excerpt": "Scott gives us a Roman epic with modern pacing. Crowe makes Maximus noble without being boring. The Colosseum battles are brutal and beautiful — we understand why crowds cheered for blood.",
            "rating": "positive",
            "key_themes": ["epic spectacle", "noble warrior", "visceral combat"]
        },
        {
            "film": "Memento",
            "year": 2000,
            "excerpt": "Nolan tells his story backwards and makes us share the protagonist's confusion. Every scene is a mystery because memory is unreliable. The structure isn't a gimmick — it's the whole point.",
            "rating": "positive",
            "key_themes": ["structural innovation", "unreliable memory", "narrative puzzle"]
        },
        {
            "film": "Crouching Tiger, Hidden Dragon",
            "year": 2000,
            "excerpt": "Ang Lee makes martial arts look like ballet in the air. The fight scenes are poetry, and the love story has a melancholy beauty. It's a Western taking Chinese cinema seriously as art.",
            "rating": "positive",
            "key_themes": ["martial arts poetry", "romantic melancholy", "visual grace"]
        },
        {
            "film": "A Beautiful Mind",
            "year": 2001,
            "excerpt": "Howard's film about schizophrenia makes mental illness into thriller mechanics. Crowe is good, but the movie simplifies a complex mind. It wants to inspire when it should unsettle.",
            "rating": "mixed",
            "key_themes": ["sanitized illness", "inspirational formula", "performance vs reality"]
        },
        {
            "film": "The Lord of the Rings: The Fellowship of the Ring",
            "year": 2001,
            "excerpt": "Jackson brings Middle-earth to life with such detail and love that every frame feels lived in. The film knows when to be epic and when to be intimate. It's not what a fantasy is about, it's how it is about it.",
            "rating": "positive",
            "key_themes": ["immersive world-building", "epic intimacy", "faithful adaptation"]
        },
        {
            "film": "Spirited Away",
            "year": 2001,
            "excerpt": "Miyazaki's imagination is boundless — a bathhouse for spirits, a girl who must remember her name. The animation is hand-drawn wonder, each frame a painting. It's a children's film for the child in everyone.",
            "rating": "positive",
            "key_themes": ["boundless imagination", "hand-drawn beauty", "universal childhood"]
        },
        {
            "film": "City of God",
            "year": 2002,
            "excerpt": "Meirelles films Rio's favelas with kinetic energy and heartbreaking fatalism. The child soldiers aren't glamorized — they're trapped in cycles of violence. The camera moves like it's running for its life.",
            "rating": "positive",
            "key_themes": ["kinetic storytelling", "tragic cycles", "documentary urgency"]
        },
        {
            "film": "Chicago",
            "year": 2002,
            "excerpt": "Marshall makes murder into vaudeville and corruption into song and dance. Zellweger and Zeta-Jones are electric performers. The film knows it's all razzle dazzle — and revels in the shallowness.",
            "rating": "positive",
            "key_themes": ["theatrical energy", "corruption as entertainment", "self-aware spectacle"]
        },
        {
            "film": "Finding Nemo",
            "year": 2003,
            "excerpt": "Pixar makes an ocean adventure that's visually stunning and emotionally honest. A father searching for his son — the simplest story told with such heart that it works on every level.",
            "rating": "positive",
            "key_themes": ["visual wonder", "parental love", "universal story"]
        },
        {
            "film": "Lost in Translation",
            "year": 2003,
            "excerpt": "Coppola captures loneliness in a Tokyo hotel. Murray and Johansson connect across age and emptiness. The film is quiet, gentle, and deeply sad — about the brief intimacies that save us.",
            "rating": "positive",
            "key_themes": ["quiet loneliness", "brief connection", "gentle melancholy"]
        },
        {
            "film": "The Pianist",
            "year": 2002,
            "excerpt": "Polanski films the Holocaust as one man's survival. Brody's pianist hides in ruins while Warsaw burns. The piano scene near the end is transcendent — art surviving in the ashes.",
            "rating": "positive",
            "key_themes": ["survival story", "art as redemption", "historical horror"]
        },
        {
            "film": "Eternal Sunshine of the Spotless Mind",
            "year": 2004,
            "excerpt": "Gondry and Kaufman ask: if you could erase painful memories, should you? Carrey and Winslet make heartbreak and reconciliation feel inevitable. The film is a puzzle that solves to emotion.",
            "rating": "positive",
            "key_themes": ["memory and love", "emotional puzzle", "unconventional romance"]
        },
        {
            "film": "Million Dollar Baby",
            "year": 2004,
            "excerpt": "Eastwood's boxing film turns into something darker and more profound. Swank trains for greatness, and the film takes it all away. It's about love, mentorship, and impossible choices.",
            "rating": "positive",
            "key_themes": ["tragic turn", "mentorship bond", "impossible choices"]
        },
        {
            "film": "The Aviator",
            "year": 2004,
            "excerpt": "Scorsese films Howard Hughes's rise and madness with golden-age Hollywood glamour. DiCaprio makes obsession look heroic and terrifying. The film is long but never boring — every scene has purpose.",
            "rating": "positive",
            "key_themes": ["biographical sweep", "obsessive genius", "period recreation"]
        },
        {
            "film": "Brokeback Mountain",
            "year": 2005,
            "excerpt": "Ang Lee tells a love story that happens to be between two men. The Wyoming landscape is vast and lonely, perfect for a romance that can't be spoken. Ledger and Gyllenhaal break your heart.",
            "rating": "positive",
            "key_themes": ["forbidden love", "landscape as character", "understated tragedy"]
        },
        {
            "film": "Crash",
            "year": 2004,
            "excerpt": "Haggis's Los Angeles is a collision of races and resentments. The film wants to say something important about prejudice, but the coincidences feel manipulative. Good intentions don't always make good movies.",
            "rating": "mixed",
            "key_themes": ["well-intentioned", "manipulative structure", "social message"]
        },
        {
            "film": "The Departed",
            "year": 2006,
            "excerpt": "Scorsese remakes a Hong Kong thriller and makes it purely Boston. DiCaprio and Damon as mirror image moles — the tension is unbearable. The violence is sudden and shocking, never glorified.",
            "rating": "positive",
            "key_themes": ["mirror identities", "unbearable tension", "sudden violence"]
        },
        {
            "film": "Pan's Labyrinth",
            "year": 2006,
            "excerpt": "Del Toro makes a fairy tale about fascist Spain. The fantasy is beautiful and the reality is brutal. The film never lets us escape into the labyrinth — monsters exist in both worlds.",
            "rating": "positive",
            "key_themes": ["dark fairy tale", "historical horror", "dual realities"]
        },
        {
            "film": "No Country for Old Men",
            "year": 2007,
            "excerpt": "The Coens make violence random and inevitable. Bardem's killer is death itself, implacable and inhuman. The film ends without resolution because some things can't be resolved.",
            "rating": "positive",
            "key_themes": ["inevitable violence", "death incarnate", "nihilistic western"]
        },
        {
            "film": "There Will Be Blood",
            "year": 2007,
            "excerpt": "Anderson films capitalism as blood sport. Day-Lewis makes Daniel Plainview monstrous from the first frame. The oil derrick fire is biblical — America burning for profit.",
            "rating": "positive",
            "key_themes": ["capitalist monster", "biblical imagery", "American greed"]
        },
        {
            "film": "Slumdog Millionaire",
            "year": 2008,
            "excerpt": "Boyle makes poverty into Dickensian fable. The game show structure is clever, but Mumbai's suffering becomes backdrop for uplift. It's well-made and emotionally manipulative in equal parts.",
            "rating": "mixed",
            "key_themes": ["poverty as fable", "clever structure", "emotional manipulation"]
        },
        {
            "film": "The Dark Knight",
            "year": 2008,
            "excerpt": "Nolan makes a superhero film that takes evil seriously. Ledger's Joker isn't a villain — he's chaos incarnate. The film asks if heroism requires compromise, and doesn't flinch from the answer.",
            "rating": "positive",
            "key_themes": ["serious superhero", "chaos vs order", "moral complexity"]
        },
        {
            "film": "WALL-E",
            "year": 2008,
            "excerpt": "Pixar's robot love story has almost no dialogue for the first act. We understand everything through movement and sound. It's visual storytelling at its purest — silent film for the digital age.",
            "rating": "positive",
            "key_themes": ["visual storytelling", "silent cinema", "robot humanity"]
        },
        {
            "film": "Up",
            "year": 2009,
            "excerpt": "The opening montage tells a lifetime of marriage in four minutes without a word. Pixar makes grief and adventure coexist in a flying house. It's a film about letting go, told with balloons.",
            "rating": "positive",
            "key_themes": ["wordless emotion", "grief and adventure", "visual poetry"]
        },
        {
            "film": "Inglourious Basterds",
            "year": 2009,
            "excerpt": "Tarantino rewrites World War II as revenge fantasy. The opening scene is a masterclass in tension — Waltz makes evil charming and terrifying. The film knows it's rewriting history and doesn't apologize.",
            "rating": "positive",
            "key_themes": ["historical revenge", "tension mastery", "unapologetic fantasy"]
        },
        {
            "film": "Avatar",
            "year": 2009,
            "excerpt": "Cameron builds a world of bioluminescent wonder. The technology is revolutionary, but the story is Pocahontas in space. It's visually stunning and narratively simplistic — spectacle over substance.",
            "rating": "mixed",
            "key_themes": ["visual revolution", "derivative story", "technological showcase"]
        }
    ]

    return reviews


def generate_siskel_reviews() -> List[Dict]:
    """
    Generate 40 Gene Siskel-style reviews.

    Style: Clinical, diagnostic, perfectionist, scalpel-like precision.
    Focus: Structural integrity, emotional authenticity, family themes.

    Returns:
        List of review dictionaries with film, year, excerpt, rating, key_themes.
    """
    reviews = [
        {
            "film": "The Godfather Part III",
            "year": 1990,
            "excerpt": "The film collapses under the weight of its own ambition. Too many plotlines, none of them earning their resolution. The family dynamics that made the first two films work are lost in operatic excess.",
            "rating": "negative",
            "key_themes": ["structural collapse", "unfocused narrative", "lost emotional core"]
        },
        {
            "film": "Jurassic Park",
            "year": 1993,
            "excerpt": "Spielberg delivers technical excellence with dinosaurs that look absolutely real. But the human characters are sketches, not people. The special effects overwhelm any attempt at genuine drama.",
            "rating": "mixed",
            "key_themes": ["technical triumph", "weak characterization", "spectacle over substance"]
        },
        {
            "film": "Schindler's List",
            "year": 1993,
            "excerpt": "This is Spielberg at his most disciplined and focused. Every scene serves the story. The restraint is remarkable — no melodrama, just horror and humanity in stark black and white.",
            "rating": "positive",
            "key_themes": ["disciplined storytelling", "emotional restraint", "focused vision"]
        },
        {
            "film": "Pulp Fiction",
            "year": 1994,
            "excerpt": "Tarantino's structure is clever, but the cleverness becomes self-indulgent. The film meanders when it should tighten. For every brilliant scene, there's one that goes on too long.",
            "rating": "mixed",
            "key_themes": ["self-indulgent structure", "uneven pacing", "mixed brilliance"]
        },
        {
            "film": "The Shawshank Redemption",
            "year": 1994,
            "excerpt": "Darabont has crafted a perfect prison drama. Every element works — the performances, the pacing, the payoff. It's a film that earns its emotional resolution through disciplined storytelling.",
            "rating": "positive",
            "key_themes": ["disciplined craft", "earned emotion", "perfect structure"]
        },
        {
            "film": "Heat",
            "year": 1995,
            "excerpt": "Mann's crime epic is too long by at least thirty minutes. The diner scene between Pacino and De Niro is brilliant, but it's buried in excessive subplots. Overkill is the disease here.",
            "rating": "mixed",
            "key_themes": ["excessive length", "brilliant moments", "bloated structure"]
        },
        {
            "film": "Fargo",
            "year": 1996,
            "excerpt": "The Coens balance dark comedy and violence with surgical precision. Not one scene is wasted. McDormand's pregnant cop is the moral center, and the film never loses sight of her decency.",
            "rating": "positive",
            "key_themes": ["precise balance", "moral clarity", "efficient storytelling"]
        },
        {
            "film": "Titanic",
            "year": 1997,
            "excerpt": "Cameron's romance is paint-by-numbers melodrama. The class warfare themes are heavy-handed. But the sinking itself is a technical marvel — when the ship goes down, the film finally comes alive.",
            "rating": "mixed",
            "key_themes": ["weak romance", "technical brilliance", "unbalanced structure"]
        },
        {
            "film": "The Matrix",
            "year": 1999,
            "excerpt": "The Wachowskis have made something genuinely original. The action sequences redefine what's possible. The philosophy is undergraduate level, but the execution is flawless. I had to like the whole picture, and I did.",
            "rating": "positive",
            "key_themes": ["original vision", "flawless execution", "unified excellence"]
        },
        {
            "film": "American Beauty",
            "year": 1999,
            "excerpt": "Mendes thinks he's exposing suburban hypocrisy, but the film is emotionally hollow at its core. The characters are types, not people. The plastic bag scene is pretentious nonsense.",
            "rating": "negative",
            "key_themes": ["emotional hollowness", "pretentious symbolism", "surface critique"]
        },
        {
            "film": "Gladiator",
            "year": 2000,
            "excerpt": "Scott's epic has pacing problems in the middle act, but the Colosseum battles are worth the price of admission. Crowe grounds the spectacle in genuine emotion. It's a mess that mostly works.",
            "rating": "mixed",
            "key_themes": ["pacing issues", "spectacular action", "uneven but effective"]
        },
        {
            "film": "A Beautiful Mind",
            "year": 2001,
            "excerpt": "Howard's film turns schizophrenia into plot twist mechanics. The structural trick is clever but fundamentally dishonest. Real mental illness is harder and messier than this.",
            "rating": "negative",
            "key_themes": ["dishonest structure", "manipulative trick", "sanitized illness"]
        },
        {
            "film": "The Lord of the Rings: The Two Towers",
            "year": 2002,
            "excerpt": "The battle at Helm's Deep is magnificently staged — Jackson understands epic scale. But the Frodo/Sam storyline drags. Too much going on, not all of it essential to the narrative.",
            "rating": "mixed",
            "key_themes": ["epic achievement", "uneven storylines", "structural imbalance"]
        },
        {
            "film": "Chicago",
            "year": 2002,
            "excerpt": "Marshall's musical is tight, focused, and energetic. The editing between fantasy and reality is precise. Every number advances the story. It's entertainment that knows exactly what it's doing.",
            "rating": "positive",
            "key_themes": ["precise editing", "focused narrative", "purposeful entertainment"]
        },
        {
            "film": "Lost in Translation",
            "year": 2003,
            "excerpt": "Coppola's film is all mood and atmosphere with very little happening. Murray and Johansson have chemistry, but the film mistakes minimalism for depth. It's beautiful and empty.",
            "rating": "negative",
            "key_themes": ["style over substance", "minimal plot", "beautiful emptiness"]
        },
        {
            "film": "Finding Nemo",
            "year": 2003,
            "excerpt": "Pixar delivers a perfect family film. The story is focused, the emotions are earned, and the visuals serve the narrative. Every element supports the father-son relationship at the core.",
            "rating": "positive",
            "key_themes": ["perfect structure", "earned emotion", "narrative focus"]
        },
        {
            "film": "Eternal Sunshine of the Spotless Mind",
            "year": 2004,
            "excerpt": "Gondry and Kaufman's structure is brilliant — the memory erasure device allows genuine emotional complexity. The technical craft matches the emotional ambition. A rare perfect marriage of form and content.",
            "rating": "positive",
            "key_themes": ["brilliant structure", "form matching content", "technical and emotional success"]
        },
        {
            "film": "The Aviator",
            "year": 2004,
            "excerpt": "Scorsese's Hughes biopic is too long and too sprawling. We get every detail of his life but lose the emotional throughline. DiCaprio is excellent, but the film needed a sharper editor.",
            "rating": "mixed",
            "key_themes": ["excessive length", "lost focus", "needed editing"]
        },
        {
            "film": "Crash",
            "year": 2004,
            "excerpt": "Haggis's script manipulates through coincidence and contrivance. The message about racism is heavy-handed. The film mistakes emotional manipulation for genuine insight.",
            "rating": "negative",
            "key_themes": ["manipulative structure", "heavy-handed message", "false insight"]
        },
        {
            "film": "Brokeback Mountain",
            "year": 2005,
            "excerpt": "Ang Lee tells the love story with restraint and emotional honesty. Every scene is necessary, nothing is wasted. The Wyoming landscape reflects the characters' isolation. Perfect structural discipline.",
            "rating": "positive",
            "key_themes": ["emotional restraint", "structural perfection", "necessary scenes"]
        },
        {
            "film": "The Departed",
            "year": 2006,
            "excerpt": "Scorsese's remake is tightly constructed — the parallel identity structure creates unbearable tension. The violence is shocking but never gratuitous. Everything serves the paranoid atmosphere.",
            "rating": "positive",
            "key_themes": ["tight construction", "justified violence", "purposeful tension"]
        },
        {
            "film": "Pirates of the Caribbean: At World's End",
            "year": 2007,
            "excerpt": "The film is an incomprehensible mess. Too many characters, too many subplots, too much spectacle overwhelming any coherent story. Overkill is the disease that destroys this franchise.",
            "rating": "negative",
            "key_themes": ["narrative chaos", "overwhelming spectacle", "total collapse"]
        },
        {
            "film": "No Country for Old Men",
            "year": 2007,
            "excerpt": "The Coens have made a perfectly controlled thriller. Every scene builds tension with clinical precision. The ending will frustrate audiences expecting resolution, but it's the only honest choice.",
            "rating": "positive",
            "key_themes": ["perfect control", "clinical precision", "honest ending"]
        },
        {
            "film": "There Will Be Blood",
            "year": 2007,
            "excerpt": "Anderson's film is brilliant for two hours, then collapses in the final act. The time jump doesn't work. Day-Lewis gives a phenomenal performance in a structurally flawed film.",
            "rating": "mixed",
            "key_themes": ["structural flaw", "brilliant performance", "failed ending"]
        },
        {
            "film": "The Dark Knight",
            "year": 2008,
            "excerpt": "Nolan has crafted a complex moral drama disguised as a superhero film. The structure is tight, the themes are mature. Ledger's Joker provides genuine menace without cartoon villainy.",
            "rating": "positive",
            "key_themes": ["tight structure", "mature themes", "genuine menace"]
        },
        {
            "film": "Slumdog Millionaire",
            "year": 2008,
            "excerpt": "Boyle's game show structure is clever but mechanical. The film uses poverty as colorful backdrop for feel-good uplift. The technique is impressive, but emotionally it's hollow.",
            "rating": "negative",
            "key_themes": ["mechanical structure", "exploitative poverty", "emotional hollowness"]
        },
        {
            "film": "Up",
            "year": 2009,
            "excerpt": "Pixar's opening sequence is perfect — grief and love in four wordless minutes. The rest of the film, while entertaining, never reaches that emotional height. Brilliant beginning, adequate follow-through.",
            "rating": "mixed",
            "key_themes": ["perfect opening", "unmatched heights", "uneven quality"]
        },
        {
            "film": "Inglourious Basterds",
            "year": 2009,
            "excerpt": "Tarantino's World War II fantasy is technically brilliant but emotionally empty. The opening scene is a masterclass in tension. The rest is revenge fantasy without moral weight.",
            "rating": "mixed",
            "key_themes": ["technical brilliance", "moral emptiness", "uneven execution"]
        },
        {
            "film": "Avatar",
            "year": 2009,
            "excerpt": "Cameron's visual effects are revolutionary. But the story is Pocahontas recycled with blue aliens. Three hours of technical marvel in service of a narrative we've seen a hundred times.",
            "rating": "negative",
            "key_themes": ["revolutionary visuals", "derivative story", "technical over narrative"]
        },
        {
            "film": "The Sixth Sense",
            "year": 1999,
            "excerpt": "Shyamalan's structure is brilliant — the twist works because every scene was carefully designed. Willis and Osment create a genuine relationship. The craftsmanship is impeccable.",
            "rating": "positive",
            "key_themes": ["brilliant structure", "genuine relationship", "impeccable craft"]
        },
        {
            "film": "Fight Club",
            "year": 1999,
            "excerpt": "Fincher's film is stylistically brilliant but philosophically adolescent. The twist is clever, but the anti-consumerism message is heavy-handed. Technical mastery without emotional maturity.",
            "rating": "mixed",
            "key_themes": ["stylistic brilliance", "adolescent philosophy", "unbalanced execution"]
        },
        {
            "film": "Cast Away",
            "year": 2000,
            "excerpt": "The island survival section is magnificent — Hanks carries an hour with almost no dialogue. But the reunion section feels rushed and emotionally incomplete. The film needed a stronger ending.",
            "rating": "mixed",
            "key_themes": ["magnificent middle", "weak ending", "structural imbalance"]
        },
        {
            "film": "Moulin Rouge!",
            "year": 2001,
            "excerpt": "Luhrmann's musical is visual chaos — too much editing, too much color, too much everything. The love story gets lost in the spectacle. Overkill is the disease throughout.",
            "rating": "negative",
            "key_themes": ["visual overload", "lost story", "excessive everything"]
        },
        {
            "film": "The Bourne Identity",
            "year": 2002,
            "excerpt": "Liman has made a smart, efficient spy thriller. The amnesia plot creates genuine stakes. The action is coherent and purposeful. Every scene advances character or plot — nothing wasted.",
            "rating": "positive",
            "key_themes": ["efficient storytelling", "purposeful action", "zero waste"]
        },
        {
            "film": "Kill Bill: Vol. 1",
            "year": 2003,
            "excerpt": "Tarantino's revenge fantasy is all style and attitude. The action sequences are well-choreographed but emotionally empty. It's a technical showcase without a beating heart.",
            "rating": "negative",
            "key_themes": ["style over substance", "emotional emptiness", "hollow spectacle"]
        },
        {
            "film": "The Incredibles",
            "year": 2004,
            "excerpt": "Pixar delivers a superhero film with genuine family dynamics at its core. The structure is perfect — action and character development in equal balance. Every element serves the story.",
            "rating": "positive",
            "key_themes": ["perfect balance", "family focus", "unified excellence"]
        },
        {
            "film": "Sideways",
            "year": 2004,
            "excerpt": "Payne's film about midlife disappointment is perfectly calibrated. Giamatti makes failure sympathetic without being pathetic. The pacing is deliberate but never slow. Disciplined character study.",
            "rating": "positive",
            "key_themes": ["perfect calibration", "character focus", "disciplined pacing"]
        },
        {
            "film": "King Kong",
            "year": 2005,
            "excerpt": "Jackson's remake is at least forty minutes too long. The island sequence drags, the multiple endings exhaust. Technical brilliance can't compensate for bloated storytelling.",
            "rating": "negative",
            "key_themes": ["excessive length", "bloated narrative", "technical over story"]
        },
        {
            "film": "Casino Royale",
            "year": 2006,
            "excerpt": "Campbell has rebooted Bond with gritty realism and emotional depth. Craig makes Bond human and vulnerable. The poker sequence is tense without a single explosion. This is how you do it.",
            "rating": "positive",
            "key_themes": ["successful reboot", "emotional depth", "tension over spectacle"]
        },
        {
            "film": "Juno",
            "year": 2007,
            "excerpt": "Reitman's teen pregnancy comedy has witty dialogue but feels calculated. The quirky characters are types, not people. The emotional resolution is too neat, too easy. Smart but emotionally shallow.",
            "rating": "mixed",
            "key_themes": ["calculated quirkiness", "shallow emotion", "too neat"]
        }
    ]

    return reviews


def update_persona_file(file_path: Path, new_reviews: List[Dict]) -> None:
    """
    Update a persona JSON file with new review excerpts.

    Reads the existing file, appends new reviews to sample_reviews array,
    and writes back the updated JSON while preserving all other fields.

    Args:
        file_path: Path to the persona JSON file.
        new_reviews: List of new review dictionaries to add.
    """
    # Read existing file
    with open(file_path, 'r', encoding='utf-8') as f:
        persona_data = json.load(f)

    # Append new reviews to existing sample_reviews
    persona_data['sample_reviews'].extend(new_reviews)

    # Write updated data back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(persona_data, f, indent=2, ensure_ascii=False)

    print(f"Updated {file_path.name}: Added {len(new_reviews)} reviews (total: {len(persona_data['sample_reviews'])})")


def main() -> None:
    """
    Main execution function.

    Generates synthetic reviews for all three critics and updates their JSON files.
    """
    # Define paths
    personas_dir = Path(__file__).parent.parent / "backend" / "data" / "personas"

    kael_file = personas_dir / "pauline_kael.json"
    ebert_file = personas_dir / "roger_ebert.json"
    siskel_file = personas_dir / "gene_siskel.json"

    # Generate reviews for each critic
    print("Generating synthetic film reviews...")
    print("-" * 60)

    kael_reviews = generate_kael_reviews()
    print(f"Generated {len(kael_reviews)} Pauline Kael reviews")

    ebert_reviews = generate_ebert_reviews()
    print(f"Generated {len(ebert_reviews)} Roger Ebert reviews")

    siskel_reviews = generate_siskel_reviews()
    print(f"Generated {len(siskel_reviews)} Gene Siskel reviews")

    print("-" * 60)
    print("Updating persona files...")
    print("-" * 60)

    # Update persona files
    update_persona_file(kael_file, kael_reviews)
    update_persona_file(ebert_file, ebert_reviews)
    update_persona_file(siskel_file, siskel_reviews)

    print("-" * 60)
    print("SUCCESS: All persona files updated with expanded review data")
    print(f"Total reviews generated: {len(kael_reviews) + len(ebert_reviews) + len(siskel_reviews)}")


if __name__ == "__main__":
    main()
