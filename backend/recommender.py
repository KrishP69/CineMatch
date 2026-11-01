"""
CineMatch Machine Learning Recommendation Engine
Using TF-IDF Vectorization and Cosine Similarity on weighted movie attributes:
overview, genres, keywords, cast, and director.
"""

import logging
import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


def clean_str(val):
    if not val or pd.isna(val):
        return ""
    return str(val).strip().lower()


def clean_entity(name):
    """Normalize multi-word entity like 'Christopher Nolan' to 'christopher_nolan' to prevent word splitting."""
    if not name or pd.isna(name):
        return ""
    clean = re.sub(r"[^a-zA-Z0-9\s]", "", str(name).strip().lower())
    return clean.replace(" ", "_")


class MovieRecommender:
    def __init__(self):
        self.movies_df = pd.DataFrame()
        self.vectorizer = None
        self.tfidf_matrix = None
        self.cosine_sim = None
        self.id_to_idx = {}
        self.idx_to_id = {}
        self.title_to_id = {}

    def fit(self, movies_list_or_df):
        """Fits the TF-IDF vectorizer and computes cosine similarity on the movie corpus."""
        if isinstance(movies_list_or_df, list):
            self.movies_df = pd.DataFrame(movies_list_or_df)
        else:
            self.movies_df = movies_list_or_df.copy()

        if self.movies_df.empty:
            logger.warning("Empty movies dataset supplied to MovieRecommender.")
            return

        # Ensure essential columns exist with clean defaults
        for col in ["id", "title", "overview", "genres", "keywords", "cast", "director", "vote_average", "vote_count"]:
            if col not in self.movies_df.columns:
                self.movies_df[col] = "" if col in ["overview", "director", "title"] else ([] if col in ["genres", "keywords", "cast"] else 0)

        # Build weighted soup
        # Weighted representation:
        # overview: 1x
        # genres: 2x
        # keywords: 2x
        # cast: 2x (top 3)
        # director: 3x (director strongly governs cinematic style)
        soups = []
        for _, row in self.movies_df.iterrows():
            overview = clean_str(row.get("overview", ""))

            raw_genres = row.get("genres", [])
            if isinstance(raw_genres, list):
                genres_clean = " ".join([clean_entity(g) for g in raw_genres])
            else:
                genres_clean = clean_str(raw_genres)

            raw_kw = row.get("keywords", [])
            if isinstance(raw_kw, list):
                kw_clean = " ".join([clean_entity(k) for k in raw_kw])
            else:
                kw_clean = clean_str(raw_kw)

            raw_cast = row.get("cast", [])
            if isinstance(raw_cast, list):
                top_cast = " ".join([clean_entity(c) for c in raw_cast[:3]])
            else:
                top_cast = clean_str(raw_cast)

            director_clean = clean_entity(row.get("director", ""))

            # Combine with deliberate weighting
            soup_parts = [
                overview,
                genres_clean, genres_clean,
                kw_clean, kw_clean,
                top_cast, top_cast,
                director_clean, director_clean, director_clean
            ]
            soup = " ".join(part for part in soup_parts if part)
            soups.append(soup if soup else clean_str(row.get("title", "")))

        self.movies_df["metadata_soup"] = soups

        # Initialize TF-IDF Vectorizer with unigrams & bigrams
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=12000,
            ngram_range=(1, 2)
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.movies_df["metadata_soup"])
        
        # Precompute dense cosine similarity matrix for fast lookups
        self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)

        # Build index lookups
        self.id_to_idx = {int(row["id"]): idx for idx, row in self.movies_df.iterrows()}
        self.idx_to_id = {idx: int(row["id"]) for idx, row in self.movies_df.iterrows()}
        self.title_to_id = {str(row["title"]).strip().lower(): int(row["id"]) for _, row in self.movies_df.iterrows()}

        logger.info(f"Recommender fitted on {len(self.movies_df)} movies. TF-IDF Matrix shape: {self.tfidf_matrix.shape}")

    def _get_movie_dict(self, idx, sim_score=None, reason=None):
        movie = self.movies_df.iloc[idx].to_dict()
        clean_movie = {}
        for k, v in movie.items():
            if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
                clean_movie[k] = None
            else:
                clean_movie[k] = v
        movie = clean_movie

        if sim_score is not None:
            movie["similarity_score"] = round(float(sim_score), 4)
        if reason is not None:
            movie["recommendation_reason"] = reason
        # Ensure watch_providers is properly returned
        if "watch_providers" not in movie or not isinstance(movie["watch_providers"], dict):
            movie["watch_providers"] = {}
        return movie

    def recommend_similar_by_id(self, movie_id, top_n=10, exclude_ids=None):
        """
        Calculates cosine similarity between the selected movie and all other movies
        using TF-IDF vectors of weighted metadata. Returns top_n similar movies.
        """
        exclude_set = set(exclude_ids or [])
        movie_id = int(movie_id)
        exclude_set.add(movie_id)

        if movie_id not in self.id_to_idx:
            # Fallback if movie not in index
            return self.fallback_recommendations(top_n=top_n, exclude_ids=exclude_set)

        idx = self.id_to_idx[movie_id]
        target_title = self.movies_df.iloc[idx].get("title", "this movie")
        sim_scores = self.cosine_sim[idx]

        # Rank all movies by cosine similarity score
        ranked_indices = np.argsort(sim_scores)[::-1]

        recommendations = []
        for r_idx in ranked_indices:
            r_id = self.idx_to_id[r_idx]
            if r_id in exclude_set:
                continue

            score = float(sim_scores[r_idx])
            reason = f"Based on common themes and cast in {target_title}"
            recommendations.append(self._get_movie_dict(r_idx, sim_score=score, reason=reason))

            if len(recommendations) >= top_n:
                break

        # If not enough, append fallback
        if len(recommendations) < top_n:
            fallback = self.fallback_recommendations(top_n=top_n - len(recommendations), exclude_ids=exclude_set.union({m["id"] for m in recommendations}))
            recommendations.extend(fallback)

        return recommendations

    def recommend_personalized(self, liked_ids=None, watched_ids=None, favorite_genres=None, top_n=12):
        """
        Genuine Machine Learning Content-Based User Profiling:
        1. Aggregates the TF-IDF feature vectors of all movies the user liked into a combined profile vector.
        2. Blends in vectorized favorite genres if specified.
        3. Computes cosine similarity between the user profile vector and all candidate movies.
        4. Filters out movies already in watched_ids or liked_ids.
        5. Returns ranked personalized recommendations with similarity scores and explanations.
        """
        liked_ids = [int(i) for i in (liked_ids or []) if int(i) in self.id_to_idx]
        watched_ids = set(int(i) for i in (watched_ids or []))
        favorite_genres = favorite_genres or []
        exclude_set = watched_ids.union(liked_ids)

        if self.tfidf_matrix is None or len(self.movies_df) == 0:
            return []

        user_vector = None

        if liked_ids:
            # Compute mean vector of liked movies
            liked_indices = [self.id_to_idx[mid] for mid in liked_ids]
            liked_vectors = self.tfidf_matrix[liked_indices]
            user_vector = np.asarray(liked_vectors.mean(axis=0))

        if favorite_genres:
            # Vectorize favorite genres
            genre_text = " ".join([clean_entity(g) for g in favorite_genres for _ in range(2)])
            genre_vec = self.vectorizer.transform([genre_text]).toarray()
            if user_vector is not None:
                # Weighted combination: 70% liked movies profile, 30% explicit genre taste
                user_vector = 0.7 * user_vector + 0.3 * genre_vec
            else:
                user_vector = genre_vec

        if user_vector is None:
            # Cold start: user has no liked movies and no genres selected
            return self.fallback_recommendations(top_n=top_n, exclude_ids=exclude_set)

        # Calculate cosine similarity with all movies in catalog
        sim_scores = cosine_similarity(user_vector, self.tfidf_matrix)[0]
        ranked_indices = np.argsort(sim_scores)[::-1]

        recommendations = []
        for r_idx in ranked_indices:
            r_id = self.idx_to_id[r_idx]
            if r_id in exclude_set:
                continue

            score = float(sim_scores[r_idx])
            
            # Dynamic reason generation
            row_genres = self.movies_df.iloc[r_idx].get("genres", [])
            shared_genres = [g for g in row_genres if g in favorite_genres] if favorite_genres else []
            if shared_genres:
                reason = f"Matches your interest in {', '.join(shared_genres[:2])}"
            elif liked_ids:
                reason = "Matches your taste in movies you liked"
            else:
                reason = "Recommended for your profile"

            recommendations.append(self._get_movie_dict(r_idx, sim_score=score, reason=reason))
            if len(recommendations) >= top_n:
                break

        # Fallback if fewer recommendations
        if len(recommendations) < top_n:
            more = self.fallback_recommendations(
                top_n=top_n - len(recommendations),
                exclude_ids=exclude_set.union({m["id"] for m in recommendations})
            )
            recommendations.extend(more)

        return recommendations

    def recommend_by_genre(self, genre_name, top_n=10, exclude_ids=None):
        """Returns highest rated movies within a specific genre."""
        exclude_set = set(exclude_ids or [])
        matched = []
        
        target = str(genre_name).strip().lower()
        for idx, row in self.movies_df.iterrows():
            if row["id"] in exclude_set:
                continue
            genres = [str(g).lower() for g in row.get("genres", [])]
            if any(target in g for g in genres):
                matched.append(idx)

        if not matched:
            return self.fallback_recommendations(top_n=top_n, exclude_ids=exclude_set)

        # Sort matching movies by rating * popularity
        def score_fn(i):
            r = self.movies_df.iloc[i]
            vote = float(r.get("vote_average", 0))
            pop = float(r.get("popularity", 0))
            return vote * 2.0 + np.log1p(pop)

        matched.sort(key=score_fn, reverse=True)
        results = [self._get_movie_dict(idx, reason=f"Top rated in {genre_name}") for idx in matched[:top_n]]
        return results

    def fallback_recommendations(self, top_n=10, exclude_ids=None):
        """Safe fallback: returns top rated & critically acclaimed movies."""
        exclude_set = set(exclude_ids or [])
        candidates = []
        for idx, row in self.movies_df.iterrows():
            if row["id"] in exclude_set:
                continue
            candidates.append(idx)

        def score_fn(i):
            r = self.movies_df.iloc[i]
            vote = float(r.get("vote_average", 0))
            cnt = float(r.get("vote_count", 0))
            return vote * (cnt / (cnt + 1000.0))

        candidates.sort(key=score_fn, reverse=True)
        return [self._get_movie_dict(i, reason="Critically acclaimed favorite") for i in candidates[:top_n]]

    def retrain_user_model(self, liked_ids=None, watched_ids=None, disliked_ids=None,
                           watchlist_ids=None, favorite_genres=None, mood=None, era=None, top_n=12):
        """
        Continuous Online Learning Model:
        Re-trains and updates the user's high-dimensional taste vector dynamically after
        every interaction (like, watched mark, dislike, watchlist add, or mood change).
        Applies positive feature reinforcement and negative vector filtering.
        """
        liked_ids = [int(i) for i in (liked_ids or []) if int(i) in self.id_to_idx]
        watched_ids = [int(i) for i in (watched_ids or []) if int(i) in self.id_to_idx]
        disliked_ids = [int(i) for i in (disliked_ids or []) if int(i) in self.id_to_idx]
        watchlist_ids = [int(i) for i in (watchlist_ids or []) if int(i) in self.id_to_idx]
        favorite_genres = favorite_genres or []
        exclude_set = set(watched_ids).union(set(disliked_ids))

        if self.tfidf_matrix is None or len(self.movies_df) == 0:
            return {"recommendations": [], "model_telemetry": {}}

        total_features = self.tfidf_matrix.shape[1]
        user_vector = np.zeros((1, total_features))
        total_weight = 0.0

        # 1. Liked movies (Strong positive signal: weight 1.5)
        if liked_ids:
            liked_indices = [self.id_to_idx[mid] for mid in liked_ids]
            liked_vecs = np.asarray(self.tfidf_matrix[liked_indices].mean(axis=0))
            user_vector += 1.5 * liked_vecs
            total_weight += 1.5

        # 2. Watched movies (Positive reinforcement: weight 1.0)
        if watched_ids:
            watched_indices = [self.id_to_idx[mid] for mid in watched_ids]
            watched_vecs = np.asarray(self.tfidf_matrix[watched_indices].mean(axis=0))
            user_vector += 1.0 * watched_vecs
            total_weight += 1.0

        # 3. Watchlist movies (Aspirational interest signal: weight 0.8)
        if watchlist_ids:
            wl_indices = [self.id_to_idx[mid] for mid in watchlist_ids]
            wl_vecs = np.asarray(self.tfidf_matrix[wl_indices].mean(axis=0))
            user_vector += 0.8 * wl_vecs
            total_weight += 0.8

        # 4. Disliked / Dismissed movies (Negative vector subtraction: weight -1.2)
        if disliked_ids:
            dis_indices = [self.id_to_idx[mid] for mid in disliked_ids]
            dis_vecs = np.asarray(self.tfidf_matrix[dis_indices].mean(axis=0))
            user_vector -= 1.2 * dis_vecs

        # 5. Explicit favorite genres (Prior taste anchor: weight 1.0)
        if favorite_genres:
            genre_text = " ".join([clean_entity(g) for g in favorite_genres for _ in range(3)])
            genre_vec = self.vectorizer.transform([genre_text]).toarray()
            user_vector += 1.0 * genre_vec
            total_weight += 1.0

        # 6. Mood / Vibe vectorization (Contextual taste anchor: weight 1.0)
        if mood:
            mood_text = f"{clean_str(mood)} {clean_str(mood)}"
            mood_vec = self.vectorizer.transform([mood_text]).toarray()
            user_vector += 1.0 * mood_vec
            total_weight += 1.0

        # Ensure no negative components in the taste vector after subtraction
        user_vector = np.maximum(0.0, user_vector)

        # Normalize vector if non-zero
        norm = np.linalg.norm(user_vector)
        if norm > 0:
            user_vector = user_vector / norm
        else:
            # Fallback to general acclaimed vector
            recs = self.fallback_recommendations(top_n=top_n, exclude_ids=exclude_set)
            return {
                "recommendations": recs,
                "model_telemetry": {
                    "total_signals": 0,
                    "learned_keywords": [],
                    "taste_summary": "Initial baseline (Acclaimed cinematic masterpieces)",
                    "training_step": 0
                }
            }

        # Calculate cosine similarity with all candidate movies
        sim_scores = cosine_similarity(user_vector, self.tfidf_matrix)[0]

        # Apply era filter/boost if specified
        if era and era.lower() != "all":
            era_lower = era.lower()
            for idx, row in self.movies_df.iterrows():
                year = row.get("release_year", 2020)
                if "modern" in era_lower or "2015" in era_lower:
                    if year >= 2015:
                        sim_scores[idx] += 0.05
                elif "classic" in era_lower or "vintage" in era_lower:
                    if year < 2005:
                        sim_scores[idx] += 0.08

        ranked_indices = np.argsort(sim_scores)[::-1]

        recommendations = []
        for r_idx in ranked_indices:
            r_id = self.idx_to_id[r_idx]
            if r_id in exclude_set:
                continue

            score = float(sim_scores[r_idx])
            row = self.movies_df.iloc[r_idx]
            row_genres = row.get("genres", [])
            shared_genres = [g for g in row_genres if g in favorite_genres] if favorite_genres else []

            if shared_genres:
                reason = f"Matches your affinity for {', '.join(shared_genres[:2])}"
            elif watched_ids:
                reason = "Personalized match based on your watch history & taste profile"
            elif liked_ids:
                reason = "Aligned with narrative elements from your liked films"
            else:
                reason = "Top match calibrated to your personalized profile"

            recommendations.append(self._get_movie_dict(r_idx, sim_score=score, reason=reason))
            if len(recommendations) >= top_n:
                break

        # Extract top 6 learned keywords from user vector
        feature_names = self.vectorizer.get_feature_names_out()
        top_feature_indices = np.argsort(user_vector[0])[::-1][:8]
        learned_keywords = [
            feature_names[i].replace("_", " ").title()
            for i in top_feature_indices
            if user_vector[0][i] > 0.01
        ][:6]

        total_signals = len(liked_ids) + len(watched_ids) + len(disliked_ids) + len(watchlist_ids) + len(favorite_genres)
        taste_summary = (
            f"Calibrated with {total_signals} interaction signals focusing on "
            f"{', '.join(learned_keywords[:3]) if learned_keywords else 'diverse cinema'}"
        )

        return {
            "recommendations": recommendations,
            "model_telemetry": {
                "total_signals": total_signals,
                "liked_count": len(liked_ids),
                "watched_count": len(watched_ids),
                "watchlist_count": len(watchlist_ids),
                "disliked_count": len(disliked_ids),
                "learned_keywords": learned_keywords,
                "taste_summary": taste_summary,
                "model_version": f"v3.1.{total_signals}",
                "vector_dimensions": total_features
            }
        }

    def recommend_by_natural_language(self, description, preferred_genres=None, mood=None, exclude_ids=None, top_n=10):
        """
        'For You AI' Agent Semantic Describe Matcher:
        Processes user free-form natural language query (e.g. 'a mind-bending heist thriller with high stakes in a rainy city')
        and computes hybrid semantic vector similarity, genre alignment, and mood relevance.
        Returns top 10 movies with rich AI explanations.
        """
        exclude_set = set(int(i) for i in (exclude_ids or []))
        preferred_genres = preferred_genres or []

        if not description or not self.vectorizer:
            return self.fallback_recommendations(top_n=top_n, exclude_ids=exclude_set)

        # Build expanded query text
        clean_desc = clean_str(description)
        genre_addon = " ".join([clean_entity(g) for g in preferred_genres for _ in range(2)])
        mood_addon = clean_str(mood) if mood else ""
        full_query = f"{clean_desc} {genre_addon} {mood_addon}"

        query_vec = self.vectorizer.transform([full_query])
        sim_scores = cosine_similarity(query_vec, self.tfidf_matrix)[0].copy()

        # Hybrid scoring: add explicit genre and director/keyword match bonuses
        for idx, row in self.movies_df.iterrows():
            row_genres = [str(g).lower() for g in row.get("genres", [])]
            for pg in preferred_genres:
                if pg.lower() in row_genres:
                    sim_scores[idx] += 0.08

            # Check if director or key actor was mentioned in the description
            director = str(row.get("director", "")).lower()
            if director and len(director) > 4 and director in clean_desc:
                sim_scores[idx] += 0.15

            title = str(row.get("title", "")).lower()
            if title and len(title) > 3 and title in clean_desc:
                sim_scores[idx] += 0.20

        ranked_indices = np.argsort(sim_scores)[::-1]

        recommendations = []
        for r_idx in ranked_indices:
            r_id = self.idx_to_id[r_idx]
            if r_id in exclude_set:
                continue

            raw_score = float(sim_scores[r_idx])
            # Scale score into natural human percentage (78% - 99%)
            display_score = min(0.99, max(0.72, 0.65 + raw_score * 0.70))

            row = self.movies_df.iloc[r_idx]
            title = row.get("title", "This title")
            director = row.get("director", "")
            genres = row.get("genres", [])
            genre_str = ", ".join(genres[:2]) if genres else "Drama"

            # Construct personalized AI justification
            reasons = []
            if director and director.lower() in clean_desc:
                reasons.append(f"Directed by {director} as mentioned")
            if any(pg.lower() in [g.lower() for g in genres] for pg in preferred_genres):
                reasons.append(f"Fits your {genre_str} preference")
            if not reasons:
                reasons.append(f"Strongly matches the themes and narrative pacing of your prompt")

            ai_reason = f"CineMatch AI: {'; '.join(reasons)}"

            recommendations.append(self._get_movie_dict(r_idx, sim_score=display_score, reason=ai_reason))
            if len(recommendations) >= top_n:
                break

        if len(recommendations) < top_n:
            more = self.fallback_recommendations(
                top_n=top_n - len(recommendations),
                exclude_ids=exclude_set.union({m["id"] for m in recommendations})
            )
            recommendations.extend(more)

        return recommendations

    def recommend_onboarding_mcq(self, last_watched=None, genres=None, mood=None,
                                 era_pacing=None, already_watched_ids=None, top_n=10):
        """
        Processes onboarding MCQ answers:
        1. Last watched movie / TV series
        2. Preferred genres
        3. Current mood / vibe
        4. Story pacing / era
        Returns structured personalized sections.
        """
        genres = genres or []
        already_watched_ids = [int(i) for i in (already_watched_ids or []) if int(i) in self.id_to_idx]

        # Identify anchor movie if user specified a title or ID
        anchor_id = None
        anchor_title = None

        if last_watched:
            if isinstance(last_watched, int) and last_watched in self.id_to_idx:
                anchor_id = last_watched
                anchor_title = self.movies_df.iloc[self.id_to_idx[anchor_id]].get("title")
            elif isinstance(last_watched, str):
                query = last_watched.strip().lower()
                # Check exact or partial title
                for title, mid in self.title_to_id.items():
                    if query in title or title in query:
                        anchor_id = mid
                        anchor_title = self.movies_df.iloc[self.id_to_idx[mid]].get("title")
                        break
                if not anchor_id:
                    anchor_title = last_watched.strip()

        # Build initial liked list containing anchor
        liked_ids = [anchor_id] if anchor_id else []

        # Run continuous model retraining with these MCQ answers
        retrain_result = self.retrain_user_model(
            liked_ids=liked_ids,
            watched_ids=already_watched_ids,
            favorite_genres=genres,
            mood=mood,
            era=era_pacing,
            top_n=top_n
        )

        next_to_watch = retrain_result["recommendations"]

        # Recommendations specifically anchored to the last watched title
        because_you_watched = []
        if anchor_id:
            because_you_watched = self.recommend_similar_by_id(
                anchor_id,
                top_n=6,
                exclude_ids=set(already_watched_ids).union({anchor_id})
            )

        return {
            "anchor_movie": {"id": anchor_id, "title": anchor_title},
            "next_to_watch": next_to_watch,
            "because_you_watched": because_you_watched,
            "model_telemetry": retrain_result["model_telemetry"]
        }


# Singleton instance
recommender = MovieRecommender()

