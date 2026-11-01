import React, { useState } from 'react';
import { X, Sparkles, ArrowRight, ArrowLeft, Check, Film, Tv, Star, Compass, Play, ChevronRight, Eye } from 'lucide-react';
import { api } from '../services/api';

const POPULAR_ANCHORS = [
  { id: 157336, title: 'Interstellar', type: 'Movie', desc: 'Space exploration & time dilation', poster: 'https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg' },
  { id: 579974, title: 'RRR', type: 'Movie', desc: 'Epic revolution, high emotion & action', poster: 'https://upload.wikimedia.org/wikipedia/en/d/d7/RRR_Poster.jpg' },
  { id: 27205, title: 'Inception', type: 'Movie', desc: 'Mind-bending dream architecture', poster: 'https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg' },
  { id: 155, title: 'The Dark Knight', type: 'Movie', desc: 'Gritty psychological crime duel', poster: 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg' },
  { id: 496243, title: 'Parasite', type: 'Movie', desc: 'Sharp social satire & thriller', poster: 'https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg' },
  { id: 872585, title: 'Oppenheimer', type: 'Movie', desc: 'Historical tension & moral drama', poster: 'https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg' },
  { id: 20453, title: '3 Idiots', type: 'Movie', desc: 'Heartwarming friendship & comedy', poster: 'https://upload.wikimedia.org/wikipedia/en/d/df/3_idiots_poster.jpg' },
  { id: 313369, title: 'La La Land', type: 'Movie', desc: 'Vibrant romance & bittersweet passion', poster: 'https://upload.wikimedia.org/wikipedia/en/a/ab/La_La_Land_%28film%29.png' },
];

const GENRE_OPTIONS = [
  { name: 'Science Fiction', icon: '🚀', color: 'from-cyan-500/20 to-blue-500/20' },
  { name: 'Action', icon: '💥', color: 'from-red-500/20 to-orange-500/20' },
  { name: 'Drama', icon: '🎭', color: 'from-amber-500/20 to-yellow-500/20' },
  { name: 'Crime', icon: '🕵️', color: 'from-slate-500/20 to-zinc-500/20' },
  { name: 'Thriller', icon: '⚡', color: 'from-purple-500/20 to-indigo-500/20' },
  { name: 'Comedy', icon: '😂', color: 'from-yellow-500/20 to-lime-500/20' },
  { name: 'Romance', icon: '❤️', color: 'from-pink-500/20 to-rose-500/20' },
  { name: 'Mystery', icon: '🔍', color: 'from-emerald-500/20 to-teal-500/20' },
  { name: 'Animation', icon: '🎨', color: 'from-violet-500/20 to-fuchsia-500/20' },
  { name: 'Adventure', icon: '🗺️', color: 'from-sky-500/20 to-blue-500/20' },
  { name: 'Horror', icon: '🕯️', color: 'from-neutral-700/30 to-stone-800/30' },
  { name: 'History', icon: '📜', color: 'from-amber-700/20 to-orange-800/20' },
];

const MOOD_OPTIONS = [
  { id: 'Mind-Bending & Complex', label: 'Mind-Bending & Complex', icon: '🧠', desc: 'Plot twists, non-linear mysteries, deep cerebral puzzles' },
  { id: 'Comfort & Feel-Good', label: 'Comfort & Feel-Good', icon: '☕', desc: 'Warm, uplifting, stress-free laughs and great vibes' },
  { id: 'Dark, Gritty & Atmospheric', label: 'Dark, Gritty & Atmospheric', icon: '🌑', desc: 'Noire aesthetics, high stakes, tension and suspense' },
  { id: 'High-Octane Adrenaline', label: 'High-Octane Adrenaline', icon: '⚡', desc: 'Explosive spectacle, edge-of-your-seat momentum' },
  { id: 'Emotional & Profound', label: 'Emotional & Profound', icon: '💎', desc: 'Moving character journeys, thought-provoking themes' },
];

const ERA_PACING_OPTIONS = [
  { id: 'Modern Blockbusters', label: 'Modern Blockbusters (2015 - Present)', icon: '🌟', desc: 'State-of-the-art visuals, dynamic modern storytelling' },
  { id: 'Golden Era 2000s & 90s', label: 'Golden Era Classics (1990 - 2014)', icon: '🎞️', desc: 'Peak storytelling depth with beloved iconic classics' },
  { id: 'Fast-Paced Rollercoaster', label: 'Fast-Paced & Punchy', icon: '⚡', desc: 'Tight pacing, quick momentum, zero filler' },
  { id: 'Slow-Burn Masterpiece', label: 'Slow-Burn Cinematic Depth', icon: '🕯️', desc: 'Rich world-building, patient build-up and massive payoffs' },
];

export default function PersonalizationQuizModal({
  isOpen,
  onClose,
  initialGenres = [],
  watchedIds = [],
  onComplete,
  onSelectMovie,
  onWatchProviders,
}) {
  const [step, setStep] = useState(1);
  const [lastWatched, setLastWatched] = useState('Interstellar');
  const [customLastWatched, setCustomLastWatched] = useState('');
  const [selectedGenres, setSelectedGenres] = useState(
    initialGenres.length > 0 ? initialGenres : ['Science Fiction', 'Action', 'Drama']
  );
  const [selectedMood, setSelectedMood] = useState('Mind-Bending & Complex');
  const [selectedEra, setSelectedEra] = useState('Modern Blockbusters');

  const [loading, setLoading] = useState(false);
  const [quizResults, setQuizResults] = useState(null);

  if (!isOpen) return null;

  const toggleGenre = (genre) => {
    setSelectedGenres(prev =>
      prev.includes(genre)
        ? prev.length > 1 ? prev.filter(g => g !== genre) : prev
        : [...prev, genre]
    );
  };

  const handleNext = () => {
    if (step < 4) {
      setStep(step + 1);
    } else {
      // Step 4 complete: compute personalized recommendations
      handleGenerateRecommendations();
    }
  };

  const handleGenerateRecommendations = async () => {
    setLoading(true);
    setStep(5);

    const anchorValue = customLastWatched.trim() || lastWatched;

    try {
      const res = await api.submitOnboardingMCQ({
        last_watched: anchorValue,
        genres: selectedGenres,
        mood: selectedMood,
        era_pacing: selectedEra,
        already_watched_ids: watchedIds,
        count: 10,
      });

      if (res.success && res.data) {
        setQuizResults(res.data);
      }
    } catch (e) {
      console.error('MCQ quiz error:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleFinishAndSave = () => {
    const anchorObj = POPULAR_ANCHORS.find(a => a.title.toLowerCase() === lastWatched.toLowerCase());
    const likedIds = anchorObj ? [anchorObj.id] : [];
    onComplete(selectedGenres, likedIds, selectedMood, selectedEra);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/85 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-3xl bg-[#14141e] rounded-3xl border border-[#2a2a3e] shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Glow Effects */}
        <div className="absolute -top-32 -right-32 w-64 h-64 bg-[#F04452]/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-32 -left-32 w-64 h-64 bg-[#38bdf8]/15 rounded-full blur-3xl pointer-events-none" />

        {/* Modal Header */}
        <div className="px-6 py-4.5 border-b border-[#242436] flex items-center justify-between relative z-10">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-[#F04452] to-[#ff6b77] flex items-center justify-center shadow-md shadow-[#F04452]/20">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div>
              <h2 className="text-base sm:text-lg font-bold text-white tracking-tight">
                AI Taste Personalization Quiz
              </h2>
              <p className="text-[11px] text-[#94a3b8]">
                {step <= 4 ? `Step ${step} of 4 • Calibrating TF-IDF Vector Engine` : 'Your Tailored Next to Watch'}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-[#1e1e2c] hover:bg-[#28283a] border border-[#2e2e42] text-[#94a3b8] hover:text-white flex items-center justify-center transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Progress Bar (Steps 1-4) */}
        {step <= 4 && (
          <div className="w-full bg-[#1c1c28] h-1.5">
            <div
              className="bg-gradient-to-r from-[#F04452] to-[#ff6b77] h-full transition-all duration-300"
              style={{ width: `${(step / 4) * 100}%` }}
            />
          </div>
        )}

        {/* Scrollable Step Body */}
        <div className="p-6 overflow-y-auto no-scrollbar flex-grow relative z-10">
          
          {/* STEP 1: Last Loved Movie or Series */}
          {step === 1 && (
            <div className="animate-in fade-in duration-200">
              <div className="mb-4">
                <span className="text-[11px] font-bold text-[#F04452] uppercase tracking-wider">
                  Question 1 / 4
                </span>
                <h3 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight mt-1">
                  What was the last movie or TV series you thoroughly enjoyed?
                </h3>
                <p className="text-xs sm:text-sm text-[#94a3b8] mt-1">
                  We use its director, screenplay themes, and tone as a strong semantic anchor in your vector profile.
                </p>
              </div>

              {/* Grid of Curated Anchor Titles */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
                {POPULAR_ANCHORS.map((m) => {
                  const isSelected = !customLastWatched && lastWatched.toLowerCase() === m.title.toLowerCase();
                  return (
                    <button
                      key={m.id}
                      type="button"
                      onClick={() => {
                        setLastWatched(m.title);
                        setCustomLastWatched('');
                      }}
                      className={`relative rounded-2xl overflow-hidden border p-2.5 text-left transition-all cursor-pointer flex flex-col justify-between aspect-[3/4] group ${
                        isSelected
                          ? 'border-[#F04452] bg-[#F04452]/10 ring-2 ring-[#F04452]/40 shadow-lg'
                          : 'border-[#262638] bg-[#181824] hover:border-[#383850]'
                      }`}
                    >
                      <img
                        src={m.poster}
                        alt={m.title}
                        className="absolute inset-0 w-full h-full object-cover filter brightness-40 group-hover:brightness-50 transition-all"
                      />
                      <div className="relative z-10 flex justify-end">
                        <div className={`w-5 h-5 rounded-full flex items-center justify-center ${
                          isSelected ? 'bg-[#F04452] text-white' : 'bg-black/60 text-transparent border border-white/20'
                        }`}>
                          <Check className="w-3 h-3 text-white" />
                        </div>
                      </div>
                      <div className="relative z-10">
                        <span className="text-[10px] font-bold text-[#38bdf8] bg-black/60 px-1.5 py-0.5 rounded">
                          {m.type}
                        </span>
                        <h4 className="text-xs font-bold text-white mt-1 line-clamp-1">{m.title}</h4>
                        <p className="text-[10px] text-[#cbd5e1] line-clamp-1 opacity-80">{m.desc}</p>
                      </div>
                    </button>
                  );
                })}
              </div>

              {/* Or Type Custom Title Input */}
              <div className="p-4 rounded-2xl bg-[#181826] border border-[#26263a]">
                <label className="block text-xs font-semibold text-[#cbd5e1] mb-1.5">
                  Or enter any custom movie or series title:
                </label>
                <input
                  type="text"
                  placeholder="e.g. Breaking Bad, Dune 2, Succession, Dark, Shutter Island..."
                  value={customLastWatched}
                  onChange={(e) => setCustomLastWatched(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-[#12121c] border border-[#2b2b40] text-sm text-white placeholder-[#64748b] focus:outline-none focus:border-[#F04452]"
                />
              </div>
            </div>
          )}

          {/* STEP 2: Favorite Genres */}
          {step === 2 && (
            <div className="animate-in fade-in duration-200">
              <div className="mb-4">
                <span className="text-[11px] font-bold text-[#F04452] uppercase tracking-wider">
                  Question 2 / 4
                </span>
                <h3 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight mt-1">
                  Which genres define your taste?
                </h3>
                <p className="text-xs sm:text-sm text-[#94a3b8] mt-1">
                  Select all that apply. These form your baseline genre space.
                </p>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                {GENRE_OPTIONS.map((g) => {
                  const isSelected = selectedGenres.includes(g.name);
                  return (
                    <button
                      key={g.name}
                      type="button"
                      onClick={() => toggleGenre(g.name)}
                      className={`p-3.5 rounded-2xl border text-left transition-all cursor-pointer flex items-center justify-between ${
                        isSelected
                          ? 'border-[#F04452] bg-[#F04452]/15 shadow-md shadow-[#F04452]/10 ring-1 ring-[#F04452]'
                          : 'border-[#262638] bg-[#181824] hover:bg-[#1e1e2e] hover:border-[#383850]'
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        <span className="text-xl">{g.icon}</span>
                        <span className="text-xs font-bold text-white">{g.name}</span>
                      </div>
                      <div className={`w-4 h-4 rounded-full flex items-center justify-center ${
                        isSelected ? 'bg-[#F04452] text-white' : 'border border-white/20'
                      }`}>
                        {isSelected && <Check className="w-2.5 h-2.5" />}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* STEP 3: Current Mood / Vibe */}
          {step === 3 && (
            <div className="animate-in fade-in duration-200">
              <div className="mb-4">
                <span className="text-[11px] font-bold text-[#F04452] uppercase tracking-wider">
                  Question 3 / 4
                </span>
                <h3 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight mt-1">
                  What mood or vibe are you craving right now?
                </h3>
                <p className="text-xs sm:text-sm text-[#94a3b8] mt-1">
                  Your mood applies contextual weighting to your recommendations.
                </p>
              </div>

              <div className="space-y-3">
                {MOOD_OPTIONS.map((m) => {
                  const isSelected = selectedMood === m.id;
                  return (
                    <button
                      key={m.id}
                      type="button"
                      onClick={() => setSelectedMood(m.id)}
                      className={`w-full p-4 rounded-2xl border text-left transition-all cursor-pointer flex items-center justify-between ${
                        isSelected
                          ? 'border-[#F04452] bg-[#F04452]/15 ring-1 ring-[#F04452]'
                          : 'border-[#262638] bg-[#181824] hover:bg-[#1e1e2e]'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{m.icon}</span>
                        <div>
                          <h4 className="text-sm font-bold text-white">{m.label}</h4>
                          <p className="text-xs text-[#94a3b8]">{m.desc}</p>
                        </div>
                      </div>
                      <div className={`w-5 h-5 rounded-full flex items-center justify-center ${
                        isSelected ? 'bg-[#F04452] text-white' : 'border border-white/20'
                      }`}>
                        {isSelected && <Check className="w-3 h-3" />}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* STEP 4: Storytelling Era & Pacing */}
          {step === 4 && (
            <div className="animate-in fade-in duration-200">
              <div className="mb-4">
                <span className="text-[11px] font-bold text-[#F04452] uppercase tracking-wider">
                  Question 4 / 4
                </span>
                <h3 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight mt-1">
                  What storytelling era or narrative pacing do you prefer?
                </h3>
                <p className="text-xs sm:text-sm text-[#94a3b8] mt-1">
                  Filter by era and pacing so your recommendations hit the exact cinematic rhythm you enjoy.
                </p>
              </div>

              <div className="space-y-3">
                {ERA_PACING_OPTIONS.map((opt) => {
                  const isSelected = selectedEra === opt.id;
                  return (
                    <button
                      key={opt.id}
                      type="button"
                      onClick={() => setSelectedEra(opt.id)}
                      className={`w-full p-4 rounded-2xl border text-left transition-all cursor-pointer flex items-center justify-between ${
                        isSelected
                          ? 'border-[#F04452] bg-[#F04452]/15 ring-1 ring-[#F04452]'
                          : 'border-[#262638] bg-[#181824] hover:bg-[#1e1e2e]'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{opt.icon}</span>
                        <div>
                          <h4 className="text-sm font-bold text-white">{opt.label}</h4>
                          <p className="text-xs text-[#94a3b8]">{opt.desc}</p>
                        </div>
                      </div>
                      <div className={`w-5 h-5 rounded-full flex items-center justify-center ${
                        isSelected ? 'bg-[#F04452] text-white' : 'border border-white/20'
                      }`}>
                        {isSelected && <Check className="w-3 h-3" />}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* STEP 5: Results Screen */}
          {step === 5 && (
            <div className="animate-in fade-in duration-300">
              {loading ? (
                <div className="py-20 text-center">
                  <div className="w-16 h-16 rounded-full border-4 border-[#F04452]/20 border-t-[#F04452] animate-spin mx-auto mb-4" />
                  <h3 className="text-lg font-bold text-white">Synthesizing Your AI Vector Profile...</h3>
                  <p className="text-xs text-[#94a3b8] mt-1 max-w-sm mx-auto">
                    Computing TF-IDF matrices, applying weighted feature soups, and ranking optimal titles.
                  </p>
                </div>
              ) : quizResults ? (
                <div>
                  {/* Telemetry Badge */}
                  <div className="p-4 rounded-2xl bg-gradient-to-r from-[#1c1c2e] to-[#181824] border border-[#2e2e44] mb-6">
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-xs font-bold text-[#fbbf24] flex items-center gap-1.5 uppercase tracking-wide">
                        <Sparkles className="w-3.5 h-3.5" />
                        Model Successfully Calibrated
                      </span>
                      <span className="text-[10px] bg-[#10b981]/20 text-[#10b981] font-mono px-2 py-0.5 rounded">
                        {quizResults.model_telemetry?.model_version || 'Ready'}
                      </span>
                    </div>
                    <p className="text-xs text-[#cbd5e1] leading-relaxed">
                      {quizResults.model_telemetry?.taste_summary}
                    </p>
                  </div>

                  {/* Curated Recommendations */}
                  <div className="mb-6">
                    <h4 className="text-base font-bold text-white mb-1 flex items-center gap-2">
                      <span className="w-2 h-4 bg-[#F04452] rounded-full" />
                      Personalized Next to Watch Tonight
                    </h4>
                    <p className="text-xs text-[#94a3b8] mb-3">
                      Ranked by high-dimensional cosine similarity matching your anchor, genres, and mood.
                    </p>

                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
                      {quizResults.next_to_watch?.slice(0, 5).map((m) => (
                        <div
                          key={m.id}
                          onClick={() => {
                            onClose();
                            onSelectMovie(m);
                          }}
                          className="group relative bg-[#181826] rounded-2xl overflow-hidden border border-[#2a2a3e] hover:border-[#F04452] transition-all cursor-pointer flex flex-col p-2"
                        >
                          <div className="relative aspect-[2/3] rounded-xl overflow-hidden mb-2 bg-[#1e1e2c]">
                            <img
                              src={m.poster_path}
                              alt={m.title}
                              className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                            />
                            {m.similarity_score && (
                              <div className="absolute top-1.5 right-1.5 bg-[#F04452] text-white text-[9px] font-extrabold px-1.5 py-0.5 rounded shadow">
                                {Math.round(m.similarity_score * 100)}%
                              </div>
                            )}
                          </div>
                          <div>
                            <h5 className="text-xs font-bold text-white line-clamp-1 group-hover:text-[#F04452] transition-colors">
                              {m.title}
                            </h5>
                            <p className="text-[10px] text-[#94a3b8]">★ {Number(m.vote_average || 8).toFixed(1)}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Because You Watched Shelf if available */}
                  {quizResults.because_you_watched && quizResults.because_you_watched.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
                        <Film className="w-4 h-4 text-[#38bdf8]" />
                        Because You Liked {quizResults.anchor_movie?.title}
                      </h4>
                      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
                        {quizResults.because_you_watched.slice(0, 5).map((m) => (
                          <div
                            key={m.id}
                            onClick={() => {
                              onClose();
                              onSelectMovie(m);
                            }}
                            className="bg-[#181826] rounded-2xl overflow-hidden border border-[#2a2a3e] hover:border-[#38bdf8] transition-all cursor-pointer p-2 flex flex-col"
                          >
                            <div className="aspect-[2/3] rounded-xl overflow-hidden mb-2 bg-[#1e1e2c]">
                              <img
                                src={m.poster_path}
                                alt={m.title}
                                className="w-full h-full object-cover"
                              />
                            </div>
                            <h5 className="text-xs font-bold text-white line-clamp-1">{m.title}</h5>
                            <p className="text-[10px] text-[#94a3b8]">★ {Number(m.vote_average || 8).toFixed(1)}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : null}
            </div>
          )}

        </div>

        {/* Modal Action Controls Footer */}
        <div className="px-6 py-4 border-t border-[#242436] flex items-center justify-between relative z-10 bg-[#161622]">
          {step > 1 && step <= 4 ? (
            <button
              onClick={() => setStep(step - 1)}
              className="px-4 py-2.5 rounded-xl bg-[#20202e] hover:bg-[#28283a] text-xs font-semibold text-[#cbd5e1] hover:text-white transition-colors cursor-pointer flex items-center gap-1.5"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              Back
            </button>
          ) : <div />}

          {step <= 4 ? (
            <button
              onClick={handleNext}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-[#F04452] to-[#e03444] hover:from-[#d63340] hover:to-[#c22838] text-white text-xs sm:text-sm font-bold shadow-lg shadow-[#F04452]/20 transition-all cursor-pointer flex items-center gap-2"
            >
              <span>{step === 4 ? 'Generate My Next to Watch' : 'Next Step'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <button
              onClick={handleFinishAndSave}
              className="w-full py-3 rounded-xl bg-[#F04452] hover:bg-[#d63340] text-white text-sm font-bold shadow-lg shadow-[#F04452]/25 transition-all cursor-pointer flex items-center justify-center gap-2"
            >
              <Check className="w-4 h-4" />
              Save Taste Profile & Explore CineMatch
            </button>
          )}
        </div>

      </div>
    </div>
  );
}

