import { useState, useEffect } from 'react';

const STORAGE_KEYS = {
  WATCHLIST: 'cinematch_watchlist',
  WATCHED: 'cinematch_watched',
  LIKED: 'cinematch_liked',
  FAV_GENRES: 'cinematch_favorite_genres',
  COUNTRY: 'cinematch_country',
  ONBOARDED: 'cinematch_has_onboarded',
};

export function useWatchlist() {
  const [watchlist, setWatchlist] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.WATCHLIST);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  const [watched, setWatched] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.WATCHED);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  const [liked, setLiked] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.LIKED);
      return stored ? JSON.parse(stored) : [157336, 27205]; // Defaults to Interstellar, Inception to give rich initial taste profile
    } catch {
      return [157336, 27205];
    }
  });

  const [favoriteGenres, setFavoriteGenres] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.FAV_GENRES);
      return stored ? JSON.parse(stored) : ['Science Fiction', 'Action', 'Drama'];
    } catch {
      return ['Science Fiction', 'Action', 'Drama'];
    }
  });

  const [country, setCountry] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_KEYS.COUNTRY) || 'IN';
    } catch {
      return 'IN';
    }
  });

  const [hasOnboarded, setHasOnboarded] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_KEYS.ONBOARDED) === 'true';
    } catch {
      return false;
    }
  });

  // Sync state changes with localStorage
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.WATCHLIST, JSON.stringify(watchlist));
    } catch (e) {
      console.warn('LocalStorage save error:', e);
    }
  }, [watchlist]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.WATCHED, JSON.stringify(watched));
    } catch (e) {
      console.warn('LocalStorage save error:', e);
    }
  }, [watched]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.LIKED, JSON.stringify(liked));
    } catch (e) {
      console.warn('LocalStorage save error:', e);
    }
  }, [liked]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.FAV_GENRES, JSON.stringify(favoriteGenres));
    } catch (e) {
      console.warn('LocalStorage save error:', e);
    }
  }, [favoriteGenres]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.COUNTRY, country);
    } catch (e) {
      console.warn('LocalStorage save error:', e);
    }
  }, [country]);

  const completeOnboarding = (genres, likedMovieIds) => {
    setFavoriteGenres(genres);
    if (likedMovieIds && likedMovieIds.length > 0) {
      setLiked(prev => Array.from(new Set([...prev, ...likedMovieIds])));
    }
    setHasOnboarded(true);
    localStorage.setItem(STORAGE_KEYS.ONBOARDED, 'true');
  };

  const isInWatchlist = (movieId) => watchlist.some(m => m.id === movieId);
  const isWatched = (movieId) => watched.includes(movieId);
  const isLiked = (movieId) => liked.includes(movieId);

  const toggleWatchlist = (movie) => {
    setWatchlist(prev => {
      const exists = prev.some(m => m.id === movie.id);
      if (exists) {
        return prev.filter(m => m.id !== movie.id);
      } else {
        return [...prev, movie];
      }
    });
  };

  const toggleWatched = (movieId) => {
    setWatched(prev => {
      if (prev.includes(movieId)) {
        return prev.filter(id => id !== movieId);
      } else {
        return [...prev, movieId];
      }
    });
  };

  const toggleLiked = (movieId) => {
    setLiked(prev => {
      if (prev.includes(movieId)) {
        return prev.filter(id => id !== movieId);
      } else {
        return [...prev, movieId];
      }
    });
  };

  const removeFromWatchlist = (movieId) => {
    setWatchlist(prev => prev.filter(m => m.id !== movieId));
  };

  return {
    watchlist,
    watched,
    liked,
    favoriteGenres,
    country,
    hasOnboarded,
    setCountry,
    setFavoriteGenres,
    toggleWatchlist,
    toggleWatched,
    toggleLiked,
    removeFromWatchlist,
    isInWatchlist,
    isWatched,
    isLiked,
    completeOnboarding,
  };
}
