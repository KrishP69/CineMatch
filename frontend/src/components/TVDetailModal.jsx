import React, { useState, useEffect } from 'react';
import {
  X, Star, Plus, Check, Tv, ExternalLink, Calendar,
  Clock, User, Film, Sparkles, Globe, AlertCircle, Share2,
  ThumbsUp, ThumbsDown, Flag, MessageSquare,
  CheckCircle2, Play, Bookmark, Eye, ListFilter
} from 'lucide-react';
import { api } from '../services/api';

const COUNTRIES = [
  { code: 'IN', name: 'India', flag: '🇮🇳' },
  { code: 'US', name: 'United States', flag: '🇺🇸' },
  { code: 'GB', name: 'United Kingdom', flag: '🇬🇧' },
  { code: 'CA', name: 'Canada', flag: '🇨🇦' },
  { code: 'AU', name: 'Australia', flag: '🇦🇺' },
];

export default function TVDetailModal({
  tvId,
  onClose,
  country = 'IN',
  setCountry = () => {},
  user = null,
  onOpenAuth = () => {},
}) {
  const [show, setShow] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  // Watch Progress State
  const [watchProgress, setWatchProgress] = useState({
    status: 'plan_to_watch',
    watched_season: 1,
    watched_episode: 0,
    last_watched_episode: ''
  });
  const [isSavedInWatchlist, setIsSavedInWatchlist] = useState(false);
  const [progressSaving, setProgressSaving] = useState(false);

  // Seasons & Episodes State
  const [seasons, setSeasons] = useState([]);
  const [activeSeasonNum, setActiveSeasonNum] = useState(1);
  const [seasonEpisodes, setSeasonEpisodes] = useState([]);
  const [episodesLoading, setEpisodesLoading] = useState(false);

  // Ratings & Reviews State
  const [ratingsSummary, setRatingsSummary] = useState(null);
  const [reviewsData, setReviewsData] = useState({ reviews: [], total: 0 });
  const [reviewsLoading, setReviewsLoading] = useState(false);
  const [reviewSort, setReviewSort] = useState('most_helpful');
  const [hoverRating, setHoverRating] = useState(0);

  // Review Form
  const [isWritingReview, setIsWritingReview] = useState(false);
  const [formTitle, setFormTitle] = useState('');
  const [formContent, setFormContent] = useState('');
  const [formRating, setFormRating] = useState(9);
  const [formSpoilers, setFormSpoilers] = useState(false);
  const [submittingReview, setSubmittingReview] = useState(false);
  const [reviewMsg, setReviewMsg] = useState(null);

  // Load TV Show Details
  useEffect(() => {
    if (!tvId) return;
    let isMounted = true;
    setLoading(true);
    setError(null);

    api.getTVDetail(tvId, country)
      .then((res) => {
        if (!isMounted) return;
        if (res.success && res.data) {
          setShow(res.data);
          setSeasons(res.data.seasons || []);
          if (res.data.user_progress) {
            setWatchProgress(res.data.user_progress);
          }
          if (res.data.community_ratings) {
            setRatingsSummary(res.data.community_ratings);
          }
          const validSeason = (res.data.seasons || []).find(s => s.season_number > 0) || res.data.seasons?.[0];
          if (validSeason) {
            setActiveSeasonNum(validSeason.season_number);
          }
        } else {
          setError(res.error || 'Failed to load show details');
        }
      })
      .catch((err) => {
        if (isMounted) setError(err.message || 'Error fetching show');
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => { isMounted = false; };
  }, [tvId, country]);

  // Check if saved in watchlist if user logged in
  useEffect(() => {
    if (!user || !tvId) return;
    api.getUserTVWatchlist()
      .then((res) => {
        if (res.success && Array.isArray(res.data)) {
          setIsSavedInWatchlist(res.data.some(s => s.tmdb_id === tvId || s.id === tvId));
        }
      })
      .catch(() => {});
  }, [user, tvId]);

  // Load Episodes for Active Season
  useEffect(() => {
    if (!tvId || !activeSeasonNum) return;
    let isMounted = true;
    setEpisodesLoading(true);

    api.getTVSeasonEpisodes(tvId, activeSeasonNum)
      .then((res) => {
        if (!isMounted) return;
        if (res.success && res.season && res.season.episodes) {
          setSeasonEpisodes(res.season.episodes);
        } else {
          setSeasonEpisodes([]);
        }
      })
      .catch(() => {
        if (isMounted) setSeasonEpisodes([]);
      })
      .finally(() => {
        if (isMounted) setEpisodesLoading(false);
      });

    return () => { isMounted = false; };
  }, [tvId, activeSeasonNum]);

  // Load Reviews
  const loadReviews = () => {
    if (!tvId) return;
    setReviewsLoading(true);
    api.getTVReviews(tvId, reviewSort)
      .then((res) => {
        if (res.success && res.data) {
          setReviewsData(res.data);
        }
      })
      .catch(() => {})
      .finally(() => setReviewsLoading(false));
  };

  useEffect(() => {
    loadReviews();
  }, [tvId, reviewSort]);

  // Toggle Watchlist
  const handleToggleWatchlist = async () => {
    if (!user) {
      onOpenAuth();
      return;
    }
    try {
      const res = await api.toggleTVWatchlist(tvId);
      if (res.success) {
        setIsSavedInWatchlist(res.in_watchlist);
      }
    } catch (err) {
      console.error('Error toggling TV watchlist:', err);
    }
  };

  // Submit Rating
  const handleRate = async (score) => {
    if (!user) {
      onOpenAuth();
      return;
    }
    try {
      const res = await api.rateTV(tvId, score);
      if (res.success && res.data) {
        setRatingsSummary(res.data);
      }
    } catch (err) {
      console.error('Failed to rate TV show:', err);
    }
  };

  // Update Watch Progress
  const handleUpdateProgress = async (newStatus, season = watchProgress.watched_season, episode = watchProgress.watched_episode, lastEpName = null) => {
    if (!user) {
      onOpenAuth();
      return;
    }
    setProgressSaving(true);
    try {
      const payload = {
        status: newStatus,
        watched_season: season,
        watched_episode: episode,
        last_watched_episode: lastEpName || `S${String(season).padStart(2, '0')}E${String(episode).padStart(2, '0')}`
      };
      const res = await api.updateTVProgress(tvId, payload);
      if (res.success && res.progress) {
        setWatchProgress(res.progress);
      }
    } catch (err) {
      console.error('Failed to update watch progress:', err);
    } finally {
      setProgressSaving(false);
    }
  };

  // Submit Review
  const handleSubmitReview = async (e) => {
    e.preventDefault();
    if (!user) {
      onOpenAuth();
      return;
    }
    if (!formTitle.trim() || !formContent.trim()) return;

    setSubmittingReview(true);
    setReviewMsg(null);
    try {
      const res = await api.submitTVReview(tvId, {
        title: formTitle,
        content: formContent,
        rating: formRating,
        contains_spoilers: formSpoilers
      });
      if (res.success) {
        setReviewMsg({ type: 'success', text: 'Review published successfully!' });
        setFormTitle('');
        setFormContent('');
        setIsWritingReview(false);
        loadReviews();
      } else {
        setReviewMsg({ type: 'error', text: res.error || 'Failed to submit review' });
      }
    } catch (err) {
      setReviewMsg({ type: 'error', text: err.message || 'Submission error' });
    } finally {
      setSubmittingReview(false);
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-in fade-in duration-200">
        <div className="w-full max-w-4xl bg-[#14141c] rounded-3xl border border-[#262638] p-8 space-y-6">
          <div className="w-full h-72 skeleton rounded-2xl" />
          <div className="space-y-3">
            <div className="w-1/3 h-8 skeleton rounded-lg" />
            <div className="w-2/3 h-4 skeleton rounded" />
            <div className="w-1/2 h-4 skeleton rounded" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !show) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md">
        <div className="max-w-md w-full bg-[#161622] border border-[#2a2a3e] p-6 rounded-2xl text-center space-y-4">
          <AlertCircle className="w-12 h-12 text-[#F04452] mx-auto" />
          <h2 className="text-xl font-bold text-white">Show Not Found</h2>
          <p className="text-sm text-[#94a3b8]">{error || 'Unable to retrieve show information.'}</p>
          <button
            onClick={onClose}
            className="px-5 py-2.5 bg-[#F04452] hover:bg-[#d93442] text-white font-bold rounded-xl text-sm transition-colors cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  const formatImg = (path, size = 'original') => {
    if (!path) return 'https://image.tmdb.org/t/p/original/xJHokMbljvjADYdit5fK5VQsXEG.jpg';
    if (path.startsWith('http')) return path;
    const clean = path.startsWith('/') ? path : `/${path}`;
    return `https://image.tmdb.org/t/p/${size}${clean}`;
  };

  const backdropUrl = formatImg(show.backdrop_path || show.poster_path, 'original');
  const posterUrl = formatImg(show.poster_path, 'w500');
  const firstYear = show.first_air_date ? show.first_air_date.split('-')[0] : '2024';
  const lastYear = show.last_air_date ? show.last_air_date.split('-')[0] : firstYear;
  const yearStr = firstYear === lastYear ? firstYear : `${firstYear} – ${lastYear}`;
  const genres = Array.isArray(show.genres) ? show.genres : [];
  const creators = Array.isArray(show.creators) ? show.creators : [];
  const networks = Array.isArray(show.networks) ? show.networks : [];
  const userRating = ratingsSummary?.user_rating;
  const avgRating = ratingsSummary?.community?.average_rating || (show.tmdb_rating ? Number(show.tmdb_rating).toFixed(1) : '8.5');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 md:p-6 bg-black/85 backdrop-blur-md overflow-y-auto animate-in fade-in duration-200">
      <div className="relative w-full max-w-5xl bg-[#14141e] border border-[#28283c] rounded-3xl overflow-hidden shadow-2xl my-auto text-[#f8fafc] max-h-[92vh] flex flex-col">
        
        {/* Floating Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-30 p-2.5 rounded-full bg-black/70 hover:bg-[#F04452] text-white border border-white/20 transition-all cursor-pointer shadow-lg"
          title="Close (Esc)"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Scrollable Container */}
        <div className="overflow-y-auto flex-grow custom-scrollbar">
          
          {/* Hero Backdrop Banner */}
          <div className="relative w-full h-[280px] sm:h-[360px] md:h-[420px] bg-[#1a1a26]">
            <img
              src={backdropUrl}
              alt={show.name}
              className="w-full h-full object-cover object-center filter brightness-65"
              onError={(e) => {
                e.currentTarget.src = posterUrl;
              }}
            />
            <div className="absolute inset-0 bg-gradient-to-t from-[#14141e] via-[#14141e]/50 to-transparent" />
            <div className="absolute inset-0 bg-gradient-to-r from-[#14141e] via-[#14141e]/70 to-transparent w-full md:w-2/3" />

            {/* Poster & Spotlight Overlay Info */}
            <div className="absolute bottom-4 sm:bottom-6 left-4 sm:left-8 right-4 sm:right-8 flex gap-4 sm:gap-6 items-end">
              <div className="hidden sm:block w-32 sm:w-44 aspect-[2/3] rounded-2xl overflow-hidden shadow-2xl border-2 border-white/10 flex-shrink-0 bg-[#161622]">
                <img src={posterUrl} alt={show.name} className="w-full h-full object-cover" />
              </div>

              <div className="flex-grow space-y-2">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="bg-[#6366f1] text-white text-[11px] font-black px-2.5 py-0.8 rounded-md tracking-wider uppercase flex items-center gap-1 shadow">
                    <Tv className="w-3 h-3" />
                    Web Series
                  </span>
                  <span className="bg-black/60 backdrop-blur-md text-[#38bdf8] border border-[#38bdf8]/30 text-xs font-bold px-2.5 py-0.8 rounded-md">
                    {show.status || 'Active'}
                  </span>
                  <div className="flex items-center gap-1 bg-black/60 backdrop-blur-md border border-white/10 text-white text-xs font-bold px-2.5 py-0.8 rounded-md">
                    <Star className="w-3.5 h-3.5 fill-[#fbbf24] text-[#fbbf24]" />
                    <span>{avgRating}</span>
                  </div>
                  <div className="flex items-center gap-1 bg-black/60 backdrop-blur-md border border-white/10 text-[#cbd5e1] text-xs font-medium px-2.5 py-0.8 rounded-md">
                    <Calendar className="w-3.5 h-3.5 text-[#94a3b8]" />
                    <span>{yearStr}</span>
                  </div>
                  <div className="text-xs text-[#cbd5e1] bg-black/60 backdrop-blur-md border border-white/10 px-2.5 py-0.8 rounded-md font-semibold">
                    {show.number_of_seasons || seasons.length} Season{show.number_of_seasons > 1 ? 's' : ''} • {show.number_of_episodes || 'Multiple'} Episodes
                  </div>
                </div>

                <h1 className="text-2xl sm:text-4xl md:text-5xl font-black text-white tracking-tight drop-shadow-md">
                  {show.name}
                </h1>
                {show.original_name && show.original_name !== show.name && (
                  <p className="text-xs text-[#94a3b8] italic">Original: {show.original_name}</p>
                )}

                {/* Genre Tags */}
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {genres.map((g) => (
                    <span key={g} className="text-xs bg-[#202030]/80 text-[#cbd5e1] px-2.5 py-0.5 rounded-full border border-white/10 font-medium">
                      {typeof g === 'object' ? g.name : g}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Body Content */}
          <div className="p-4 sm:p-8 space-y-8">
            
            {/* Quick Actions Tray & Watch Progress Tracker */}
            <div className="p-4 sm:p-5 rounded-2xl bg-[#1a1a28] border border-[#2c2c42] flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 shadow-lg">
              
              {/* Watchlist & Share */}
              <div className="flex items-center gap-2.5">
                <button
                  onClick={handleToggleWatchlist}
                  className={`px-4 py-2.5 rounded-xl font-bold text-xs sm:text-sm flex items-center gap-2 transition-all cursor-pointer ${
                    isSavedInWatchlist
                      ? 'bg-[#F04452] text-white shadow-lg shadow-[#F04452]/20'
                      : 'bg-[#262638] hover:bg-[#F04452] text-white border border-white/10'
                  }`}
                >
                  {isSavedInWatchlist ? <Check className="w-4 h-4" /> : <Bookmark className="w-4 h-4" />}
                  <span>{isSavedInWatchlist ? 'In Watchlist' : 'Add to Watchlist'}</span>
                </button>

                <button
                  onClick={() => {
                    navigator.clipboard.writeText(window.location.href);
                    setCopied(true);
                    setTimeout(() => setCopied(false), 2000);
                  }}
                  className="p-2.5 rounded-xl bg-[#262638] hover:bg-[#32324a] text-[#cbd5e1] border border-white/10 transition-colors cursor-pointer"
                  title="Copy Link"
                >
                  <Share2 className="w-4 h-4" />
                </button>
                {copied && <span className="text-xs text-[#10b981] font-bold">Copied!</span>}
              </div>

              {/* Watch Progress Status Selector */}
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-[#94a3b8]">Status:</span>
                {[
                  { id: 'watching', label: 'Watching', color: 'bg-[#3b82f6]' },
                  { id: 'completed', label: 'Completed', color: 'bg-[#10b981]' },
                  { id: 'plan_to_watch', label: 'Plan to Watch', color: 'bg-[#8b5cf6]' },
                  { id: 'dropped', label: 'Dropped', color: 'bg-[#64748b]' },
                ].map((s) => (
                  <button
                    key={s.id}
                    onClick={() => handleUpdateProgress(s.id)}
                    disabled={progressSaving}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                      watchProgress.status === s.id
                        ? `${s.color} text-white shadow-md`
                        : 'bg-[#222232] text-[#94a3b8] hover:text-white border border-white/5'
                    }`}
                  >
                    {s.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Synopsis & Creators */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="md:col-span-2 space-y-3">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Film className="w-4 h-4 text-[#F04452]" />
                  Overview
                </h3>
                <p className="text-sm sm:text-base text-[#cbd5e1] leading-relaxed">
                  {show.overview || 'No synopsis available for this title.'}
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-[#181824] border border-[#26263a] space-y-3 text-xs">
                {creators.length > 0 && (
                  <div>
                    <span className="text-[#94a3b8] uppercase font-bold tracking-wider block mb-1">Created By</span>
                    <span className="text-white font-medium">{creators.join(', ')}</span>
                  </div>
                )}
                {networks.length > 0 && (
                  <div>
                    <span className="text-[#94a3b8] uppercase font-bold tracking-wider block mb-1">Network</span>
                    <span className="text-white font-medium">{networks.join(', ')}</span>
                  </div>
                )}
                <div>
                  <span className="text-[#94a3b8] uppercase font-bold tracking-wider block mb-1">Original Language</span>
                  <span className="text-white font-medium uppercase">{show.original_language || 'EN'}</span>
                </div>
              </div>
            </div>

            {/* SEASONS & EPISODES ACCORDION */}
            <div className="space-y-4 pt-2">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-black text-white flex items-center gap-2">
                  <ListFilter className="w-5 h-5 text-[#6366f1]" />
                  Seasons & Episodes
                </h3>
                {watchProgress.last_watched_episode && (
                  <span className="text-xs bg-[#3b82f6]/20 text-[#60a5fa] border border-[#3b82f6]/40 px-2.5 py-1 rounded-lg font-bold">
                    Currently at: {watchProgress.last_watched_episode}
                  </span>
                )}
              </div>

              {/* Season Selection Pills */}
              <div className="flex gap-2 overflow-x-auto pb-2 custom-scrollbar">
                {seasons.map((s) => (
                  <button
                    key={s.id || s.season_number}
                    onClick={() => setActiveSeasonNum(s.season_number)}
                    className={`px-4 py-2 rounded-xl text-xs font-bold flex-shrink-0 transition-all cursor-pointer ${
                      activeSeasonNum === s.season_number
                        ? 'bg-[#6366f1] text-white shadow-lg shadow-[#6366f1]/25'
                        : 'bg-[#1a1a28] hover:bg-[#252538] text-[#cbd5e1] border border-white/5'
                    }`}
                  >
                    {s.name || `Season ${s.season_number}`}
                    {s.episode_count ? ` (${s.episode_count} eps)` : ''}
                  </button>
                ))}
              </div>

              {/* Episodes List */}
              <div className="space-y-3 pt-2">
                {episodesLoading ? (
                  <div className="space-y-3">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="h-20 skeleton rounded-2xl" />
                    ))}
                  </div>
                ) : seasonEpisodes.length > 0 ? (
                  seasonEpisodes.map((ep) => {
                    const epCode = `S${String(activeSeasonNum).padStart(2, '0')}E${String(ep.episode_number).padStart(2, '0')}`;
                    const isWatched = watchProgress.watched_season > activeSeasonNum ||
                      (watchProgress.watched_season === activeSeasonNum && watchProgress.watched_episode >= ep.episode_number);

                    return (
                      <div
                        key={ep.id || ep.episode_number}
                        className={`p-3 sm:p-4 rounded-2xl border transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 ${
                          isWatched
                            ? 'bg-[#181d28]/70 border-[#2563eb]/40'
                            : 'bg-[#161622] hover:bg-[#1a1a2a] border-[#262638]'
                        }`}
                      >
                        <div className="flex items-start sm:items-center gap-3.5 flex-grow">
                          {/* Episode Still / Thumbnail */}
                          <div className="w-20 sm:w-28 aspect-video rounded-xl overflow-hidden bg-[#222234] flex-shrink-0 relative">
                            {ep.still_path ? (
                              <img src={formatImg(ep.still_path, 'w500')} alt={ep.name} className="w-full h-full object-cover" />
                            ) : (
                              <div className="w-full h-full flex items-center justify-center text-[#64748b]">
                                <Play className="w-5 h-5" />
                              </div>
                            )}
                            <div className="absolute top-1 left-1 bg-black/80 px-1.5 py-0.5 rounded text-[10px] font-bold text-white">
                              {ep.episode_number}
                            </div>
                          </div>

                          {/* Episode Details */}
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-black text-[#6366f1]">{epCode}</span>
                              <h4 className="text-sm font-bold text-white tracking-tight">{ep.name}</h4>
                            </div>
                            <div className="flex items-center gap-2 text-[11px] text-[#94a3b8]">
                              {ep.air_date && <span>{ep.air_date}</span>}
                              {ep.runtime && <span>• {ep.runtime} min</span>}
                              {ep.vote_average > 0 && (
                                <span className="flex items-center gap-0.5 text-[#fbbf24]">
                                  • ★ {Number(ep.vote_average).toFixed(1)}
                                </span>
                              )}
                            </div>
                            {ep.overview && (
                              <p className="text-xs text-[#cbd5e1] line-clamp-2 max-w-2xl">{ep.overview}</p>
                            )}
                          </div>
                        </div>

                        {/* Mark Watched Button */}
                        <button
                          onClick={() => handleUpdateProgress('watching', activeSeasonNum, ep.episode_number, `${epCode} - ${ep.name}`)}
                          className={`px-3 py-1.8 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all flex-shrink-0 cursor-pointer ${
                            isWatched
                              ? 'bg-[#2563eb]/20 text-[#60a5fa] border border-[#2563eb]/40'
                              : 'bg-[#262638] hover:bg-[#2563eb] text-white border border-white/10'
                          }`}
                        >
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>{isWatched ? 'Watched' : 'Mark Watched'}</span>
                        </button>
                      </div>
                    );
                  })
                ) : (
                  <p className="text-sm text-[#94a3b8] italic p-4 bg-[#181824] rounded-xl text-center">
                    No episode records found for this season.
                  </p>
                )}
              </div>
            </div>

            {/* RATINGS & REVIEWS SECTION */}
            <div className="space-y-6 pt-4 border-t border-[#262638]">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <h3 className="text-lg font-black text-white flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-[#F04452]" />
                    Audience Reviews & Community Score
                  </h3>
                  <p className="text-xs text-[#94a3b8]">Share your thoughts with CineMatch enthusiasts</p>
                </div>

                {/* Rating Input */}
                <div className="flex items-center gap-2 bg-[#1a1a28] px-4 py-2 rounded-2xl border border-[#2c2c42]">
                  <span className="text-xs font-bold text-[#cbd5e1]">Your Rating:</span>
                  <div className="flex items-center gap-1">
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((star) => (
                      <button
                        key={star}
                        onClick={() => handleRate(star)}
                        onMouseEnter={() => setHoverRating(star)}
                        onMouseLeave={() => setHoverRating(0)}
                        className="p-0.5 text-xs focus:outline-none cursor-pointer"
                        title={`Rate ${star}/10`}
                      >
                        <Star
                          className={`w-4 h-4 transition-colors ${
                            star <= (hoverRating || userRating || 0)
                              ? 'fill-[#fbbf24] text-[#fbbf24]'
                              : 'text-[#475569]'
                          }`}
                        />
                      </button>
                    ))}
                  </div>
                  {userRating && (
                    <span className="text-xs font-bold text-[#fbbf24] ml-1">{userRating}/10</span>
                  )}
                </div>
              </div>

              {/* Review Write Button */}
              {!isWritingReview ? (
                <button
                  onClick={() => {
                    if (!user) onOpenAuth();
                    else setIsWritingReview(true);
                  }}
                  className="px-5 py-2.5 bg-[#F04452] hover:bg-[#d93442] text-white font-bold rounded-xl text-xs transition-colors cursor-pointer flex items-center gap-2 shadow"
                >
                  <MessageSquare className="w-4 h-4" />
                  Write a Review
                </button>
              ) : (
                <form onSubmit={handleSubmitReview} className="p-5 rounded-2xl bg-[#181826] border border-[#2a2a40] space-y-4">
                  <h4 className="text-sm font-bold text-white">Write Your Review</h4>
                  {reviewMsg && (
                    <div className={`p-3 rounded-xl text-xs font-bold ${reviewMsg.type === 'success' ? 'bg-green-900/40 text-green-300' : 'bg-red-900/40 text-red-300'}`}>
                      {reviewMsg.text}
                    </div>
                  )}
                  <input
                    type="text"
                    placeholder="Headline or summary (e.g., Mindblowing plot twist!)"
                    value={formTitle}
                    onChange={(e) => setFormTitle(e.target.value)}
                    required
                    className="w-full px-4 py-2.5 rounded-xl bg-[#222234] border border-[#34344e] text-white text-xs focus:outline-none focus:border-[#F04452]"
                  />
                  <textarea
                    placeholder="Write your in-depth review here..."
                    rows={4}
                    value={formContent}
                    onChange={(e) => setFormContent(e.target.value)}
                    required
                    className="w-full px-4 py-2.5 rounded-xl bg-[#222234] border border-[#34344e] text-white text-xs focus:outline-none focus:border-[#F04452]"
                  />
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <label className="flex items-center gap-2 text-xs text-[#cbd5e1] cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formSpoilers}
                        onChange={(e) => setFormSpoilers(e.target.checked)}
                        className="rounded accent-[#F04452]"
                      />
                      <span>Contains spoilers</span>
                    </label>

                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => setIsWritingReview(false)}
                        className="px-4 py-2 rounded-xl bg-[#252538] text-[#cbd5e1] text-xs font-bold hover:bg-[#303046] cursor-pointer"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        disabled={submittingReview}
                        className="px-5 py-2 rounded-xl bg-[#F04452] hover:bg-[#d93442] text-white text-xs font-bold transition-colors cursor-pointer"
                      >
                        {submittingReview ? 'Publishing...' : 'Submit Review'}
                      </button>
                    </div>
                  </div>
                </form>
              )}

              {/* Reviews List */}
              <div className="space-y-4 pt-2">
                {reviewsLoading ? (
                  <div className="space-y-3">
                    {[1, 2].map((i) => (
                      <div key={i} className="h-24 skeleton rounded-2xl" />
                    ))}
                  </div>
                ) : reviewsData.reviews && reviewsData.reviews.length > 0 ? (
                  reviewsData.reviews.map((rev) => (
                    <div key={rev.id} className="p-4 rounded-2xl bg-[#161622] border border-[#242436] space-y-2.5">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2.5">
                          <span className="text-xl">{rev.avatar || '🍿'}</span>
                          <div>
                            <span className="text-xs font-bold text-white">{rev.username}</span>
                            <div className="flex items-center gap-2 text-[10px] text-[#94a3b8]">
                              <span>★ {rev.rating}/10</span>
                              {rev.sentiment && (
                                <span className={`px-1.5 py-0.2 rounded font-bold uppercase ${
                                  rev.sentiment === 'positive'
                                    ? 'bg-green-500/10 text-green-400'
                                    : rev.sentiment === 'negative'
                                    ? 'bg-red-500/10 text-red-400'
                                    : 'bg-yellow-500/10 text-yellow-400'
                                }`}>
                                  {rev.sentiment}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>

                      <h4 className="text-sm font-bold text-white">{rev.title}</h4>
                      <p className="text-xs text-[#cbd5e1] leading-relaxed">{rev.content}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-[#94a3b8] italic p-4 bg-[#181824] rounded-xl text-center">
                    No community reviews yet. Be the first to share your thoughts!
                  </p>
                )}
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
}

