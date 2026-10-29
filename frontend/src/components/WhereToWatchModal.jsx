import React, { useState, useEffect } from 'react';
import { X, Tv, Globe, ExternalLink, AlertCircle, Film } from 'lucide-react';
import { api } from '../services/api';

const COUNTRIES = [
  { code: 'IN', name: 'India', flag: '🇮🇳' },
  { code: 'US', name: 'United States', flag: '🇺🇸' },
  { code: 'GB', name: 'United Kingdom', flag: '🇬🇧' },
  { code: 'CA', name: 'Canada', flag: '🇨🇦' },
  { code: 'AU', name: 'Australia', flag: '🇦🇺' },
];

export default function WhereToWatchModal({
  movie,
  onClose,
  country = 'IN',
  setCountry,
}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!movie) return;

    let isMounted = true;
    setLoading(true);

    api.getWatchProviders(movie.id, country)
      .then((res) => {
        if (isMounted && res.success) {
          setData(res.data);
        }
      })
      .catch((err) => {
        console.error('Failed to load OTT data:', err);
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [movie, country]);

  if (!movie) return null;

  const selectedCountry = COUNTRIES.find(c => c.code === country) || COUNTRIES[0];

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/85 backdrop-blur-md flex items-center justify-center p-4 animate-in fade-in duration-200">
      
      {/* Backdrop click to close */}
      <div className="fixed inset-0" onClick={onClose} />

      <div className="relative z-10 w-full max-w-lg bg-[#14141e] border border-[#2e2e42] rounded-2xl shadow-2xl overflow-hidden p-6">
        
        {/* Header */}
        <div className="flex items-start justify-between pb-4 border-b border-[#242434] mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#F04452]/20 border border-[#F04452]/30 flex items-center justify-center">
              <Tv className="w-5 h-5 text-[#F04452]" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white line-clamp-1">
                Where to Watch {movie.title}
              </h3>
              <p className="text-xs text-[#94a3b8]">
                Official legal viewing options
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-[#1e1e2c] hover:bg-[#28283a] text-white flex items-center justify-center transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Region Switcher */}
        <div className="flex items-center justify-between bg-[#1a1a26] p-2.5 rounded-xl border border-[#282838] mb-5">
          <span className="text-xs text-[#cbd5e1] flex items-center gap-1.5 font-medium">
            <Globe className="w-3.5 h-3.5 text-[#38bdf8]" />
            Streaming Country:
          </span>

          <select
            value={country}
            onChange={(e) => setCountry(e.target.value)}
            className="bg-[#222234] text-xs font-semibold text-white px-2.5 py-1 rounded-lg border border-[#34344a] focus:outline-none focus:border-[#F04452] cursor-pointer"
          >
            {COUNTRIES.map(c => (
              <option key={c.code} value={c.code}>
                {c.flag} {c.name}
              </option>
            ))}
          </select>
        </div>

        {/* Content Body */}
        {loading ? (
          <div className="py-12 flex flex-col items-center justify-center">
            <div className="w-8 h-8 border-2 border-[#F04452] border-t-transparent rounded-full animate-spin mb-3" />
            <p className="text-xs text-[#94a3b8]">Checking streaming platforms...</p>
          </div>
        ) : data ? (
          <div className="space-y-4">
            
            {/* Subscription */}
            {data.subscription && data.subscription.length > 0 && (
              <div>
                <p className="text-[11px] font-bold text-[#10b981] uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#10b981]" />
                  Subscription Streaming
                </p>
                <div className="space-y-2">
                  {data.subscription.map((p, idx) => (
                    <a
                      key={idx}
                      href={p.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-between p-3 rounded-xl bg-[#1c1c28] hover:bg-[#242436] border border-[#2c2c3e] hover:border-[#F04452] transition-all group"
                    >
                      <div className="flex items-center gap-3">
                        {p.logo && (
                          <img
                            src={p.logo}
                            alt={p.name}
                            className="w-8 h-8 rounded-lg object-cover"
                            onError={(e) => { e.currentTarget.style.display = 'none'; }}
                          />
                        )}
                        <div>
                          <p className="text-xs font-bold text-white group-hover:text-[#F04452] transition-colors">
                            {p.name}
                          </p>
                          <span className="text-[10px] text-[#10b981]">Included in plan</span>
                        </div>
                      </div>

                      <span className="flex items-center gap-1 text-xs font-bold text-white bg-[#F04452] px-3 py-1.5 rounded-lg shadow-sm group-hover:scale-103 transition-transform">
                        Watch Now
                        <ExternalLink className="w-3 h-3" />
                      </span>
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Rent & Buy */}
            {(data.rent?.length > 0 || data.buy?.length > 0) && (
              <div>
                <p className="text-[11px] font-bold text-[#38bdf8] uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#38bdf8]" />
                  Rent or Buy
                </p>
                <div className="space-y-2">
                  {[...(data.rent || []), ...(data.buy || [])].slice(0, 3).map((p, idx) => (
                    <a
                      key={idx}
                      href={p.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-between p-2.5 rounded-xl bg-[#181824] hover:bg-[#202030] border border-[#28283a] text-xs transition-colors"
                    >
                      <div className="flex items-center gap-2.5">
                        {p.logo && (
                          <img
                            src={p.logo}
                            alt={p.name}
                            className="w-6 h-6 rounded-md object-cover"
                            onError={(e) => { e.currentTarget.style.display = 'none'; }}
                          />
                        )}
                        <span className="font-medium text-white">{p.name}</span>
                        <span className="text-[10px] text-[#94a3b8]">({p.type} {p.price})</span>
                      </div>
                      <ExternalLink className="w-3.5 h-3.5 text-[#94a3b8]" />
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Fallback Search */}
            {!data.has_availability && (
              <div className="p-4 rounded-xl bg-[#1c1c28] border border-[#2c2c3e] text-center">
                <AlertCircle className="w-6 h-6 text-[#fbbf24] mx-auto mb-2" />
                <p className="text-xs text-[#cbd5e1] font-medium mb-1">
                  Streaming availability not indexed for {selectedCountry.name}.
                </p>
                <p className="text-[11px] text-[#94a3b8] mb-4">
                  Check verified legal platform search directly:
                </p>

                <div className="flex flex-wrap justify-center gap-2">
                  {(data.fallback_search_links || []).map((link, idx) => (
                    <a
                      key={idx}
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-3 py-1.5 rounded-lg bg-[#242436] hover:bg-[#2e2e44] text-xs font-semibold text-white border border-[#38384e] flex items-center gap-1.5"
                    >
                      <span>{link.name}</span>
                      <ExternalLink className="w-3 h-3 text-[#94a3b8]" />
                    </a>
                  ))}
                </div>
              </div>
            )}

          </div>
        ) : null}

        {/* Footer Notice */}
        <p className="text-[10px] text-[#64748b] text-center mt-5">
          Provider links navigate directly to official streaming platforms. Safe & legal.
        </p>

      </div>
    </div>
  );
}
