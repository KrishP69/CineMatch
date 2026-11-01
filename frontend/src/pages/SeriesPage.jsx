import React, { useState, useEffect } from 'react';
import { Tv, Search, Star, Sparkles, Filter, RefreshCw, AlertCircle, Compass } from 'lucide-react';
import { api } from '../services/api';
import MovieCard from '../components/MovieCard';

const GENRE_PILLS = [
  'All',
  'Drama',
  'Crime',
  'Sci-Fi & Fantasy',
  'Action & Adventure',
  'Comedy',
  'Animation',
  'Mystery'
];

export default function SeriesPage({
  onSelectSeries,
  onWatchProviders,
  watchlistState,
}) {
  const { watchlist, toggleWatchlist, watched, toggleWatched } = watchlistState || {};
  const [activeCategory, setActiveCategory] = useState('trending'); // 'trending' | 'popular' | 'top_rated'
  const [activeGenre, setActiveGenre] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [shows, setShows] = useState([]);
  const [spotlightShow, setSpotlightShow] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Load TV Catalog
  const loadShows = (resetPage = false) => {
    setLoading(true);
    setError(null);
    const targetPage = resetPage ? 1 : page;

    let fetchPromise;
    if (searchQuery.trim()) {
      fetchPromise = api.searchTV(searchQuery.trim(), targetPage, 24);
    } else if (activeGenre !== 'All') {
      fetchPromise = api.getTVShows({ genre: activeGenre, page: targetPage, per_page: 24 });
    } else if (activeCategory === 'top_rated') {
      fetchPromise = api.getTVTopRated(targetPage, 24);
    } else if (activeCategory === 'popular') {
      fetchPromise = api.getTVPopular(targetPage, 24);
    } else {
      fetchPromise = api.getTVTrending(targetPage, 24);
    }

    fetchPromise
      .then((res) => {
        if (res.success && res.data) {
          const fetchedShows = res.data.shows || [];
          setShows(fetchedShows);
          setTotalPages(res.data.total_pages || 1);
          if (resetPage) setPage(1);
          if (!spotlightShow && fetchedShows.length > 0) {
            setSpotlightShow(fetchedShows[0]);
          }
        } else {
          setError(res.error || 'Failed to load web series.');
        }
      })
      .catch((err) => {
        console.error('Error fetching series:', err);
        setError(err.message || 'Unable to connect to web series service.');
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    loadShows(true);
  }, [activeCategory, activeGenre, searchQuery]);

  useEffect(() => {
    if (page > 1) {
      loadShows(false);
    }
  }, [page]);

  const formatImg = (path) => {
    if (!path) return 'https://image.tmdb.org/t/p/original/xJHokMbljvjADYdit5fK5VQsXEG.jpg';
    if (path.startsWith('http')) return path;
    const clean = path.startsWith('/') ? path : `/${path}`;
    return `https://image.tmdb.org/t/p/original${clean}`;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 animate-in fade-in duration-300 space-y-8">
      
      {/* Spotlight Series Banner */}
      {spotlightShow && !searchQuery && (
        <div className="relative w-full rounded-2xl md:rounded-3xl overflow-hidden bg-[#14141c] border border-[#262638] shadow-2xl group min-h-[360px] md:min-h-[440px] flex items-end">
          <img
            src={formatImg(spotlightShow.backdrop_path || spotlightShow.poster_path)}
            alt={spotlightShow.name}
            className="absolute inset-0 w-full h-full object-cover object-center filter brightness-60 group-hover:scale-102 transition-transform duration-1000"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#101014] via-[#101014]/60 to-transparent" />
          <div className="absolute inset-0 bg-gradient-to-r from-[#101014] via-[#101014]/80 to-transparent w-full md:w-3/4" />

          <div className="relative z-10 p-6 sm:p-10 max-w-2xl space-y-3">
            <div className="flex items-center gap-2">
              <span className="bg-[#6366f1] text-white text-xs font-black px-2.5 py-0.8 rounded-md uppercase tracking-wider flex items-center gap-1 shadow">
                <Tv className="w-3.5 h-3.5" />
                Spotlight Series
              </span>
              <div className="flex items-center gap-1 bg-black/60 backdrop-blur-md px-2.5 py-0.8 rounded-md text-xs font-bold text-white border border-white/10">
                <Star className="w-3.5 h-3.5 fill-[#fbbf24] text-[#fbbf24]" />
                <span>{spotlightShow.tmdb_rating ? Number(spotlightShow.tmdb_rating).toFixed(1) : '8.6'}</span>
              </div>
              <span className="text-xs text-[#cbd5e1] bg-black/60 backdrop-blur-md px-2.5 py-0.8 rounded-md border border-white/10 font-semibold">
                {spotlightShow.number_of_seasons || 1} Season{spotlightShow.number_of_seasons > 1 ? 's' : ''}
              </span>
            </div>

            <h1 className="text-2xl sm:text-4xl md:text-5xl font-black text-white tracking-tight drop-shadow-md">
              {spotlightShow.name}
            </h1>

            <p className="text-xs sm:text-sm text-[#cbd5e1] line-clamp-3 leading-relaxed drop-shadow">
              {spotlightShow.overview}
            </p>

            <div className="flex flex-wrap items-center gap-3 pt-2">
              <button
                onClick={() => onSelectSeries(spotlightShow)}
                className="px-6 py-2.8 rounded-xl bg-[#6366f1] hover:bg-[#4f46e5] text-white text-xs sm:text-sm font-bold flex items-center gap-2 transition-all shadow-lg shadow-[#6366f1]/25 cursor-pointer"
              >
                <Tv className="w-4 h-4" />
                Explore Series
              </button>
              <button
                onClick={() => onWatchProviders && onWatchProviders(spotlightShow)}
                className="px-5 py-2.8 rounded-xl bg-[#222232] hover:bg-[#2c2c40] text-white text-xs sm:text-sm font-bold flex items-center gap-2 border border-white/10 transition-colors cursor-pointer"
              >
                Where to Watch
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header, Search & Filter Bar */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
              <Tv className="w-6 h-6 text-[#6366f1]" />
              Web Series Catalogue
            </h2>
            <p className="text-xs sm:text-sm text-[#94a3b8]">
              Discover, rate, and track binge-worthy series with persistent episode tracking
            </p>
          </div>

          {/* Quick Search */}
          <div className="relative max-w-xs w-full">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#94a3b8]" />
            <input
              type="text"
              placeholder="Search series by title or keywords..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#161622] border border-[#2a2a3e] text-white text-xs focus:outline-none focus:border-[#6366f1] transition-colors"
            />
          </div>
        </div>

        {/* Category Selector Tabs */}
        {!searchQuery && (
          <div className="flex flex-wrap items-center justify-between gap-3 p-2 rounded-2xl bg-[#161622] border border-[#242436]">
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0 custom-scrollbar">
              {[
                { id: 'trending', label: 'Trending Series' },
                { id: 'popular', label: 'Most Popular' },
                { id: 'top_rated', label: 'Top Rated Classics' },
              ].map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => {
                    setActiveCategory(cat.id);
                    setActiveGenre('All');
                  }}
                  className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer flex-shrink-0 ${
                    activeCategory === cat.id && activeGenre === 'All'
                      ? 'bg-[#6366f1] text-white shadow-md shadow-[#6366f1]/20'
                      : 'text-[#94a3b8] hover:text-white hover:bg-[#1f1f2e]'
                  }`}
                >
                  {cat.label}
                </button>
              ))}
            </div>

            {/* Genre Pills */}
            <div className="flex items-center gap-1 overflow-x-auto custom-scrollbar">
              {GENRE_PILLS.map((genre) => (
                <button
                  key={genre}
                  onClick={() => setActiveGenre(genre)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors cursor-pointer flex-shrink-0 ${
                    activeGenre === genre
                      ? 'bg-[#6366f1]/20 text-[#818cf8] border border-[#6366f1]/40 font-bold'
                      : 'text-[#94a3b8] hover:text-white hover:bg-[#1a1a28]'
                  }`}
                >
                  {genre}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Series Cards Grid / Loading / Error State */}
      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((i) => (
            <div key={i} className="aspect-[2/3] skeleton rounded-2xl" />
          ))}
        </div>
      ) : error ? (
        <div className="p-8 rounded-3xl bg-[#161622] border border-[#2a2a3e] text-center space-y-4 max-w-lg mx-auto">
          <AlertCircle className="w-12 h-12 text-[#F04452] mx-auto" />
          <h3 className="text-lg font-bold text-white">Unable to Load Series</h3>
          <p className="text-xs text-[#94a3b8]">{error}</p>
          <button
            onClick={() => loadShows(true)}
            className="px-5 py-2.5 bg-[#6366f1] hover:bg-[#4f46e5] text-white font-bold rounded-xl text-xs transition-colors cursor-pointer inline-flex items-center gap-2 shadow"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Try Again
          </button>
        </div>
      ) : shows.length > 0 ? (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 sm:gap-5">
            {shows.map((show) => (
              <MovieCard
                key={show.id || show.tmdb_id}
                movie={show}
                onSelect={() => onSelectSeries(show)}
                onWatchProviders={onWatchProviders}
                inWatchlist={watchlist ? watchlist.some(m => m.id === show.id || m.tmdb_id === show.tmdb_id) : false}
                onToggleWatchlist={toggleWatchlist}
                isWatched={watched ? (watched.includes(show.id) || watched.includes(show.tmdb_id)) : false}
                onToggleWatched={toggleWatched}
              />
            ))}
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-3 pt-6">
              <button
                disabled={page <= 1}
                onClick={() => setPage(p => Math.max(1, p - 1))}
                className="px-4 py-2 rounded-xl bg-[#181824] hover:bg-[#222234] disabled:opacity-40 text-xs font-bold text-white border border-white/5 transition-colors cursor-pointer"
              >
                Previous
              </button>
              <span className="text-xs text-[#94a3b8]">
                Page <strong className="text-white">{page}</strong> of <strong className="text-white">{totalPages}</strong>
              </span>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                className="px-4 py-2 rounded-xl bg-[#181824] hover:bg-[#222234] disabled:opacity-40 text-xs font-bold text-white border border-white/5 transition-colors cursor-pointer"
              >
                Next
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="p-12 text-center rounded-3xl bg-[#161622] border border-[#262638] space-y-3">
          <Tv className="w-12 h-12 text-[#64748b] mx-auto" />
          <h3 className="text-base font-bold text-white">No Web Series Found</h3>
          <p className="text-xs text-[#94a3b8]">
            {searchQuery ? `No series match query "${searchQuery}".` : 'No series found in this category.'}
          </p>
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="text-xs text-[#6366f1] font-bold underline"
            >
              Clear Search Query
            </button>
          )}
        </div>
      )}

    </div>
  );
}

