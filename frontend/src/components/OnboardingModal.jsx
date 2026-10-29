import React, { useState } from 'react';
import { X, Sparkles, Check, Film, ArrowRight } from 'lucide-react';

const POPULAR_GENRES = [
  'Science Fiction', 'Action', 'Drama', 'Adventure', 'Comedy',
  'Crime', 'Thriller', 'Animation', 'Romance', 'Mystery', 'Horror', 'Family'
];

const SEED_MOVIES = [
  { id: 157336, title: 'Interstellar', year: 2014, poster: 'https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg' },
  { id: 27205, title: 'Inception', year: 2010, poster: 'https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg' },
  { id: 155, title: 'The Dark Knight', year: 2008, poster: 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg' },
  { id: 496243, title: 'Parasite', year: 2019, poster: 'https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg' },
  { id: 872585, title: 'Oppenheimer', year: 2023, poster: 'https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg' },
  { id: 579974, title: 'RRR', year: 2022, poster: 'https://image.tmdb.org/t/p/w500/wE0noFUq1q16nmnV8I5U0Jd4b9x.jpg' },
  { id: 324857, title: 'Spider-Verse', year: 2018, poster: 'https://image.tmdb.org/t/p/w500/iiZZdoQBEYBv6id8su7ImL0oCbD.jpg' },
  { id: 438631, title: 'Dune', year: 2021, poster: 'https://image.tmdb.org/t/p/w500/d5NXSklXo0qyIYkgV94XAgMIckC.jpg' },
  { id: 313369, title: 'La La Land', year: 2016, poster: 'https://image.tmdb.org/t/p/w500/uDO8zWDhfWwoFdKS4fzkVJt0Rf0.jpg' },
];

export default function OnboardingModal({
  isOpen,
  onClose,
  initialGenres = [],
  initialLiked = [],
  onComplete,
}) {
  const [selectedGenres, setSelectedGenres] = useState(initialGenres.length > 0 ? initialGenres : ['Science Fiction', 'Action', 'Drama']);
  const [selectedMovies, setSelectedMovies] = useState(initialLiked.length > 0 ? initialLiked : [157336, 27205]);
  const [step, setStep] = useState(1);

  if (!isOpen) return null;

  const toggleGenre = (genre) => {
    setSelectedGenres(prev =>
      prev.includes(genre) ? prev.filter(g => g !== genre) : [...prev, genre]
    );
  };

  const toggleMovie = (id) => {
    setSelectedMovies(prev =>
      prev.includes(id) ? prev.filter(m => m !== id) : [...prev, id]
    );
  };

  const handleFinish = () => {
    onComplete(selectedGenres, selectedMovies);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/85 backdrop-blur-md flex items-center justify-center p-4 animate-in fade-in duration-200">
      
      {/* Background click */}
      <div className="fixed inset-0" onClick={onClose} />

      <div className="relative z-10 w-full max-w-xl bg-[#14141e] border border-[#2e2e42] rounded-3xl shadow-2xl p-6 sm:p-8 overflow-hidden">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 w-8 h-8 rounded-full bg-[#1e1e2c] hover:bg-[#28283a] text-white flex items-center justify-center transition-colors cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Header */}
        <div className="text-center mb-6">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-[#F04452] to-[#ff6b77] mx-auto flex items-center justify-center mb-3 shadow-lg shadow-[#F04452]/25">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            {step === 1 ? 'Tune Your AI Taste Profile' : 'Select Movies You Enjoyed'}
          </h2>
          <p className="text-xs sm:text-sm text-[#94a3b8] mt-1 max-w-sm mx-auto">
            {step === 1
              ? 'Select your favorite genres so CineMatch can calculate personalized recommendations.'
              : 'Pick 2 or 3 favorites to seed your content-based feature vector.'}
          </p>
        </div>

        {/* Step Indicator */}
        <div className="flex items-center justify-center gap-2 mb-6">
          <div className={`h-1.5 rounded-full transition-all ${step === 1 ? 'w-8 bg-[#F04452]' : 'w-4 bg-[#2e2e42]'}`} />
          <div className={`h-1.5 rounded-full transition-all ${step === 2 ? 'w-8 bg-[#F04452]' : 'w-4 bg-[#2e2e42]'}`} />
        </div>

        {/* Step 1: Genres */}
        {step === 1 && (
          <div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 mb-6">
              {POPULAR_GENRES.map((genre) => {
                const isSelected = selectedGenres.includes(genre);
                return (
                  <button
                    key={genre}
                    onClick={() => toggleGenre(genre)}
                    className={`p-3 rounded-xl border text-xs font-semibold flex items-center justify-between transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-[#F04452]/15 border-[#F04452] text-white shadow-sm'
                        : 'bg-[#181824] hover:bg-[#202030] border-[#28283a] text-[#cbd5e1]'
                    }`}
                  >
                    <span>{genre}</span>
                    {isSelected && <Check className="w-3.5 h-3.5 text-[#F04452]" />}
                  </button>
                );
              })}
            </div>

            <button
              onClick={() => setStep(2)}
              disabled={selectedGenres.length === 0}
              className="w-full py-3.5 px-4 rounded-xl bg-[#F04452] hover:bg-[#d63340] disabled:opacity-50 text-white font-bold text-sm flex items-center justify-center gap-2 transition-all cursor-pointer shadow-lg shadow-[#F04452]/20"
            >
              <span>Continue to Favorite Movies</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Step 2: Seed Movies */}
        {step === 2 && (
          <div>
            <div className="grid grid-cols-3 gap-3 mb-6 max-h-[320px] overflow-y-auto no-scrollbar pr-1">
              {SEED_MOVIES.map((movie) => {
                const isSelected = selectedMovies.includes(movie.id);
                return (
                  <div
                    key={movie.id}
                    onClick={() => toggleMovie(movie.id)}
                    className={`relative rounded-xl overflow-hidden aspect-[2/3] border cursor-pointer group transition-all ${
                      isSelected
                        ? 'border-[#F04452] ring-2 ring-[#F04452]/50 scale-98'
                        : 'border-[#28283a] hover:border-white/30'
                    }`}
                  >
                    <img
                      src={movie.poster}
                      alt={movie.title}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent flex flex-col justify-end p-2">
                      <p className="text-[11px] font-bold text-white line-clamp-1">{movie.title}</p>
                      <p className="text-[9px] text-[#94a3b8]">{movie.year}</p>
                    </div>

                    {isSelected && (
                      <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-[#F04452] text-white flex items-center justify-center shadow">
                        <Check className="w-3 h-3 stroke-[3]" />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setStep(1)}
                className="py-3 px-4 rounded-xl bg-[#1e1e2c] hover:bg-[#28283c] border border-[#303044] text-xs font-semibold text-white transition-colors cursor-pointer"
              >
                Back
              </button>

              <button
                onClick={handleFinish}
                className="flex-grow py-3.5 px-4 rounded-xl bg-[#F04452] hover:bg-[#d63340] text-white font-bold text-sm flex items-center justify-center gap-2 transition-all cursor-pointer shadow-lg shadow-[#F04452]/20"
              >
                <Sparkles className="w-4 h-4" />
                <span>Save Taste & Generate Feed</span>
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
