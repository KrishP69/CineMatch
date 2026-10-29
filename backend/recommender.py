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


# Singleton instance
recommender = MovieRecommender()
