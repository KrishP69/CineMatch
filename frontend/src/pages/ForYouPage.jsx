import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  SlidersHorizontal,
  Heart,
  Eye,
  RefreshCw,
  Zap,
  Bot,
  Cpu,
  Database,
  Layers,
  Activity,
  CheckCircle2,
  X,
  Play,
  RotateCw,
} from 'lucide-react';
import MovieCard from '../components/MovieCard';
import ForYouAIAgent from '../components/ForYouAIAgent';
import { api } from '../services/api';

export default function ForYouPage({
  onSelectMovie,
  onWatchProviders,
  watchlistState,
  onOpenOnboarding,
}) {
  const {
    watchlist,
    toggleWatchlist,
    liked,
    watched,
    disliked,
    favoriteGenres,
    mood,
    era,
    toggleLiked,
    toggleWatched,
    modelTelemetry,
    retrainModel,
  } = watchlistState;

  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeView, setActiveView] = useState('feed'); // 'feed' | 'ai_agent'
  const [engineMode, setEngineMode] = useState('neural'); // 'neural' | 'vector'
  const [gpuMeta, setGpuMeta] = useState(null);
  const [isNeuralModalOpen, setIsNeuralModalOpen] = useState(false);
  const [isTraining, setIsTraining] = useState(false);
  const [trainingLog, setTrainingLog] = useState(null);

  // Load hardware / model status
  const fetchModelStatus = async () => {
    try {
      const res = await api.getModelStatus();
      if (res.success && res.data) {
        setGpuMeta(res.data);
      }
    } catch (err) {
      console.warn('Could not fetch model telemetry:', err);
    }
  };

  const fetchPersonalized = async (mode = engineMode) => {
    setLoading(true);
    try {
      if (mode === 'neural') {
        const res = await api.getNeuralRecommendations({
          liked_ids: liked,
          watched_ids: watched,
          exclude_ids: watched,
          top_n: 18,
        });
        if (res.success) {
          setRecommendations(res.recommendations || []);
        }
      } else {
        const res = await api.retrainModel({
          liked_movie_ids: liked,
          watched_movie_ids: watched,
          disliked_movie_ids: disliked,
          watchlist_movie_ids: watchlist.map((m) => m.id),
          favorite_genres: favoriteGenres,
          mood: mood,
          era: era,
          count: 18,
        });
        if (res.success) {
          setRecommendations(res.recommendations || []);
        }
      }
    } catch (err) {
      console.error('Error fetching personalized recommendations:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchModelStatus();
  }, []);

  useEffect(() => {
    fetchPersonalized(engineMode);
  }, [liked, watched, favoriteGenres, mood, era, engineMode]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchPersonalized(engineMode);
  };

  const handleRunLocalTraining = async () => {
    setIsTraining(true);
    setTrainingLog(null);
    try {
      const res = await api.trainNeuralModel();
      if (res.success) {
        setTrainingLog(res.meta);
        await fetchModelStatus();
        await fetchPersonalized('neural');
      }
    } catch (err) {
      console.error('Local training failed:', err);
    } finally {
      setIsTraining(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 animate-in fade-in duration-300">
      
      {/* View Switcher: Feed vs AI Agent */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-2 bg-[#161622] p-1.5 rounded-2xl border border-[#262638]">
          <button
            onClick={() => setActiveView('feed')}
            className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all cursor-pointer flex items-center gap-2 ${
              activeView === 'feed'
                ? 'bg-[#F04452] text-white shadow-md shadow-[#F04452]/20'
                : 'text-[#94a3b8] hover:text-white'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>Personalized For You</span>
          </button>

          <button
            onClick={() => setActiveView('ai_agent')}
            className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all cursor-pointer flex items-center gap-2 ${
              activeView === 'ai_agent'
                ? 'bg-gradient-to-r from-[#38bdf8] to-[#0284c7] text-white shadow-md'
                : 'text-[#94a3b8] hover:text-white'
            }`}
          >
            <Bot className="w-4 h-4 text-[#38bdf8]" />
            <span>Ask For You AI Agent</span>
            <span className="bg-white/20 text-white text-[10px] px-1.5 py-0.2 rounded-full uppercase">
              Top 10
            </span>
          </button>
        </div>

        {/* Local Hardware Lab Telemetry Pill */}
        <button
          onClick={() => setIsNeuralModalOpen(true)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#141420] border border-[#2a2a3e] hover:border-[#38bdf8]/50 text-xs text-[#cbd5e1] hover:text-white transition-all cursor-pointer"
        >
          <Cpu className="w-4 h-4 text-[#38bdf8]" />
          <span>
            <strong className="text-white">RTX 5060</strong> Neural Engine
          </span>
          <span className="bg-[#10b981]/20 text-[#10b981] text-[10px] px-2 py-0.5 rounded-full font-bold">
            1.35M Params
          </span>
        </button>
      </div>

      {/* VIEW 1: For You AI Agent */}
      {activeView === 'ai_agent' && (
        <ForYouAIAgent
          onSelectMovie={onSelectMovie}
          onWatchProviders={onWatchProviders}
          watchlistState={watchlistState}
        />
      )}

      {/* VIEW 2: Personalized Feed */}
      {activeView === 'feed' && (
        <>
          {/* Engine Selector Pill & Taste Profile Banner */}
          <div className="relative rounded-2xl md:rounded-3xl p-6 sm:p-8 bg-gradient-to-r from-[#181826] via-[#1c1c2e] to-[#161622] border border-[#2b2b3e] shadow-xl mb-10 overflow-hidden">
            <div className="absolute top-0 right-0 w-80 h-80 bg-[#F04452]/10 rounded-full blur-3xl pointer-events-none" />

            <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div>
                {/* Engine Mode Toggle */}
                <div className="flex flex-wrap items-center gap-2 mb-3">
                  <button
                    onClick={() => setEngineMode('neural')}
                    className={`px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                      engineMode === 'neural'
                        ? 'bg-[#38bdf8]/20 border border-[#38bdf8]/50 text-[#38bdf8] shadow-sm'
                        : 'bg-[#14141e] border border-[#262638] text-[#94a3b8] hover:text-white'
                    }`}
                  >
                    <Cpu className="w-3.5 h-3.5" />
                    <span>Deep Neural NCF (MovieLens 100k • RTX 5060)</span>
                  </button>

                  <button
                    onClick={() => setEngineMode('vector')}
                    className={`px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                      engineMode === 'vector'
                        ? 'bg-[#fbbf24]/20 border border-[#fbbf24]/50 text-[#fbbf24] shadow-sm'
                        : 'bg-[#14141e] border border-[#262638] text-[#94a3b8] hover:text-white'
                    }`}
                  >
                    <Zap className="w-3.5 h-3.5" />
                    <span>Continuous Vector Space (TF-IDF)</span>
                  </button>
                </div>

                <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                  Personalized Next to Watch
                </h1>

                <p className="text-xs sm:text-sm text-[#cbd5e1] mt-1 max-w-xl leading-relaxed">
                  {engineMode === 'neural'
                    ? 'Dual-Tower Neural Collaborative Filtering (GMF + MLP) model evaluating 64-dimensional latent movie embeddings on your RTX 5060.'
                    : (modelTelemetry?.taste_summary ||
                      'Retrained after every movie interaction via TF-IDF vectorization and cosine similarity.')}
                </p>

                {/* Taste Stats */}
                <div className="flex flex-wrap items-center gap-2.5 mt-4">
                  <span className="text-xs text-[#cbd5e1] bg-[#14141e] px-3 py-1.5 rounded-lg border border-[#282838] flex items-center gap-1.5">
                    <Heart className="w-3.5 h-3.5 text-[#ec4899]" />
                    <strong>{liked.length}</strong> Liked
                  </span>

                  <span className="text-xs text-[#cbd5e1] bg-[#14141e] px-3 py-1.5 rounded-lg border border-[#282838] flex items-center gap-1.5">
                    <Eye className="w-3.5 h-3.5 text-[#3b82f6]" />
                    <strong>{watched.length}</strong> Watched (Filtered)
                  </span>

                  <span className="text-xs text-[#10b981] bg-[#10b981]/10 px-3 py-1.5 rounded-lg border border-[#10b981]/20 flex items-center gap-1.5">
                    <Database className="w-3.5 h-3.5" />
                    MovieLens 100k Benchmark
                  </span>
                </div>
              </div>

              {/* Controls */}
              <div className="flex items-center gap-2">
                <button
                  onClick={handleRefresh}
                  disabled={refreshing}
                  className="p-3 rounded-xl bg-[#1e1e2c] hover:bg-[#28283c] border border-[#303044] text-[#cbd5e1] hover:text-white transition-colors cursor-pointer disabled:opacity-50"
                  title="Recalculate AI Vectors"
                >
                  <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin text-[#F04452]' : ''}`} />
                </button>

                <button
                  onClick={() => setIsNeuralModalOpen(true)}
                  className="px-3.5 py-3 rounded-xl bg-[#1e1e2c] hover:bg-[#28283c] border border-[#38bdf8]/30 text-[#38bdf8] text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer"
                  title="View Model Specs and Retrain on GPU"
                >
                  <Cpu className="w-4 h-4" />
                  <span>Model Lab</span>
                </button>

                <button
                  onClick={onOpenOnboarding}
                  className="px-4 py-3 rounded-xl bg-[#F04452] hover:bg-[#d63340] text-white text-xs sm:text-sm font-bold flex items-center gap-2 shadow-lg shadow-[#F04452]/20 transition-all cursor-pointer hover:scale-103"
                >
                  <SlidersHorizontal className="w-4 h-4" />
                  <span>Personalization MCQ</span>
                </button>
              </div>
            </div>
          </div>

          {/* Grid of Recommendations */}
          <div>
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <div
                  className={`w-1.5 h-5 rounded-full ${
                    engineMode === 'neural' ? 'bg-[#38bdf8]' : 'bg-[#fbbf24]'
                  }`}
                />
                <h2 className="text-xl font-bold text-white tracking-tight">
                  {engineMode === 'neural'
                    ? 'Neural NCF Recommended Matches'
                    : 'Vector Space Recommended Matches'}
                </h2>
                <span className="text-xs text-[#94a3b8] font-medium ml-2">
                  ({recommendations.length} titles scored)
                </span>
              </div>
            </div>

            {loading ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 sm:gap-5">
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((i) => (
                  <div key={i} className="aspect-[2/3] skeleton rounded-2xl" />
                ))}
              </div>
            ) : recommendations.length > 0 ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 sm:gap-5">
                {recommendations.map((movie) => (
                  <MovieCard
                    key={movie.id}
                    movie={movie}
                    onSelect={onSelectMovie}
                    onWatchProviders={onWatchProviders}
                    inWatchlist={watchlist.some((m) => m.id === movie.id)}
                    onToggleWatchlist={toggleWatchlist}
                    isWatched={watched.includes(movie.id)}
                    onToggleWatched={toggleWatched}
                    similarityScore={movie.similarity_score}
                    recommendationReason={movie.recommendation_reason}
                  />
                ))}
              </div>
            ) : (
              <div className="py-16 text-center bg-[#14141e] rounded-3xl border border-[#242434] p-8">
                <Sparkles className="w-10 h-10 text-[#64748b] mx-auto mb-3" />
                <h3 className="text-base font-bold text-white mb-1">
                  No Recommendations Generated
                </h3>
                <p className="text-xs text-[#94a3b8] max-w-sm mx-auto mb-4">
                  Take the quick MCQ quiz or like a movie to initialize your taste profile.
                </p>
                <button
                  onClick={onOpenOnboarding}
                  className="px-5 py-2.5 rounded-xl bg-[#F04452] text-white text-xs font-bold shadow-md cursor-pointer"
                >
                  Start Personalization Quiz
                </button>
              </div>
            )}
          </div>
        </>
      )}

      {/* NEURAL MODEL LAB MODAL */}
      {isNeuralModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
          <div className="relative w-full max-w-2xl bg-[#161622] rounded-3xl border border-[#2e2e42] shadow-2xl overflow-hidden p-6 sm:p-8">
            <button
              onClick={() => setIsNeuralModalOpen(false)}
              className="absolute top-5 right-5 w-8 h-8 rounded-full bg-[#20202e] hover:bg-[#2c2c3e] border border-[#34344a] text-[#94a3b8] hover:text-white flex items-center justify-center transition-colors cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>

            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-[#38bdf8] to-[#0284c7] flex items-center justify-center text-white shadow-lg shadow-[#38bdf8]/20">
                <Cpu className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">Local RTX 5060 Neural Lab</h2>
                <p className="text-xs text-[#94a3b8]">
                  PyTorch Deep Collaborative Filtering (NCF / NeuMF) trained on your device
                </p>
              </div>
            </div>

            {/* Model Specs Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
              <div className="bg-[#141420] p-3 rounded-2xl border border-[#262638]">
                <p className="text-[10px] text-[#94a3b8] uppercase font-bold">Target Hardware</p>
                <p className="text-sm font-extrabold text-[#38bdf8] mt-0.5 truncate">
                  RTX 5060 (8GB VRAM)
                </p>
              </div>

              <div className="bg-[#141420] p-3 rounded-2xl border border-[#262638]">
                <p className="text-[10px] text-[#94a3b8] uppercase font-bold">Parameters</p>
                <p className="text-sm font-extrabold text-white mt-0.5">
                  1,349,953
                </p>
              </div>

              <div className="bg-[#141420] p-3 rounded-2xl border border-[#262638]">
                <p className="text-[10px] text-[#94a3b8] uppercase font-bold">Dataset</p>
                <p className="text-sm font-extrabold text-[#10b981] mt-0.5">
                  MovieLens 100k
                </p>
              </div>

              <div className="bg-[#141420] p-3 rounded-2xl border border-[#262638]">
                <p className="text-[10px] text-[#94a3b8] uppercase font-bold">Latent Dimension</p>
                <p className="text-sm font-extrabold text-white mt-0.5">
                  64 (Dual-Tower)
                </p>
              </div>

              <div className="bg-[#141420] p-3 rounded-2xl border border-[#262638]">
                <p className="text-[10px] text-[#94a3b8] uppercase font-bold">Val RMSE</p>
                <p className="text-sm font-extrabold text-[#fbbf24] mt-0.5">
                  {gpuMeta?.meta?.final_val_rmse || '0.9311'}
                </p>
              </div>

              <div className="bg-[#141420] p-3 rounded-2xl border border-[#262638]">
                <p className="text-[10px] text-[#94a3b8] uppercase font-bold">Model Status</p>
                <p className="text-sm font-extrabold text-[#10b981] mt-0.5 flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Loaded
                </p>
              </div>
            </div>

            {/* Architecture Explainer */}
            <div className="p-4 rounded-2xl bg-[#141420] border border-[#262638] mb-6">
              <h4 className="text-xs font-bold text-white mb-1 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-[#38bdf8]" />
                Dual-Tower Neural Architecture (NeuMF)
              </h4>
              <p className="text-xs text-[#94a3b8] leading-relaxed">
                Fuses Generalized Matrix Factorization (GMF element-wise embedding interaction) with a 3-layer Multi-Layer Perceptron (MLP 128 &rarr; 64 &rarr; 32 with ReLU and BatchNorm) to capture non-linear user-movie preferences across 100,836 ratings.
              </p>
            </div>

            {/* Retrain Action */}
            <div className="space-y-3">
              <button
                onClick={handleRunLocalTraining}
                disabled={isTraining}
                className="w-full py-3.5 px-4 rounded-xl bg-gradient-to-r from-[#38bdf8] to-[#0284c7] hover:from-[#0284c7] hover:to-[#0369a1] text-white font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-[#38bdf8]/20 transition-all cursor-pointer disabled:opacity-50"
              >
                {isTraining ? (
                  <>
                    <RotateCw className="w-4 h-4 animate-spin" />
                    <span>Training 10 Epochs Locally on Your Device...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 fill-white" />
                    <span>Retrain Neural Model Locally on My RTX 5060</span>
                  </>
                )}
              </button>

              {trainingLog && (
                <div className="p-3 bg-[#10b981]/10 border border-[#10b981]/30 rounded-xl text-xs text-[#10b981] text-center font-medium">
                  &check; Local training complete! Val RMSE: {trainingLog.final_val_rmse} in {trainingLog.training_time_sec}s. Neural weights reloaded.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
