/**
 * CineMatch API Client
 * Connects to the Flask backend ML recommender, OTT service, Community, and Auth.
 */

const rawBase = (import.meta.env.VITE_API_URL || '').trim();
const API_BASE = rawBase
  ? (rawBase.endsWith('/api') ? rawBase : `${rawBase.replace(/\/+$/, '')}/api`)
  : '/api';

export function getAuthToken() {
  return localStorage.getItem('cinematch_token');
}

export function setAuthToken(token) {
  if (token) {
    localStorage.setItem('cinematch_token', token);
  } else {
    localStorage.removeItem('cinematch_token');
  }
}

async function fetchJSON(url, options = {}) {
  const token = getAuthToken();
  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};

  try {
    const res = await fetch(`${API_BASE}${url}`, {
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders,
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

  // Continuous Online Learning Model Retraining
  retrainModel: (payload) =>
    fetchJSON('/recommend/retrain', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // Onboarding Personalization MCQ
  submitOnboardingMCQ: (payload) =>
    fetchJSON('/recommend/onboarding', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // 'For You AI' Agent Semantic Describe Match
  aiDescribeMatch: (payload) =>
    fetchJSON('/ai/describe-match', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // Legal OTT watch providers (Subscription, Rent, Buy)
  getWatchProviders: (id, country = 'IN') => fetchJSON(`/watch-providers/${id}?country=${country}`),

  // Deep Neural Collaborative Filtering & Hardware Telemetry
  getModelStatus: () => fetchJSON('/model/status'),

  trainNeuralModel: () =>
    fetchJSON('/model/train', {
      method: 'POST',
    }),

  getNeuralRecommendations: ({ liked_ids = [], watched_ids = [], exclude_ids = [], top_n = 12 }) =>
    fetchJSON('/recommend/neural', {
      method: 'POST',
      body: JSON.stringify({
        liked_ids,
        watched_ids,
        exclude_ids,
        top_n,
      }),
    }),

  // -------------------------------------------------------------
  // AUTHENTICATION
  // -------------------------------------------------------------
  register: (username, email, password, avatar = '🎬') =>
    fetchJSON('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password, avatar }),
    }),

  login: (username_or_email, password) =>
    fetchJSON('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username_or_email, password }),
    }),

  getMe: () => fetchJSON('/auth/me'),

  // -------------------------------------------------------------
  // RATINGS & COMMUNITY REVIEWS
  // -------------------------------------------------------------
  getMovieRatings: (movieId) => fetchJSON(`/movies/${movieId}/ratings`),

  rateMovie: (movieId, rating) =>
    fetchJSON(`/movies/${movieId}/rating`, {
      method: 'POST',
      body: JSON.stringify({ rating }),
    }),

  deleteRating: (movieId) =>
    fetchJSON(`/movies/${movieId}/rating`, {
      method: 'DELETE',
    }),

  getMovieReviews: (movieId, sortBy = 'most_helpful', page = 1, perPage = 10) =>
    fetchJSON(`/movies/${movieId}/reviews?sort_by=${sortBy}&page=${page}&per_page=${perPage}`),

  submitReview: (movieId, { title, content, rating, contains_spoilers = false }) =>
    fetchJSON(`/movies/${movieId}/reviews`, {
      method: 'POST',
      body: JSON.stringify({ title, content, rating, contains_spoilers }),
    }),

  editReview: (reviewId, payload) =>
    fetchJSON(`/reviews/${reviewId}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),

  deleteReview: (reviewId) =>
    fetchJSON(`/reviews/${reviewId}`, {
      method: 'DELETE',
    }),

  voteReview: (reviewId, voteType) =>
    fetchJSON(`/reviews/${reviewId}/vote`, {
      method: 'POST',
      body: JSON.stringify({ vote_type: voteType }),
    }),

  reportReview: (reviewId, reason) =>
    fetchJSON(`/reviews/${reviewId}/report`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    }),

  // -------------------------------------------------------------
  // USER WATCHLIST & WATCH HISTORY
  // -------------------------------------------------------------
  toggleUserWatchlist: (movieId) =>
    fetchJSON(`/user/watchlist/${movieId}`, {
      method: 'POST',
    }),

  toggleUserWatched: (movieId) =>
    fetchJSON(`/user/watched/${movieId}`, {
      method: 'POST',
    }),

  getUserWatchlist: () => fetchJSON('/user/watchlist'),
  getUserWatched: () => fetchJSON('/user/watched'),
  getUserRatingsHistory: () => fetchJSON('/user/ratings'),

  // -------------------------------------------------------------
  // DISCOVERY SERVICE
  // -------------------------------------------------------------
  discoverMovies: (payload) =>
    fetchJSON('/discovery/recommend', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // -------------------------------------------------------------
  // DEDICATED TV / WEB SERIES SERVICE
  // -------------------------------------------------------------
  getTVShows: (params = {}) => {
    const qs = new URLSearchParams();
    if (params.genre) qs.append('genre', params.genre);
    if (params.min_rating) qs.append('min_rating', params.min_rating);
    if (params.sort_by) qs.append('sort_by', params.sort_by);
    if (params.page) qs.append('page', params.page);
    if (params.per_page) qs.append('per_page', params.per_page);
    return fetchJSON(`/tv?${qs.toString()}`);
  },

  getTVTrending: (page = 1, perPage = 20) =>
    fetchJSON(`/tv/trending?page=${page}&per_page=${perPage}`),

  getTVPopular: (page = 1, perPage = 20) =>
    fetchJSON(`/tv/popular?page=${page}&per_page=${perPage}`),

  getTVTopRated: (page = 1, perPage = 20) =>
    fetchJSON(`/tv/top-rated?page=${page}&per_page=${perPage}`),

  searchTV: (query, page = 1, perPage = 20) => {
    const qs = new URLSearchParams();
    qs.append('q', query);
    qs.append('page', page);
    qs.append('per_page', perPage);
    return fetchJSON(`/tv/search?${qs.toString()}`);
  },

  getTVDetail: (tmdbId, country = 'IN') =>
    fetchJSON(`/tv/${tmdbId}?country=${country}`),

  getTVSeasons: (tmdbId) =>
    fetchJSON(`/tv/${tmdbId}/seasons`),

  getTVSeasonEpisodes: (tmdbId, seasonNumber = 1) =>
    fetchJSON(`/tv/${tmdbId}/seasons/${seasonNumber}`),

  rateTV: (tmdbId, rating) =>
    fetchJSON(`/tv/${tmdbId}/rate`, {
      method: 'POST',
      body: JSON.stringify({ rating }),
    }),

  deleteTVRating: (tmdbId) =>
    fetchJSON(`/tv/${tmdbId}/rate`, {
      method: 'DELETE',
    }),

  getTVReviews: (tmdbId, sortBy = 'most_helpful', page = 1, perPage = 10) =>
    fetchJSON(`/tv/${tmdbId}/reviews?sort_by=${sortBy}&page=${page}&per_page=${perPage}`),

  submitTVReview: (tmdbId, payload) =>
    fetchJSON(`/tv/${tmdbId}/review`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  voteTVReview: (reviewId, voteType) =>
    fetchJSON(`/tv/reviews/${reviewId}/vote`, {
      method: 'POST',
      body: JSON.stringify({ vote_type: voteType }),
    }),

  reportTVReview: (reviewId, reason) =>
    fetchJSON(`/tv/reviews/${reviewId}/report`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    }),

  toggleTVWatchlist: (tmdbId) =>
    fetchJSON(`/tv/${tmdbId}/watchlist`, {
      method: 'POST',
    }),

  updateTVProgress: (tmdbId, payload) =>
    fetchJSON(`/tv/${tmdbId}/progress`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  getUserTVWatchlist: () => fetchJSON('/user/tv/watchlist'),
  getUserTVProgress: () => fetchJSON('/user/tv/progress'),
};
