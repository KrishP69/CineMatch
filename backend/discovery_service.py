"""
CineMatch Personalized Movie Discovery Service
Supports rich multi-filter inputs:
  - 13 Genres
  - 10 Moods
  - 10 'Feel Like Watching' Themes
  - Language, Runtime, Release Year, Minimum Rating, Streaming Platform
  - Dynamic Semantic Feature Mapping & Explainability
  - Negative Filtering (Watched / Disliked)
"""

import json
import logging
from database import get_db
from movie_service import movie_service
from ott_service import ott_service

logger = logging.getLogger(__name__)

# Semantic Mood-to-Metadata & Keyword Affinities
MOOD_MAP = {
    "Happy": ["feel-good", "comedy", "uplifting", "lighthearted", "fun", "friendship", "laughter"],
    "Sad": ["tragedy", "tearjerker", "emotional", "loss", "grief", "melancholy", "heartbreaking"],
    "Romantic": ["love", "romance", "couple", "passion", "relationship", "dating", "soulmates"],
    "Dark": ["dark", "gritty", "noir", "cynical", "gloomy", "bleak", "murder", "corruption"],
    "Suspenseful": ["suspense", "tension", "thriller", "edge of your seat", "mystery", "investigation"],
    "Exciting": ["action", "adrenaline", "blockbuster", "adventure", "chase", "explosive", "heroic"],
    "Relaxing": ["gentle", "calm", "wholesome", "peaceful", "slice of life", "nature", "warm"],
    "Inspiring": ["inspirational", "triumph", "overcoming adversity", "biography", "hope", "courage"],
    "Emotional": ["deep emotion", "family", "drama", "poignant", "bittersweet", "human connection"],
    "Mind-bending": ["plot twist", "nonlinear", "mind-bending", "psychological", "puzzle", "simulation", "time travel", "philosophical"]
}

# 'What Do You Feel Like Watching?' Semantic Concepts
THEME_MAP = {
    "Plot twists": ["twist ending", "unexpected", "revelation", "deception", "secret", "shyamalan"],
    "Psychological thrillers": ["psychological", "paranoia", "insanity", "manipulation", "mind games", "obsession"],
    "Mind-bending stories": ["reality", "multiverse", "dream", "consciousness", "existential", "quantum", "inception"],
    "Feel-good movies": ["wholesome", "heartwarming", "feel good", "joy", "cheerful", "triumph"],
    "Survival stories": ["survival", "wilderness", "stranded", "disaster", "apocalypse", "endurance", "against all odds"],
    "Mystery investigations": ["detective", "investigation", "clues", "whodunit", "crime scene", "sherlock"],
    "Underrated movies": ["cult classic", "sleeper hit", "indie gem", "overlooked", "hidden treasure"],
    "Intense action": ["high octane", "martial arts", "gunplay", "car chase", "combat", "explosions"],
    "Emotional storytelling": ["character study", "coming of age", "redemption", "tears", "profound", "family bond"],
    "Dark atmosphere": ["rain-soaked", "shadows", "dystopian", "macabre", "gothic", "neo-noir"]
}

class DiscoveryService:
    def discover_movies(
        self,
        genres=None,
        moods=None,
        themes=None,
        min_rating=0.0,
        release_year_min=1900,
        release_year_max=2030,
        max_runtime=None,
        min_runtime=None,
        language="Any",
        streaming_platform=None,
        exclude_ids=None,
        liked_ids=None,
        sort_by="relevance",
        page=1,
        per_page=18
    ):
        genres = [g.strip() for g in (genres or []) if g.strip()]
        moods = [m.strip() for m in (moods or []) if m.strip()]
        themes = [t.strip() for t in (themes or []) if t.strip()]
        exclude_set = set(int(i) for i in (exclude_ids or []) if str(i).isdigit())
        liked_set = set(int(i) for i in (liked_ids or []) if str(i).isdigit())

        candidates = []
        for m in movie_service.movies:
            mid = int(m["id"])
            if mid in exclude_set:
                continue

            # Rating filter
            vote_avg = float(m.get("vote_average", 0.0))
            if vote_avg < min_rating:
                continue

            # Year filter
            year = int(m.get("release_year") or (m.get("release_date", "2000")[:4]))
            if not (release_year_min <= year <= release_year_max):
                continue

            # Runtime filter
            runtime = int(m.get("runtime", 120))
            if min_runtime and runtime < min_runtime:
                continue
            if max_runtime and runtime > max_runtime:
                continue

            # Language filter
            if language and language != "Any":
                original_lang = m.get("original_language", "en")
                if language.lower() not in [original_lang.lower(), m.get("language", "").lower()]:
                    continue

            # Streaming provider filter
            if streaming_platform and streaming_platform != "Any":
                plat_needle = streaming_platform.lower()
                bundled_wp = m.get("watch_providers", {})
                country_bundle = bundled_wp.get("IN", {}) if isinstance(bundled_wp, dict) else {}
                flatrate_names = [p.get("name", "").lower() for p in country_bundle.get("flatrate", [])]
                rent_names = [p.get("name", "").lower() for p in country_bundle.get("rent", [])]
                buy_names = [p.get("name", "").lower() for p in country_bundle.get("buy", [])]
                all_providers = flatrate_names + rent_names + buy_names
                if not any(plat_needle in prov or prov in plat_needle for prov in all_providers):
                    continue

            # Calculate Semantic Multi-Factor Score
            score = 0.5 # Baseline
            matched_aspects = []

            # 1. Genre match
            movie_genres = m.get("genres", [])
            if genres:
                matched_genres = [g for g in genres if any(g.lower() == mg.lower() for mg in movie_genres)]
                if matched_genres:
                    genre_weight = len(matched_genres) / len(genres)
                    score += genre_weight * 0.35
                    matched_aspects.append(f"Genres ({', '.join(matched_genres)})")
                else:
                    score -= 0.15

            # 2. Mood match via metadata soup & keywords
            soup = (m.get("metadata_soup", "") + " " + m.get("overview", "")).lower()
            if moods:
                matched_moods = []
                for mood in moods:
                    keywords = MOOD_MAP.get(mood, [mood.lower()])
                    if any(kw in soup for kw in keywords):
                        matched_moods.append(mood)
                if matched_moods:
                    score += (len(matched_moods) / len(moods)) * 0.25
                    matched_aspects.append(f"Mood ({', '.join(matched_moods)})")

            # 3. Theme / 'Feel like watching' match
            if themes:
                matched_themes = []
                for theme in themes:
                    keywords = THEME_MAP.get(theme, [theme.lower()])
                    if any(kw in soup for kw in keywords):
                        matched_themes.append(theme)
                if matched_themes:
                    score += (len(matched_themes) / len(themes)) * 0.25
                    matched_aspects.append(f"Theme: {', '.join(matched_themes)}")

            # 4. High ratings & popularity signal
            quality_boost = (vote_avg / 10.0) * 0.15
            score += quality_boost

            # 5. Liked synergy
            if mid in liked_set:
                score += 0.10

            # Normalize match percentage (65% to 99%)
            display_match = min(0.99, max(0.65, 0.60 + score * 0.25))

            # Compose human-explainable reason
            if matched_aspects:
                reason = f"Recommended because you selected {' + '.join(matched_aspects)}."
            elif genres:
                reason = f"Curated match matching your genre tastes in {', '.join(movie_genres[:2])}."
            else:
                reason = f"High-affinity match based on your preferences and quality ratings."

            m_copy = dict(m)
            m_copy["discovery_score"] = round(float(score), 4)
            m_copy["similarity_score"] = round(display_match, 4)
            m_copy["recommendation_reason"] = reason

            candidates.append(m_copy)

        # Sorting
        if sort_by == "rating":
            candidates.sort(key=lambda x: x.get("vote_average", 0), reverse=True)
        elif sort_by == "release_date":
            candidates.sort(key=lambda x: x.get("release_date", ""), reverse=True)
        elif sort_by == "popularity":
            candidates.sort(key=lambda x: x.get("popularity", 0), reverse=True)
        else: # relevance
            candidates.sort(key=lambda x: x["discovery_score"], reverse=True)

        total_count = len(candidates)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_results = candidates[start_idx:end_idx]

        for m_res in paginated_results:
            bundled_wp = m_res.get("watch_providers", {})
            in_bundle = bundled_wp.get("IN") if isinstance(bundled_wp, dict) else None
            if in_bundle:
                m_res["watch_providers"] = {
                    "subscription": in_bundle.get("flatrate", []),
                    "rent": in_bundle.get("rent", []),
                    "buy": in_bundle.get("buy", []),
                    "has_availability": True,
                    "source": "Catalogue Pre-indexed"
                }
            else:
                m_res["watch_providers"] = {
                    "subscription": [],
                    "rent": [],
                    "buy": [],
                    "has_availability": False,
                    "source": "Catalogue Pre-indexed"
                }

        return {
            "total": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_count + per_page - 1) // per_page,
            "movies": paginated_results
        }

discovery_service = DiscoveryService()

