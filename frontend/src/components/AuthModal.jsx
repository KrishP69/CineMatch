import React, { useState } from 'react';
import {
  X, User, Sparkles, Check, LogOut, Film, Heart, Eye,
  Bookmark, ShieldCheck, Cpu, KeyRound, Mail, AlertCircle, ArrowRight
} from 'lucide-react';
import { api, setAuthToken } from '../services/api';

const AVATARS = ['🎬', '🍿', '🚀', '🎭', '👑', '🕵️', '⚡', '☕'];

export default function AuthModal({
  isOpen,
  onClose,
  user,
  onLoginSuccess,
  onLogout,
  onOpenMCQ,
  stats = {},
  modelTelemetry = null,
}) {
  const [mode, setMode] = useState('login'); // 'login' | 'register'
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [avatar, setAvatar] = useState('🎬');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (mode === 'register') {
        const res = await api.register(username, email, password, avatar);
        if (res.success) {
          setAuthToken(res.token);
          onLoginSuccess(res.user);
          onClose();
        } else {
          setError(res.error || 'Registration failed');
        }
      } else {
        const res = await api.login(username, password);
        if (res.success) {
          setAuthToken(res.token);
          onLoginSuccess(res.user);
          onClose();
        } else {
          setError(res.error || 'Invalid credentials');
        }
      }
    } catch (err) {
      setError(err.message || 'Authentication error. Please check your network.');
    } finally {
      setLoading(false);
    }
  };

  const handleGuestLogin = () => {
    onLoginSuccess({
      id: 9999,
      username: 'Guest Cinephile',
      email: 'guest@cinematch.ai',
      avatar: '🎬',
      isGuest: true,
      role: 'guest',
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-md bg-[#161622] rounded-3xl border border-[#2e2e42] shadow-2xl overflow-hidden p-6 sm:p-8">
        
        {/* Ambient Glow */}
        <div className="absolute -top-20 -right-20 w-44 h-44 bg-[#F04452]/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-20 -left-20 w-44 h-44 bg-[#38bdf8]/15 rounded-full blur-3xl pointer-events-none" />

        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 w-8 h-8 rounded-full bg-[#20202e] hover:bg-[#2c2c3e] border border-[#34344a] text-[#94a3b8] hover:text-white flex items-center justify-center transition-colors cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>

        {user && user.isLoggedIn ? (
          /* Profile Details View */
          <div>
            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-[#F04452] to-[#ff6b77] flex items-center justify-center text-3xl shadow-lg shadow-[#F04452]/25">
                {user.avatar || '🍿'}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-xl font-bold text-white">{user.username || user.name}</h2>
                  <span className="bg-[#10b981]/20 text-[#10b981] text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
                    <ShieldCheck className="w-3 h-3" /> {user.isGuest ? 'Guest' : 'Authenticated'}
                  </span>
                </div>
                <p className="text-xs text-[#94a3b8] mt-0.5">{user.email}</p>
              </div>
            </div>

            {/* Interaction Stats */}
            <div className="grid grid-cols-3 gap-2.5 mb-6">
              <div className="bg-[#1a1a28] p-3 rounded-2xl border border-[#28283a] text-center">
                <Bookmark className="w-4 h-4 text-[#a855f7] mx-auto mb-1" />
                <p className="text-base font-extrabold text-white">{stats.watchlistCount || 0}</p>
                <p className="text-[10px] text-[#94a3b8] uppercase font-semibold">Watchlist</p>
              </div>

              <div className="bg-[#1a1a28] p-3 rounded-2xl border border-[#28283a] text-center">
                <Eye className="w-4 h-4 text-[#3b82f6] mx-auto mb-1" />
                <p className="text-base font-extrabold text-white">{stats.watchedCount || 0}</p>
                <p className="text-[10px] text-[#94a3b8] uppercase font-semibold">Watched</p>
              </div>

              <div className="bg-[#1a1a28] p-3 rounded-2xl border border-[#28283a] text-center">
                <Heart className="w-4 h-4 text-[#ec4899] mx-auto mb-1" />
                <p className="text-base font-extrabold text-white">{stats.likedCount || 0}</p>
                <p className="text-[10px] text-[#94a3b8] uppercase font-semibold">Liked</p>
              </div>
            </div>

            {/* Model Telemetry */}
            <div className="p-4 rounded-2xl bg-[#141420] border border-[#2a2a3e] mb-6 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-[#fbbf24]" />
                  AI Taste Engine Status
                </span>
                <span className="text-[10px] text-[#10b981] font-mono bg-[#10b981]/10 px-2 py-0.5 rounded">
                  {modelTelemetry?.model_version || 'Active'}
                </span>
              </div>
              <p className="text-xs text-[#cbd5e1] leading-relaxed">
                {modelTelemetry?.taste_summary || 'Model continuously calibrated to your viewing choices.'}
              </p>
              <div className="pt-2 border-t border-[#262638] flex items-center justify-between text-[11px] text-[#94a3b8]">
                <span className="flex items-center gap-1 text-[#38bdf8]">
                  <Cpu className="w-3.5 h-3.5" />
                  RTX 5060 Neural Acceleration
                </span>
                <span className="text-white font-mono">1.35M weights</span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex flex-col gap-2.5">
              <button
                onClick={() => {
                  onClose();
                  onOpenMCQ();
                }}
                className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-[#F04452] to-[#e03444] hover:from-[#d63340] hover:to-[#c22838] text-white font-bold text-xs sm:text-sm flex items-center justify-center gap-2 shadow-lg shadow-[#F04452]/20 transition-all cursor-pointer"
              >
                <Sparkles className="w-4 h-4" />
                Retune Personalization MCQ Quiz
              </button>

              <button
                onClick={() => {
                  setAuthToken(null);
                  onLogout();
                  onClose();
                }}
                className="w-full py-2.5 px-4 rounded-xl bg-[#20202e] hover:bg-[#28283a] border border-[#303044] text-[#cbd5e1] hover:text-white font-semibold text-xs flex items-center justify-center gap-2 transition-colors cursor-pointer"
              >
                <LogOut className="w-3.5 h-3.5 text-[#ef4444]" />
                Log Out
              </button>
            </div>
          </div>
        ) : (
          /* Sign In / Sign Up Form */
          <div>
            <div className="text-center mb-6">
              <div className="w-13 h-13 rounded-2xl bg-gradient-to-tr from-[#F04452] to-[#ff6b77] flex items-center justify-center mx-auto mb-3 text-2xl shadow-lg shadow-[#F04452]/25">
                <User className="w-6 h-6 text-white" />
              </div>
              <h2 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
                {mode === 'login' ? 'Welcome Back to CineMatch' : 'Join CineMatch Community'}
              </h2>
              <p className="text-xs text-[#94a3b8] mt-1 max-w-xs mx-auto">
                {mode === 'login'
                  ? 'Sign in to sync your reviews, ratings, and continuous AI recommendations.'
                  : 'Create an account to rate movies, write reviews with sentiment analysis, and train your neural taste profile.'}
              </p>
            </div>

            {/* Mode Switcher */}
            <div className="flex items-center gap-1.5 p-1 bg-[#14141e] rounded-xl border border-[#28283a] mb-5">
              <button
                type="button"
                onClick={() => { setMode('login'); setError(''); }}
                className={`flex-1 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                  mode === 'login'
                    ? 'bg-[#F04452] text-white shadow-sm'
                    : 'text-[#94a3b8] hover:text-white'
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => { setMode('register'); setError(''); }}
                className={`flex-1 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                  mode === 'register'
                    ? 'bg-[#F04452] text-white shadow-sm'
                    : 'text-[#94a3b8] hover:text-white'
                }`}
              >
                Create Account
              </button>
            </div>

            {error && (
              <div className="p-3 mb-4 rounded-xl bg-[#ef4444]/15 border border-[#ef4444]/30 flex items-center gap-2 text-xs text-[#fca5a5]">
                <AlertCircle className="w-4 h-4 flex-shrink-0 text-[#ef4444]" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-3.5">
              {/* Avatar Selector (Registration Only) */}
              {mode === 'register' && (
                <div>
                  <label className="block text-[11px] font-semibold text-[#cbd5e1] mb-1">
                    Choose Your Cinephile Avatar
                  </label>
                  <div className="flex items-center justify-between gap-1 p-1.5 bg-[#1a1a28] rounded-xl border border-[#2a2a3e]">
                    {AVATARS.map((av) => (
                      <button
                        key={av}
                        type="button"
                        onClick={() => setAvatar(av)}
                        className={`w-8 h-8 rounded-lg flex items-center justify-center text-base transition-transform cursor-pointer ${
                          avatar === av
                            ? 'bg-[#F04452] scale-110 shadow-md shadow-[#F04452]/30'
                            : 'hover:bg-[#262638]'
                        }`}
                      >
                        {av}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Username */}
              <div>
                <label className="block text-[11px] font-semibold text-[#cbd5e1] mb-1">
                  {mode === 'login' ? 'Username or Email' : 'Cinephile Username'}
                </label>
                <div className="relative">
                  <input
                    type="text"
                    required
                    placeholder={mode === 'login' ? 'alex or alex@cinematch.ai' : 'alex_cinephile'}
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-[#1a1a28] border border-[#2a2a3e] text-xs text-white placeholder-[#64748b] focus:outline-none focus:border-[#F04452]"
                  />
                  <User className="w-3.5 h-3.5 text-[#64748b] absolute right-3.5 top-3.5" />
                </div>
              </div>

              {/* Email (Registration Only) */}
              {mode === 'register' && (
                <div>
                  <label className="block text-[11px] font-semibold text-[#cbd5e1] mb-1">
                    Email Address
                  </label>
                  <div className="relative">
                    <input
                      type="email"
                      required
                      placeholder="alex@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-[#1a1a28] border border-[#2a2a3e] text-xs text-white placeholder-[#64748b] focus:outline-none focus:border-[#F04452]"
                    />
                    <Mail className="w-3.5 h-3.5 text-[#64748b] absolute right-3.5 top-3.5" />
                  </div>
                </div>
              )}

              {/* Password */}
              <div>
                <label className="block text-[11px] font-semibold text-[#cbd5e1] mb-1">
                  Password
                </label>
                <div className="relative">
                  <input
                    type="password"
                    required
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-[#1a1a28] border border-[#2a2a3e] text-xs text-white placeholder-[#64748b] focus:outline-none focus:border-[#F04452]"
                  />
                  <KeyRound className="w-3.5 h-3.5 text-[#64748b] absolute right-3.5 top-3.5" />
                </div>
              </div>

              {/* Submit */}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-4 rounded-xl bg-[#F04452] hover:bg-[#d63340] text-white font-bold text-xs sm:text-sm shadow-lg shadow-[#F04452]/25 transition-all cursor-pointer mt-3 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <span>{loading ? 'Authenticating...' : mode === 'login' ? 'Sign In to CineMatch' : 'Create Account'}</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              <div className="text-center pt-2">
                <button
                  type="button"
                  onClick={handleGuestLogin}
                  className="text-xs text-[#94a3b8] hover:text-white underline cursor-pointer"
                >
                  Continue as Guest Explorer
                </button>
              </div>
            </form>
          </div>
        )}

      </div>
    </div>
  );
}
