import React, { useState, useEffect } from 'react';
import {
  SlidersHorizontal, ArrowUpDown, Film, Sparkles, Filter,
  RotateCcw, Tv, Globe, Clock, Star, Flame, Check
} from 'lucide-react';
import MovieCard from '../components/MovieCard';
import { api } from '../services/api';

const GENRES_LIST = [
  'Action', 'Adventure', 'Comedy', 'Crime', 'Drama', 'Horror',
  'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'Documentary',
  'Animation', 'Fantasy'
];

const MOODS_LIST = [
  { name: 'Happy', emoji: '😄' },
  { name: 'Sad', emoji: '😢' },
  { name: 'Romantic', emoji: '❤️' },
  { name: 'Dark', emoji: '🌑' },
  { name: 'Suspenseful', emoji: '⚡' },
  { name: 'Exciting', emoji: '🔥' },
  { name: 'Relaxing', emoji: '☕' },
  { name: 'Inspiring', emoji: '✨' },
  { name: 'Emotional', emoji: '🥺' },
  { name: 'Mind-bending', emoji: '🌀' },
];

const THEMES_LIST = [
  'Plot twists',
  'Psychological thrillers',
  'Mind-bending stories',
  'Feel-good movies',
  'Survival stories',
  'Mystery investigations',
  'Underrated movies',
  'Intense action',
  'Emotional storytelling',
  'Dark atmosphere'
];

const STREAMING_PLATFORMS = [
  'Any',
  'Netflix',
  'Prime Video',
  'JioHotstar',
  'Apple TV',
  'SonyLIV',
  'Zee5'
];

export default function GenresPage({
  initialGenre = 'All',
  onSelectMovie,
  onWatchProviders,
  watchlistState,
}) {
  const { watchlist, toggleWatchlist, watched, toggleWatched, liked, toggleLiked } = watchlistState;

  // Multi-Filter Inputs
  const [selectedGenres, setSelectedGenres] = useState(
    initialGenre && initialGenre !== 'All' ? [initialGenre] : []
  );
  const [selectedMoods, setSelectedMoods] = useState(['Mind-bending']);
  const [selectedThemes, setSelectedThemes] = useState(['Plot twists']);
  const [minRating, setMinRating] = useState(7.0);
  const [yearMin, setYearMin] = useState(1990);
  const [yearMax, setYearMax] = useState(2026);
  const [streamingPlatform, setStreamingPlatform] = useState('Any');
  const [sortBy, setSortBy] = useState('relevance'); // 'relevance' | 'rating' | 'popularity' | 'release_date'

  // Results State
  const [movies, setMovies] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);

  // Sync initialGenre
  useEffect(() => {
    if (initialGenre && initialGenre !== 'All' && !selectedGenres.includes(initialGenre)) {
      setSelectedGenres([initialGenre]);
    }
  }, [initialGenre]);

  const toggleItem = (list, setList, item) => {
    if (list.includes(item)) {
      setList(list.filter((x) => x !== item));
    } else {
      setList([...list, item]);
    }
  };

  const handleResetFilters = () => {
    setSelectedGenres([]);
    setSelectedMoods([]);
    setSelectedThemes([]);
    setMinRating(6.5);
    setYearMin(1980);
    setYearMax(2026);
    setStreamingPlatform('Any');
    setSortBy('relevance');
  };

  const fetchDiscoveryMovies = async () => {
    setLoading(true);
    try {
      const res = await api.discoverMovies({
        genres: selectedGenres,
        moods: selectedMoods,
        themes: selectedThemes,
        min_rating: minRating,
        release_year_min: yearMin,
        release_year_max: yearMax,
        streaming_platform: streamingPlatform === 'Any' ? null : streamingPlatform,
        exclude_ids: watched, // Negative filtering of watched titles!
        liked_ids: liked,
        sort_by: sortBy,
        per_page: 24,
      });

      if (res.success && res.data) {
        setMovies(res.data.movies || []);
        setTotalCount(res.data.total || 0);
      }
    } catch (err) {
      console.error('Failed to run discovery recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDiscoveryMovies();
  }, [selectedGenres, selectedMoods, selectedThemes, minRating, yearMin, yearMax, streamingPlatform, sortBy, watched]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 animate-in fade-in duration-300">
      
      {/* Title & Discovery Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
            <SlidersHorizontal className="w-6 h-6 text-[#38bdf8]" />
            Personalized Movie Discovery Lab
          </h1>
          <p className="text-xs sm:text-sm text-[#94a3b8] mt-1 max-w-xl">
            Combine multiple genres, emotional moods, and storytelling styles. Powered by semantic mapping and negative filtering of watched titles.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start md:self-auto">
          <button
            onClick={handleResetFilters}
            className="px-3.5 py-2 rounded-xl bg-[#1e1e2c] hover:bg-[#28283a] text-xs font-semibold text-[#cbd5e1] hover:text-white border border-[#2e2e42] transition-colors cursor-pointer flex items-center gap-1.5"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Filters</span>
          </button>

          <div className="flex items-center gap-1.5 bg-[#181824] px-3 py-2 rounded-xl border border-[#2e2e42]">
            <ArrowUpDown className="w-3.5 h-3.5 text-[#94a3b8]" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-transparent text-xs font-semibold text-white focus:outline-none cursor-pointer"
            >
              <option value="relevance" className="bg-[#181824]">Hybrid Relevance</option>
              <option value="rating" className="bg-[#181824]">Highest Rated</option>
              <option value="popularity" className="bg-[#181824]">Most Popular</option>
              <option value="release_date" className="bg-[#181824]">Release Year</option>
            </select>
          </div>
        </div>
      </div>

      {/* FILTER CONTROL CENTER */}
      <div className="p-5 sm:p-6 rounded-3xl bg-[#161622] border border-[#262638] shadow-xl mb-8 space-y-6">
        
        {/* 1. Genres */}
        <div>
          <div className="flex items-center justify-between mb-2.5">
            <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <Film className="w-3.5 h-3.5 text-[#F04452]" />
              Select Genres ({selectedGenres.length} selected)
            </span>
            {selectedGenres.length > 0 && (
              <button
                onClick={() => setSelectedGenres([])}
                className="text-[10px] text-[#F04452] hover:underline cursor-pointer"
              >
                Clear
              </button>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            {GENRES_LIST.map((g) => {
              const active = selectedGenres.includes(g);
              return (
                <button
                  key={g}
                  type="button"
                  onClick={() => toggleItem(selectedGenres, setSelectedGenres, g)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                    active
                      ? 'bg-[#F04452] text-white shadow-md shadow-[#F04452]/20'
                      : 'bg-[#1c1c28] hover:bg-[#252538] text-[#cbd5e1] border border-[#2c2c3e]'
                  }`}
                >
                  {active && <Check className="w-3 h-3" />}
                  <span>{g}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* 2. Moods */}
        <div>
          <div className="flex items-center justify-between mb-2.5">
            <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-[#fbbf24]" />
              Current Mood & Emotional Vibe
            </span>
            {selectedMoods.length > 0 && (
              <button
                onClick={() => setSelectedMoods([])}
                className="text-[10px] text-[#fbbf24] hover:underline cursor-pointer"
              >
                Clear
              </button>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            {MOODS_LIST.map((m) => {
              const active = selectedMoods.includes(m.name);
              return (
                <button
                  key={m.name}
                  type="button"
                  onClick={() => toggleItem(selectedMoods, setSelectedMoods, m.name)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                    active
                      ? 'bg-[#fbbf24] text-[#121218] shadow-md shadow-[#fbbf24]/20'
                      : 'bg-[#1c1c28] hover:bg-[#252538] text-[#cbd5e1] border border-[#2c2c3e]'
                  }`}
                >
                  <span>{m.emoji}</span>
                  <span>{m.name}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* 3. What do you feel like watching? */}
        <div>
          <div className="flex items-center justify-between mb-2.5">
            <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <Flame className="w-3.5 h-3.5 text-[#38bdf8]" />
              What Do You Feel Like Watching?
            </span>
            {selectedThemes.length > 0 && (
              <button
                onClick={() => setSelectedThemes([])}
                className="text-[10px] text-[#38bdf8] hover:underline cursor-pointer"
              >
                Clear
              </button>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            {THEMES_LIST.map((th) => {
              const active = selectedThemes.includes(th);
              return (
                <button
                  key={th}
                  type="button"
                  onClick={() => toggleItem(selectedThemes, setSelectedThemes, th)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                    active
                      ? 'bg-[#38bdf8] text-[#0f172a] shadow-md shadow-[#38bdf8]/20'
                      : 'bg-[#1c1c28] hover:bg-[#252538] text-[#cbd5e1] border border-[#2c2c3e]'
                  }`}
                >
                  {active && <Check className="w-3 h-3" />}
                  <span>{th}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* 4. Sliders & Advanced Dropdowns */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 pt-4 border-t border-[#242436]">
          {/* Min Rating */}
          <div>
            <div className="flex items-center justify-between text-xs font-semibold text-[#cbd5e1] mb-1.5">
              <span className="flex items-center gap-1">
                <Star className="w-3.5 h-3.5 text-[#fbbf24]" /> Min Rating:
              </span>
              <span className="text-white font-bold">{minRating.toFixed(1)}+</span>
            </div>
            <input
              type="range"
              min="5.0"
              max="9.0"
              step="0.1"
              value={minRating}
              onChange={(e) => setMinRating(parseFloat(e.target.value))}
              className="w-full accent-[#F04452] cursor-pointer"
            />
          </div>

          {/* Release Year Range */}
          <div>
            <div className="flex items-center justify-between text-xs font-semibold text-[#cbd5e1] mb-1.5">
              <span>Release Era:</span>
              <span className="text-white font-bold">{yearMin} &ndash; {yearMax}</span>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="number"
                min="1950"
                max="2026"
                value={yearMin}
                onChange={(e) => setYearMin(parseInt(e.target.value) || 1950)}
                className="w-1/2 px-2.5 py-1.5 rounded-lg bg-[#14141e] border border-[#2e2e42] text-xs text-white"
              />
              <span className="text-[#94a3b8]">-</span>
              <input
                type="number"
                min="1950"
                max="2026"
                value={yearMax}
                onChange={(e) => setYearMax(parseInt(e.target.value) || 2026)}
                className="w-1/2 px-2.5 py-1.5 rounded-lg bg-[#14141e] border border-[#2e2e42] text-xs text-white"
              />
            </div>
          </div>

          {/* Streaming Platform */}
          <div>
            <label className="block text-xs font-semibold text-[#cbd5e1] mb-1.5 flex items-center gap-1.5">
              <Tv className="w-3.5 h-3.5 text-[#10b981]" /> Authorized OTT Platform:
            </label>
            <select
              value={streamingPlatform}
              onChange={(e) => setStreamingPlatform(e.target.value)}
              className="w-full bg-[#14141e] border border-[#2e2e42] text-xs font-semibold text-white px-3 py-2 rounded-xl focus:outline-none focus:border-[#F04452] cursor-pointer"
            >
              {STREAMING_PLATFORMS.map((plat) => (
                <option key={plat} value={plat} className="bg-[#14141e]">
                  {plat}
                </option>
              ))}
            </select>
          </div>
        </div>

      </div>

      {/* RESULTS HEADER */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-5 bg-[#38bdf8] rounded-full" />
          <h2 className="text-xl font-bold text-white tracking-tight">
            Curated Discovery Results
          </h2>
          <span className="text-xs text-[#94a3b8] font-medium ml-2">
            ({totalCount} titles matching filters • Watched titles filtered)
          </span>
        </div>
      </div>

      {/* MOVIES GRID */}
      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 sm:gap-5">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((i) => (
            <div key={i} className="aspect-[2/3] skeleton rounded-2xl" />
          ))}
        </div>
      ) : movies.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 sm:gap-5">
          {movies.map((movie) => (
            <MovieCard
              key={movie.id}
              movie={movie}
              onSelect={onSelectMovie}
              onWatchProviders={onWatchProviders}
              inWatchlist={watchlist.some((m) => m.id === movie.id)}
              onToggleWatchlist={toggleWatchlist}
              isWatched={watched.includes(movie.id)}
              onToggleWatched={toggleWatched}
              similarityScore={movie.similarity_score}
              recommendationReason={movie.recommendation_reason}
            />
          ))}
        </div>
      ) : (
        <div className="py-16 text-center bg-[#14141e] rounded-3xl border border-[#242434] p-8">
          <Filter className="w-10 h-10 text-[#64748b] mx-auto mb-3" />
          <h3 className="text-base font-bold text-white mb-1">
            No Movies Matched All Selected Filters
          </h3>
          <p className="text-xs text-[#94a3b8] max-w-sm mx-auto mb-4">
            Try adjusting your minimum rating, widening the release years, or removing a mood filter.
          </p>
          <button
            onClick={handleResetFilters}
            className="px-5 py-2.5 rounded-xl bg-[#F04452] text-white text-xs font-bold shadow-md cursor-pointer"
          >
            Reset Filters
          </button>
        </div>
      )}

    </div>
  );
}
