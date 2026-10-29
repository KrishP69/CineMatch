import React, { useState } from 'react';
import { Bookmark, Eye, Trash2, Clock, Film, Sparkles, Tv, Check } from 'lucide-react';
import MovieCard from '../components/MovieCard';

export default function WatchlistPage({
  onSelectMovie,
  onWatchProviders,
  watchlistState,
  onNavigateDiscover,
}) {
  const {
    watchlist,
    toggleWatchlist,
    removeFromWatchlist,
    watched,
    toggleWatched,
  } = watchlistState;

  const [activeTab, setActiveTab] = useState('watchlist'); // 'watchlist' or 'history'
  const [filterGenre, setFilterGenre] = useState('All');

  // Compute stats
  const totalRuntimeMin = watchlist.reduce((acc, m) => acc + (m.runtime || 120), 0);
  const totalHours = Math.floor(totalRuntimeMin / 60);
  const totalMin = totalRuntimeMin % 60;

  // Extract distinct genres from saved watchlist
  const watchlistGenres = Array.from(
    new Set(watchlist.flatMap(m => m.genres || []))
  );

  const displayedMovies = activeTab === 'watchlist'
    ? watchlist.filter(m => filterGenre === 'All' || (m.genres || []).includes(filterGenre))
    : watchlist.filter(m => watched.includes(m.id));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 animate-in fade-in duration-300">
      
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
            <Bookmark className="w-6 h-6 text-[#a855f7]" />
            My Movie Library
          </h1>
          <p className="text-xs sm:text-sm text-[#94a3b8] mt-1">
            Persistent across sessions via browser storage. Filter, track, and locate legal streaming options.
          </p>
        </div>

        {/* Stats Pill */}
        {watchlist.length > 0 && (
          <div className="flex items-center gap-3 bg-[#181824] px-4 py-2.5 rounded-2xl border border-[#2a2a3c]">
            <div className="flex items-center gap-1.5 text-xs text-[#cbd5e1]">
              <Film className="w-4 h-4 text-[#F04452]" />
              <strong>{watchlist.length}</strong> Movies
            </div>
            <span className="text-[#3a3a52]">•</span>
            <div className="flex items-center gap-1.5 text-xs text-[#cbd5e1]">
              <Clock className="w-4 h-4 text-[#38bdf8]" />
              <span>{totalHours}h {totalMin}m runtime</span>
            </div>
          </div>
        )}
      </div>

      {/* Tabs Switcher: Want to Watch vs Watched */}
      <div className="flex items-center gap-2 border-b border-[#242434] pb-4 mb-6">
        <button
          onClick={() => setActiveTab('watchlist')}
          className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all cursor-pointer flex items-center gap-2 ${
            activeTab === 'watchlist'
              ? 'bg-[#a855f7]/20 border border-[#a855f7] text-white shadow-sm'
              : 'text-[#94a3b8] hover:text-white hover:bg-[#181824]'
          }`}
        >
          <Bookmark className="w-4 h-4 text-[#a855f7]" />
          <span>Want to Watch ({watchlist.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('history')}
          className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all cursor-pointer flex items-center gap-2 ${
            activeTab === 'history'
              ? 'bg-[#3b82f6]/20 border border-[#3b82f6] text-white shadow-sm'
              : 'text-[#94a3b8] hover:text-white hover:bg-[#181824]'
          }`}
        >
          <Eye className="w-4 h-4 text-[#3b82f6]" />
          <span>Watched History ({watchlist.filter(m => watched.includes(m.id)).length})</span>
        </button>

        {/* Genre Filter if multiple genres in watchlist */}
        {activeTab === 'watchlist' && watchlistGenres.length > 1 && (
          <div className="ml-auto flex items-center gap-2">
            <span className="text-xs text-[#94a3b8] hidden sm:inline">Filter Genre:</span>
            <select
              value={filterGenre}
              onChange={(e) => setFilterGenre(e.target.value)}
              className="bg-[#181824] border border-[#2e2e40] text-xs font-semibold text-white px-2.5 py-1.5 rounded-xl focus:outline-none cursor-pointer"
            >
              <option value="All">All ({watchlist.length})</option>
              {watchlistGenres.map((g) => (
                <option key={g} value={g}>{g}</option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Movies Grid */}
      {displayedMovies.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 sm:gap-5">
          {displayedMovies.map((movie) => (
            <div key={movie.id} className="relative group/item flex flex-col">
              <MovieCard
                movie={movie}
                onSelect={onSelectMovie}
                onWatchProviders={onWatchProviders}
                inWatchlist={true}
                onToggleWatchlist={toggleWatchlist}
              />
              {/* Extra Watchlist Actions bar */}
              <div className="flex items-center justify-between pt-2 px-1 text-xs">
                <button
                  onClick={() => toggleWatched(movie.id)}
                  className={`flex items-center gap-1 text-[11px] font-medium transition-colors cursor-pointer ${
                    watched.includes(movie.id) ? 'text-[#3b82f6]' : 'text-[#94a3b8] hover:text-white'
                  }`}
                >
                  <Eye className="w-3 h-3" />
                  <span>{watched.includes(movie.id) ? 'Watched' : 'Mark Seen'}</span>
                </button>

                <button
                  onClick={() => removeFromWatchlist(movie.id)}
                  className="text-[#ef4444]/80 hover:text-[#ef4444] transition-colors cursor-pointer p-1"
                  title="Remove from Watchlist"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Empty State */
        <div className="py-20 text-center bg-[#14141e] rounded-3xl border border-[#242434] p-8 max-w-lg mx-auto my-6">
          <div className="w-16 h-16 rounded-2xl bg-[#a855f7]/15 border border-[#a855f7]/30 flex items-center justify-center mx-auto mb-4">
            <Bookmark className="w-8 h-8 text-[#a855f7]" />
          </div>
          <h3 className="text-lg font-bold text-white mb-2">
            {activeTab === 'watchlist' ? 'Your Watchlist is Empty' : 'No Watched Films Yet'}
          </h3>
          <p className="text-xs sm:text-sm text-[#94a3b8] max-w-sm mx-auto mb-6">
            {activeTab === 'watchlist'
              ? 'Save films you discover to track them and get instant notifications on where to watch them legally.'
              : 'Mark films as seen from their details view or cards to improve your AI recommendation profile.'}
          </p>
          <button
            onClick={onNavigateDiscover}
            className="px-6 py-3 rounded-xl bg-[#F04452] hover:bg-[#d63340] text-white font-bold text-xs sm:text-sm shadow-lg shadow-[#F04452]/20 transition-all cursor-pointer"
          >
            Explore Discover Catalog
          </button>
        </div>
      )}

    </div>
  );
}
