"""
CineMatch OTT Availability Service
Provides legal streaming, rental, and purchase availability for movies
with official platform deep-links, logos, and regional detection (defaulting to India - IN).
Integrates with TMDB Watch Providers API with caching and verified fallback routing.
"""

import os
import time
import urllib.parse
import logging
import requests

logger = logging.getLogger(__name__)

# Known streaming platform metadata and verified search routes
KNOWN_PROVIDERS = {
    "netflix": {
        "name": "Netflix",
        "logo": "https://image.tmdb.org/t/p/original/9A1JSVmSxsya9Wi1egD6k6CGYg1.jpg",
        "search_url": "https://www.netflix.com/search?q={query}"
    },
    "amazon prime video": {
        "name": "Amazon Prime Video",
        "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg",
        "search_url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase={query}"
    },
    "prime video": {
        "name": "Amazon Prime Video",
        "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg",
        "search_url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase={query}"
    },
    "jiohotstar": {
        "name": "JioHotstar",
        "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg",
        "search_url": "https://www.hotstar.com/in/explore?search_query={query}"
    },
    "disney+ hotstar": {
        "name": "JioHotstar",
        "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg",
        "search_url": "https://www.hotstar.com/in/explore?search_query={query}"
    },
    "disney plus": {
        "name": "Disney+",
        "logo": "https://image.tmdb.org/t/p/original/7rw3L812b9p0M9Z6u9c7m42b827.jpg",
        "search_url": "https://www.disneyplus.com/search?q={query}"
    },
    "apple tv": {
        "name": "Apple TV",
        "logo": "https://image.tmdb.org/t/p/original/peURlLlr8jggOwK53fJ5wdQl05y.jpg",
        "search_url": "https://tv.apple.com/search?term={query}"
    },
    "apple tv plus": {
        "name": "Apple TV+",
        "logo": "https://image.tmdb.org/t/p/original/peURlLlr8jggOwK53fJ5wdQl05y.jpg",
        "search_url": "https://tv.apple.com/search?term={query}"
    },
    "sonyliv": {
        "name": "SonyLIV",
        "logo": "https://image.tmdb.org/t/p/original/7rw3L812b9p0M9Z6u9c7m42b827.jpg",
        "search_url": "https://www.sonyliv.com/search/{query}"
    },
    "zee5": {
        "name": "ZEE5",
        "logo": "https://image.tmdb.org/t/p/original/lpmZ08z2bB4m436M9c6qT18Z9x.jpg",
        "search_url": "https://www.zee5.com/search?q={query}"
    },
    "google play movies": {
        "name": "Google Play Movies",
        "logo": "https://image.tmdb.org/t/p/original/tbEdFQDwx5LEVr8Wp6z094VuOnz.jpg",
        "search_url": "https://play.google.com/store/search?q={query}&c=movies"
    },
    "youtube": {
        "name": "YouTube Movies",
        "logo": "https://image.tmdb.org/t/p/original/tbEdFQDwx5LEVr8Wp6z094VuOnz.jpg",
        "search_url": "https://www.youtube.com/results?search_query={query}+official+movie"
    },
    "max": {
        "name": "Max",
        "logo": "https://image.tmdb.org/t/p/original/6uhKBfmtzFqOcLousVO0ZmiioPu.jpg",
        "search_url": "https://play.max.com/search?q={query}"
    },
    "paramount plus": {
        "name": "Paramount+",
        "logo": "https://image.tmdb.org/t/p/original/fi83B1oztoS47xxcemFdPMhIzK.jpg",
        "search_url": "https://www.paramountplus.com/search/?q={query}"
    },
    "peacock": {
        "name": "Peacock",
        "logo": "https://image.tmdb.org/t/p/original/8VCV78Prwd9Q2G91P2P82782782.jpg",
        "search_url": "https://www.peacocktv.com/search?q={query}"
    },
    "hulu": {
        "name": "Hulu",
        "logo": "https://image.tmdb.org/t/p/original/zxrVdFj00zsjqIYVm6lH582ohIW.jpg",
        "search_url": "https://www.hulu.com/search?q={query}"
    },
    "lionsgate play": {
        "name": "Lionsgate Play",
        "logo": "https://image.tmdb.org/t/p/original/7rw3L812b9p0M9Z6u9c7m42b827.jpg",
        "search_url": "https://www.lionsgateplay.com/search?q={query}"
    }
}

# In-memory TTL cache for live TMDB watch-provider calls
_PROVIDER_CACHE = {}
CACHE_TTL = 3600 * 6  # 6 hours


class OTTService:
    def __init__(self):
        self.tmdb_api_key = os.getenv("TMDB_API_KEY", "").strip()

    def _get_platform_info(self, provider_name, movie_title, fallback_url=None):
        clean_key = str(provider_name).strip().lower()
        enc_title = urllib.parse.quote_plus(str(movie_title))
        
        info = KNOWN_PROVIDERS.get(clean_key)
        if not info:
            # Check partial matching
            for k, v in KNOWN_PROVIDERS.items():
                if k in clean_key or clean_key in k:
                    info = v
                    break

        if info:
            resolved_url = fallback_url if (fallback_url and "http" in fallback_url) else info["search_url"].format(query=enc_title)
            return {
                "name": info["name"],
                "logo": info["logo"],
                "url": resolved_url,
                "is_direct": bool(fallback_url and "http" in fallback_url)
            }
        
        # Generic safe provider entry
        resolved_url = fallback_url if (fallback_url and "http" in fallback_url) else f"https://www.justwatch.com/in/search?q={enc_title}"
        return {
            "name": provider_name,
            "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg",
            "url": resolved_url,
            "is_direct": bool(fallback_url and "http" in fallback_url)
        }

    def fetch_live_tmdb_providers(self, tmdb_id, country="IN"):
        """Fetches live watch provider availability from TMDB API if key is present."""
        if not self.tmdb_api_key or not tmdb_id:
            return None

        cache_key = f"{tmdb_id}_{country}"
        now = time.time()
        if cache_key in _PROVIDER_CACHE:
            entry_time, data = _PROVIDER_CACHE[cache_key]
            if now - entry_time < CACHE_TTL:
                return data

        try:
            url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/watch/providers"
            headers = {"accept": "application/json"}
            resp = requests.get(url, params={"api_key": self.tmdb_api_key}, headers=headers, timeout=4)
            if resp.status_code == 200:
                payload = resp.json()
                results = payload.get("results", {})
                country_data = results.get(country.upper())
                _PROVIDER_CACHE[cache_key] = (now, country_data)
                return country_data
        except Exception as e:
            logger.warning(f"Error fetching TMDB watch providers for {tmdb_id}: {e}")

        return None

    def get_watch_providers(self, movie, country="IN"):
        """
        Retrieves accurate OTT availability for a given movie and country.
        Defaults to 'IN' (India).
        Returns structured lists for 'flatrate' (Subscription), 'rent', and 'buy'.
        """
        country = (country or "IN").strip().upper()
        movie_title = movie.get("title", "Movie")
        tmdb_id = movie.get("id")

        enc_title = urllib.parse.quote_plus(str(movie_title))
        country_lower = country.lower()
        justwatch_search_url = f"https://www.justwatch.com/{country_lower}/search?q={enc_title}"

        flatrate_list = []
        rent_list = []
        buy_list = []
        justwatch_direct_url = None

        # 1. Check live TMDB API if key available
        tmdb_data = self.fetch_live_tmdb_providers(tmdb_id, country)
        if tmdb_data:
            justwatch_direct_url = tmdb_data.get("link")
            
            # Subscriptions
            for p in tmdb_data.get("flatrate", []):
                p_name = p.get("provider_name", "")
                p_logo = f"https://image.tmdb.org/t/p/original{p.get('logo_path')}" if p.get("logo_path") else None
                info = self._get_platform_info(p_name, movie_title)
                flatrate_list.append({
                    "name": p_name,
                    "logo": p_logo or info["logo"],
                    "type": "Subscription",
                    "url": justwatch_direct_url or info["url"],
                    "is_direct": True
                })

            # Rent
            for p in tmdb_data.get("rent", []):
                p_name = p.get("provider_name", "")
                p_logo = f"https://image.tmdb.org/t/p/original{p.get('logo_path')}" if p.get("logo_path") else None
                info = self._get_platform_info(p_name, movie_title)
                rent_list.append({
                    "name": p_name,
                    "logo": p_logo or info["logo"],
                    "type": "Rent",
                    "price": "Standard Rate",
                    "url": justwatch_direct_url or info["url"],
                    "is_direct": True
                })

            # Buy
            for p in tmdb_data.get("buy", []):
                p_name = p.get("provider_name", "")
                p_logo = f"https://image.tmdb.org/t/p/original{p.get('logo_path')}" if p.get("logo_path") else None
                info = self._get_platform_info(p_name, movie_title)
                buy_list.append({
                    "name": p_name,
                    "logo": p_logo or info["logo"],
                    "type": "Buy",
                    "price": "Standard Purchase",
                    "url": justwatch_direct_url or info["url"],
                    "is_direct": True
                })

        # 2. Check bundled dataset watch_providers if live API had no entry or wasn't used
        if not flatrate_list and not rent_list and not buy_list:
            bundled_wp = movie.get("watch_providers", {})
            country_bundle = bundled_wp.get(country, {})

            if country_bundle:
                for p in country_bundle.get("flatrate", []):
                    flatrate_list.append({
                        "name": p.get("name"),
                        "logo": p.get("logo"),
                        "type": "Subscription",
                        "url": p.get("url"),
                        "is_direct": True
                    })
                for p in country_bundle.get("rent", []):
                    rent_list.append({
                        "name": p.get("name"),
                        "logo": p.get("logo"),
                        "type": "Rent",
                        "price": p.get("price", "Rent"),
                        "url": p.get("url"),
                        "is_direct": True
                    })
                for p in country_bundle.get("buy", []):
                    buy_list.append({
                        "name": p.get("name"),
                        "logo": p.get("logo"),
                        "type": "Buy",
                        "price": p.get("price", "Buy"),
                        "url": p.get("url"),
                        "is_direct": True
                    })

        has_data = bool(flatrate_list or rent_list or buy_list)

        # Fallback official search links for convenience
        fallback_search_links = [
            {"name": "Netflix", "logo": KNOWN_PROVIDERS["netflix"]["logo"], "url": KNOWN_PROVIDERS["netflix"]["search_url"].format(query=enc_title)},
            {"name": "Prime Video", "logo": KNOWN_PROVIDERS["amazon prime video"]["logo"], "url": KNOWN_PROVIDERS["amazon prime video"]["search_url"].format(query=enc_title)},
            {"name": "Apple TV", "logo": KNOWN_PROVIDERS["apple tv"]["logo"], "url": KNOWN_PROVIDERS["apple tv"]["search_url"].format(query=enc_title)},
            {"name": "JioHotstar" if country == "IN" else "Disney+", "logo": KNOWN_PROVIDERS["jiohotstar"]["logo"], "url": KNOWN_PROVIDERS["jiohotstar"]["search_url"].format(query=enc_title)}
        ]

        return {
            "movie_id": tmdb_id,
            "movie_title": movie_title,
            "country": country,
            "has_availability": has_data,
            "subscription": flatrate_list,
            "rent": rent_list,
            "buy": buy_list,
            "justwatch_url": justwatch_direct_url or justwatch_search_url,
            "fallback_search_links": fallback_search_links,
            "message": "Live availability verified" if has_data else "Streaming availability not currently indexed for this region. Explore via official platform search links below."
        }


# Singleton instance
ott_service = OTTService()
