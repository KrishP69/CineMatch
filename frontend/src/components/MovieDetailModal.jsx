import React, { useState, useEffect } from 'react';
import {
  X, Star, Plus, Check, Heart, Eye, Tv, ExternalLink, Calendar,
  Clock, User, Film, Sparkles, Globe, AlertCircle, Share2,
  ThumbsUp, ThumbsDown, Flag, MessageSquare, ShieldAlert,
  Send, Trash2, Award, ChevronDown, CheckCircle2
} from 'lucide-react';
import { api } from '../services/api';

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
  user = null,
  onOpenAuth = () => {},
}) {
  const [movie, setMovie] = useState(null);
  const [providers, setProviders] = useState(null);
  const [similarMovies, setSimilarMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  // Community Ratings & Reviews State
  const [ratingsSummary, setRatingsSummary] = useState(null);
  const [reviewsData, setReviewsData] = useState({ reviews: [], external_reviews: [], total: 0 });
  const [reviewsLoading, setReviewsLoading] = useState(false);
  const [reviewSort, setReviewSort] = useState('most_helpful');
  const [hoverRating, setHoverRating] = useState(0);

  // Review Form State
  const [isWritingReview, setIsWritingReview] = useState(false);
  const [formTitle, setFormTitle] = useState('');
  const [formContent, setFormContent] = useState('');
  const [formRating, setFormRating] = useState(8);
  const [formSpoilers, setFormSpoilers] = useState(false);
  const [submittingReview, setSubmittingReview] = useState(false);
  const [reviewError, setReviewError] = useState('');
  const [reviewSuccess, setReviewSuccess] = useState('');

  // Unblurred spoilers set
  const [revealedSpoilers, setRevealedSpoilers] = useState(new Set());

  // Load Movie Details & Ratings
  const fetchMovieData = async () => {
    if (!movieId) return;
    setLoading(true);

    try {
      const res = await api.getMovieDetail(movieId, country);
      if (res.success) {
        setMovie(res.movie);
        setProviders(res.watch_providers);
        setSimilarMovies(res.similar_movies || []);
      }
    } catch (err) {
      console.error('Failed to load movie details:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchRatingsAndReviews = async () => {
    if (!movieId) return;
    setReviewsLoading(true);
    try {
      const [ratingsRes, reviewsRes] = await Promise.all([
        api.getMovieRatings(movieId).catch(() => ({ success: false })),
        api.getMovieReviews(movieId, reviewSort).catch(() => ({ success: false })),
      ]);

      if (ratingsRes.success) setRatingsSummary(ratingsRes.data);
      if (reviewsRes.success) setReviewsData(reviewsRes.data);
    } catch (err) {
      console.error('Failed to load ratings/reviews:', err);
    } finally {
      setReviewsLoading(false);
    }
  };

  useEffect(() => {
    fetchMovieData();
  }, [movieId, country]);

  useEffect(() => {
    fetchRatingsAndReviews();
  }, [movieId, reviewSort]);

  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!movieId) return null;

  const inWatchlist = movie ? watchlist.some((m) => m.id === movie.id) : false;
  const isWatched = movie ? watched.includes(movie.id) : false;
  const isLiked = movie ? liked.includes(movie.id) : false;

  const handleShare = () => {
    if (navigator.clipboard && movie) {
      navigator.clipboard.writeText(window.location.origin + `?movie=${movie.id}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleRate = async (ratingVal) => {
    if (!user || !user.isLoggedIn) {
      onOpenAuth();
      return;
    }
    try {
      const res = await api.rateMovie(movie.id, ratingVal);
      if (res.success) {
        setRatingsSummary(res.data);
      }
    } catch (err) {
      console.error('Error submitting rating:', err);
    }
  };

  const handleDeleteRating = async () => {
    if (!user || !user.isLoggedIn) return;
    try {
      const res = await api.deleteRating(movie.id);
      if (res.success) {
        setRatingsSummary(res.data);
      }
    } catch (err) {
      console.error('Error deleting rating:', err);
    }
  };

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    if (!user || !user.isLoggedIn) {
      onOpenAuth();
      return;
    }

    setReviewError('');
    setReviewSuccess('');
    setSubmittingReview(true);

    try {
      const res = await api.submitReview(movie.id, {
        title: formTitle,
        content: formContent,
        rating: formRating,
        contains_spoilers: formSpoilers,
      });

      if (res.success) {
        setReviewSuccess('Review published successfully with VADER sentiment classification!');
        setFormTitle('');
        setFormContent('');
        setIsWritingReview(false);
        await fetchRatingsAndReviews();
      } else {
        setReviewError(res.error || 'Failed to submit review');
      }
    } catch (err) {
      setReviewError(err.message || 'Error publishing review');
    } finally {
      setSubmittingReview(false);
    }
  };

  const handleVoteReview = async (reviewId, voteType) => {
    if (!user || !user.isLoggedIn) {
      onOpenAuth();
      return;
    }

    try {
      const res = await api.voteReview(reviewId, voteType);
      if (res.success) {
        setReviewsData((prev) => ({
          ...prev,
          reviews: prev.reviews.map((r) =>
            r.id === reviewId
              ? {
                  ...r,
                  helpful_count: res.helpful_count,
                  unhelpful_count: res.unhelpful_count,
                  user_vote: res.user_vote,
                }
              : r
          ),
        }));
      }
    } catch (err) {
      console.error('Failed to vote review:', err);
    }
  };

  const handleReportReview = async (reviewId) => {
    if (!user || !user.isLoggedIn) {
      onOpenAuth();
      return;
    }
    const reason = prompt('Please describe why this review violates community guidelines:');
    if (!reason || !reason.trim()) return;

    try {
      await api.reportReview(reviewId, reason.trim());
      alert('Thank you. The review has been flagged for moderation.');
    } catch (err) {
      console.error('Report error:', err);
    }
  };

  const toggleRevealSpoiler = (reviewId) => {
    setRevealedSpoilers((prev) => {
      const next = new Set(prev);
      if (next.has(reviewId)) next.delete(reviewId);
      else next.add(reviewId);
      return next;
    });
  };

  const selectedCountry = COUNTRIES.find((c) => c.code === country) || COUNTRIES[0];
  const userPersonalRating = ratingsSummary?.user_rating || null;
  const communityAvg = ratingsSummary?.community?.average_rating;
  const communityCount = ratingsSummary?.community?.total_ratings || 0;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/85 backdrop-blur-md flex items-center justify-center p-3 sm:p-5 md:p-8 animate-in fade-in duration-200">
      <div className="fixed inset-0" onClick={onClose} />

      <div className="relative z-10 w-full max-w-4xl bg-[#14141e] border border-[#2c2c3c] rounded-2xl md:rounded-3xl shadow-2xl overflow-hidden max-h-[92vh] flex flex-col my-auto">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-30 w-9 h-9 rounded-full bg-black/70 hover:bg-black text-white flex items-center justify-center transition-colors cursor-pointer border border-white/10"
        >
          <X className="w-4 h-4" />
        </button>

        {loading || !movie ? (
          <div className="p-8 space-y-6">
            <div className="w-full h-64 skeleton rounded-2xl" />
            <div className="w-2/3 h-8 skeleton rounded" />
            <div className="w-full h-24 skeleton rounded" />
          </div>
        ) : (
          <div className="overflow-y-auto flex-1">
            {/* Backdrop Banner */}
            <div className="relative h-64 sm:h-80 md:h-96 w-full overflow-hidden bg-[#1a1a24]">
              <img
                src={movie.backdrop_path}
                alt={movie.title}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.currentTarget.src =
                    'https://images.unsplash.com/photo-1536440136628-849c177e76a1?auto=format&fit=crop&w=1200&q=80';
                }}
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#14141e] via-[#14141e]/60 to-transparent" />
              <div className="absolute inset-0 bg-gradient-to-r from-[#14141e] via-transparent to-transparent" />

              <div className="absolute bottom-6 left-6 right-6 flex flex-wrap items-end justify-between gap-4">
                <div>
                  <h1 className="text-2xl sm:text-3xl md:text-4xl font-black text-white tracking-tight drop-shadow-md">
                    {movie.title}
                  </h1>
                  {movie.tagline && (
                    <p className="text-xs sm:text-sm text-[#cbd5e1] italic mt-1 drop-shadow">
                      "{movie.tagline}"
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => onToggleWatched(movie)}
                    className={`px-3.5 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer backdrop-blur-md ${
                      isWatched
                        ? 'bg-[#3b82f6] text-white shadow-lg shadow-[#3b82f6]/30'
                        : 'bg-black/60 hover:bg-black/80 text-white border border-white/20'
                    }`}
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>{isWatched ? 'Watched' : 'Mark Watched'}</span>
                  </button>

                  <button
                    onClick={() => onToggleLiked(movie)}
                    className={`p-2.5 rounded-xl transition-all cursor-pointer backdrop-blur-md ${
                      isLiked
                        ? 'bg-[#ec4899] text-white shadow-lg shadow-[#ec4899]/30'
                        : 'bg-black/60 hover:bg-black/80 text-white border border-white/20'
                    }`}
                  >
                    <Heart className={`w-4 h-4 ${isLiked ? 'fill-current' : ''}`} />
                  </button>

                  <button
                    onClick={() => onToggleWatchlist(movie)}
                    className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer ${
                      inWatchlist
                        ? 'bg-[#10b981] text-white shadow-md'
                        : 'bg-[#F04452] hover:bg-[#d63340] text-white shadow-lg shadow-[#F04452]/25'
                    }`}
                  >
                    {inWatchlist ? <Check className="w-3.5 h-3.5" /> : <Plus className="w-3.5 h-3.5" />}
                    <span>{inWatchlist ? 'In Watchlist' : 'Add to Watchlist'}</span>
                  </button>

                  <button
                    onClick={handleShare}
                    className="p-2.5 rounded-xl bg-black/60 hover:bg-black/80 text-white border border-white/20 transition-all cursor-pointer"
                    title="Copy Share Link"
                  >
                    {copied ? <Check className="w-4 h-4 text-[#10b981]" /> : <Share2 className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>

            <div className="p-6 sm:p-8 space-y-8">
              {/* Ratings Breakdown Grid (TMDB vs Community vs User) */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4 rounded-2xl bg-[#181826] border border-[#26263a]">
                {/* 1. TMDB Verified Rating */}
                <div className="flex items-center gap-3 border-b sm:border-b-0 sm:border-r border-[#26263a] pb-3 sm:pb-0 sm:pr-3">
                  <div className="w-10 h-10 rounded-xl bg-[#032541] flex items-center justify-center font-black text-[#01b4e4] text-xs">
                    TMDB
                  </div>
                  <div>
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4 text-[#fbbf24] fill-current" />
                      <span className="text-base font-extrabold text-white">
                        {Number(movie.vote_average || 8.0).toFixed(1)}
                      </span>
                      <span className="text-xs text-[#94a3b8]">/ 10</span>
                    </div>
                    <p className="text-[10px] text-[#94a3b8] uppercase font-semibold">
                      {(movie.vote_count || 1000).toLocaleString()} Verified TMDB Votes
                    </p>
                  </div>
                </div>

                {/* 2. CineMatch Community Average */}
                <div className="flex items-center gap-3 border-b sm:border-b-0 sm:border-r border-[#26263a] pb-3 sm:pb-0 sm:pr-3">
                  <div className="w-10 h-10 rounded-xl bg-[#F04452]/20 border border-[#F04452]/40 flex items-center justify-center text-[#F04452] font-black text-xs">
                    CM
                  </div>
                  <div>
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4 text-[#F04452] fill-current" />
                      <span className="text-base font-extrabold text-white">
                        {communityAvg ? communityAvg.toFixed(1) : '8.6'}
                      </span>
                      <span className="text-xs text-[#94a3b8]">/ 10</span>
                    </div>
                    <p className="text-[10px] text-[#94a3b8] uppercase font-semibold">
                      {communityCount > 0 ? `${communityCount} Community Ratings` : 'Community CineMatch Score'}
                    </p>
                  </div>
                </div>

                {/* 3. Your Personal Rating */}
                <div className="flex flex-col justify-center">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] uppercase font-bold text-[#cbd5e1]">
                      Your Rating:
                    </span>
                    {userPersonalRating && (
                      <button
                        onClick={handleDeleteRating}
                        className="text-[10px] text-[#ef4444] hover:underline cursor-pointer"
                      >
                        Remove ({userPersonalRating}/10)
                      </button>
                    )}
                  </div>
                  <div className="flex items-center gap-1">
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((starVal) => (
                      <button
                        key={starVal}
                        type="button"
                        onClick={() => handleRate(starVal)}
                        onMouseEnter={() => setHoverRating(starVal)}
                        onMouseLeave={() => setHoverRating(0)}
                        className="p-0.5 transition-transform hover:scale-120 cursor-pointer"
                        title={`Rate ${starVal}/10`}
                      >
                        <Star
                          className={`w-3.5 h-3.5 ${
                            (hoverRating || userPersonalRating || 0) >= starVal
                              ? 'text-[#fbbf24] fill-current'
                              : 'text-[#475569]'
                          }`}
                        />
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Movie Info & Overview */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="md:col-span-2 space-y-4">
                  <div className="flex flex-wrap items-center gap-2">
                    {movie.genres?.map((g) => (
                      <span
                        key={g}
                        className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-[#20202e] text-[#cbd5e1] border border-[#2e2e40]"
                      >
                        {g}
                      </span>
                    ))}
                    <span className="text-xs text-[#94a3b8] flex items-center gap-1 ml-2">
                      <Clock className="w-3.5 h-3.5" /> {movie.runtime || 120} min
                    </span>
                    <span className="text-xs text-[#94a3b8] flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5" /> {movie.release_year || movie.release_date?.slice(0, 4)}
                    </span>
                  </div>

                  <div>
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-1.5">Overview</h3>
                    <p className="text-xs sm:text-sm text-[#cbd5e1] leading-relaxed">
                      {movie.overview}
                    </p>
                  </div>

                  {movie.director && (
                    <p className="text-xs text-[#94a3b8]">
                      <strong className="text-white">Director:</strong> {movie.director}
                    </p>
                  )}
                  {movie.cast && movie.cast.length > 0 && (
                    <p className="text-xs text-[#94a3b8]">
                      <strong className="text-white">Cast:</strong> {movie.cast.join(', ')}
                    </p>
                  )}
                </div>

                {/* Poster Card */}
                <div className="hidden md:block">
                  <img
                    src={movie.poster_path}
                    alt={movie.title}
                    className="w-full aspect-[2/3] rounded-2xl object-cover shadow-xl border border-[#2a2a3c]"
                  />
                </div>
              </div>

              {/* Where to Watch (OTT) */}
              <div className="pt-6 border-t border-[#242434]">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Tv className="w-5 h-5 text-[#F04452]" />
                    <h3 className="text-base font-bold text-white">Where to Watch in {selectedCountry.name}</h3>
                    {providers?.is_live ? (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#10b981]/20 text-[#10b981] border border-[#10b981]/30">
                        ● Live TMDB
                      </span>
                    ) : (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#64748b]/20 text-[#94a3b8] border border-[#64748b]/30">
                        Catalogue
                      </span>
                    )}
                  </div>
                  <select
                    value={country}
                    onChange={(e) => setCountry(e.target.value)}
                    className="bg-[#1e1e2c] text-xs font-semibold text-white px-2.5 py-1.5 rounded-xl border border-[#323246]"
                  >
                    {COUNTRIES.map((c) => (
                      <option key={c.code} value={c.code}>
                        {c.flag} {c.name}
                      </option>
                    ))}
                  </select>
                </div>

                {providers?.message && (
                  <p className="text-[11px] text-[#94a3b8] mb-3 leading-relaxed">
                    {providers.message}
                  </p>
                )}

                {providers?.subscription?.length > 0 ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                    {providers.subscription.map((p, idx) => (
                      <a
                        key={idx}
                        href={p.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center justify-between p-3 rounded-xl bg-[#1a1a26] hover:bg-[#222234] border border-[#2c2c3e] hover:border-[#F04452] transition-all"
                      >
                        <div className="flex items-center gap-3">
                          {p.logo && <img src={p.logo} alt={p.name} className="w-8 h-8 rounded-lg object-cover" />}
                          <div>
                            <p className="text-xs font-bold text-white">{p.name}</p>
                            <span className="text-[10px] text-[#10b981]">Subscription</span>
                          </div>
                        </div>
                        <ExternalLink className="w-3.5 h-3.5 text-[#F04452]" />
                      </a>
                    ))}
                  </div>
                ) : (
                  <div className="p-4 rounded-xl bg-[#181824] border border-[#262638] text-xs text-[#cbd5e1] flex items-center justify-between">
                    <span>Available on Rent or Buy via Apple TV, Google Play & Amazon.</span>
                    <a
                      href={providers?.justwatch_url || '#'}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[#fbbf24] hover:underline"
                    >
                      Check JustWatch ↗
                    </a>
                  </div>
                )}
              </div>

              {/* ========================================================== */}
              {/* COMMUNITY REVIEWS & VADER SENTIMENT CLASSIFICATION        */}
              {/* ========================================================== */}
              <div className="pt-6 border-t border-[#242434] space-y-5">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-[#38bdf8]" />
                    <h3 className="text-base font-bold text-white">Community Reviews & Critic Reactions</h3>
                    <span className="text-xs text-[#94a3b8]">
                      ({reviewsData.reviews?.length || 0} reviews)
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    {/* Sort Selector */}
                    <select
                      value={reviewSort}
                      onChange={(e) => setReviewSort(e.target.value)}
                      className="bg-[#1a1a28] border border-[#2e2e42] text-xs font-semibold text-white px-3 py-1.5 rounded-xl cursor-pointer"
                    >
                      <option value="most_helpful">Most Helpful</option>
                      <option value="newest">Newest</option>
                      <option value="highest_rated">Highest Rated</option>
                      <option value="lowest_rated">Lowest Rated</option>
                    </select>

                    <button
                      onClick={() => {
                        if (!user || !user.isLoggedIn) onOpenAuth();
                        else setIsWritingReview((prev) => !prev);
                      }}
                      className="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-[#38bdf8] to-[#0284c7] hover:from-[#0284c7] hover:to-[#0369a1] text-white text-xs font-bold shadow-md cursor-pointer flex items-center gap-1.5"
                    >
                      <Plus className="w-3.5 h-3.5" />
                      <span>Write Review</span>
                    </button>
                  </div>
                </div>

                {/* Review Form Drawer */}
                {isWritingReview && (
                  <form
                    onSubmit={handleSubmitReview}
                    className="p-4 sm:p-5 rounded-2xl bg-[#181826] border border-[#323248] space-y-3.5 animate-in fade-in"
                  >
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                        Share Your Cinephile Verdict
                      </h4>
                      <span className="text-[10px] text-[#38bdf8] font-mono">
                        VADER NLP Sentiment Enabled
                      </span>
                    </div>

                    {reviewError && (
                      <p className="text-xs text-[#ef4444] bg-[#ef4444]/10 p-2 rounded-lg">{reviewError}</p>
                    )}

                    <div>
                      <input
                        type="text"
                        required
                        placeholder="Headline / Summary (e.g. A visual masterpiece of sci-fi cinema)"
                        value={formTitle}
                        onChange={(e) => setFormTitle(e.target.value)}
                        className="w-full px-3.5 py-2 rounded-xl bg-[#12121c] border border-[#28283a] text-xs text-white placeholder-[#64748b] focus:outline-none focus:border-[#38bdf8]"
                      />
                    </div>

                    <div className="flex items-center gap-3">
                      <span className="text-xs text-[#cbd5e1] font-semibold">Your Rating:</span>
                      <div className="flex items-center gap-1">
                        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
                          <button
                            key={num}
                            type="button"
                            onClick={() => setFormRating(num)}
                            className={`w-7 h-7 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                              formRating === num
                                ? 'bg-[#F04452] text-white'
                                : 'bg-[#1e1e2c] text-[#94a3b8] hover:text-white'
                            }`}
                          >
                            {num}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div>
                      <textarea
                        required
                        rows={3}
                        placeholder="Write your in-depth review, thoughts on performance, pacing, cinematography..."
                        value={formContent}
                        onChange={(e) => setFormContent(e.target.value)}
                        className="w-full px-3.5 py-2 rounded-xl bg-[#12121c] border border-[#28283a] text-xs text-white placeholder-[#64748b] focus:outline-none focus:border-[#38bdf8]"
                      />
                    </div>

                    <div className="flex items-center justify-between pt-1">
                      <label className="flex items-center gap-2 text-xs text-[#cbd5e1] cursor-pointer">
                        <input
                          type="checkbox"
                          checked={formSpoilers}
                          onChange={(e) => setFormSpoilers(e.target.checked)}
                          className="rounded bg-[#12121c] border-[#38384a] text-[#F04452] focus:ring-0"
                        />
                        <span>Contains Spoilers (Will blur text for other users)</span>
                      </label>

                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => setIsWritingReview(false)}
                          className="px-3 py-1.5 rounded-xl bg-[#20202e] text-xs font-semibold text-[#cbd5e1] hover:text-white cursor-pointer"
                        >
                          Cancel
                        </button>
                        <button
                          type="submit"
                          disabled={submittingReview}
                          className="px-4 py-1.5 rounded-xl bg-[#F04452] hover:bg-[#d63340] text-xs font-bold text-white shadow-md cursor-pointer flex items-center gap-1.5 disabled:opacity-50"
                        >
                          <Send className="w-3.5 h-3.5" />
                          <span>{submittingReview ? 'Publishing...' : 'Publish Review'}</span>
                        </button>
                      </div>
                    </div>
                  </form>
                )}

                {/* Reviews List */}
                <div className="space-y-3">
                  {reviewsData.reviews?.length > 0 ? (
                    reviewsData.reviews.map((rev) => {
                      const isSpoilerHidden = rev.contains_spoilers && !revealedSpoilers.has(rev.id);
                      return (
                        <div
                          key={rev.id}
                          className="p-4 rounded-2xl bg-[#181826] border border-[#262638] space-y-2.5 transition-colors"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2.5">
                              <span className="text-xl">{rev.avatar || '🎬'}</span>
                              <div>
                                <div className="flex items-center gap-2">
                                  <span className="text-xs font-bold text-white">{rev.username}</span>
                                  {/* Sentiment Badge */}
                                  <span
                                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                                      rev.sentiment === 'positive'
                                        ? 'bg-[#10b981]/15 text-[#10b981]'
                                        : rev.sentiment === 'negative'
                                        ? 'bg-[#ef4444]/15 text-[#ef4444]'
                                        : 'bg-[#94a3b8]/15 text-[#cbd5e1]'
                                    }`}
                                  >
                                    {rev.sentiment} ({rev.sentiment_score > 0 ? `+${rev.sentiment_score}` : rev.sentiment_score})
                                  </span>
                                </div>
                                <span className="text-[10px] text-[#94a3b8]">{rev.created_at?.slice(0, 10)}</span>
                              </div>
                            </div>

                            <div className="flex items-center gap-1 bg-[#101018] px-2.5 py-1 rounded-lg border border-[#2a2a3e]">
                              <Star className="w-3.5 h-3.5 text-[#fbbf24] fill-current" />
                              <span className="text-xs font-bold text-white">{rev.rating}/10</span>
                            </div>
                          </div>

                          <h4 className="text-xs font-bold text-white">{rev.title}</h4>

                          {/* Content with Spoiler Mask */}
                          {isSpoilerHidden ? (
                            <div
                              onClick={() => toggleRevealSpoiler(rev.id)}
                              className="p-3 rounded-xl bg-[#20202e] border border-[#34344a] text-xs text-[#cbd5e1] cursor-pointer hover:bg-[#28283a] flex items-center justify-between"
                            >
                              <span className="flex items-center gap-1.5 text-[#fbbf24]">
                                <ShieldAlert className="w-4 h-4" />
                                Review contains spoilers. Click to reveal.
                              </span>
                              <ChevronDown className="w-4 h-4 text-[#94a3b8]" />
                            </div>
                          ) : (
                            <p className="text-xs text-[#cbd5e1] leading-relaxed whitespace-pre-line">
                              {rev.content}
                            </p>
                          )}

                          {/* Footer Actions: Helpful / Unhelpful & Report */}
                          <div className="pt-2 border-t border-[#222232] flex items-center justify-between text-[11px] text-[#94a3b8]">
                            <div className="flex items-center gap-3">
                              <button
                                onClick={() => handleVoteReview(rev.id, 1)}
                                className={`flex items-center gap-1 px-2 py-1 rounded-lg transition-colors cursor-pointer ${
                                  rev.user_vote === 1
                                    ? 'bg-[#10b981]/20 text-[#10b981]'
                                    : 'hover:text-white'
                                }`}
                              >
                                <ThumbsUp className="w-3 h-3" />
                                <span>Helpful ({rev.helpful_count || 0})</span>
                              </button>

                              <button
                                onClick={() => handleVoteReview(rev.id, -1)}
                                className={`flex items-center gap-1 px-2 py-1 rounded-lg transition-colors cursor-pointer ${
                                  rev.user_vote === -1
                                    ? 'bg-[#ef4444]/20 text-[#ef4444]'
                                    : 'hover:text-white'
                                }`}
                              >
                                <ThumbsDown className="w-3 h-3" />
                                <span>Not Helpful ({rev.unhelpful_count || 0})</span>
                              </button>
                            </div>

                            <button
                              onClick={() => handleReportReview(rev.id)}
                              className="hover:text-[#ef4444] transition-colors flex items-center gap-1 cursor-pointer"
                              title="Flag review for moderation"
                            >
                              <Flag className="w-3 h-3" />
                              <span>Report</span>
                            </button>
                          </div>
                        </div>
                      );
                    })
                  ) : (
                    <div className="p-6 text-center rounded-2xl bg-[#161622] border border-[#242436]">
                      <p className="text-xs text-[#94a3b8]">
                        No community reviews yet. Be the first cinephile to share your thoughts!
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Similar Movies Carousel */}
              {similarMovies && similarMovies.length > 0 && (
                <div className="pt-6 border-t border-[#242434]">
                  <div className="flex items-center gap-2 mb-4">
                    <Sparkles className="w-4 h-4 text-[#fbbf24]" />
                    <h3 className="text-base font-bold text-white">More Like This</h3>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
                    {similarMovies.slice(0, 6).map((sim) => (
                      <div
                        key={sim.id}
                        onClick={() => onSelectMovie(sim)}
                        className="group bg-[#181824] rounded-xl overflow-hidden border border-[#28283a] hover:border-[#F04452] p-1.5 cursor-pointer transition-all"
                      >
                        <img
                          src={sim.poster_path}
                          alt={sim.title}
                          className="w-full aspect-[2/3] object-cover rounded-lg group-hover:scale-105 transition-transform"
                        />
                        <p className="text-xs font-semibold text-white mt-1.5 truncate">{sim.title}</p>
                        <p className="text-[10px] text-[#94a3b8]">★ {Number(sim.vote_average || 8).toFixed(1)}</p>
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
