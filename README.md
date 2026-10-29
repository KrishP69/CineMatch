# CineMatch — AI-Powered Movie Recommendation & Legal OTT Discovery Platform

![CineMatch Banner](https://image.tmdb.org/t/p/original/xJHokMbljvjADYdit5fK5VQsXEG.jpg)

**CineMatch** is a full-stack, production-quality movie discovery web application inspired by modern cinematic entertainment interfaces (Netflix, Prime Video) but with its own signature dark aesthetic, genuine machine learning recommendation engine, and legal Over-The-Top (OTT) streaming availability with direct deep-links.

---

## 🌟 Key Features

### 1. Cinematic Dark Interface
- **Near-Black Palette**: Engineered with `#101014` primary dark background, rich charcoal card surfaces (`#161620`), subtle borders (`#282836`), and cinematic crimson red (`#F04452`) accents.
- **Cinematic Hero Banner**: Showcases spotlight titles with high-resolution backdrops, rating badges, runtime, genres, taglines, and quick action buttons (*Explore Movie*, *Add to Watchlist*, *Where to Watch*).
- **Horizontally Scrollable Shelves**: Smooth desktop/mobile carousel rows with left/right hardware-accelerated navigation for *Trending Now*, *Top Rated Masterpieces*, *Sci-Fi & Mind Benders*, *Indian Cinema Gems*, *Hidden Gems*, *Because You Liked...*, and *Action Spectacles*.
- **Shimmer Skeletons & Responsive Design**: Zero layout shifts during network loading; fully responsive across smartphones, tablets, and 4K displays.

### 2. Genuine Machine Learning Recommendation Engine
- **Content-Based Vector Space Model**: Uses **TF-IDF (Term Frequency-Inverse Document Frequency) Vectorization** and **Cosine Similarity** from Python's `scikit-learn` library.
- **Weighted Feature Soup**: Intelligently combines:
  - *Director* (3x weight): Directorial vision strongly influences tone and pacing.
  - *Starring Cast* (2x weight): Top 3 billed actors.
  - *Keywords & Themes* (2x weight): Plot concepts (e.g. `time dilation`, `space travel`, `heist`).
  - *Genres* (2x weight): Structural categorization.
  - *Overview / Synopsis* (1x weight): Natural language context.
- **Personalized User Vector Profiling**: Generates real-time custom recommendations by synthesizing a mathematical user vector from the mean of TF-IDF vectors of liked movies combined with vectorized favorite genres:
  $$\vec{v}_{\text{user}} = 0.7 \times \left(\frac{1}{|L|}\sum_{m \in L}\vec{v}_m\right) + 0.3 \times \vec{v}_{\text{genres}}$$
- **Negative Filtering**: Dynamically excludes already watched or saved titles from the recommendation pool.
- **Similarity Confidence Score**: Every recommendation returns an exact similarity score (e.g. `89.4% Match`) and transparent human-readable explanation reason (e.g. `"Based on common themes and cast in Interstellar"`).

### 3. Legal OTT Streaming Direct Links (Essential Feature)
- **Authorized Availability**: Identifies official legal streaming platforms across **Subscription (Flatrate)**, **Rental**, and **Purchase**.
- **Supported Platforms**: Netflix, Amazon Prime Video, Disney+ / JioHotstar, Apple TV, SonyLIV, ZEE5, Google Play Movies, and YouTube.
- **Country Detection & Switching**:
  - **Defaults to India (`IN`)** as primary market.
  - Supports switching to **United States (`US`)**, **United Kingdom (`GB`)**, **Canada (`CA`)**, and **Australia (`AU`)**.
- **Direct Viewing & Safe Platform Search**:
  - Direct verified links to official platform pages.
  - Safe link attributes: `target="_blank" rel="noopener noreferrer"`.
  - Legitimate fallback search and JustWatch direct exploration for titles not currently indexed in specific regions.
  - **Zero piracy / zero illegal streaming links**.

### 4. Search & Multi-Factor Discovery
- **Instant Search**: Real-time debounced queries matching title, actor, director, and plot keywords.
- **Granular Filters**: Filter by genre, minimum audience rating (★ 7.0+, 8.0+, 8.5+), and sort by popularity, rating, release year, or title.
- **Persistent Watchlist & Taste Profile**: Saved in `localStorage` across browser reloads without requiring mandatory login walls.

---

## 📐 Machine Learning Theory & Viva Defense Guide

> **Prepared for BTech Computer Science / Information Technology Project Viva Voce**

### Q1: What recommendation technique is implemented in CineMatch?
**Answer**: CineMatch implements a **Content-Based Filtering Recommendation System** operating in a high-dimensional vector space. Unlike Collaborative Filtering (which suffers from the *Cold Start Problem* for new items and requires millions of user rating matrices), Content-Based Filtering models the intrinsic semantic and artistic properties of movies (director, cast, keywords, genres, synopsis) to recommend items that are mathematically closest to the user's explicit taste.

### Q2: What is TF-IDF and why is it preferred over simple Word Count (CountVectorizer)?
**Answer**: 
- **Term Frequency ($TF$)**: Measures the frequency of a term $t$ in a document $d$:
  $$TF(t, d) = \frac{f_{t,d}}{\sum_{t' \in d} f_{t',d}}$$
- **Inverse Document Frequency ($IDF$)**: Measures how rare or informative a term is across the entire corpus $D$:
  $$IDF(t, D) = \log\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$
- **TF-IDF Weight**:
  $$TF\text{-}IDF(t, d, D) = TF(t, d) \times IDF(t, D)$$

*CountVectorizer* merely tallies occurrences, biasing the model towards words that appear frequently everywhere (like "the", "man", "movie"). *TF-IDF* penalizes common non-discriminative terms while heavily weighting distinctive terms (such as "wormhole", "tesseract", "mafia", "inception") that define a movie's unique identity.

### Q3: Why is Cosine Similarity used instead of Euclidean Distance?
**Answer**: 
Cosine similarity measures the **cosine of the angle between two multi-dimensional vectors**, independent of their magnitude:
$$\text{Cosine Similarity}(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|} = \frac{\sum_{i=1}^n u_i v_i}{\sqrt{\sum_{i=1}^n u_i^2} \sqrt{\sum_{i=1}^n v_i^2}}$$

In text processing, documents vary in length (a 500-word synopsis vs a 50-word synopsis). Euclidean distance would register two films with identical themes as "distant" simply because one synopsis is longer. Cosine Similarity normalizes vector length and compares only orientation, making it invariant to document length.

### Q4: How is the multi-attribute feature soup engineered?
**Answer**:
1. Multi-word entities (like `"Christopher Nolan"` or `"Leonardo DiCaprio"`) are normalized to `"christopher_nolan"` and `"leonardo_dicaprio"`. This prevents the vectorizer from splitting the director's first and last name and erroneously matching another person named "Christopher".
2. Weighted repetition:
   $$\text{Soup} = \text{Overview} + 2 \times \text{Genres} + 2 \times \text{Keywords} + 2 \times \text{Cast}_{1..3} + 3 \times \text{Director}$$
   This guarantees that a film directed by the same auteur or with similar thematic keywords ranks higher than one merely sharing generic descriptive adjectives in the synopsis.

---

## 🛠 Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, Vite, Tailwind CSS v4, Lucide React, LocalStorage API |
| **Backend** | Python 3.12, Flask, Flask-CORS, Pandas, NumPy, Scikit-Learn |
| **ML Engine** | `TfidfVectorizer(ngram_range=(1, 2))`, `cosine_similarity` |
| **APIs & Data** | TMDB API (Optional live sync), Curated Offline Database (84+ titles), JustWatch OTT routing |

---

## 📁 Project Architecture

```
CineMatch/
├── backend/
│   ├── app.py                 # Flask REST API & Single Page Application server
│   ├── recommender.py         # Scikit-learn TF-IDF & Cosine Similarity ML engine
│   ├── movie_service.py       # Catalog manager, multi-factor search, genre aggregation
│   ├── ott_service.py         # Legal OTT provider resolver (IN, US, GB, CA, AU)
│   ├── requirements.txt       # Python dependencies
│   ├── data/
│   │   ├── movies.json        # Curated seed database with complete metadata & OTT links
│   │   ├── build_dataset.py   # Dataset builder script
│   │   └── append_dataset.py  # Dataset expansion utility
│   └── .env                   # Local backend environment variables
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx            # Top navigation with country selector & search
│   │   │   ├── HeroSection.jsx       # Cinematic backdrop spotlight banner
│   │   │   ├── MovieCard.jsx         # 2:3 portrait cards with quick action overlays
│   │   │   ├── MovieCarousel.jsx     # Smooth horizontally scrolling shelf rows
│   │   │   ├── MovieDetailModal.jsx  # Full details, ratings, cast, OTT, ML similar
│   │   │   ├── WhereToWatchModal.jsx # Quick dedicated OTT provider popup
│   │   │   ├── OnboardingModal.jsx   # First-visit AI taste configuration
│   │   │   └── Footer.jsx            # Branding, legal terms, & viva notes
│   │   ├── pages/
│   │   │   ├── DiscoverPage.jsx      # Homepage with spotlight & curated carousels
│   │   │   ├── ForYouPage.jsx        # Personalized ML recommendation dashboard
│   │   │   ├── GenresPage.jsx        # Genre directory & filtered exploration
│   │   │   ├── WatchlistPage.jsx     # Persistent library (want to watch / seen)
│   │   │   └── SearchPage.jsx        # Real-time multi-factor catalog search
│   │   ├── services/
│   │   │   └── api.js                # Unified REST API client
│   │   ├── hooks/
│   │   │   └── useWatchlist.js       # LocalStorage state management
│   │   ├── App.jsx                   # Root application state & modal coordinator
│   │   ├── main.jsx                  # React DOM entrypoint
│   │   └── index.css                 # Custom scrollbars, animations, theme tokens
│   ├── vite.config.js                # Vite config with Tailwind plugin & API proxy
│   ├── package.json                  # Frontend dependencies
│   └── dist/                         # Production optimized build bundle
├── .env.example                      # Sample configuration
└── README.md                         # Comprehensive documentation
```

---

## 🚀 Setup & Local Execution

### Prerequisites
- **Python**: 3.10+ installed
- **Node.js**: v18+ and `npm` installed

### Step 1: Clone or Navigate to Directory
```bash
cd c:\Users\Admin\Desktop\CineMatch
```

### Step 2: Install Backend Dependencies
```bash
cd backend
python -m pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp ../.env.example .env
```
*(Optional)* Add your free TMDB API key if you wish to enable live dynamic syncing:
```env
PORT=5000
FLASK_DEBUG=False
TMDB_API_KEY=your_tmdb_api_key_here
```
> **Note**: Even with `TMDB_API_KEY=` left blank, CineMatch runs 100% functional out of the box using its rich bundled offline dataset!

### Step 4: Run the Application

#### Option A: Unified Server (Recommended)
The Flask backend is configured to automatically serve the optimized production React build directly:
```bash
cd backend
python app.py
```
Open **[http://localhost:5000](http://localhost:5000)** in your browser!

#### Option B: Development Mode with Hot Reload
In terminal 1 (Backend):
```bash
cd backend
python app.py
```
In terminal 2 (Frontend Dev Server):
```bash
cd frontend
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** in your browser (all `/api` requests are automatically proxied to Flask on port 5000).

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Returns server status, movie count, and recommender health. |
| `GET` | `/api/featured` | Returns hero spotlight movie and curated homepage shelves. |
| `GET` | `/api/movies` | Paginated movie catalog with `genre`, `year`, `min_rating`, and `sort_by` query params. |
| `GET` | `/api/movies/:id` | Full metadata for a specific movie, including immediate OTT links and similar titles. |
| `GET` | `/api/search?q=:query` | Multi-factor search across title, cast, director, and keywords. |
| `GET` | `/api/genres` | List of all genres with catalog count. |
| `GET` | `/api/recommend/:id?count=10` | Computes top similar movies using Content-Based TF-IDF Cosine Similarity. |
| `POST` | `/api/recommend/personalized` | Body: `{ liked_movie_ids, watched_movie_ids, favorite_genres, count }`. Returns tailored recommendations. |
| `GET` | `/api/watch-providers/:id?country=IN` | Returns verified legal streaming, rental, and purchase platforms for the selected country. |

---

## 🌐 Production Deployment Guide

### Deploying to Render / Railway / Heroku
1. Push the project repository to GitHub.
2. In your deployment dashboard (e.g., Render), create a new **Web Service**.
3. Set **Build Command**:
   ```bash
   cd frontend && npm install && npm run build && cd ../backend && pip install -r requirements.txt
   ```
4. Set **Start Command**:
   ```bash
   cd backend && gunicorn app:app --bind 0.0.0.0:$PORT
   ```
5. Add any desired environment variables (`TMDB_API_KEY`, etc.).

---

## ⚖️ Legal & Compliance
- **Data Attribution**: Movie posters, backdrops, and metadata are property of their respective copyright holders and indexed via TMDB.
- **Authorized OTT Deep-Linking**: Streaming availability data links directly to official subscriber portals (Netflix, Prime Video, JioHotstar, Apple TV, ZEE5, SonyLIV) or legitimate index pages on JustWatch.
- **No Piracy**: CineMatch strictly opposes copyright infringement and never links to unauthorized third-party streaming sites.
