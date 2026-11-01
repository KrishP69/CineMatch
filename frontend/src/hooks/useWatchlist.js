import { useState, useEffect, useCallback, useRef } from 'react';
import { api } from '../services/api';

const STORAGE_KEYS = {
  USER: 'cinematch_user',
  WATCHLIST: 'cinematch_watchlist',
  WATCHED: 'cinematch_watched',
  LIKED: 'cinematch_liked',
  DISLIKED: 'cinematch_disliked',
  FAV_GENRES: 'cinematch_favorite_genres',
  MOOD: 'cinematch_mood',
  ERA: 'cinematch_era',
  COUNTRY: 'cinematch_country',
  ONBOARDED: 'cinematch_has_onboarded',
  TELEMETRY: 'cinematch_model_telemetry',
};

const DEFAULT_USER = {
  name: 'Movie Buff',
  email: 'explorer@cinematch.ai',
  avatar: '🎬',
  isLoggedIn: false,
};

export function useWatchlist() {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.USER);
      return stored ? JSON.parse(stored) : DEFAULT_USER;
    } catch {
      return DEFAULT_USER;
    }
  });

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
      return stored ? JSON.parse(stored) : [157336, 27205]; // Defaults to Interstellar, Inception
    } catch {
      return [157336, 27205];
    }
  });

  const [disliked, setDisliked] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.DISLIKED);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
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

  const [mood, setMood] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_KEYS.MOOD) || 'Mind-Bending & Complex';
    } catch {
      return 'Mind-Bending & Complex';
    }
  });

  const [era, setEra] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_KEYS.ERA) || 'Modern Blockbusters';
    } catch {
      return 'Modern Blockbusters';
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

  const [modelTelemetry, setModelTelemetry] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.TELEMETRY);
      return stored ? JSON.parse(stored) : {
        total_signals: 5,
        taste_summary: 'Calibrated with 5 signals focusing on Science Fiction, Drama, Action',
        learned_keywords: ['Space', 'Nolan', 'Sci-Fi'],
        model_version: 'v3.1.5',
      };
    } catch {
      return null;
    }
  });

  const [trainingToast, setTrainingToast] = useState(null);
  const toastTimerRef = useRef(null);

  // Trigger continuous model retraining
  const retrainModel = useCallback(async (overrides = {}) => {
    const curLiked = overrides.liked ?? liked;
    const curWatched = overrides.watched ?? watched;
    const curDisliked = overrides.disliked ?? disliked;
    const curWatchlist = overrides.watchlist ?? watchlist;
    const curGenres = overrides.favoriteGenres ?? favoriteGenres;
    const curMood = overrides.mood ?? mood;
    const curEra = overrides.era ?? era;

    try {
      const res = await api.retrainModel({
        liked_movie_ids: curLiked,
        watched_movie_ids: curWatched,
        disliked_movie_ids: curDisliked,
        watchlist_movie_ids: curWatchlist.map(m => m.id),
        favorite_genres: curGenres,
        mood: curMood,
        era: curEra,
        count: 12,
      });

      if (res.success && res.model_telemetry) {
        setModelTelemetry(res.model_telemetry);
        try {
          localStorage.setItem(STORAGE_KEYS.TELEMETRY, JSON.stringify(res.model_telemetry));
        } catch {}

        // Show feedback toast
        const total = res.model_telemetry.total_signals || 0;
        const msg = `🧠 ML Model Retrained: ${total} interaction signals calibrated`;
        setTrainingToast({ message: msg, timestamp: Date.now() });

        if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
        toastTimerRef.current = setTimeout(() => {
          setTrainingToast(null);
        }, 3200);

        return res;
      }
    } catch (e) {
      console.warn('Continuous retraining update error:', e);
    }
    return null;
  }, [liked, watched, disliked, watchlist, favoriteGenres, mood, era]);

  // Sync state changes with localStorage
  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user)); } catch {}
  }, [user]);

  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEYS.WATCHLIST, JSON.stringify(watchlist)); } catch {}
  }, [watchlist]);

  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEYS.WATCHED, JSON.stringify(watched)); } catch {}
  }, [watched]);

  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEYS.LIKED, JSON.stringify(liked)); } catch {}
  }, [liked]);

  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEYS.DISLIKED, JSON.stringify(disliked)); } catch {}
  }, [disliked]);

  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEYS.FAV_GENRES, JSON.stringify(favoriteGenres)); } catch {}
  }, [favoriteGenres]);

  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEYS.MOOD, mood); } catch {}
  }, [mood]);

  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEYS.ERA, era); } catch {}
  }, [era]);

  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEYS.COUNTRY, country); } catch {}
  }, [country]);

  // Auto-verify stored JWT token on mount
  useEffect(() => {
    const token = localStorage.getItem('cinematch_token');
    if (token) {
      api.getMe()
        .then((res) => {
          if (res.success && res.user) {
            setUser({
              ...res.user,
              name: res.user.username,
              isLoggedIn: true,
            });
          }
        })
        .catch(() => {
          localStorage.removeItem('cinematch_token');
        });
    }
  }, []);

  // Auth methods
  const login = (name, email, avatar = '🍿') => {
    const updated = {
      name: name || 'Movie Buff',
      username: name || 'Movie Buff',
      email: email || 'buff@cinematch.ai',
      avatar,
      isLoggedIn: true,
    };
    setUser(updated);
    return updated;
  };

  const logout = () => {
    localStorage.removeItem('cinematch_token');
    setUser({ ...DEFAULT_USER, isLoggedIn: false });
  };

  const completeOnboarding = async (genres, likedMovieIds, selectedMood, selectedEra) => {
    setFavoriteGenres(genres);
    const updatedLiked = likedMovieIds && likedMovieIds.length > 0
      ? Array.from(new Set([...liked, ...likedMovieIds]))
      : liked;
    setLiked(updatedLiked);

    if (selectedMood) setMood(selectedMood);
    if (selectedEra) setEra(selectedEra);

    setHasOnboarded(true);
    localStorage.setItem(STORAGE_KEYS.ONBOARDED, 'true');

    // Trigger instant model retrain
    await retrainModel({
      liked: updatedLiked,
      favoriteGenres: genres,
      mood: selectedMood || mood,
      era: selectedEra || era,
    });
  };

  const isInWatchlist = (movieId) => watchlist.some(m => m.id === movieId);
  const isWatched = (movieId) => watched.includes(movieId);
  const isLiked = (movieId) => liked.includes(movieId);
  const isDisliked = (movieId) => disliked.includes(movieId);

  const toggleWatchlist = (movie) => {
    setWatchlist(prev => {
      const exists = prev.some(m => m.id === movie.id);
      const updated = exists ? prev.filter(m => m.id !== movie.id) : [...prev, movie];
      retrainModel({ watchlist: updated });
      return updated;
    });
  };

  const toggleWatched = (movieId) => {
    setWatched(prev => {
      const updated = prev.includes(movieId)
        ? prev.filter(id => id !== movieId)
        : [...prev, movieId];
      // When marked as watched, retrain model immediately
      retrainModel({ watched: updated });
      return updated;
    });
  };

  const toggleLiked = (movieId) => {
    setLiked(prev => {
      const updated = prev.includes(movieId)
        ? prev.filter(id => id !== movieId)
        : [...prev, movieId];
      retrainModel({ liked: updated });
      return updated;
    });
  };

  const toggleDisliked = (movieId) => {
    setDisliked(prev => {
      const updated = prev.includes(movieId)
        ? prev.filter(id => id !== movieId)
        : [...prev, movieId];
      retrainModel({ disliked: updated });
      return updated;
    });
  };

  const removeFromWatchlist = (movieId) => {
    setWatchlist(prev => {
      const updated = prev.filter(m => m.id !== movieId);
      retrainModel({ watchlist: updated });
      return updated;
    });
  };

  const removeFromWatched = (movieId) => {
    setWatched(prev => {
      const updated = prev.filter(id => id !== movieId);
      retrainModel({ watched: updated });
      return updated;
    });
  };

  return {
    user,
    login,
    logout,
    watchlist,
    watched,
    liked,
    disliked,
    favoriteGenres,
    mood,
    era,
    country,
    hasOnboarded,
    modelTelemetry,
    trainingToast,
    setCountry,
    setFavoriteGenres,
    setMood,
    setEra,
    toggleWatchlist,
    toggleWatched,
    toggleLiked,
    toggleDisliked,
    removeFromWatchlist,
    removeFromWatched,
    isInWatchlist,
    isWatched,
    isLiked,
    isDisliked,
    completeOnboarding,
    retrainModel,
  };
}
