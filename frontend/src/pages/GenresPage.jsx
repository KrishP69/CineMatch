import React, { useState, useEffect } from 'react';
import { SlidersHorizontal, ArrowUpDown, Film } from 'lucide-react';
import MovieCard from '../components/MovieCard';
import { api } from '../services/api';

export default function GenresPage({
  initialGenre = 'All',
  onSelectMovie,
  onWatchProviders,
  watchlistState,
}) {
  const { watchlist, toggleWatchlist } = watchlistState;
  const [genres, setGenres] = useState([]);
  const [selectedGenre, setSelectedGenre] = useState(initialGenre);
  const [sortBy, setSortBy] = useState('popularity');
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);

  // Load available genres
  useEffect(() => {
    api.getGenres()
      .then((res) => {
        if (res.success) {
          setGenres(res.genres || []);
        }
      })
      .catch((err) => console.error('Failed to load genres:', err));
  }, []);

  // Update selected genre if initialGenre changes externally
  useEffect(() => {
    if (initialGenre) setSelectedGenre(initialGenre);
  }, [initialGenre]);

  // Load movies matching genre & sort
  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    api.getMovies({
      genre: selectedGenre === 'All' ? null : selectedGenre,
      sort_by: sortBy,
      per_page: 36,
    })
      .then((res) => {
        if (isMounted && res.success) {
          setMovies(res.data.movies || []);
        }
      })
      .catch((err) => console.error('Failed to load genre movies:', err))
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [selectedGenre, sortBy]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 animate-in fade-in duration-300">
      
      {/* Page Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
            <SlidersHorizontal className="w-6 h-6 text-[#38bdf8]" />
            Browse Movies by Genre
          </h1>
          <p className="text-xs sm:text-sm text-[#94a3b8] mt-1">
            Explore curated titles across high-octane action, mind-bending sci-fi, and moving drama.
          </p>
        </div>

        {/* Sort Controls */}
        <div className="flex items-center gap-2">
          <ArrowUpDown className="w-4 h-4 text-[#94a3b8]" />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="bg-[#181824] border border-[#2e2e42] text-xs font-semibold text-white px-3 py-2 rounded-xl focus:outline-none focus:border-[#F04452] cursor-pointer"
          >
            <option value="popularity">Most Popular</option>
            <option value="rating">Highest Rated</option>
            <option value="year">Release Year (Newest)</option>
            <option value="title">Alphabetical (A-Z)</option>
          </select>
        </div>
      </div>

      {/* Genre Chips Bar */}
      <div className="flex flex-wrap gap-2 mb-8 p-3 rounded-2xl bg-[#14141e] border border-[#242434]">
        <button
          onClick={() => setSelectedGenre('All')}
          className={`px-3.5 py-1.8 rounded-xl text-xs font-bold transition-all cursor-pointer ${
            selectedGenre === 'All'
              ? 'bg-[#F04452] text-white shadow-md'
              : 'bg-[#1c1c28] hover:bg-[#252538] text-[#cbd5e1] border border-[#2e2e40]'
          }`}
        >
          All Genres
        </button>

        {genres.map((g) => (
          <button
            key={g.id}
            onClick={() => setSelectedGenre(g.name)}
            className={`px-3 py-1.8 rounded-xl text-xs font-medium transition-all cursor-pointer flex items-center gap-1.5 ${
              selectedGenre === g.name
                ? 'bg-[#F04452] text-white font-bold shadow-md'
                : 'bg-[#1c1c28] hover:bg-[#252538] text-[#cbd5e1] border border-[#2e2e40]'
            }`}
          >
            <span>{g.name}</span>
            <span className="text-[10px] opacity-60">({g.count})</span>
          </button>
        ))}
      </div>

      {/* Movies Grid */}
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
              inWatchlist={watchlist.some(m => m.id === movie.id)}
              onToggleWatchlist={toggleWatchlist}
            />
          ))}
        </div>
      ) : (
        <div className="py-16 text-center bg-[#14141e] rounded-3xl border border-[#242434] p-8">
          <Film className="w-10 h-10 text-[#64748b] mx-auto mb-3" />
          <h3 className="text-base font-bold text-white mb-1">No movies found in this genre</h3>
          <p className="text-xs text-[#94a3b8] mb-4">Try selecting another genre or changing sort criteria.</p>
        </div>
      )}

    </div>
  );
}
