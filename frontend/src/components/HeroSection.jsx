import React from 'react';
import { Star, Plus, Check, Play, Info, Tv, Clock, Calendar } from 'lucide-react';

export default function HeroSection({
  movie,
  onExplore,
  onWatchProviders,
  inWatchlist,
  onToggleWatchlist,
}) {
  if (!movie) {
    return (
      <div className="w-full h-[480px] skeleton rounded-3xl mx-auto my-6 max-w-7xl" />
    );
  }

  const backdropUrl = movie.backdrop_path || movie.poster_path;
  const rating = movie.vote_average ? Number(movie.vote_average).toFixed(1) : '8.5';
  const year = movie.release_year || (movie.release_date ? movie.release_date.split('-')[0] : '2024');
  const runtime = movie.runtime ? `${Math.floor(movie.runtime / 60)}h ${movie.runtime % 60}m` : null;

  return (
    <div className="relative w-full rounded-2xl md:rounded-3xl overflow-hidden bg-[#14141c] border border-[#242434] shadow-2xl mb-10 group">
      
      {/* Background Backdrop Image with Multi-Gradient Overlays */}
      <div className="absolute inset-0 z-0">
        <img
          src={backdropUrl}
          alt={movie.title}
          className="w-full h-full object-cover object-center filter brightness-60 scale-100 group-hover:scale-102 transition-transform duration-1000 ease-out"
          onError={(e) => {
            e.currentTarget.src = 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1920&q=80';
          }}
        />
        {/* Gradients */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#101014] via-[#101014]/60 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-r from-[#101014] via-[#101014]/80 to-transparent w-full md:w-3/4" />
      </div>

      {/* Content Container */}
      <div className="relative z-10 max-w-3xl px-6 sm:px-10 py-12 md:py-20 flex flex-col justify-end min-h-[460px] md:min-h-[520px]">
        
        {/* Badges / Meta Info */}
        <div className="flex flex-wrap items-center gap-2.5 mb-3.5">
          <span className="bg-[#F04452] text-white text-xs font-bold px-2.5 py-0.8 rounded-md tracking-wide uppercase flex items-center gap-1 shadow-sm">
            Spotlight Feature
          </span>

          <div className="flex items-center gap-1 bg-[#1c1c28]/90 backdrop-blur-md px-2.5 py-0.8 rounded-md border border-[#303044] text-xs font-semibold text-[#f8fafc]">
            <Star className="w-3.5 h-3.5 fill-[#fbbf24] text-[#fbbf24]" />
            <span>{rating}</span>
            <span className="text-[10px] text-[#94a3b8] font-normal">TMDB</span>
          </div>

          <div className="flex items-center gap-1 text-xs text-[#cbd5e1] bg-[#1c1c28]/80 backdrop-blur-md px-2.5 py-0.8 rounded-md border border-[#303044]">
            <Calendar className="w-3.5 h-3.5 text-[#94a3b8]" />
            <span>{year}</span>
          </div>

          {runtime && (
            <div className="flex items-center gap-1 text-xs text-[#cbd5e1] bg-[#1c1c28]/80 backdrop-blur-md px-2.5 py-0.8 rounded-md border border-[#303044]">
              <Clock className="w-3.5 h-3.5 text-[#94a3b8]" />
              <span>{runtime}</span>
            </div>
          )}
        </div>

        {/* Title */}
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-black text-white tracking-tight leading-tight mb-2 drop-shadow-md">
          {movie.title}
        </h1>

        {/* Tagline */}
        {movie.tagline && (
          <p className="text-sm md:text-base font-medium text-[#F04452] italic mb-3">
            "{movie.tagline}"
          </p>
        )}

        {/* Genres */}
        <div className="flex flex-wrap gap-1.5 mb-4">
          {(movie.genres || []).slice(0, 4).map((genre) => (
            <span
              key={genre}
              className="text-xs bg-[#222232]/80 text-[#cbd5e1] px-2.5 py-0.5 rounded-full border border-[#34344a]"
            >
              {genre}
            </span>
          ))}
        </div>

        {/* Overview Excerpt */}
        <p className="text-sm sm:text-base text-[#cbd5e1] line-clamp-3 mb-6 max-w-2xl leading-relaxed drop-shadow">
          {movie.overview}
        </p>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Explore Movie */}
          <button
            onClick={() => onExplore(movie)}
            className="flex items-center gap-2 px-5 py-3 rounded-xl bg-[#F04452] hover:bg-[#d63340] text-white font-semibold text-sm transition-all shadow-lg shadow-[#F04452]/25 cursor-pointer hover:scale-103 active:scale-97"
          >
            <Info className="w-4 h-4" />
            Explore Movie
          </button>

          {/* Add to Watchlist */}
          <button
            onClick={() => onToggleWatchlist(movie)}
            className={`flex items-center gap-2 px-5 py-3 rounded-xl border text-sm font-semibold transition-all cursor-pointer hover:scale-103 active:scale-97 ${
              inWatchlist
                ? 'bg-[#10b981]/15 border-[#10b981]/50 text-[#10b981]'
                : 'bg-[#1e1e2c]/90 hover:bg-[#28283c] border-[#36364c] text-white'
            }`}
          >
            {inWatchlist ? <Check className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
            {inWatchlist ? 'In Watchlist' : 'Add to Watchlist'}
          </button>

          {/* Where to Watch */}
          <button
            onClick={() => onWatchProviders(movie)}
            className="flex items-center gap-2 px-5 py-3 rounded-xl bg-[#1e1e2c]/90 hover:bg-[#28283c] border border-[#36364c] text-[#f8fafc] text-sm font-semibold transition-all cursor-pointer hover:border-[#F04452] hover:scale-103 active:scale-97"
          >
            <Tv className="w-4 h-4 text-[#F04452]" />
            Where to Watch
          </button>
        </div>

      </div>
    </div>
  );
}
