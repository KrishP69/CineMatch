import React, { useState } from 'react';
import { Sparkles, Tv, Check, Plus, Eye, RefreshCw, ArrowRight } from 'lucide-react';
import { api } from '../services/api';

const QUICK_PROMPTS = [
  'A mind-bending psychological thriller with plot twists and non-linear timelines',
  'An epic historical drama with high emotions, brotherhood, and rebellion',
  'A tense detective investigation in a rain-soaked noir city',
  'A clever, high-stakes heist where nothing goes as planned',
  'Emotional journey through space, time dilation, and family sacrifice',
  'Dark atmospheric neo-noir with philosophical depth and high stakes',
];

const GENRE_CHIPS = [
  'Science Fiction', 'Action', 'Drama', 'Thriller', 'Crime',
  'Comedy', 'Romance', 'Mystery', 'Animation', 'Adventure'
];

export default function ForYouAIAgent({
  onSelectMovie,
  onWatchProviders,
  watchlistState,
}) {
  const { watchlist, toggleWatchlist, watched, toggleWatched } = watchlistState;

  const [selectedGenres, setSelectedGenres] = useState(['Science Fiction', 'Thriller']);
  const [description, setDescription] = useState('');
  const [mood, setMood] = useState('Mind-Bending');
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [hasQueried, setHasQueried] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const toggleGenre = (genre) => {
    setSelectedGenres(prev =>
      prev.includes(genre)
        ? prev.filter(g => g !== genre)
        : [...prev, genre]
    );
  };

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!description.trim() && selectedGenres.length === 0) {
      setErrorMsg('Please select at least one genre or describe what you want to watch.');
      return;
    }
    setErrorMsg('');
    setLoading(true);
    setHasQueried(true);

    try {
      const res = await api.aiDescribeMatch({
        description: description.trim(),
        preferred_genres: selectedGenres,
        mood: mood,
        exclude_ids: watched,
        count: 10,
      });

      if (res.success && res.recommendations) {
        setRecommendations(res.recommendations);
      }
    } catch (err) {
      console.error('AI match error:', err);
      setErrorMsg('Unable to retrieve AI matches. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-3xl bg-gradient-to-br from-[#161624] via-[#1a1a2e] to-[#141420] border border-[#2c2c42] p-6 sm:p-8 shadow-2xl relative overflow-hidden mb-12">
      
      {/* Background ambient glowing spheres */}
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-[#F04452]/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-[#38bdf8]/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-[#F04452] to-[#ff6b77] flex items-center justify-center shadow-lg shadow-[#F04452]/25">
            <Sparkles className="w-6 h-6 text-white animate-pulse" />
          </div>
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#fbbf24]/15 border border-[#fbbf24]/30 text-[11px] font-bold text-[#fbbf24] uppercase tracking-wider mb-0.5">
              <span>Interactive CineMatch AI Assistant</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight">
              For You AI — Natural Language Movie Matcher
            </h2>
          </div>
        </div>

        {hasQueried && (
          <button
            onClick={() => {
              setHasQueried(false);
              setRecommendations([]);
              setDescription('');
            }}
            className="self-start md:self-auto px-4 py-2 rounded-xl bg-[#202030] hover:bg-[#28283c] border border-[#303046] text-xs font-semibold text-[#cbd5e1] hover:text-white flex items-center gap-2 transition-colors cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>New Prompt</span>
          </button>
        )}
      </div>

      <p className="relative z-10 text-xs sm:text-sm text-[#94a3b8] mb-6 max-w-2xl leading-relaxed">
        Tell our AI agent what you want to watch in your own words. We vectorize your plot description,
        cross-reference director styles, themes, and genres, and recommend your exact <strong>Top 10 matches</strong>.
      </p>

      {/* Input Form */}
      <form onSubmit={handleSearch} className="relative z-10 space-y-5">
        
        {/* Step 1: Genre Preference Chips */}
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-[#cbd5e1] mb-2 flex items-center gap-2">
            <span className="w-5 h-5 rounded-full bg-[#F04452]/20 text-[#F04452] text-[11px] flex items-center justify-center font-bold">1</span>
            Which genres are you in the mood for?
          </label>
          <div className="flex flex-wrap gap-2">
            {GENRE_CHIPS.map((g) => {
              const active = selectedGenres.includes(g);
              return (
                <button
                  key={g}
                  type="button"
                  onClick={() => toggleGenre(g)}
                  className={`text-xs px-3 py-1.8 rounded-xl font-semibold transition-all cursor-pointer border flex items-center gap-1.5 ${
                    active
                      ? 'bg-[#F04452] text-white border-[#F04452] shadow-md shadow-[#F04452]/20'
                      : 'bg-[#181826] hover:bg-[#222234] text-[#cbd5e1] border-[#2b2b40]'
                  }`}
                >
                  {active && <Check className="w-3 h-3" />}
                  <span>{g}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Step 2: Natural Language Plot / Vibe Description */}
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-[#cbd5e1] mb-2 flex items-center gap-2">
            <span className="w-5 h-5 rounded-full bg-[#F04452]/20 text-[#F04452] text-[11px] flex items-center justify-center font-bold">2</span>
            Describe what you want to watch in your own words:
          </label>
          <div className="relative">
            <textarea
              rows={3}
              placeholder="e.g. A dark, rain-soaked detective mystery where nothing is what it seems and there is a shocking plot twist at the climax..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full p-4 rounded-2xl bg-[#12121e] border border-[#2c2c42] text-sm text-white placeholder-[#64748b] focus:outline-none focus:border-[#F04452] transition-colors leading-relaxed"
            />
          </div>

          {/* Quick Prompt Inspiration Chips */}
          <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
            <span className="text-[11px] font-semibold text-[#94a3b8] mr-1">Inspirations:</span>
            {QUICK_PROMPTS.map((p, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setDescription(p)}
                className="text-[11px] px-2.5 py-1 rounded-lg bg-[#181826] hover:bg-[#222234] text-[#cbd5e1] hover:text-white border border-[#2b2b40] transition-colors cursor-pointer text-left line-clamp-1 max-w-xs"
                title={p}
              >
                "{p}"
              </button>
            ))}
          </div>
        </div>

        {errorMsg && (
          <p className="text-xs text-[#ef4444] font-medium">{errorMsg}</p>
        )}

        {/* Submit Button */}
        <div>
          <button
            type="submit"
            disabled={loading}
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-gradient-to-r from-[#F04452] to-[#ff4757] hover:from-[#d63340] hover:to-[#e8414f] text-white font-bold text-sm flex items-center justify-center gap-2.5 shadow-xl shadow-[#F04452]/25 transition-all cursor-pointer hover:scale-102 active:scale-98 disabled:opacity-50"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>AI Analyzing Semantic Vectors...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Curate Top 10 Matches</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>

      </form>

      {/* RESULTS DISPLAY: Top 10 Ranked Matches */}
      {hasQueried && !loading && recommendations.length > 0 && (
        <div className="relative z-10 mt-10 pt-8 border-t border-[#2a2a3e] animate-in fade-in duration-300">
          
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg sm:text-xl font-extrabold text-white flex items-center gap-2">
                <span className="w-2 h-5 bg-[#F04452] rounded-full" />
                Top 10 Curated Matches For Your Description
              </h3>
              <p className="text-xs text-[#94a3b8] mt-0.5">
                Ranked strictly by semantic cosine similarity with your prompt & selected genres.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommendations.slice(0, 10).map((movie, idx) => {
              const inWl = watchlist.some(m => m.id === movie.id);
              const isW = watched.includes(movie.id);
              const pct = movie.similarity_score ? Math.round(movie.similarity_score * 100) : 92;

              return (
                <div
                  key={movie.id}
                  className="bg-[#141420] rounded-2xl border border-[#28283c] hover:border-[#F04452]/60 p-3.5 flex gap-4 transition-all duration-200 hover:shadow-xl hover:shadow-[#F04452]/10 group"
                >
                  {/* Poster Thumbnail + Rank Badge */}
                  <div
                    onClick={() => onSelectMovie(movie)}
                    className="relative w-24 sm:w-28 aspect-[2/3] rounded-xl overflow-hidden bg-[#1c1c28] flex-shrink-0 cursor-pointer"
                  >
                    <img
                      src={movie.poster_path}
                      alt={movie.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                    <div className="absolute top-1.5 left-1.5 w-6 h-6 rounded-lg bg-black/80 backdrop-blur-md text-[11px] font-black text-white flex items-center justify-center border border-white/10 shadow">
                      #{idx + 1}
                    </div>
                  </div>

                  {/* Info & AI Reasoning */}
                  <div className="flex flex-col justify-between flex-grow min-w-0">
                    <div>
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <h4
                          onClick={() => onSelectMovie(movie)}
                          className="text-sm sm:text-base font-bold text-white tracking-tight line-clamp-1 group-hover:text-[#F04452] transition-colors cursor-pointer"
                          title={movie.title}
                        >
                          {movie.title}
                        </h4>

                        <span className="bg-[#F04452] text-white text-[10px] font-extrabold px-1.8 py-0.5 rounded-md flex-shrink-0">
                          {pct}% MATCH
                        </span>
                      </div>

                      <div className="flex items-center gap-2 text-[11px] text-[#94a3b8] mb-2">
                        <span>★ {Number(movie.vote_average || 8).toFixed(1)}</span>
                        <span>•</span>
                        <span>{movie.release_year || 2022}</span>
                        {movie.director && (
                          <>
                            <span>•</span>
                            <span className="line-clamp-1">Dir: {movie.director}</span>
                          </>
                        )}
                      </div>

                      {/* AI Reasoning Box */}
                      {movie.recommendation_reason && (
                        <div className="p-2 rounded-xl bg-[#1c1c2c] border border-[#2e2e44] text-[11px] text-[#38bdf8] mb-2.5 line-clamp-2 leading-relaxed">
                          {movie.recommendation_reason}
                        </div>
                      )}
                    </div>

                    {/* Action Buttons Tray */}
                    <div className="flex flex-wrap items-center gap-1.5 pt-1">
                      <button
                        onClick={() => onWatchProviders(movie)}
                        className="py-1.5 px-2.5 rounded-lg bg-[#F04452] hover:bg-[#d63340] text-white text-[11px] font-bold flex items-center gap-1 shadow-sm transition-colors cursor-pointer"
                      >
                        <Tv className="w-3 h-3" />
                        Where to Watch
                      </button>

                      <button
                        onClick={() => toggleWatchlist(movie)}
                        className={`py-1.5 px-2.5 rounded-lg border text-[11px] font-semibold flex items-center gap-1 transition-colors cursor-pointer ${
                          inWl
                            ? 'bg-[#10b981]/20 border-[#10b981] text-[#10b981]'
                            : 'bg-[#1c1c28] hover:bg-[#242436] border-[#2e2e40] text-white'
                        }`}
                      >
                        {inWl ? <Check className="w-3 h-3 text-[#10b981]" /> : <Plus className="w-3 h-3" />}
                        {inWl ? 'Saved' : 'Watchlist'}
                      </button>

                      <button
                        onClick={() => toggleWatched(movie.id)}
                        className={`py-1.5 px-2.5 rounded-lg border text-[11px] font-semibold flex items-center gap-1 transition-colors cursor-pointer ${
                          isW
                            ? 'bg-[#3b82f6]/20 border-[#3b82f6] text-[#60a5fa]'
                            : 'bg-[#1c1c28] hover:bg-[#242436] border-[#2e2e40] text-[#94a3b8] hover:text-white'
                        }`}
                        title={isW ? 'Marked as Watched' : 'Mark as Already Watched'}
                      >
                        <Eye className="w-3 h-3" />
                        {isW ? 'Seen' : 'Watched'}
                      </button>
                    </div>

                  </div>
                </div>
              );
            })}
          </div>

        </div>
      )}

    </div>
  );
}
