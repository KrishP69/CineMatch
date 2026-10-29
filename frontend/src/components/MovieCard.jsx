import React, { useState } from 'react';
import { Star, Plus, Check, Tv, Info, Film } from 'lucide-react';

export default function MovieCard({
  movie,
  onSelect,
  onWatchProviders,
  inWatchlist,
  onToggleWatchlist,
  similarityScore,
  recommendationReason,
}) {
  const [imgError, setImgError] = useState(false);

  if (!movie) return null;

  const rating = movie.vote_average ? Number(movie.vote_average).toFixed(1) : '8.0';
  const year = movie.release_year || (movie.release_date ? movie.release_date.split('-')[0] : '');
  const primaryGenre = movie.genres && movie.genres.length > 0 ? movie.genres[0] : '';
  const matchPct = similarityScore ? Math.round(similarityScore * 100) : null;

  return (
    <div className="group relative flex-shrink-0 w-[170px] sm:w-[200px] md:w-[220px] rounded-2xl bg-[#161620] border border-[#242432] hover:border-[#F04452]/60 transition-all duration-300 hover:shadow-xl hover:shadow-[#F04452]/10 hover:-translate-y-1.5 flex flex-col overflow-hidden cursor-pointer select-none">
      
      {/* Poster Image Container */}
      <div
        className="relative w-full aspect-[2/3] overflow-hidden bg-[#1a1a24]"
        onClick={() => onSelect(movie)}
      >
        {!imgError && movie.poster_path ? (
          <img
            src={movie.poster_path}
            alt={movie.title}
            loading="lazy"
            className="w-full h-full object-cover transition-transform duration-500 ease-out group-hover:scale-105"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center p-4 bg-gradient-to-br from-[#1a1a26] to-[#252538] text-center">
            <Film className="w-10 h-10 text-[#64748b] mb-2" />
            <p className="text-xs font-semibold text-[#cbd5e1] line-clamp-3">{movie.title}</p>
          </div>
        )}

        {/* Gradient Shadow Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#161620] via-transparent to-black/30 opacity-80 group-hover:opacity-60 transition-opacity" />

        {/* Top Floating Badges */}
        <div className="absolute top-2.5 left-2.5 right-2.5 flex items-center justify-between gap-1 z-10 pointer-events-none">
          {/* Rating Badge */}
          <div className="flex items-center gap-1 bg-black/75 backdrop-blur-md px-2 py-0.8 rounded-lg text-xs font-bold text-white border border-white/10 shadow-sm">
            <Star className="w-3 h-3 fill-[#fbbf24] text-[#fbbf24]" />
            <span>{rating}</span>
          </div>

          {/* AI Match % if available */}
          {matchPct !== null && (
            <div className="bg-[#F04452] text-white text-[10px] font-extrabold px-1.8 py-0.6 rounded-md shadow-md tracking-wider">
              {matchPct}% MATCH
            </div>
          )}
        </div>

        {/* Hover Quick Action Tray */}
        <div className="absolute inset-0 z-20 flex flex-col items-center justify-center gap-2.5 bg-black/60 backdrop-blur-[2px] opacity-0 group-hover:opacity-100 transition-opacity duration-200 p-3">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onSelect(movie);
            }}
            className="w-full py-2 px-3 rounded-xl bg-white text-black text-xs font-bold flex items-center justify-center gap-1.5 hover:bg-[#e2e8f0] transition-colors shadow cursor-pointer"
          >
            <Info className="w-3.5 h-3.5" />
            View Details
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();
              onWatchProviders(movie);
            }}
            className="w-full py-2 px-3 rounded-xl bg-[#F04452] text-white text-xs font-bold flex items-center justify-center gap-1.5 hover:bg-[#d63340] transition-colors shadow cursor-pointer"
          >
            <Tv className="w-3.5 h-3.5" />
            Where to Watch
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleWatchlist(movie);
            }}
            className={`w-full py-1.8 px-3 rounded-xl border text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors cursor-pointer ${
              inWatchlist
                ? 'bg-[#10b981]/20 border-[#10b981] text-[#10b981]'
                : 'bg-black/60 border-white/20 text-white hover:bg-black/80'
            }`}
          >
            {inWatchlist ? <Check className="w-3.5 h-3.5" /> : <Plus className="w-3.5 h-3.5" />}
            {inWatchlist ? 'Saved' : 'Watchlist'}
          </button>
        </div>

      </div>

      {/* Card Info Footer */}
      <div className="p-3.5 flex flex-col flex-grow justify-between bg-[#161620]">
        <div>
          <h3
            onClick={() => onSelect(movie)}
            className="text-sm font-semibold text-white tracking-tight line-clamp-1 group-hover:text-[#F04452] transition-colors"
            title={movie.title}
          >
            {movie.title}
          </h3>

          <div className="flex items-center gap-2 mt-1 text-[11px] text-[#94a3b8]">
            {year && <span>{year}</span>}
            {year && primaryGenre && <span>•</span>}
            {primaryGenre && <span className="line-clamp-1">{primaryGenre}</span>}
          </div>
        </div>

        {/* Dynamic ML recommendation reason pill if present */}
        {recommendationReason && (
          <div className="mt-2 text-[10px] text-[#38bdf8] bg-[#38bdf8]/10 border border-[#38bdf8]/20 px-2 py-0.8 rounded-md line-clamp-1">
            {recommendationReason}
          </div>
        )}
      </div>

    </div>
  );
}
