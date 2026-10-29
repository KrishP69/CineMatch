import React, { useState, useEffect } from 'react';
import {
  X, Star, Plus, Check, Heart, Eye, Tv, ExternalLink, Calendar,
  Clock, User, Film, Sparkles, Globe, AlertCircle, Share2
} from 'lucide-react';
import { api } from '../services/api';
import MovieCard from './MovieCard';

const COUNTRIES = [
  { code: 'IN', name: 'India', flag: '🇮🇳' },
  { code: 'US', name: 'United States', flag: '🇺🇸' },
  { code: 'GB', name: 'United Kingdom', flag: '🇬🇧' },
  { code: 'CA', name: 'Canada', flag: '🇨🇦' },
  { code: 'AU', name: 'Australia', flag: '🇦🇺' },
];

export default function MovieDetailModal({
  movieId,
  onClose,
  country = 'IN',
  setCountry,
  watchlist = [],
  onToggleWatchlist,
  watched = [],
  onToggleWatched,
  liked = [],
  onToggleLiked,
  onSelectMovie,
}) {
  const [movie, setMovie] = useState(null);
  const [providers, setProviders] = useState(null);
  const [similarMovies, setSimilarMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!movieId) return;

    let isMounted = true;
    setLoading(true);

    api.getMovieDetail(movieId, country)
      .then((res) => {
        if (isMounted && res.success) {
          setMovie(res.movie);
          setProviders(res.watch_providers);
          setSimilarMovies(res.similar_movies || []);
        }
      })
      .catch((err) => {
        console.error('Failed to load movie details:', err);
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [movieId, country]);

  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!movieId) return null;

  const inWatchlist = movie ? watchlist.some(m => m.id === movie.id) : false;
  const isWatched = movie ? watched.includes(movie.id) : false;
  const isLiked = movie ? liked.includes(movie.id) : false;

  const handleShare = () => {
    if (navigator.clipboard && movie) {
      navigator.clipboard.writeText(window.location.origin + `?movie=${movie.id}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const selectedCountry = COUNTRIES.find(c => c.code === country) || COUNTRIES[0];

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/85 backdrop-blur-md flex items-center justify-center p-3 sm:p-5 md:p-8 animate-in fade-in duration-200">
      
      {/* Click outside to close */}
      <div className="fixed inset-0" onClick={onClose} />

      {/* Modal Container */}
      <div className="relative z-10 w-full max-w-4xl bg-[#14141e] border border-[#2c2c3c] rounded-2xl md:rounded-3xl shadow-2xl overflow-hidden max-h-[92vh] flex flex-col my-auto">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-30 w-9 h-9 rounded-full bg-black/70 hover:bg-black text-white flex items-center justify-center transition-colors cursor-pointer border border-white/10"
          aria-label="Close modal"
        >
          <X className="w-5 h-5" />
        </button>

        {loading || !movie ? (
          <div className="p-12 flex flex-col items-center justify-center min-h-[450px]">
            <div className="w-12 h-12 border-3 border-[#F04452] border-t-transparent rounded-full animate-spin mb-4" />
            <p className="text-sm text-[#94a3b8]">Loading movie intelligence...</p>
          </div>
        ) : (
          <div className="overflow-y-auto flex-grow no-scrollbar">
            
            {/* Header Backdrop Banner */}
            <div className="relative w-full h-[220px] sm:h-[300px] md:h-[340px] bg-[#1a1a24]">
              <img
                src={movie.backdrop_path || movie.poster_path}
                alt={movie.title}
                className="w-full h-full object-cover filter brightness-50"
                onError={(e) => {
                  e.currentTarget.src = 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1200&q=80';
                }}
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#14141e] via-[#14141e]/50 to-transparent" />
              
              {/* Floating Title on Backdrop */}
              <div className="absolute bottom-6 left-6 right-6 flex items-end justify-between">
                <div>
                  <h1 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-white tracking-tight drop-shadow-md">
                    {movie.title}
                  </h1>
                  {movie.tagline && (
                    <p className="text-sm text-[#F04452] font-medium italic mt-1 drop-shadow">
                      "{movie.tagline}"
                    </p>
                  )}
                </div>

                <button
                  onClick={handleShare}
                  className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-black/60 hover:bg-black/90 text-xs text-[#cbd5e1] border border-white/10 transition-colors cursor-pointer"
                >
                  <Share2 className="w-3.5 h-3.5" />
                  {copied ? 'Link Copied!' : 'Share'}
                </button>
              </div>
            </div>

            {/* Modal Body */}
            <div className="p-6 sm:p-8">
              
              {/* Top Meta Attributes Bar */}
              <div className="flex flex-wrap items-center gap-3 pb-6 border-b border-[#242434] mb-6">
                
                {/* TMDB Rating */}
                <div className="flex items-center gap-1.5 bg-[#1e1e2c] px-3 py-1 rounded-lg border border-[#303044]">
                  <Star className="w-4 h-4 fill-[#fbbf24] text-[#fbbf24]" />
                  <span className="text-sm font-bold text-white">{Number(movie.vote_average || 8).toFixed(1)}</span>
                  <span className="text-[10px] text-[#94a3b8] font-semibold uppercase">TMDB</span>
                </div>

                {/* IMDb Rating */}
                {movie.imdb_rating && (
                  <div className="flex items-center gap-1.5 bg-[#f5c518]/15 px-3 py-1 rounded-lg border border-[#f5c518]/30">
                    <span className="text-xs font-black text-[#f5c518]">IMDb</span>
                    <span className="text-sm font-bold text-white">{movie.imdb_rating}</span>
                  </div>
                )}

                {/* Year */}
                <div className="flex items-center gap-1 text-xs text-[#cbd5e1] bg-[#1e1e2c] px-3 py-1 rounded-lg border border-[#303044]">
                  <Calendar className="w-3.5 h-3.5 text-[#94a3b8]" />
                  <span>{movie.release_year || movie.release_date?.split('-')[0]}</span>
                </div>

                {/* Runtime */}
                {movie.runtime && (
                  <div className="flex items-center gap-1 text-xs text-[#cbd5e1] bg-[#1e1e2c] px-3 py-1 rounded-lg border border-[#303044]">
                    <Clock className="w-3.5 h-3.5 text-[#94a3b8]" />
                    <span>{Math.floor(movie.runtime / 60)}h {movie.runtime % 60}m</span>
                  </div>
                )}

                {/* Genre badges */}
                <div className="flex flex-wrap gap-1.5 ml-auto">
                  {(movie.genres || []).map((genre) => (
                    <span
                      key={genre}
                      className="text-xs bg-[#222232] text-[#94a3b8] px-2.5 py-0.8 rounded-md border border-[#323246]"
                    >
                      {genre}
                    </span>
                  ))}
                </div>
              </div>

              {/* Two Column Layout: Actions & Details */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
                
                {/* Left Column: Poster & Quick Controls */}
                <div className="flex flex-col items-center sm:items-start">
                  <div className="w-[190px] aspect-[2/3] rounded-2xl overflow-hidden shadow-xl border border-[#2e2e40] mb-4 bg-[#1a1a24]">
                    <img
                      src={movie.poster_path}
                      alt={movie.title}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.currentTarget.src = 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=400&q=80';
                      }}
                    />
                  </div>

                  {/* Actions Tray */}
                  <div className="w-full max-w-[190px] flex flex-col gap-2">
                    <button
                      onClick={() => onToggleWatchlist(movie)}
                      className={`w-full py-2.5 px-3 rounded-xl border text-xs font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                        inWatchlist
                          ? 'bg-[#10b981]/20 border-[#10b981] text-[#10b981]'
                          : 'bg-[#F04452] hover:bg-[#d63340] border-[#F04452] text-white shadow-md shadow-[#F04452]/20'
                      }`}
                    >
                      {inWatchlist ? <Check className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
                      {inWatchlist ? 'In Watchlist' : 'Add to Watchlist'}
                    </button>

                    <div className="grid grid-cols-2 gap-2">
                      <button
                        onClick={() => onToggleWatched(movie.id)}
                        className={`py-2 px-2 rounded-xl border text-xs font-medium flex items-center justify-center gap-1.5 transition-colors cursor-pointer ${
                          isWatched
                            ? 'bg-[#3b82f6]/20 border-[#3b82f6] text-[#3b82f6]'
                            : 'bg-[#1e1e2c] hover:bg-[#28283c] border-[#303044] text-[#cbd5e1]'
                        }`}
                        title="Mark as Watched"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        {isWatched ? 'Watched' : 'Seen'}
                      </button>

                      <button
                        onClick={() => onToggleLiked(movie.id)}
                        className={`py-2 px-2 rounded-xl border text-xs font-medium flex items-center justify-center gap-1.5 transition-colors cursor-pointer ${
                          isLiked
                            ? 'bg-[#ec4899]/20 border-[#ec4899] text-[#ec4899]'
                            : 'bg-[#1e1e2c] hover:bg-[#28283c] border-[#303044] text-[#cbd5e1]'
                        }`}
                        title="Like movie for AI recommendations"
                      >
                        <Heart className={`w-3.5 h-3.5 ${isLiked ? 'fill-current' : ''}`} />
                        {isLiked ? 'Liked' : 'Like'}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Right Column: Overview, Cast, Director */}
                <div className="md:col-span-2 flex flex-col justify-between">
                  <div>
                    <h2 className="text-sm font-bold uppercase tracking-wider text-[#94a3b8] mb-2">
                      Synopsis
                    </h2>
                    <p className="text-sm sm:text-base text-[#e2e8f0] leading-relaxed mb-6 font-normal">
                      {movie.overview}
                    </p>

                    {/* Director */}
                    {movie.director && (
                      <div className="mb-4">
                        <span className="text-xs text-[#94a3b8] font-semibold block mb-1">DIRECTOR</span>
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-[#1e1e2c] border border-[#2e2e40] text-xs font-medium text-white">
                          <User className="w-3.5 h-3.5 text-[#F04452]" />
                          <span>{movie.director}</span>
                        </div>
                      </div>
                    )}

                    {/* Top Cast */}
                    {movie.cast && movie.cast.length > 0 && (
                      <div className="mb-4">
                        <span className="text-xs text-[#94a3b8] font-semibold block mb-1.5">STARRING CAST</span>
                        <div className="flex flex-wrap gap-1.5">
                          {movie.cast.map((actor) => (
                            <span
                              key={actor}
                              className="text-xs bg-[#1a1a26] text-[#cbd5e1] px-2.5 py-1 rounded-lg border border-[#2b2b3a]"
                            >
                              {actor}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Keywords */}
                    {movie.keywords && movie.keywords.length > 0 && (
                      <div>
                        <span className="text-xs text-[#64748b] font-semibold block mb-1.5">THEMES & KEYWORDS</span>
                        <div className="flex flex-wrap gap-1">
                          {movie.keywords.slice(0, 6).map((kw) => (
                            <span
                              key={kw}
                              className="text-[11px] text-[#94a3b8] bg-[#161622] px-2 py-0.5 rounded border border-[#262634]"
                            >
                              #{kw}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

              </div>

              {/* ========================================================== */}
              {/* WHERE TO WATCH (LEGAL OTT STREAMING SECTION)               */}
              {/* ========================================================== */}
              <div className="mt-8 pt-8 border-t border-[#242434]">
                <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-xl bg-[#F04452]/20 border border-[#F04452]/30 flex items-center justify-center">
                      <Tv className="w-4 h-4 text-[#F04452]" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        Where to Watch
                        <span className="text-[10px] font-semibold text-[#10b981] bg-[#10b981]/15 px-2 py-0.5 rounded-full uppercase">
                          Authorized OTT
                        </span>
                      </h3>
                      <p className="text-xs text-[#94a3b8]">
                        Official legal streaming availability in {selectedCountry.name}
                      </p>
                    </div>
                  </div>

                  {/* Country Selector */}
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-[#94a3b8] flex items-center gap-1">
                      <Globe className="w-3.5 h-3.5" />
                      Region:
                    </span>
                    <select
                      value={country}
                      onChange={(e) => setCountry(e.target.value)}
                      className="bg-[#1e1e2c] text-xs font-semibold text-white px-2.5 py-1.5 rounded-xl border border-[#323246] focus:outline-none focus:border-[#F04452] cursor-pointer"
                    >
                      {COUNTRIES.map(c => (
                        <option key={c.code} value={c.code}>
                          {c.flag} {c.name} ({c.code})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* OTT Provider Listings */}
                {providers ? (
                  <div className="space-y-4">
                    
                    {/* 1. Subscription / Flatrate */}
                    {providers.subscription && providers.subscription.length > 0 && (
                      <div>
                        <h4 className="text-xs font-bold text-[#94a3b8] uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                          <span className="w-2 h-2 rounded-full bg-[#10b981]" />
                          Stream with Subscription
                        </h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                          {providers.subscription.map((p, idx) => (
                            <a
                              key={idx}
                              href={p.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center justify-between p-3 rounded-xl bg-[#1a1a26] hover:bg-[#222234] border border-[#2c2c3e] hover:border-[#F04452] transition-all group/prov shadow-sm"
                            >
                              <div className="flex items-center gap-3">
                                {p.logo ? (
                                  <img
                                    src={p.logo}
                                    alt={p.name}
                                    className="w-8 h-8 rounded-lg object-cover shadow"
                                    onError={(e) => { e.currentTarget.style.display = 'none'; }}
                                  />
                                ) : (
                                  <div className="w-8 h-8 rounded-lg bg-[#2a2a3e] flex items-center justify-center font-bold text-xs text-white">
                                    {p.name.charAt(0)}
                                  </div>
                                )}
                                <div>
                                  <p className="text-xs font-bold text-white group-hover/prov:text-[#F04452] transition-colors">
                                    {p.name}
                                  </p>
                                  <span className="text-[10px] text-[#10b981] font-medium">Included</span>
                                </div>
                              </div>

                              <span className="flex items-center gap-1 text-xs font-semibold text-[#F04452] bg-[#F04452]/10 px-2.5 py-1 rounded-lg group-hover/prov:bg-[#F04452] group-hover/prov:text-white transition-all">
                                Watch
                                <ExternalLink className="w-3 h-3" />
                              </span>
                            </a>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 2. Rent / Buy Options */}
                    {(providers.rent?.length > 0 || providers.buy?.length > 0) && (
                      <div>
                        <h4 className="text-xs font-bold text-[#94a3b8] uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                          <span className="w-2 h-2 rounded-full bg-[#38bdf8]" />
                          Rent or Buy
                        </h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                          {[...(providers.rent || []), ...(providers.buy || [])].slice(0, 4).map((p, idx) => (
                            <a
                              key={idx}
                              href={p.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center justify-between p-3 rounded-xl bg-[#181824] hover:bg-[#202030] border border-[#28283a] hover:border-[#38bdf8] transition-all group/prov"
                            >
                              <div className="flex items-center gap-3">
                                {p.logo && (
                                  <img
                                    src={p.logo}
                                    alt={p.name}
                                    className="w-7 h-7 rounded-lg object-cover"
                                    onError={(e) => { e.currentTarget.style.display = 'none'; }}
                                  />
                                )}
                                <div>
                                  <p className="text-xs font-semibold text-white">
                                    {p.name}
                                  </p>
                                  <span className="text-[10px] text-[#94a3b8]">
                                    {p.type} {p.price ? `(${p.price})` : ''}
                                  </span>
                                </div>
                              </div>
                              <ExternalLink className="w-3.5 h-3.5 text-[#94a3b8] group-hover/prov:text-white transition-colors" />
                            </a>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 3. Fallback when not indexed or unavailable */}
                    {!providers.has_availability && (
                      <div className="p-4 rounded-xl bg-[#1a1a26] border border-[#2d2d3e]">
                        <div className="flex items-center gap-2 text-xs text-[#cbd5e1] mb-3">
                          <AlertCircle className="w-4 h-4 text-[#fbbf24] flex-shrink-0" />
                          <span>
                            Direct subscription data for <strong>{selectedCountry.name}</strong> is not listed yet.
                            Explore verified streaming search links:
                          </span>
                        </div>

                        <div className="flex flex-wrap gap-2">
                          {(providers.fallback_search_links || []).map((link, idx) => (
                            <a
                              key={idx}
                              href={link.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#222234] hover:bg-[#2c2c42] border border-[#34344c] text-xs font-medium text-white transition-colors"
                            >
                              <span>{link.name}</span>
                              <ExternalLink className="w-3 h-3 text-[#94a3b8]" />
                            </a>
                          ))}

                          <a
                            href={providers.justwatch_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#fbbf24]/15 hover:bg-[#fbbf24]/25 border border-[#fbbf24]/30 text-xs font-semibold text-[#fbbf24] transition-colors"
                          >
                            <span>Check on JustWatch ↗</span>
                          </a>
                        </div>
                      </div>
                    )}

                  </div>
                ) : (
                  <p className="text-xs text-[#94a3b8]">Checking streaming providers...</p>
                )}
              </div>

              {/* ========================================================== */}
              {/* MACHINE LEARNING "MORE LIKE THIS" RECOMMENDATIONS          */}
              {/* ========================================================== */}
              {similarMovies && similarMovies.length > 0 && (
                <div className="mt-10 pt-8 border-t border-[#242434]">
                  <div className="flex items-center gap-2 mb-4">
                    <Sparkles className="w-4 h-4 text-[#fbbf24]" />
                    <h3 className="text-lg font-bold text-white">
                      More Like This
                    </h3>
                    <span className="text-[11px] text-[#94a3b8] ml-2">
                      Calculated via TF-IDF Cosine Similarity
                    </span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 sm:gap-4">
                    {similarMovies.slice(0, 6).map((simMovie) => (
                      <div
                        key={simMovie.id}
                        onClick={() => onSelectMovie(simMovie)}
                        className="group/card bg-[#181824] rounded-xl overflow-hidden border border-[#28283a] hover:border-[#F04452] transition-all cursor-pointer p-2 flex flex-col justify-between"
                      >
                        <div className="relative aspect-[2/3] rounded-lg overflow-hidden mb-2 bg-[#20202e]">
                          <img
                            src={simMovie.poster_path}
                            alt={simMovie.title}
                            className="w-full h-full object-cover group-hover/card:scale-105 transition-transform"
                            onError={(e) => {
                              e.currentTarget.src = 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=400&q=80';
                            }}
                          />
                          {simMovie.similarity_score && (
                            <div className="absolute top-1.5 right-1.5 bg-[#F04452] text-white text-[9px] font-extrabold px-1.5 py-0.5 rounded">
                              {Math.round(simMovie.similarity_score * 100)}%
                            </div>
                          )}
                        </div>
                        <div>
                          <p className="text-xs font-semibold text-white line-clamp-1 group-hover/card:text-[#F04452] transition-colors">
                            {simMovie.title}
                          </p>
                          <p className="text-[10px] text-[#94a3b8]">
                            ★ {Number(simMovie.vote_average || 8).toFixed(1)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </div>
          </div>
        )}

      </div>
    </div>
  );
}
