import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import DiscoverPage from './pages/DiscoverPage';
import SeriesPage from './pages/SeriesPage';
import ForYouPage from './pages/ForYouPage';
import GenresPage from './pages/GenresPage';
import WatchlistPage from './pages/WatchlistPage';
import SearchPage from './pages/SearchPage';
import MovieDetailModal from './components/MovieDetailModal';
import TVDetailModal from './components/TVDetailModal';
import WhereToWatchModal from './components/WhereToWatchModal';
import PersonalizationQuizModal from './components/PersonalizationQuizModal';
import AuthModal from './components/AuthModal';
import { useWatchlist } from './hooks/useWatchlist';
import { Zap, Sparkles } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('discover'); // 'discover' | 'series' | 'foryou' | 'genres' | 'watchlist' | 'search'
  const [selectedMovieId, setSelectedMovieId] = useState(null);
  const [selectedTVId, setSelectedTVId] = useState(null);
  const [selectedOttMovie, setSelectedOttMovie] = useState(null);
  const [onboardingOpen, setOnboardingOpen] = useState(false);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [activeGenreFilter, setActiveGenreFilter] = useState('All');
  const [initialSearchQuery, setInitialSearchQuery] = useState('');

  const watchlistState = useWatchlist();
  const {
    user,
    login,
    logout,
    watchlist,
    watched,
    liked,
    country,
    setCountry,
    hasOnboarded,
    favoriteGenres,
    modelTelemetry,
    trainingToast,
    completeOnboarding,
  } = watchlistState;

  // Show onboarding quiz on initial visit if user hasn't configured taste yet
  useEffect(() => {
    if (!hasOnboarded) {
      const timer = setTimeout(() => {
        setOnboardingOpen(true);
      }, 1000);
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
    if (movie.number_of_seasons || (movie.name && !movie.title)) {
      setSelectedTVId(movie.tmdb_id || movie.id);
    } else {
      setSelectedMovieId(movie.id || movie.tmdb_id);
    }
  };

  const handleSelectSeries = (show) => {
    setSelectedTVId(show.tmdb_id || show.id);
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
    <div className="min-h-screen bg-[#101014] text-[#f8fafc] flex flex-col font-sans selection:bg-[#F04452] selection:text-white relative">
      
      {/* Top Navigation Bar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenSearch={handleOpenSearch}
        watchlistCount={watchlist.length}
        country={country}
        setCountry={setCountry}
        onOpenOnboarding={() => setOnboardingOpen(true)}
        user={user}
        onOpenAuth={() => setAuthModalOpen(true)}
      />

      {/* Main Content Area */}
      <main className="flex-grow">
        {activeTab === 'discover' && (
          <DiscoverPage
            onSelectMovie={handleSelectMovie}
            onSelectSeries={handleSelectSeries}
            onWatchProviders={handleWatchProviders}
            watchlistState={watchlistState}
            onOpenGenre={handleOpenGenre}
          />
        )}

        {activeTab === 'series' && (
          <SeriesPage
            onSelectSeries={handleSelectSeries}
            onWatchProviders={handleWatchProviders}
            watchlistState={watchlistState}
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
          user={user}
          onOpenAuth={() => setAuthModalOpen(true)}
        />
      )}

      {/* TV Series Details Modal */}
      {selectedTVId && (
        <TVDetailModal
          tvId={selectedTVId}
          onClose={() => setSelectedTVId(null)}
          country={country}
          setCountry={setCountry}
          user={user}
          onOpenAuth={() => setAuthModalOpen(true)}
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

      {/* User Auth / Profile Modal */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        user={user}
        onLoginSuccess={(userData) => login(userData.username, userData.email, userData.avatar)}
        onLogout={logout}
        onOpenMCQ={() => setOnboardingOpen(true)}
        stats={{
          watchlistCount: watchlist.length,
          watchedCount: watched.length,
          likedCount: liked.length,
        }}
        modelTelemetry={modelTelemetry}
      />

      {/* Personalization MCQ Quiz Modal */}
      <PersonalizationQuizModal
        isOpen={onboardingOpen}
        onClose={() => setOnboardingOpen(false)}
        initialGenres={favoriteGenres}
        watchedIds={watched}
        onComplete={completeOnboarding}
        onSelectMovie={handleSelectMovie}
        onWatchProviders={handleWatchProviders}
      />

      {/* Continuous Learning Retraining Floating Toast */}
      {trainingToast && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2.5 px-4 py-3 rounded-2xl bg-[#181828]/95 border border-[#3b82f6]/40 text-white text-xs font-semibold shadow-2xl backdrop-blur-md animate-in slide-in-from-bottom-5 duration-300">
          <div className="w-6 h-6 rounded-lg bg-[#3b82f6]/20 flex items-center justify-center">
            <Zap className="w-3.5 h-3.5 text-[#60a5fa] animate-pulse" />
          </div>
          <span>{trainingToast.message}</span>
        </div>
      )}

      {/* Footer */}
      <Footer onOpenOnboarding={() => setOnboardingOpen(true)} />

    </div>
  );
}
