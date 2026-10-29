"""
CineMatch Movie Catalog Service
Provides search, filtering, genre extraction, curated homepage sections,
and fallback logic for missing data.
"""

import json
import os
import logging
import pandas as pd
from recommender import recommender

logger = logging.getLogger(__name__)

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "movies.json")


class MovieService:
    def __init__(self):
        self.movies = []
        self.movies_dict = {}
        self.load_data()

    def load_data(self):
        """Loads bundled JSON dataset and initializes ML recommender."""
        if not os.path.exists(DATA_PATH):
            logger.error(f"Movie dataset not found at {DATA_PATH}")
            return

        with open(DATA_PATH, "r", encoding="utf-8") as f:
            self.movies = json.load(f)

        self.movies_dict = {int(m["id"]): m for m in self.movies}
        
        # Fit the TF-IDF and Cosine Similarity recommender engine
        recommender.fit(self.movies)
        logger.info(f"Loaded {len(self.movies)} movies into catalog.")

    def get_movie_by_id(self, movie_id):
        """Fetches a single movie record with all metadata."""
        try:
            mid = int(movie_id)
            return self.movies_dict.get(mid)
        except (ValueError, TypeError):
            return None

    def get_all_movies(self, genre=None, year=None, min_rating=None, sort_by="popularity", page=1, per_page=24):
        """Filters, sorts and paginates movies."""
        filtered = list(self.movies)

        if genre and genre.lower() != "all":
            g_target = genre.lower()
            filtered = [m for m in filtered if any(g_target in g.lower() for g in m.get("genres", []))]

        if year:
            try:
                y = int(year)
                filtered = [m for m in filtered if m.get("release_year") == y]
            except ValueError:
                pass

        if min_rating is not None:
            try:
                mr = float(min_rating)
                filtered = [m for m in filtered if float(m.get("vote_average", 0)) >= mr]
            except ValueError:
                pass

        # Sorting
        if sort_by == "rating":
            filtered.sort(key=lambda m: float(m.get("vote_average", 0)), reverse=True)
        elif sort_by == "release_date" or sort_by == "year":
            filtered.sort(key=lambda m: str(m.get("release_date", "")), reverse=True)
        elif sort_by == "title":
            filtered.sort(key=lambda m: str(m.get("title", "")).lower())
        else:  # default popularity
            filtered.sort(key=lambda m: float(m.get("popularity", 0)), reverse=True)

        total = len(filtered)
        start = (page - 1) * per_page
        end = start + per_page
        paginated = filtered[start:end]

        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page if per_page else 1,
            "movies": paginated
        }

    def search_movies(self, query, genre=None, min_rating=None, sort_by="relevance", limit=20):
        """
        Multi-attribute instant search matching title, actor, director, and keywords.
        """
        if not query or not query.strip():
            return self.get_all_movies(genre=genre, min_rating=min_rating, sort_by=sort_by, page=1, per_page=limit)

        q = query.strip().lower()
        scored_results = []

        for m in self.movies:
            # Apply filters first
            if genre and genre.lower() != "all":
                g_target = genre.lower()
                if not any(g_target in g.lower() for g in m.get("genres", [])):
                    continue

            if min_rating:
                try:
                    if float(m.get("vote_average", 0)) < float(min_rating):
                        continue
                except ValueError:
                    pass

            score = 0
            title = str(m.get("title", "")).lower()
            orig_title = str(m.get("original_title", "")).lower()
            director = str(m.get("director", "")).lower()
            cast = [str(c).lower() for c in m.get("cast", [])]
            keywords = [str(k).lower() for k in m.get("keywords", [])]
            overview = str(m.get("overview", "")).lower()

            # Exact title match
            if q == title or q == orig_title:
                score += 100
            elif title.startswith(q):
                score += 60
            elif q in title:
                score += 40

            # Director match
            if q in director:
                score += 35

            # Cast match
            for actor in cast:
                if q in actor:
                    score += 30
                    break

            # Keyword match
            for kw in keywords:
                if q in kw:
                    score += 15

            # Overview match
            if q in overview:
                score += 5

            if score > 0:
                scored_results.append((score, m))

        # Sort by score or chosen sort
        if sort_by == "rating":
            scored_results.sort(key=lambda x: float(x[1].get("vote_average", 0)), reverse=True)
        elif sort_by == "year":
            scored_results.sort(key=lambda x: str(x[1].get("release_date", "")), reverse=True)
        else:
            # Relevance + popularity boost
            scored_results.sort(key=lambda x: x[0] * 2 + float(x[1].get("popularity", 0)) * 0.1, reverse=True)

        results = [m for _, m in scored_results[:limit]]
        return {
            "query": query,
            "total": len(results),
            "movies": results
        }

    def get_genres(self):
        """Returns distinct genres with count of available movies."""
        counts = {}
        for m in self.movies:
            for g in m.get("genres", []):
                counts[g] = counts.get(g, 0) + 1

        genre_list = [{"id": g.lower().replace(" ", "-"), "name": g, "count": counts[g]} for g in sorted(counts.keys())]
        return genre_list

    def get_featured_content(self):
        """
        Constructs a cinematic homepage bundle:
        - Hero movie (high impact, visual, popular)
        - Curated horizontal shelf rows
        """
        # Hero candidate (Interstellar, Oppenheimer, Dune or Inception)
        hero_candidates = [157336, 872585, 27205, 438631, 155]
        hero = None
        for hid in hero_candidates:
            if hid in self.movies_dict:
                hero = self.movies_dict[hid]
                break
        if not hero and self.movies:
            hero = self.movies[0]

        # Trending Now: sorted by popularity
        trending = sorted(self.movies, key=lambda m: float(m.get("popularity", 0)), reverse=True)[:14]

        # Top Rated: sorted by vote_average
        top_rated = sorted(self.movies, key=lambda m: (float(m.get("vote_average", 0)), float(m.get("vote_count", 0))), reverse=True)[:14]

        # Hidden Gems: vote_average >= 8.0, high ratings
        hidden_gems = [m for m in self.movies if float(m.get("vote_average", 0)) >= 8.0]
        # sort by release year or distinct vibe
        hidden_gems.sort(key=lambda m: (m.get("release_year", 0), float(m.get("vote_average", 0))), reverse=True)
        hidden_gems = hidden_gems[4:18] if len(hidden_gems) > 10 else hidden_gems

        # Sci-Fi & Mind Benders
        scifi = [m for m in self.movies if "Science Fiction" in m.get("genres", []) or "Mystery" in m.get("genres", [])][:14]

        # Action & Adrenaline
        action = [m for m in self.movies if "Action" in m.get("genres", [])][:14]

        # Indian Cinema Gems
        indian = [m for m in self.movies if any(kw in ["india", "bihar", "pune", "maharashtra", "haryana", "mahishmati kingdom", "british raj"] for kw in m.get("keywords", [])) or m.get("director") in ["S.S. Rajamouli", "Rajkumar Hirani", "Anurag Kashyap", "Sriram Raghavan", "Nitesh Tiwari", "Rahi Anil Barve", "Aditya Chopra"]][:14]

        # Award Winning Drama
        drama = [m for m in self.movies if "Drama" in m.get("genres", []) and float(m.get("vote_average", 0)) >= 8.1][:14]

        # Animation & Family
        animation = [m for m in self.movies if "Animation" in m.get("genres", [])][:14]

        return {
            "hero": hero,
            "sections": [
                {"id": "trending", "title": "Trending Now", "subtitle": "Most watched and popular titles right now", "movies": trending},
                {"id": "top_rated", "title": "Top Rated Masterpieces", "subtitle": "Highest rated films by global audiences & critics", "movies": top_rated},
                {"id": "scifi", "title": "Sci-Fi & Mind Benders", "subtitle": "Expand your consciousness across time & space", "movies": scifi},
                {"id": "indian_gems", "title": "Indian Cinema Gems", "subtitle": "Acclaimed blockbusters and cinematic milestones", "movies": indian},
                {"id": "hidden_gems", "title": "Hidden Gems & Modern Classics", "subtitle": "Overlooked cinematic treasures worth your time", "movies": hidden_gems},
                {"id": "action", "title": "High Octane & Adrenaline", "subtitle": "Action-packed spectacles and thrilling adventures", "movies": action},
                {"id": "drama", "title": "Critically Acclaimed Dramas", "subtitle": "Compelling human stories and powerful performances", "movies": drama},
                {"id": "animation", "title": "Animated Brilliance", "subtitle": "Visually stunning stories for all ages", "movies": animation}
            ]
        }


# Singleton instance
movie_service = MovieService()
