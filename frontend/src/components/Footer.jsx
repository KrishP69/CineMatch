import React from 'react';
import { Film, Sparkles, Tv, ShieldCheck, Code2 } from 'lucide-react';

export default function Footer({ onOpenOnboarding }) {
  return (
    <footer className="mt-20 border-t border-[#20202e] bg-[#0c0c10] text-[#94a3b8] py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
          
          {/* Brand Info */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-2.5 mb-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[#F04452] to-[#ff6b77] flex items-center justify-center">
                <Film className="w-4 h-4 text-white" />
              </div>
              <span className="text-xl font-bold tracking-tight text-white">
                Cine<span className="text-[#F04452]">Match</span>
              </span>
            </div>
            <p className="text-xs sm:text-sm text-[#94a3b8] max-w-md leading-relaxed mb-4">
              AI-powered movie recommendation platform built with genuine Machine Learning.
              Combines TF-IDF vectorization and cosine similarity on weighted metadata with direct legal OTT streaming links.
            </p>
            <div className="flex items-center gap-2 text-xs text-[#cbd5e1]">
              <span className="inline-flex items-center gap-1 bg-[#161622] px-2.5 py-1 rounded-md border border-[#262634]">
                <Sparkles className="w-3 h-3 text-[#fbbf24]" />
                TF-IDF + Cosine Sim
              </span>
              <span className="inline-flex items-center gap-1 bg-[#161622] px-2.5 py-1 rounded-md border border-[#262634]">
                <Tv className="w-3 h-3 text-[#10b981]" />
                Legal OTT Providers
              </span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">
              Features
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <button
                  onClick={onOpenOnboarding}
                  className="hover:text-white transition-colors cursor-pointer text-left"
                >
                  Tune AI Taste Profile
                </button>
              </li>
              <li>
                <span className="text-[#64748b]">Content-Based Filtering</span>
              </li>
              <li>
                <span className="text-[#64748b]">Multi-Factor Catalog Search</span>
              </li>
              <li>
                <span className="text-[#64748b]">Regional OTT Availability (IN / US / GB)</span>
              </li>
            </ul>
          </div>

          {/* Tech & Viva Notes */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">
              Architecture
            </h4>
            <ul className="space-y-1.5 text-xs text-[#94a3b8]">
              <li className="flex items-center gap-1.5">
                <Code2 className="w-3.5 h-3.5 text-[#F04452]" />
                <span>Backend: Python / Flask / Scikit-Learn</span>
              </li>
              <li className="flex items-center gap-1.5">
                <Code2 className="w-3.5 h-3.5 text-[#38bdf8]" />
                <span>Frontend: React 19 / Vite / Tailwind</span>
              </li>
              <li className="flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-[#10b981]" />
                <span>Data: TMDB / JustWatch Compliance</span>
              </li>
            </ul>
          </div>

        </div>

        {/* Legal Disclaimer & Bottom Credits */}
        <div className="pt-6 border-t border-[#181824] flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-[#64748b]">
          <p>
            © {new Date().getFullYear()} CineMatch. All movie metadata and streaming availability are indexed from legitimate sources. Never facilitates piracy.
          </p>
          <p className="flex items-center gap-1">
            Engineered with <span className="text-[#F04452]">♥</span> for Entertainment & AI
          </p>
        </div>

      </div>
    </footer>
  );
}
