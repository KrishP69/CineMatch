import React, { useState, useEffect, useRef } from 'react';
import { Search, X, SlidersHorizontal, Star, Film, Sparkles } from 'lucide-react';
import MovieCard from '../components/MovieCard';
import { api } from '../services/api';

export default function SearchPage({
  initialQuery = '',
  onSelectMovie,
  onWatchProviders,
  watchlistState,
}) {
  const { watchlist, toggleWatchlist, watched, toggleWatched } = watchlistState;
  const [query, setQuery] = useState(initialQuery);
  const [selectedGenre, setSelectedGenre] = useState('');
  const [minRating, setMinRating] = useState('');
  const [sortBy, setSortBy] = useState('relevance');
  const [genres, setGenres] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef(null);

  // Focus input on load
  useEffect(() => {
    if (inputRef.current) inputRef.current.focus();
  }, []);

  // Load genres
  useEffect(() => {
    api.getGenres().then((res) => {
      if (res.success) setGenres(res.genres || []);
    }).catch(() => {});
  }, []);

  // Update query if initialQuery changes
  useEffect(() => {
    if (initialQuery !== undefined) setQuery(initialQuery);
  }, [initialQuery]);

  // Debounced search
  useEffect(() => {
    const handler = setTimeout(() => {
      setLoading(true);
      api.searchMovies(query, {
        genre: selectedGenre,
        min_rating: minRating,
        sort_by: sortBy,
        limit: 30,
      })
        .then((res) => {
          if (res.success) {
            setResults(res.data.movies || []);
          }
        })
        .catch((err) => {
          console.error('Search error:', err);
        })
        .finally(() => {
          setLoading(false);
        });
    }, 250);

    return () => clearTimeout(handler);
  }, [query, selectedGenre, minRating, sortBy]);

  const clearQuery = () => {
    setQuery('');
    if (inputRef.current) inputRef.current.focus();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 animate-in fade-in duration-300">
      
      {/* Search Bar Input Container */}
      <div className="relative max-w-3xl mx-auto mb-8">
        <div className="relative flex items-center">
          <Search className="absolute left-4.5 w-5 h-5 text-[#94a3b8] pointer-events-none" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by title, actor (e.g. Leonardo DiCaprio), director (e.g. Nolan), keywords..."
            className="w-full pl-12 pr-12 py-4 rounded-2xl bg-[#161622] border border-[#2e2e42] focus:border-[#F04452] text-white text-sm sm:text-base placeholder-[#64748b] focus:outline-none focus:ring-2 focus:ring-[#F04452]/20 shadow-xl transition-all"
          />
          {query && (
            <button
              onClick={clearQuery}
              className="absolute right-4 w-7 h-7 rounded-full bg-[#252538] hover:bg-[#34344e] text-white flex items-center justify-center transition-colors cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Quick query tags */}
        <div className="flex flex-wrap items-center gap-1.5 mt-3 px-1 text-xs text-[#94a3b8]">
          <span className="font-semibold text-[#64748b]">Try searching:</span>
          {['Christopher Nolan', 'Space', 'Leonardo DiCaprio', 'Dune', 'India', 'Mind Game'].map((tag) => (
            <button
              key={tag}
              onClick={() => setQuery(tag)}
              className="px-2 py-0.5 rounded-md bg-[#181826] hover:bg-[#222234] border border-[#2a2a3c] text-[#cbd5e1] hover:text-[#F04452] transition-colors cursor-pointer"
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-2xl bg-[#14141e] border border-[#242434] mb-8">
        
        {/* Left: Filters */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Genre Filter */}
          <div className="flex items-center gap-1.5 text-xs text-[#cbd5e1]">
            <span className="text-[#94a3b8]">Genre:</span>
            <select
              value={selectedGenre}
              onChange={(e) => setSelectedGenre(e.target.value)}
              className="bg-[#1c1c28] border border-[#2e2e40] text-xs font-semibold text-white px-2.5 py-1.5 rounded-xl focus:outline-none cursor-pointer"
            >
              <option value="">All Genres</option>
              {genres.map((g) => (
                <option key={g.id} value={g.name}>{g.name}</option>
              ))}
            </select>
          </div>

          {/* Rating Filter */}
          <div className="flex items-center gap-1.5 text-xs text-[#cbd5e1]">
            <span className="text-[#94a3b8]">Min Rating:</span>
            <select
              value={minRating}
              onChange={(e) => setMinRating(e.target.value)}
              className="bg-[#1c1c28] border border-[#2e2e40] text-xs font-semibold text-white px-2.5 py-1.5 rounded-xl focus:outline-none cursor-pointer"
            >
              <option value="">Any Rating</option>
              <option value="7.0">★ 7.0+</option>
              <option value="8.0">★ 8.0+ (Top Rated)</option>
              <option value="8.5">★ 8.5+ (Masterpiece)</option>
            </select>
          </div>
        </div>

        {/* Right: Sort */}
        <div className="flex items-center gap-1.5 text-xs text-[#cbd5e1]">
          <span className="text-[#94a3b8]">Sort By:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="bg-[#1c1c28] border border-[#2e2e40] text-xs font-semibold text-white px-2.5 py-1.5 rounded-xl focus:outline-none cursor-pointer"
          >
            <option value="relevance">Relevance</option>
            <option value="rating">Rating</option>
            <option value="year">Release Date</option>
          </select>
        </div>

      </div>

      {/* Results Header */}
      <div className="flex items-center justify-between mb-6 px-1">
        <h2 className="text-base sm:text-lg font-bold text-white flex items-center gap-2">
          {query ? (
            <span>Search Results for "<span className="text-[#F04452]">{query}</span>"</span>
          ) : (
            <span>Browse All Movies</span>
          )}
          <span className="text-xs text-[#94a3b8] font-normal">
            ({results.length} found)
          </span>
        </h2>
      </div>

      {/* Results Grid */}
      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 sm:gap-5">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((i) => (
            <div key={i} className="aspect-[2/3] skeleton rounded-2xl" />
          ))}
        </div>
      ) : results.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 sm:gap-5">
          {results.map((movie) => (
            <MovieCard
              key={movie.id}
              movie={movie}
              onSelect={onSelectMovie}
              onWatchProviders={onWatchProviders}
              inWatchlist={watchlist.some(m => m.id === movie.id)}
              onToggleWatchlist={toggleWatchlist}
              isWatched={watched.includes(movie.id)}
              onToggleWatched={toggleWatched}
            />
          ))}
        </div>
      ) : (
        <div className="py-20 text-center bg-[#14141e] rounded-3xl border border-[#242434] p-8 max-w-md mx-auto my-6">
          <Film className="w-12 h-12 text-[#64748b] mx-auto mb-3" />
          <h3 className="text-base font-bold text-white mb-1">
            No matching titles found
          </h3>
          <p className="text-xs text-[#94a3b8] mb-4">
            Try checking for spelling errors, searching by actor name or director, or clearing your active filters.
          </p>
          <button
            onClick={() => {
              setQuery('');
              setSelectedGenre('');
              setMinRating('');
            }}
            className="px-4 py-2 rounded-xl bg-[#F04452] text-white text-xs font-semibold cursor-pointer"
          >
            Reset Filters
          </button>
        </div>
      )}

    </div>
  );
}

