import React, { useState, useEffect } from 'react';
import HeroSection from '../components/HeroSection';
import MovieCarousel from '../components/MovieCarousel';
import { api } from '../services/api';
import { Sparkles, Compass, Flame } from 'lucide-react';

export default function DiscoverPage({
  onSelectMovie,
  onWatchProviders,
  watchlistState,
  onOpenGenre,
}) {
  const { watchlist, toggleWatchlist, liked, watched } = watchlistState;
  const [featuredData, setFeaturedData] = useState(null);
  const [becauseWatchedMovies, setBecauseWatchedMovies] = useState(null);
  const [becauseMovieTitle, setBecauseMovieTitle] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    api.getFeatured()
      .then((res) => {
        if (isMounted && res.success) {
          setFeaturedData(res.data);
        }
      })
      .catch((err) => {
        console.error('Error fetching featured content:', err);
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  // Fetch "Because You Watched..." based on most recently liked or watched movie
  useEffect(() => {
    const seedId = (liked && liked.length > 0) ? liked[liked.length - 1] : 157336; // Default Interstellar
    if (!seedId) return;

    let isMounted = true;
    api.getSimilarMovies(seedId, 10)
      .then((res) => {
        if (isMounted && res.success) {
          setBecauseWatchedMovies(res.recommendations);
          // Look up title from seed
          api.getMovieDetail(seedId).then(d => {
            if (isMounted && d.movie) setBecauseMovieTitle(d.movie.title);
          }).catch(() => {});
        }
      })
      .catch(() => {});

    return () => {
      isMounted = false;
    };
  }, [liked, watched]);

  if (loading || !featuredData) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="w-full h-[450px] skeleton rounded-3xl mb-10" />
        <div className="space-y-8">
          <div className="w-48 h-6 skeleton rounded mb-4" />
          <div className="flex gap-4 overflow-hidden">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="w-[200px] h-[320px] skeleton rounded-2xl flex-shrink-0" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  const { hero, sections } = featuredData;
  const inHeroWatchlist = hero ? watchlist.some(m => m.id === hero.id) : false;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 animate-in fade-in duration-300">
      
      {/* Hero Banner Section */}
      <HeroSection
        movie={hero}
        onExplore={onSelectMovie}
        onWatchProviders={onWatchProviders}
        inWatchlist={inHeroWatchlist}
        onToggleWatchlist={toggleWatchlist}
      />

      {/* Quick Genre Jump Bar */}
      <div className="mb-10 p-4 rounded-2xl bg-[#161622] border border-[#242436] flex flex-wrap items-center justify-between gap-3 shadow-md">
        <div className="flex items-center gap-2">
          <Compass className="w-4 h-4 text-[#F04452]" />
          <span className="text-xs font-bold uppercase tracking-wider text-white">
            Explore by Genre
          </span>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {['Science Fiction', 'Action', 'Drama', 'Comedy', 'Thriller', 'Animation', 'Crime', 'Romance'].map((genre) => (
            <button
              key={genre}
              onClick={() => onOpenGenre(genre)}
              className="text-xs px-3 py-1.5 rounded-xl bg-[#1e1e2c] hover:bg-[#F04452] text-[#cbd5e1] hover:text-white border border-[#2e2e40] hover:border-[#F04452] transition-colors cursor-pointer"
            >
              {genre}
            </button>
          ))}
        </div>
      </div>

      {/* "Because You Watched..." Dynamic ML Recommendation Shelf */}
      {becauseWatchedMovies && becauseWatchedMovies.length > 0 && (
        <MovieCarousel
          title={`Because You Liked ${becauseMovieTitle || 'Sci-Fi'}`}
          subtitle="Direct content-based vector similarity calculated by our ML model"
          movies={becauseWatchedMovies}
          onSelectMovie={onSelectMovie}
          onWatchProviders={onWatchProviders}
          watchlist={watchlist}
          onToggleWatchlist={toggleWatchlist}
        />
      )}

      {/* Curated Curated Rows */}
      {sections.map((section) => (
        <MovieCarousel
          key={section.id}
          title={section.title}
          subtitle={section.subtitle}
          movies={section.movies}
          onSelectMovie={onSelectMovie}
          onWatchProviders={onWatchProviders}
          watchlist={watchlist}
          onToggleWatchlist={toggleWatchlist}
        />
      ))}

    </div>
  );
}
