import React, { useRef } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import MovieCard from './MovieCard';

export default function MovieCarousel({
  title,
  subtitle,
  movies = [],
  onSelectMovie,
  onWatchProviders,
  watchlist = [],
  onToggleWatchlist,
  watched = [],
  onToggleWatched,
}) {
  const scrollRef = useRef(null);

  const scroll = (direction) => {
    if (scrollRef.current) {
      const scrollAmount = direction === 'left' ? -650 : 650;
      scrollRef.current.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
  };

  if (!movies || movies.length === 0) return null;

  return (
    <div className="mb-10 relative group">
      
      {/* Section Header */}
      <div className="flex items-end justify-between mb-4 px-1">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-1.5 h-5 bg-[#F04452] rounded-full" />
            <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              {title}
            </h2>
          </div>
          {subtitle && (
            <p className="text-xs sm:text-sm text-[#94a3b8] mt-0.5 ml-3.5">
              {subtitle}
            </p>
          )}
        </div>

        {/* Scroll Nav Buttons */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => scroll('left')}
            className="w-8 h-8 rounded-full bg-[#181824] hover:bg-[#252536] border border-[#2e2e40] text-white flex items-center justify-center transition-colors cursor-pointer shadow-md hover:border-[#F04452]"
            aria-label="Scroll left"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            onClick={() => scroll('right')}
            className="w-8 h-8 rounded-full bg-[#181824] hover:bg-[#252536] border border-[#2e2e40] text-white flex items-center justify-center transition-colors cursor-pointer shadow-md hover:border-[#F04452]"
            aria-label="Scroll right"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Horizontal Scroll Track */}
      <div
        ref={scrollRef}
        className="flex items-stretch gap-4 sm:gap-5 overflow-x-auto no-scrollbar py-2 px-1 scroll-smooth"
      >
        {movies.map((movie) => (
          <MovieCard
            key={movie.id}
            movie={movie}
            onSelect={onSelectMovie}
            onWatchProviders={onWatchProviders}
            inWatchlist={watchlist.some(m => m.id === movie.id)}
            onToggleWatchlist={onToggleWatchlist}
            isWatched={watched.includes(movie.id)}
            onToggleWatched={onToggleWatched}
            similarityScore={movie.similarity_score}
            recommendationReason={movie.recommendation_reason}
          />
        ))}
      </div>

    </div>
  );
}

