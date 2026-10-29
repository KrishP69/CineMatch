/**
 * CineMatch API Client
 * Connects to the Flask backend ML recommender & OTT service.
 */

const API_BASE = import.meta.env.VITE_API_URL || '/api';

async function fetchJSON(url, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${url}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      throw new Error(errBody.error || `Request failed with status ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    console.error(`API Error on ${url}:`, error);
    throw error;
  }
}

export const api = {
  // Check API & Recommender Health
  getHealth: () => fetchJSON('/health'),

  // Curated Homepage & Hero
  getFeatured: () => fetchJSON('/featured'),

  // Movie list with optional filters
  getMovies: (params = {}) => {
    const qs = new URLSearchParams();
    if (params.genre) qs.append('genre', params.genre);
    if (params.year) qs.append('year', params.year);
    if (params.min_rating) qs.append('min_rating', params.min_rating);
    if (params.sort_by) qs.append('sort_by', params.sort_by);
    if (params.page) qs.append('page', params.page);
    if (params.per_page) qs.append('per_page', params.per_page);
    return fetchJSON(`/movies?${qs.toString()}`);
  },

  // Detailed movie metadata
  getMovieDetail: (id, country = 'IN') => fetchJSON(`/movies/${id}?country=${country}`),

  // Instant multi-attribute search
  searchMovies: (query, params = {}) => {
    const qs = new URLSearchParams();
    qs.append('q', query);
    if (params.genre) qs.append('genre', params.genre);
    if (params.min_rating) qs.append('min_rating', params.min_rating);
    if (params.sort_by) qs.append('sort_by', params.sort_by);
    if (params.limit) qs.append('limit', params.limit);
    return fetchJSON(`/search?${qs.toString()}`);
  },

  // Distinct genres with counts
  getGenres: () => fetchJSON('/genres'),

  // Content-Based ML Recommender for single movie
  getSimilarMovies: (id, count = 10) => fetchJSON(`/recommend/${id}?count=${count}`),

  // Personalized Content-Based ML Recommender from taste profile
  getPersonalizedRecommendations: ({ liked_movie_ids = [], watched_movie_ids = [], favorite_genres = [], count = 12 }) =>
    fetchJSON('/recommend/personalized', {
      method: 'POST',
      body: JSON.stringify({
        liked_movie_ids,
        watched_movie_ids,
        favorite_genres,
        count,
      }),
    }),

  // Legal OTT watch providers (Subscription, Rent, Buy)
  getWatchProviders: (id, country = 'IN') => fetchJSON(`/watch-providers/${id}?country=${country}`),
};
