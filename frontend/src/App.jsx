import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import DiscoverPage from './pages/DiscoverPage';
import ForYouPage from './pages/ForYouPage';
import GenresPage from './pages/GenresPage';
import WatchlistPage from './pages/WatchlistPage';
import SearchPage from './pages/SearchPage';
import MovieDetailModal from './components/MovieDetailModal';
import WhereToWatchModal from './components/WhereToWatchModal';
import OnboardingModal from './components/OnboardingModal';
import { useWatchlist } from './hooks/useWatchlist';

export default function App() {
  const [activeTab, setActiveTab] = useState('discover'); // 'discover' | 'foryou' | 'genres' | 'watchlist' | 'search'
  const [selectedMovieId, setSelectedMovieId] = useState(null);
  const [selectedOttMovie, setSelectedOttMovie] = useState(null);
  const [onboardingOpen, setOnboardingOpen] = useState(false);
  const [activeGenreFilter, setActiveGenreFilter] = useState('All');
  const [initialSearchQuery, setInitialSearchQuery] = useState('');

  const watchlistState = useWatchlist();
  const {
    watchlist,
    country,
    setCountry,
    hasOnboarded,
    favoriteGenres,
    liked,
    completeOnboarding,
  } = watchlistState;

  // Show onboarding modal on initial visit if user hasn't configured taste yet
  useEffect(() => {
    if (!hasOnboarded) {
      const timer = setTimeout(() => {
        setOnboardingOpen(true);
      }, 1200);
      return () => clearTimeout(timer);
    }
  }, [hasOnboarded]);

  // Global keyboard shortcut: Ctrl+K or Cmd+K to trigger instant search
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setActiveTab('search');
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSelectMovie = (movie) => {
    setSelectedMovieId(movie.id);
  };

  const handleWatchProviders = (movie) => {
    setSelectedOttMovie(movie);
  };

  const handleOpenSearch = () => {
    setActiveTab('search');
  };

  const handleOpenGenre = (genreName) => {
    setActiveGenreFilter(genreName);
    setActiveTab('genres');
  };

  return (
    <div className="min-h-screen bg-[#101014] text-[#f8fafc] flex flex-col font-sans selection:bg-[#F04452] selection:text-white">
      
      {/* Top Navigation Bar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenSearch={handleOpenSearch}
        watchlistCount={watchlist.length}
        country={country}
        setCountry={setCountry}
        onOpenOnboarding={() => setOnboardingOpen(true)}
      />

      {/* Main Content Area */}
      <main className="flex-grow">
        {activeTab === 'discover' && (
          <DiscoverPage
            onSelectMovie={handleSelectMovie}
            onWatchProviders={handleWatchProviders}
            watchlistState={watchlistState}
            onOpenGenre={handleOpenGenre}
          />
        )}

        {activeTab === 'foryou' && (
          <ForYouPage
            onSelectMovie={handleSelectMovie}
            onWatchProviders={handleWatchProviders}
            watchlistState={watchlistState}
            onOpenOnboarding={() => setOnboardingOpen(true)}
          />
        )}

        {activeTab === 'genres' && (
          <GenresPage
            initialGenre={activeGenreFilter}
            onSelectMovie={handleSelectMovie}
            onWatchProviders={handleWatchProviders}
            watchlistState={watchlistState}
          />
        )}

        {activeTab === 'watchlist' && (
          <WatchlistPage
            onSelectMovie={handleSelectMovie}
            onWatchProviders={handleWatchProviders}
            watchlistState={watchlistState}
            onNavigateDiscover={() => setActiveTab('discover')}
          />
        )}

        {activeTab === 'search' && (
          <SearchPage
            initialQuery={initialSearchQuery}
            onSelectMovie={handleSelectMovie}
            onWatchProviders={handleWatchProviders}
            watchlistState={watchlistState}
          />
        )}
      </main>

      {/* Movie Details Modal */}
      {selectedMovieId && (
        <MovieDetailModal
          movieId={selectedMovieId}
          onClose={() => setSelectedMovieId(null)}
          country={country}
          setCountry={setCountry}
          watchlist={watchlistState.watchlist}
          onToggleWatchlist={watchlistState.toggleWatchlist}
          watched={watchlistState.watched}
          onToggleWatched={watchlistState.toggleWatched}
          liked={watchlistState.liked}
          onToggleLiked={watchlistState.toggleLiked}
          onSelectMovie={(movie) => setSelectedMovieId(movie.id)}
        />
      )}

      {/* Direct OTT "Where to Watch" Quick Modal */}
      {selectedOttMovie && (
        <WhereToWatchModal
          movie={selectedOttMovie}
          onClose={() => setSelectedOttMovie(null)}
          country={country}
          setCountry={setCountry}
        />
      )}

      {/* Onboarding Taste Tuning Modal */}
      <OnboardingModal
        isOpen={onboardingOpen}
        onClose={() => setOnboardingOpen(false)}
        initialGenres={favoriteGenres}
        initialLiked={liked}
        onComplete={completeOnboarding}
      />

      {/* Footer */}
      <Footer onOpenOnboarding={() => setOnboardingOpen(true)} />

    </div>
  );
}
