import React, { useState, useEffect } from 'react';
import HeroSection from '../components/HeroSection';
import MovieCarousel from '../components/MovieCarousel';
import { api } from '../services/api';
import { Compass, AlertCircle, RefreshCw, Tv } from 'lucide-react';

export default function DiscoverPage({
  onSelectMovie,
  onSelectSeries,
  onWatchProviders,
  watchlistState,
  onOpenGenre,
}) {
  const { watchlist, toggleWatchlist, liked, watched, toggleWatched } = watchlistState || {};
  const [featuredData, setFeaturedData] = useState(null);
  const [becauseWatchedMovies, setBecauseWatchedMovies] = useState(null);
  const [becauseMovieTitle, setBecauseMovieTitle] = useState('');
  const [trendingSeries, setTrendingSeries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadFeaturedContent = () => {
    let isMounted = true;
    setLoading(true);
    setError(null);

    Promise.all([
      api.getFeatured(),
      api.getTVTrending(1, 14).catch(() => ({ success: false, data: { shows: [] } }))
    ])
      .then(([resFeatured, resTV]) => {
        if (!isMounted) return;
        if (resFeatured && resFeatured.success && resFeatured.data) {
          setFeaturedData(resFeatured.data);
        } else {
          setError(resFeatured?.error || 'Failed to load featured movies');
        }

        if (resTV && resTV.success && resTV.data?.shows) {
          setTrendingSeries(resTV.data.shows);
        }
      })
      .catch((err) => {
        console.error('Error fetching featured content:', err);
        if (isMounted) {
          setError(err.message || 'Unable to connect to CineMatch server.');
        }
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  };

  useEffect(() => {
    loadFeaturedContent();
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

  if (loading) {
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

  if (error || !featuredData) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="max-w-md mx-auto p-8 rounded-3xl bg-[#161622] border border-[#262638] text-center space-y-4">
          <AlertCircle className="w-12 h-12 text-[#F04452] mx-auto" />
          <h2 className="text-xl font-bold text-white">Could Not Load Movies</h2>
          <p className="text-xs text-[#94a3b8]">{error || 'Server returned empty featured catalogue.'}</p>
          <button
            onClick={loadFeaturedContent}
            className="px-6 py-2.5 bg-[#F04452] hover:bg-[#d93442] text-white text-xs font-bold rounded-xl transition-colors cursor-pointer inline-flex items-center gap-2 shadow-lg shadow-[#F04452]/20"
          >
            <RefreshCw className="w-4 h-4" />
            Retry
          </button>
        </div>
      </div>
    );
  }

  const { hero, sections } = featuredData;
  const inHeroWatchlist = hero && watchlist ? watchlist.some(m => m.id === hero.id) : false;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 animate-in fade-in duration-300">
      
      {/* Hero Banner Section */}
      <HeroSection
        movie={hero}
        onExplore={onSelectMovie}
        onWatchProviders={onWatchProviders}
        inWatchlist={inHeroWatchlist}
        onToggleWatchlist={toggleWatchlist}
        isWatched={hero && watched ? watched.includes(hero.id) : false}
        onToggleWatched={toggleWatched}
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
              onClick={() => onOpenGenre && onOpenGenre(genre)}
              className="text-xs px-3 py-1.5 rounded-xl bg-[#1e1e2c] hover:bg-[#F04452] text-[#cbd5e1] hover:text-white border border-[#2e2e40] hover:border-[#F04452] transition-colors cursor-pointer"
            >
              {genre}
            </button>
          ))}
        </div>
      </div>

      {/* "Trending Web Series" Carousel Shelf */}
      {trendingSeries && trendingSeries.length > 0 && (
        <div className="mb-8">
          <MovieCarousel
            title="Trending Web Series"
            subtitle="Top rated television and streaming series with persistent episode tracking"
            movies={trendingSeries}
            onSelectMovie={(show) => (onSelectSeries ? onSelectSeries(show) : onSelectMovie(show))}
            onWatchProviders={onWatchProviders}
            watchlist={watchlist}
            onToggleWatchlist={toggleWatchlist}
            watched={watched}
            onToggleWatched={toggleWatched}
          />
        </div>
      )}

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
          watched={watched}
          onToggleWatched={toggleWatched}
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
          watched={watched}
          onToggleWatched={toggleWatched}
        />
      ))}

    </div>
  );
}
