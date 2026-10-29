import React, { useState, useEffect } from 'react';
import { Sparkles, SlidersHorizontal, Heart, Eye, CheckCircle2, RefreshCw } from 'lucide-react';
import MovieCard from '../components/MovieCard';
import { api } from '../services/api';

export default function ForYouPage({
  onSelectMovie,
  onWatchProviders,
  watchlistState,
  onOpenOnboarding,
}) {
  const {
    watchlist,
    toggleWatchlist,
    liked,
    watched,
    favoriteGenres,
    toggleLiked,
    toggleWatched,
  } = watchlistState;

  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchPersonalized = () => {
    setLoading(true);
    api.getPersonalizedRecommendations({
      liked_movie_ids: liked,
      watched_movie_ids: watched,
      favorite_genres: favoriteGenres,
      count: 18,
    })
      .then((res) => {
        if (res.success) {
          setRecommendations(res.recommendations || []);
        }
      })
      .catch((err) => {
        console.error('Error fetching personalized recommendations:', err);
      })
      .finally(() => {
        setLoading(false);
        setRefreshing(false);
      });
  };

  useEffect(() => {
    fetchPersonalized();
  }, [liked, watched, favoriteGenres]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchPersonalized();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 animate-in fade-in duration-300">
      
      {/* Taste Profile Banner */}
      <div className="relative rounded-2xl md:rounded-3xl p-6 sm:p-8 bg-gradient-to-r from-[#181826] via-[#1c1c2e] to-[#161622] border border-[#2b2b3e] shadow-xl mb-10 overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-[#F04452]/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#fbbf24]/15 border border-[#fbbf24]/30 text-xs font-semibold text-[#fbbf24] mb-3">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Machine Learning Taste Profile</span>
            </div>
            
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Personalized Recommendations
            </h1>
            
            <p className="text-xs sm:text-sm text-[#94a3b8] mt-1 max-w-xl">
              Computed in real time by vectorizing your favorite genres and liked films.
              Weighted cosine similarity matches titles closely aligned with your cinematic preferences.
            </p>

            {/* Taste Stats */}
            <div className="flex flex-wrap items-center gap-2.5 mt-4">
              <span className="text-xs text-[#cbd5e1] bg-[#14141e] px-3 py-1 rounded-lg border border-[#282838] flex items-center gap-1.5">
                <Heart className="w-3.5 h-3.5 text-[#ec4899]" />
                <strong>{liked.length}</strong> Movies Liked
              </span>

              <span className="text-xs text-[#cbd5e1] bg-[#14141e] px-3 py-1 rounded-lg border border-[#282838] flex items-center gap-1.5">
                <Eye className="w-3.5 h-3.5 text-[#3b82f6]" />
                <strong>{watched.length}</strong> Watched Filtered
              </span>

              {favoriteGenres.map((g) => (
                <span
                  key={g}
                  className="text-xs text-[#38bdf8] bg-[#38bdf8]/10 px-2.5 py-1 rounded-lg border border-[#38bdf8]/20 font-medium"
                >
                  {g}
                </span>
              ))}
            </div>
          </div>

          {/* Retune Profile Controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="p-3 rounded-xl bg-[#1e1e2c] hover:bg-[#28283c] border border-[#303044] text-[#cbd5e1] hover:text-white transition-colors cursor-pointer disabled:opacity-50"
              title="Recalculate AI Vectors"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin text-[#F04452]' : ''}`} />
            </button>

            <button
              onClick={onOpenOnboarding}
              className="px-4 py-3 rounded-xl bg-[#F04452] hover:bg-[#d63340] text-white text-xs sm:text-sm font-bold flex items-center gap-2 shadow-lg shadow-[#F04452]/20 transition-all cursor-pointer hover:scale-103"
            >
              <SlidersHorizontal className="w-4 h-4" />
              <span>Tune Taste Profile</span>
            </button>
          </div>
        </div>
      </div>

      {/* Grid of ML Recommendations */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <div className="w-1.5 h-5 bg-[#fbbf24] rounded-full" />
            <h2 className="text-xl font-bold text-white tracking-tight">
              Top Picks For Your Taste
            </h2>
            <span className="text-xs text-[#94a3b8] font-medium ml-2">
              ({recommendations.length} calculated matches)
            </span>
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 sm:gap-5">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((i) => (
              <div key={i} className="aspect-[2/3] skeleton rounded-2xl" />
            ))}
          </div>
        ) : recommendations.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 sm:gap-5">
            {recommendations.map((movie) => (
              <MovieCard
                key={movie.id}
                movie={movie}
                onSelect={onSelectMovie}
                onWatchProviders={onWatchProviders}
                inWatchlist={watchlist.some(m => m.id === movie.id)}
                onToggleWatchlist={toggleWatchlist}
                similarityScore={movie.similarity_score}
                recommendationReason={movie.recommendation_reason}
              />
            ))}
          </div>
        ) : (
          <div className="py-16 text-center bg-[#14141e] rounded-3xl border border-[#242434] p-8">
            <Sparkles className="w-10 h-10 text-[#64748b] mx-auto mb-3" />
            <h3 className="text-base font-bold text-white mb-1">
              No Recommendations Generated
            </h3>
            <p className="text-xs text-[#94a3b8] max-w-sm mx-auto mb-4">
              Select your favorite genres or like a few movies to allow our content-based model to build your profile.
            </p>
            <button
              onClick={onOpenOnboarding}
              className="px-5 py-2.5 rounded-xl bg-[#F04452] text-white text-xs font-bold shadow-md cursor-pointer"
            >
              Pick Favorite Genres
            </button>
          </div>
        )}
      </div>

    </div>
  );
}
