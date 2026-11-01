import React, { useState } from 'react';
import { Film, Search, Bookmark, Compass, Sparkles, SlidersHorizontal, Globe, Tv } from 'lucide-react';

const COUNTRIES = [
  { code: 'IN', name: 'India', flag: '🇮🇳' },
  { code: 'US', name: 'United States', flag: '🇺🇸' },
  { code: 'GB', name: 'United Kingdom', flag: '🇬🇧' },
  { code: 'CA', name: 'Canada', flag: '🇨🇦' },
  { code: 'AU', name: 'Australia', flag: '🇦🇺' },
];

export default function Navbar({
  activeTab,
  setActiveTab,
  onOpenSearch,
  watchlistCount,
  country,
  setCountry,
  onOpenOnboarding,
  user,
  onOpenAuth,
}) {
  const [showCountryMenu, setShowCountryMenu] = useState(false);

  const selectedCountry = COUNTRIES.find(c => c.code === country) || COUNTRIES[0];

  return (
    <nav className="sticky top-0 z-40 bg-[#101014]/90 backdrop-blur-md border-b border-[#242432] transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-18">
          
          {/* Logo */}
          <div className="flex items-center gap-8">
            <button
              onClick={() => setActiveTab('discover')}
              className="flex items-center gap-2.5 text-left group cursor-pointer focus:outline-none"
            >
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#F04452] to-[#ff6b77] flex items-center justify-center shadow-lg shadow-[#F04452]/20 group-hover:scale-105 transition-transform">
                <Film className="w-5 h-5 text-white" />
              </div>
              <div>
                <span className="text-xl font-bold tracking-tight text-white flex items-center">
                  Cine<span className="text-[#F04452]">Match</span>
                </span>
                <span className="text-[10px] uppercase tracking-widest text-[#94a3b8] font-semibold block -mt-1">
                  AI Discovery & OTT
                </span>
              </div>
            </button>

            {/* Desktop Navigation Links */}
            <div className="hidden md:flex items-center gap-1">
              <button
                onClick={() => setActiveTab('discover')}
                className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer flex items-center gap-2 ${
                  activeTab === 'discover'
                    ? 'bg-[#1e1e2a] text-white shadow-inner'
                    : 'text-[#94a3b8] hover:text-white hover:bg-[#161620]'
                }`}
              >
                <Compass className="w-4 h-4 text-[#F04452]" />
                Discover
              </button>

              <button
                onClick={() => setActiveTab('series')}
                className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer flex items-center gap-2 ${
                  activeTab === 'series'
                    ? 'bg-[#1e1e2a] text-white shadow-inner'
                    : 'text-[#94a3b8] hover:text-white hover:bg-[#161620]'
                }`}
              >
                <Tv className="w-4 h-4 text-[#6366f1]" />
                Web Series
              </button>

              <button
                onClick={() => setActiveTab('foryou')}
                className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer flex items-center gap-2 ${
                  activeTab === 'foryou'
                    ? 'bg-[#1e1e2a] text-white shadow-inner'
                    : 'text-[#94a3b8] hover:text-white hover:bg-[#161620]'
                }`}
              >
                <Sparkles className="w-4 h-4 text-[#fbbf24]" />
                For You
                <span className="bg-[#F04452]/20 text-[#F04452] text-[10px] font-bold px-1.5 py-0.5 rounded-full uppercase">
                  AI
                </span>
              </button>

              <button
                onClick={() => setActiveTab('genres')}
                className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer flex items-center gap-2 ${
                  activeTab === 'genres'
                    ? 'bg-[#1e1e2a] text-white shadow-inner'
                    : 'text-[#94a3b8] hover:text-white hover:bg-[#161620]'
                }`}
              >
                <SlidersHorizontal className="w-4 h-4 text-[#38bdf8]" />
                Genres
              </button>

              <button
                onClick={() => setActiveTab('watchlist')}
                className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer flex items-center gap-2 ${
                  activeTab === 'watchlist'
                    ? 'bg-[#1e1e2a] text-white shadow-inner'
                    : 'text-[#94a3b8] hover:text-white hover:bg-[#161620]'
                }`}
              >
                <Bookmark className="w-4 h-4 text-[#a855f7]" />
                My Watchlist
                {watchlistCount > 0 && (
                  <span className="bg-[#F04452] text-white text-[11px] font-bold px-2 py-0.2 rounded-full">
                    {watchlistCount}
                  </span>
                )}
              </button>
            </div>
          </div>

          {/* Right Action Controls */}
          <div className="flex items-center gap-3">
            {/* Instant Search Button */}
            <button
              onClick={onOpenSearch}
              className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#181822] hover:bg-[#20202c] border border-[#2b2b3a] text-sm text-[#94a3b8] hover:text-white transition-all cursor-pointer shadow-sm group"
              title="Search movies, actors, directors"
            >
              <Search className="w-4 h-4 text-[#94a3b8] group-hover:text-[#F04452] transition-colors" />
              <span className="hidden sm:inline">Search movies, directors...</span>
              <kbd className="hidden lg:inline-block text-[10px] bg-[#242434] text-[#94a3b8] px-1.5 py-0.5 rounded border border-[#343446]">
                Ctrl K
              </kbd>
            </button>

            {/* Country Selector for OTT Legal Availability */}
            <div className="relative">
              <button
                onClick={() => {
                  setShowCountryMenu(!showCountryMenu);
                  setShowProfileMenu(false);
                }}
                className="flex items-center gap-1.5 px-2.5 py-1.8 rounded-xl bg-[#181822] hover:bg-[#222230] border border-[#2b2b3a] text-xs font-medium text-white transition-all cursor-pointer"
                title={`OTT Region: ${selectedCountry.name}`}
              >
                <span className="text-base leading-none">{selectedCountry.flag}</span>
                <span className="font-semibold text-[#cbd5e1]">{selectedCountry.code}</span>
              </button>

              {showCountryMenu && (
                <div className="absolute right-0 mt-2 w-48 rounded-xl bg-[#181824] border border-[#2e2e40] shadow-2xl py-2 z-50 animate-in fade-in zoom-in-95 duration-100">
                  <div className="px-3 py-1.5 border-b border-[#282838] mb-1">
                    <p className="text-[11px] font-semibold text-[#94a3b8] uppercase tracking-wider flex items-center gap-1.5">
                      <Globe className="w-3.5 h-3.5 text-[#F04452]" />
                      OTT Streaming Region
                    </p>
                  </div>
                  {COUNTRIES.map(c => (
                    <button
                      key={c.code}
                      onClick={() => {
                        setCountry(c.code);
                        setShowCountryMenu(false);
                      }}
                      className={`w-full text-left px-3.5 py-2 text-xs flex items-center justify-between transition-colors cursor-pointer ${
                        country === c.code
                          ? 'bg-[#F04452]/15 text-[#F04452] font-semibold'
                          : 'text-[#e2e8f0] hover:bg-[#202030]'
                      }`}
                    >
                      <span className="flex items-center gap-2">
                        <span>{c.flag}</span>
                        <span>{c.name}</span>
                      </span>
                      {country === c.code && <span className="text-[10px] text-[#F04452]">Active</span>}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Profile / Login Trigger */}
            <div className="relative">
              <button
                onClick={onOpenAuth}
                className="flex items-center gap-2 px-3 py-1.8 rounded-xl bg-gradient-to-tr from-[#1e1e2c] to-[#2a2a3e] border border-[#3c3c54] text-white hover:border-[#F04452] transition-all cursor-pointer shadow-sm group"
                title={user?.isLoggedIn ? `Profile: ${user.name}` : 'Sign In & Personalize'}
              >
                <span className="text-base">{user?.avatar || '🍿'}</span>
                <span className="text-xs font-bold text-white hidden sm:inline max-w-[90px] truncate">
                  {user?.isLoggedIn ? user.name : 'Sign In'}
                </span>
                {!user?.isLoggedIn && (
                  <span className="w-2 h-2 rounded-full bg-[#F04452] animate-ping" />
                )}
              </button>
            </div>

          </div>
        </div>

        {/* Mobile Navigation Bar */}
        <div className="flex md:hidden items-center justify-around py-2.5 border-t border-[#20202c]">
          <button
            onClick={() => setActiveTab('discover')}
            className={`text-xs font-medium py-1 px-2 rounded-lg flex items-center gap-1.5 ${
              activeTab === 'discover' ? 'text-[#F04452] bg-[#F04452]/10 font-semibold' : 'text-[#94a3b8]'
            }`}
          >
            <Compass className="w-3.5 h-3.5" />
            Discover
          </button>
          <button
            onClick={() => setActiveTab('series')}
            className={`text-xs font-medium py-1 px-2 rounded-lg flex items-center gap-1.5 ${
              activeTab === 'series' ? 'text-[#6366f1] bg-[#6366f1]/10 font-semibold' : 'text-[#94a3b8]'
            }`}
          >
            <Tv className="w-3.5 h-3.5" />
            Series
          </button>
          <button
            onClick={() => setActiveTab('foryou')}
            className={`text-xs font-medium py-1 px-2 rounded-lg flex items-center gap-1.5 ${
              activeTab === 'foryou' ? 'text-[#fbbf24] bg-[#fbbf24]/10 font-semibold' : 'text-[#94a3b8]'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            For You
          </button>
          <button
            onClick={() => setActiveTab('genres')}
            className={`text-xs font-medium py-1 px-2 rounded-lg flex items-center gap-1.5 ${
              activeTab === 'genres' ? 'text-[#38bdf8] bg-[#38bdf8]/10 font-semibold' : 'text-[#94a3b8]'
            }`}
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            Genres
          </button>
          <button
            onClick={() => setActiveTab('watchlist')}
            className={`text-xs font-medium py-1 px-2 rounded-lg flex items-center gap-1.5 ${
              activeTab === 'watchlist' ? 'text-[#a855f7] bg-[#a855f7]/10 font-semibold' : 'text-[#94a3b8]'
            }`}
          >
            <Bookmark className="w-3.5 h-3.5" />
            Watchlist ({watchlistCount})
          </button>
        </div>

      </div>
    </nav>
  );
}

