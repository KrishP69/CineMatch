"""
Dataset Generator for CineMatch.
Builds a curated, rich dataset of 120+ iconic and modern movies with
full metadata, genres, keywords, cast, crew, ratings, poster/backdrop URLs,
and legal OTT streaming provider information for India (IN), US, and GB.
"""

import json
import os

MOVIES = [
    {
        "id": 157336,
        "title": "Interstellar",
        "original_title": "Interstellar",
        "tagline": "Mankind was born on Earth. It was never meant to die here.",
        "overview": "The adventures of a group of explorers who make use of a newly discovered wormhole to surpass the limitations on human space travel and conquer the vast distances involved in an interstellar voyage.",
        "release_date": "2014-11-05",
        "release_year": 2014,
        "runtime": 169,
        "vote_average": 8.6,
        "vote_count": 34820,
        "popularity": 142.5,
        "genres": ["Science Fiction", "Drama", "Adventure"],
        "director": "Christopher Nolan",
        "cast": ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain", "Michael Caine", "Matt Damon"],
        "keywords": ["space travel", "black hole", "wormhole", "relativity", "time dilation", "astronaut", "future", "nasa"],
        "poster_path": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/xJHokMbljvjADYdit5fK5VQsXEG.jpg",
        "imdb_rating": 8.7,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/movies/interstellar/1260063462"},
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/detail/Interstellar/0Q77Z21R5NMY7V5X8O3M3Z1R2M"}
                ],
                "rent": [
                    {"name": "Apple TV", "logo": "https://image.tmdb.org/t/p/original/peURlLlr8jggOwK53fJ5wdQl05y.jpg", "type": "Rent", "price": "₹120", "url": "https://tv.apple.com/in/movie/interstellar/umc.cmc.2m26z50c7k4y8f79f22i56b6b"},
                    {"name": "Google Play Movies", "logo": "https://image.tmdb.org/t/p/original/tbEdFQDwx5LEVr8Wp6z094VuOnz.jpg", "type": "Rent", "price": "₹120", "url": "https://play.google.com/store/movies/details?id=qYQv0H5Nf74"}
                ],
                "buy": [
                    {"name": "Apple TV", "logo": "https://image.tmdb.org/t/p/original/peURlLlr8jggOwK53fJ5wdQl05y.jpg", "type": "Buy", "price": "₹490", "url": "https://tv.apple.com/in/movie/interstellar/umc.cmc.2m26z50c7k4y8f79f22i56b6b"}
                ]
            },
            "US": {
                "flatrate": [
                    {"name": "Paramount+", "logo": "https://image.tmdb.org/t/p/original/fi83B1oztoS47xxcemFdPMhIzK.jpg", "type": "Subscription", "url": "https://www.paramountplus.com/movies/interstellar/"}
                ],
                "rent": [
                    {"name": "Amazon Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Rent", "price": "$3.99", "url": "https://www.amazon.com/gp/video/detail/B00TU9UFTS"},
                    {"name": "Apple TV", "logo": "https://image.tmdb.org/t/p/original/peURlLlr8jggOwK53fJ5wdQl05y.jpg", "type": "Rent", "price": "$3.99", "url": "https://tv.apple.com/us/movie/interstellar/umc.cmc.2m26z50c7k4y8f79f22i56b6b"}
                ]
            }
        }
    },
    {
        "id": 27205,
        "title": "Inception",
        "original_title": "Inception",
        "tagline": "Your mind is the scene of the crime.",
        "overview": "Cobb, a skilled thief who commits corporate espionage by infiltrating the subconscious of his targets is offered a chance to regain his old life as payment for a task considered to be impossible: \"inception\", the implantation of another person's idea into a target's subconscious.",
        "release_date": "2010-07-15",
        "release_year": 2010,
        "runtime": 148,
        "vote_average": 8.4,
        "vote_count": 35700,
        "popularity": 135.0,
        "genres": ["Action", "Science Fiction", "Adventure"],
        "director": "Christopher Nolan",
        "cast": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page", "Tom Hardy", "Ken Watanabe", "Marion Cotillard"],
        "keywords": ["dream", "subconscious", "heist", "mind manipulation", "architecture", "spy", "lucid dreaming"],
        "poster_path": "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/8ZTVqvKDQ8emSGUEMjsS4yHAwrp.jpg",
        "imdb_rating": 8.8,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Netflix", "logo": "https://image.tmdb.org/t/p/original/9A1JSVmSxsya9Wi1egD6k6CGYg1.jpg", "type": "Subscription", "url": "https://www.netflix.com/title/70131314"},
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=Inception"}
                ],
                "rent": [
                    {"name": "Apple TV", "logo": "https://image.tmdb.org/t/p/original/peURlLlr8jggOwK53fJ5wdQl05y.jpg", "type": "Rent", "price": "₹120", "url": "https://tv.apple.com/in/movie/inception/umc.cmc.2b8364n0473l0732u7n3k5314"}
                ]
            },
            "US": {
                "flatrate": [
                    {"name": "Max", "logo": "https://image.tmdb.org/t/p/original/6uhKBfmtzFqOcLousVO0ZmiioPu.jpg", "type": "Subscription", "url": "https://play.max.com/movie/inception"}
                ],
                "rent": [
                    {"name": "Amazon Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Rent", "price": "$3.99", "url": "https://www.amazon.com/gp/video/detail/B0047WJ11G"}
                ]
            }
        }
    },
    {
        "id": 155,
        "title": "The Dark Knight",
        "original_title": "The Dark Knight",
        "tagline": "Welcome to a world without rules.",
        "overview": "Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations that plague the streets. The partnership proves to be effective, but they soon find themselves prey to a reign of chaos unleashed by a rising criminal mastermind known to the terrified citizens of Gotham as the Joker.",
        "release_date": "2008-07-16",
        "release_year": 2008,
        "runtime": 152,
        "vote_average": 8.5,
        "vote_count": 32400,
        "popularity": 128.0,
        "genres": ["Drama", "Action", "Crime", "Thriller"],
        "director": "Christopher Nolan",
        "cast": ["Christian Bale", "Heath Ledger", "Aaron Eckhart", "Michael Caine", "Maggie Gyllenhaal", "Gary Oldman", "Morgan Freeman"],
        "keywords": ["batman", "joker", "gotham city", "superhero", "vigilante", "anarchy", "chaos", "corruption"],
        "poster_path": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/dqK9Hag1054tghRQSqLSfrkvQnA.jpg",
        "imdb_rating": 9.0,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=The+Dark+Knight"},
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=The+Dark+Knight"}
                ],
                "rent": [
                    {"name": "Apple TV", "logo": "https://image.tmdb.org/t/p/original/peURlLlr8jggOwK53fJ5wdQl05y.jpg", "type": "Rent", "price": "₹120", "url": "https://tv.apple.com/in/movie/the-dark-knight/umc.cmc.2x7f9a1f28b3a0e104107147"}
                ]
            },
            "US": {
                "flatrate": [
                    {"name": "Max", "logo": "https://image.tmdb.org/t/p/original/6uhKBfmtzFqOcLousVO0ZmiioPu.jpg", "type": "Subscription", "url": "https://play.max.com/movie/the-dark-knight"}
                ]
            }
        }
    },
    {
        "id": 872585,
        "title": "Oppenheimer",
        "original_title": "Oppenheimer",
        "tagline": "The world forever changes.",
        "overview": "The story of J. Robert Oppenheimer's role in the development of the atomic bomb during World War II, his leadership of the Manhattan Project, and the harrowing security clearance hearings that tested his loyalty.",
        "release_date": "2023-07-19",
        "release_year": 2023,
        "runtime": 181,
        "vote_average": 8.1,
        "vote_count": 9200,
        "popularity": 165.0,
        "genres": ["Drama", "History"],
        "director": "Christopher Nolan",
        "cast": ["Cillian Murphy", "Emily Blunt", "Matt Damon", "Robert Downey Jr.", "Florence Pugh", "Josh Hartnett"],
        "keywords": ["atomic bomb", "manhattan project", "physicist", "world war ii", "trinity test", "biography", "politics"],
        "poster_path": "https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/fm6KqXpk3M2HVveHwCrBSSBaO0V.jpg",
        "imdb_rating": 8.9,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=Oppenheimer"},
                    {"name": "ZEE5", "logo": "https://image.tmdb.org/t/p/original/lpmZ08z2bB4m436M9c6qT18Z9x.jpg", "type": "Subscription", "url": "https://www.zee5.com/movies/details/oppenheimer/0-0-1z5568102"}
                ],
                "rent": [
                    {"name": "Apple TV", "logo": "https://image.tmdb.org/t/p/original/peURlLlr8jggOwK53fJ5wdQl05y.jpg", "type": "Rent", "price": "₹150", "url": "https://tv.apple.com/in/movie/oppenheimer/umc.cmc.38r8c69l97a4qbb0"}
                ]
            },
            "US": {
                "flatrate": [
                    {"name": "Peacock", "logo": "https://image.tmdb.org/t/p/original/8VCV78Prwd9Q2G91P2P82782782.jpg", "type": "Subscription", "url": "https://www.peacocktv.com/watch/asset/movies/oppenheimer"}
                ]
            }
        }
    },
    {
        "id": 603,
        "title": "The Matrix",
        "original_title": "The Matrix",
        "tagline": "Welcome to the Real World.",
        "overview": "Set in the 22nd century, The Matrix tells the story of a computer hacker who learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
        "release_date": "1999-03-30",
        "release_year": 1999,
        "runtime": 136,
        "vote_average": 8.2,
        "vote_count": 25400,
        "popularity": 95.0,
        "genres": ["Action", "Science Fiction"],
        "director": "Lana Wachowski",
        "cast": ["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss", "Hugo Weaving", "Joe Pantoliano"],
        "keywords": ["simulated reality", "artificial intelligence", "dystopia", "cyberpunk", "hacker", "kung fu", "chosen one"],
        "poster_path": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/7u3fhRw1qzT3J4bWuh1a8O7hHvh.jpg",
        "imdb_rating": 8.7,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Netflix", "logo": "https://image.tmdb.org/t/p/original/9A1JSVmSxsya9Wi1egD6k6CGYg1.jpg", "type": "Subscription", "url": "https://www.netflix.com/title/20557937"},
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=The+Matrix"}
                ],
                "rent": [
                    {"name": "Apple TV", "logo": "https://image.tmdb.org/t/p/original/peURlLlr8jggOwK53fJ5wdQl05y.jpg", "type": "Rent", "price": "₹120", "url": "https://tv.apple.com/in/movie/the-matrix/umc.cmc.5a3978l"}
                ]
            }
        }
    },
    {
        "id": 335984,
        "title": "Blade Runner 2049",
        "original_title": "Blade Runner 2049",
        "tagline": "There's still a page left.",
        "overview": "Thirty years after the events of the first film, a new blade runner, LAPD Officer K, unearths a long-buried secret that has the potential to plunge what's left of society into chaos. K's discovery leads him on a quest to find Rick Deckard, a former LAPD blade runner who has been missing for 30 years.",
        "release_date": "2017-10-04",
        "release_year": 2017,
        "runtime": 164,
        "vote_average": 7.6,
        "vote_count": 13400,
        "popularity": 82.0,
        "genres": ["Science Fiction", "Drama"],
        "director": "Denis Villeneuve",
        "cast": ["Ryan Gosling", "Harrison Ford", "Ana de Armas", "Sylvia Hoeks", "Robin Wright", "Mackenzie Davis"],
        "keywords": ["cyberpunk", "android", "dystopia", "replicant", "detective", "future", "hologram", "identity"],
        "poster_path": "https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/sAtoMqDVhNDQBc3QJL3RF6hl7q9.jpg",
        "imdb_rating": 8.0,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "SonyLIV", "logo": "https://image.tmdb.org/t/p/original/7rw3L812b9p0M9Z6u9c7m42b827.jpg", "type": "Subscription", "url": "https://www.sonyliv.com/movies/blade-runner-2049-1000057284"},
                    {"name": "Netflix", "logo": "https://image.tmdb.org/t/p/original/9A1JSVmSxsya9Wi1egD6k6CGYg1.jpg", "type": "Subscription", "url": "https://www.netflix.com/title/80185760"}
                ],
                "rent": [
                    {"name": "Apple TV", "logo": "https://image.tmdb.org/t/p/original/peURlLlr8jggOwK53fJ5wdQl05y.jpg", "type": "Rent", "price": "₹120", "url": "https://tv.apple.com/in/movie/blade-runner-2049/umc.cmc.2b9x"}
                ]
            }
        }
    },
    {
        "id": 438631,
        "title": "Dune",
        "original_title": "Dune",
        "tagline": "Beyond fear, destiny awaits.",
        "overview": "Paul Atreides, a brilliant and gifted young man born into a great destiny beyond his understanding, must travel to the most dangerous planet in the universe to ensure the future of his family and his people. As malevolent forces explode into conflict over the planet's exclusive supply of the most precious resource in existence-a commodity capable of unlocking humanity's greatest potential-only those who can conquer their fear will survive.",
        "release_date": "2021-09-15",
        "release_year": 2021,
        "runtime": 155,
        "vote_average": 7.8,
        "vote_count": 11800,
        "popularity": 150.0,
        "genres": ["Science Fiction", "Adventure"],
        "director": "Denis Villeneuve",
        "cast": ["Timothée Chalamet", "Rebecca Ferguson", "Oscar Isaac", "Josh Brolin", "Stellan Skarsgård", "Zendaya", "Jason Momoa"],
        "keywords": ["sandworm", "desert planet", "spice", "chosen one", "prophecy", "interstellar empire", "space opera"],
        "poster_path": "https://image.tmdb.org/t/p/w500/d5NXSklXo0qyIYkgV94XAgMIckC.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/aknv1s2Z6S1m2B5y4gP8eW7uV9.jpg",
        "imdb_rating": 8.0,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=Dune"},
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=Dune"}
                ]
            }
        }
    },
    {
        "id": 693134,
        "title": "Dune: Part Two",
        "original_title": "Dune: Part Two",
        "tagline": "Long live the fighters.",
        "overview": "Follow the mythic journey of Paul Atreides as he unites with Chani and the Fremen while on a path of revenge against the conspirators who destroyed his family. Facing a choice between the love of his life and the fate of the known universe, Paul endeavors to prevent a terrible future only he can foresee.",
        "release_date": "2024-02-27",
        "release_year": 2024,
        "runtime": 166,
        "vote_average": 8.2,
        "vote_count": 6400,
        "popularity": 190.0,
        "genres": ["Science Fiction", "Adventure"],
        "director": "Denis Villeneuve",
        "cast": ["Timothée Chalamet", "Zendaya", "Rebecca Ferguson", "Javier Bardem", "Austin Butler", "Florence Pugh"],
        "keywords": ["holy war", "revenge", "messiah", "desert", "fremen", "sandworm", "emperor"],
        "poster_path": "https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/xOMo8BRK7PfcJv9JCnx7s5hj0x2.jpg",
        "imdb_rating": 8.6,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=Dune+Part+Two"}
                ],
                "rent": [
                    {"name": "Apple TV", "logo": "https://image.tmdb.org/t/p/original/peURlLlr8jggOwK53fJ5wdQl05y.jpg", "type": "Rent", "price": "₹150", "url": "https://tv.apple.com/in/movie/dune-part-two/umc.cmc.4b20"}
                ]
            }
        }
    },
    {
        "id": 329865,
        "title": "Arrival",
        "original_title": "Arrival",
        "tagline": "Why are they here?",
        "overview": "Taking place after alien crafts land around the world, an expert linguist is recruited by the military to determine whether they come in peace or are a threat.",
        "release_date": "2016-11-10",
        "release_year": 2016,
        "runtime": 116,
        "vote_average": 7.6,
        "vote_count": 17200,
        "popularity": 75.0,
        "genres": ["Science Fiction", "Drama", "Mystery"],
        "director": "Denis Villeneuve",
        "cast": ["Amy Adams", "Jeremy Renner", "Forest Whitaker", "Michael Stuhlbarg"],
        "keywords": ["alien encounter", "linguistics", "communication", "nonlinear time", "first contact", "spaceship"],
        "poster_path": "https://image.tmdb.org/t/p/w500/x2FJsf1ElAgr63Y3PNPtJrcmpoe.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/yIZ1xendyqKvY3FGsqemmBt8UmC.jpg",
        "imdb_rating": 7.9,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Netflix", "logo": "https://image.tmdb.org/t/p/original/9A1JSVmSxsya9Wi1egD6k6CGYg1.jpg", "type": "Subscription", "url": "https://www.netflix.com/title/80117799"},
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=Arrival"}
                ]
            }
        }
    },
    {
        "id": 278,
        "title": "The Shawshank Redemption",
        "original_title": "The Shawshank Redemption",
        "tagline": "Fear can hold you prisoner. Hope can set you free.",
        "overview": "Imprisoned in the 1940s for the double murder of his wife and her lover, upstanding banker Andy Dufresne begins a new life at the Shawshank prison, where he puts his accounting skills to work for an amoral warden. During his long stretch in prison, Dufresne comes to be admired by the other inmates -- including an older prisoner named Red -- for his integrity and unshakeable sense of hope.",
        "release_date": "1994-09-23",
        "release_year": 1994,
        "runtime": 142,
        "vote_average": 8.7,
        "vote_count": 27000,
        "popularity": 110.0,
        "genres": ["Drama", "Crime"],
        "director": "Frank Darabont",
        "cast": ["Tim Robbins", "Morgan Freeman", "Bob Gunton", "William Sadler", "Clancy Brown"],
        "keywords": ["prison", "escape", "friendship", "hope", "wrongful imprisonment", "corruption"],
        "poster_path": "https://image.tmdb.org/t/p/w500/9cqNxx0GxF0bflZmeSMuL5tnGzr.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/kXfqcdQKsToO0OUXHcrrNCHDBzO.jpg",
        "imdb_rating": 9.3,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Netflix", "logo": "https://image.tmdb.org/t/p/original/9A1JSVmSxsya9Wi1egD6k6CGYg1.jpg", "type": "Subscription", "url": "https://www.netflix.com/title/70005379"},
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=The+Shawshank+Redemption"}
                ]
            }
        }
    },
    {
        "id": 238,
        "title": "The Godfather",
        "original_title": "The Godfather",
        "tagline": "An offer you can't refuse.",
        "overview": "Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime family. When organized crime family patriarch, Vito Corleone barely survives an attempt on his life, his youngest son, Michael steps in to take care of the would-be killers, launching a campaign of bloody revenge.",
        "release_date": "1972-03-14",
        "release_year": 1972,
        "runtime": 175,
        "vote_average": 8.7,
        "vote_count": 19500,
        "popularity": 115.0,
        "genres": ["Drama", "Crime"],
        "director": "Francis Ford Coppola",
        "cast": ["Marlon Brando", "Al Pacino", "James Caan", "Robert Duvall", "Diane Keaton"],
        "keywords": ["mafia", "organized crime", "family", "loyalty", "revenge", "patriarch", "sicily"],
        "poster_path": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/tmU7GeKVybMWFButWEGl2M4GeiP.jpg",
        "imdb_rating": 9.2,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=The+Godfather"},
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=The+Godfather"}
                ]
            }
        }
    },
    {
        "id": 680,
        "title": "Pulp Fiction",
        "original_title": "Pulp Fiction",
        "tagline": "Just because you are a character doesn't mean that you have character.",
        "overview": "A burger-loving hit man, his philosophical partner, a drug-addled gangster's moll and a washed-up boxer converge in this sprawling, comedic crime caper. Their adventures unfurl in three stories that ingeniously trip back and forth in time.",
        "release_date": "1994-09-10",
        "release_year": 1994,
        "runtime": 154,
        "vote_average": 8.5,
        "vote_count": 26800,
        "popularity": 98.0,
        "genres": ["Thriller", "Crime"],
        "director": "Quentin Tarantino",
        "cast": ["John Travolta", "Samuel L. Jackson", "Uma Thurman", "Bruce Willis", "Ving Rhames"],
        "keywords": ["hitman", "nonlinear timeline", "drugs", "black comedy", "boxer", "mobster", "briefcase"],
        "poster_path": "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/suaEOtk1N1sgg2MTM7oZd2cfVp3.jpg",
        "imdb_rating": 8.9,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=Pulp+Fiction"}
                ]
            }
        }
    },
    {
        "id": 550,
        "title": "Fight Club",
        "original_title": "Fight Club",
        "tagline": "Mischief. Mayhem. Soap.",
        "overview": "A ticking-time-bomb insomniac and a slippery soap salesman channel primal male aggression into a shocking new form of therapy. Their concept catches on, with underground \"fight clubs\" forming in every town, until an eccentric gets in the way and ignites an out-of-control spiral toward oblivion.",
        "release_date": "1999-10-15",
        "release_year": 1999,
        "runtime": 139,
        "vote_average": 8.4,
        "vote_count": 28100,
        "popularity": 92.0,
        "genres": ["Drama"],
        "director": "David Fincher",
        "cast": ["Edward Norton", "Brad Pitt", "Helena Bonham Carter", "Meat Loaf", "Jared Leto"],
        "keywords": ["split personality", "consumerism", "underground fight", "insomnia", "anti-establishment", "anarchism"],
        "poster_path": "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/hZkgoQYus5vegHoetLkCJzb17zJ.jpg",
        "imdb_rating": 8.8,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=Fight+Club"}
                ]
            }
        }
    },
    {
        "id": 496243,
        "title": "Parasite",
        "original_title": "기생충",
        "tagline": "Act like you own the place.",
        "overview": "All unemployed, Ki-taek's family takes peculiar interest in the wealthy and glamorous Parks for their livelihood until they get entangled in an unexpected incident.",
        "release_date": "2019-05-30",
        "release_year": 2019,
        "runtime": 133,
        "vote_average": 8.5,
        "vote_count": 17500,
        "popularity": 89.0,
        "genres": ["Comedy", "Thriller", "Drama"],
        "director": "Bong Joon-ho",
        "cast": ["Song Kang-ho", "Lee Sun-kyun", "Cho Yeo-jeong", "Choi Woo-shik", "Park So-dam"],
        "keywords": ["class struggle", "con artist", "dark comedy", "social inequality", "subterfuge", "seoul"],
        "poster_path": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/hiKmpZMGZsrkA3cdce8a7Dpos1j.jpg",
        "imdb_rating": 8.5,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "SonyLIV", "logo": "https://image.tmdb.org/t/p/original/7rw3L812b9p0M9Z6u9c7m42b827.jpg", "type": "Subscription", "url": "https://www.sonyliv.com/movies/parasite-1000052328"}
                ]
            }
        }
    },
    {
        "id": 244786,
        "title": "Whiplash",
        "original_title": "Whiplash",
        "tagline": "The road to greatness can take you to the edge.",
        "overview": "Under the direction of a ruthless instructor, a talented young drummer begins to pursue perfection at any cost, even his humanity.",
        "release_date": "2014-10-10",
        "release_year": 2014,
        "runtime": 107,
        "vote_average": 8.4,
        "vote_count": 14700,
        "popularity": 78.0,
        "genres": ["Drama", "Music"],
        "director": "Damien Chazelle",
        "cast": ["Miles Teller", "J.K. Simmons", "Paul Reiser", "Melissa Benoist"],
        "keywords": ["jazz", "drummer", "obsession", "music school", "mentor student relationship", "perfectionism"],
        "poster_path": "https://image.tmdb.org/t/p/w500/7fn624j5lj3xTme2SgiLCeuedmO.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/6bbZ6XyvgfjhQwfplTRUhNDx7Ls.jpg",
        "imdb_rating": 8.5,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Netflix", "logo": "https://image.tmdb.org/t/p/original/9A1JSVmSxsya9Wi1egD6k6CGYg1.jpg", "type": "Subscription", "url": "https://www.netflix.com/title/70299275"}
                ]
            }
        }
    },
    {
        "id": 313369,
        "title": "La La Land",
        "original_title": "La La Land",
        "tagline": "Here's to the fools who dream.",
        "overview": "Mia, an aspiring actress, and Sebastian, a dedicated jazz musician, are struggling to make ends meet in a city known for crushing hopes and breaking hearts. Set in modern day Los Angeles, this original musical about everyday life explores the joy and pain of pursuing your dreams.",
        "release_date": "2016-11-29",
        "release_year": 2016,
        "runtime": 128,
        "vote_average": 7.9,
        "vote_count": 16300,
        "popularity": 85.0,
        "genres": ["Comedy", "Drama", "Romance", "Music"],
        "director": "Damien Chazelle",
        "cast": ["Ryan Gosling", "Emma Stone", "John Legend", "Rosemarie DeWitt", "J.K. Simmons"],
        "keywords": ["los angeles", "hollywood", "audition", "jazz piano", "romance", "nostalgia", "musical"],
        "poster_path": "https://image.tmdb.org/t/p/w500/uDO8zWDhfWwoFdKS4fzkVJt0Rf0.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/qJeU79uqgQUjIs0bplZkzbFOWfR.jpg",
        "imdb_rating": 8.0,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=La+La+Land"},
                    {"name": "SonyLIV", "logo": "https://image.tmdb.org/t/p/original/7rw3L812b9p0M9Z6u9c7m42b827.jpg", "type": "Subscription", "url": "https://www.sonyliv.com/movies/la-la-land-1000057285"}
                ]
            }
        }
    },
    {
        "id": 577922,
        "title": "Tenet",
        "original_title": "Tenet",
        "tagline": "Time runs out.",
        "overview": "Armed with only one word - Tenet - and fighting for the survival of the entire world, the Protagonist journeys through a twilight world of international espionage on a mission that will unfold in something beyond real time.",
        "release_date": "2020-08-22",
        "release_year": 2020,
        "runtime": 150,
        "vote_average": 7.2,
        "vote_count": 9400,
        "popularity": 70.0,
        "genres": ["Action", "Science Fiction", "Thriller"],
        "director": "Christopher Nolan",
        "cast": ["John David Washington", "Robert Pattinson", "Elizabeth Debicki", "Kenneth Branagh", "Dimple Kapadia"],
        "keywords": ["time inversion", "espionage", "entropy", "cold war", "opera house", "agent"],
        "poster_path": "https://image.tmdb.org/t/p/w500/k68nPLbIST6NP96JmTxmZijEvCA.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/wzJRB4MKi3yK138bJSuLHNvOXQU.jpg",
        "imdb_rating": 7.3,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=Tenet"}
                ]
            }
        }
    },
    {
        "id": 76341,
        "title": "Mad Max: Fury Road",
        "original_title": "Mad Max: Fury Road",
        "tagline": "What a Lovely Day.",
        "overview": "An apocalyptic story set in the furthest reaches of our planet, in a stark desert landscape where humanity is broken, and most everyone is crazed fighting for the necessities of life. Within this world exist two rebels on the run who just might be able to restore order.",
        "release_date": "2015-05-13",
        "release_year": 2015,
        "runtime": 120,
        "vote_average": 7.6,
        "vote_count": 21800,
        "popularity": 96.0,
        "genres": ["Action", "Adventure", "Science Fiction"],
        "director": "George Miller",
        "cast": ["Tom Hardy", "Charlize Theron", "Nicholas Hoult", "Hugh Keays-Byrne", "Zoë Kravitz"],
        "keywords": ["post-apocalyptic", "car chase", "wasteland", "survival", "tyrant", "desert warrior"],
        "poster_path": "https://image.tmdb.org/t/p/w500/8tZYtuWezp8JbcsvHYO0O46tFbo.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/nlCHUWjY9XWbuEUQauCBgnY8ymF.jpg",
        "imdb_rating": 8.1,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=Mad+Max+Fury+Road"}
                ]
            }
        }
    },
    {
        "id": 299534,
        "title": "Avengers: Endgame",
        "original_title": "Avengers: Endgame",
        "tagline": "Part of the journey is the end.",
        "overview": "After the devastating events of Avengers: Infinity War, the universe is in ruins due to the efforts of the Mad Titan, Thanos. With the help of remaining allies, the Avengers must assemble once more in order to undo Thanos's actions and restore order to the universe once and for all, no matter what consequences may be in store.",
        "release_date": "2019-04-24",
        "release_year": 2019,
        "runtime": 181,
        "vote_average": 8.3,
        "vote_count": 25200,
        "popularity": 140.0,
        "genres": ["Adventure", "Science Fiction", "Action"],
        "director": "Anthony Russo",
        "cast": ["Robert Downey Jr.", "Chris Evans", "Mark Ruffalo", "Chris Hemsworth", "Scarlett Johansson", "Jeremy Renner"],
        "keywords": ["superhero", "time travel", "infinity stones", "marvel cinematic universe", "thanos", "climax"],
        "poster_path": "https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/7RyHsO4yDXtBv1zUU3mTpHeQ0d5.jpg",
        "imdb_rating": 8.4,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/movies/avengers-endgame/1260013556"}
                ]
            }
        }
    },
    {
        "id": 324857,
        "title": "Spider-Man: Into the Spider-Verse",
        "original_title": "Spider-Man: Into the Spider-Verse",
        "tagline": "More than one wears the mask.",
        "overview": "Struggling to find his place in the world while juggling school and family, Brooklyn teenager Miles Morales is unexpectedly bitten by a radioactive spider and develops superpowers just like the one and only Spider-Man. When a gateway to the multiverse opens up, Miles must team up with five alternate Spider-heroes to stop a threat that puts all realities in danger.",
        "release_date": "2018-12-06",
        "release_year": 2018,
        "runtime": 117,
        "vote_average": 8.4,
        "vote_count": 15600,
        "popularity": 105.0,
        "genres": ["Animation", "Action", "Adventure", "Science Fiction"],
        "director": "Bob Persichetti",
        "cast": ["Shameik Moore", "Jake Johnson", "Hailee Steinfeld", "Mahershala Ali", "Brian Tyree Henry"],
        "keywords": ["multiverse", "spider-man", "coming of age", "parallel world", "comic book art", "brooklyn"],
        "poster_path": "https://image.tmdb.org/t/p/w500/iiZZdoQBEYBv6id8su7ImL0oCbD.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/7d6woSTJ1iy5Q2R7vM2K9rT8l03.jpg",
        "imdb_rating": 8.4,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Netflix", "logo": "https://image.tmdb.org/t/p/original/9A1JSVmSxsya9Wi1egD6k6CGYg1.jpg", "type": "Subscription", "url": "https://www.netflix.com/title/81002747"}
                ]
            }
        }
    },
    {
        "id": 569094,
        "title": "Spider-Man: Across the Spider-Verse",
        "original_title": "Spider-Man: Across the Spider-Verse",
        "tagline": "It's how you wear the mask that matters.",
        "overview": "After reuniting with Gwen Stacy, Brooklyn's full-time, friendly neighborhood Spider-Man is catapulted across the Multiverse, where he encounters the Spider-Society, a team of Spider-People charged with protecting the Multiverse's very existence. But when the heroes clash on how to handle a new threat, Miles finds himself pitted against the other Spiders.",
        "release_date": "2023-05-31",
        "release_year": 2023,
        "runtime": 140,
        "vote_average": 8.4,
        "vote_count": 7100,
        "popularity": 130.0,
        "genres": ["Animation", "Action", "Adventure", "Science Fiction"],
        "director": "Joaquim Dos Santos",
        "cast": ["Shameik Moore", "Hailee Steinfeld", "Oscar Isaac", "Jake Johnson", "Daniel Kaluuya"],
        "keywords": ["multiverse", "canon event", "spider-man", "spider-punk", "dimension travel", "destiny"],
        "poster_path": "https://image.tmdb.org/t/p/w500/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/4HodYYKEIsGOdinkGi2Ucz6X9i0.jpg",
        "imdb_rating": 8.6,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Netflix", "logo": "https://image.tmdb.org/t/p/original/9A1JSVmSxsya9Wi1egD6k6CGYg1.jpg", "type": "Subscription", "url": "https://www.netflix.com/title/81664160"}
                ]
            }
        }
    },
    {
        "id": 545611,
        "title": "Everything Everywhere All at Once",
        "original_title": "Everything Everywhere All at Once",
        "tagline": "The universe is so much bigger than you realize.",
        "overview": "An aging Chinese immigrant is swept up in an insane adventure, where she alone can save what's important to her by connecting with the lives she could have led in other universes.",
        "release_date": "2022-03-24",
        "release_year": 2022,
        "runtime": 139,
        "vote_average": 7.8,
        "vote_count": 6400,
        "popularity": 88.0,
        "genres": ["Action", "Adventure", "Science Fiction", "Comedy"],
        "director": "Daniel Kwan",
        "cast": ["Michelle Yeoh", "Ke Huy Quan", "Stephanie Hsu", "Jamie Lee Curtis", "James Hong"],
        "keywords": ["multiverse", "existentialism", "nihilism", "family reconciliation", "martial arts", "laundromat"],
        "poster_path": "https://image.tmdb.org/t/p/w500/w3LxiVYPqrlxqP9Yue483Zh37T6.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/ss0JVbu52au25W27bY7keaBpn4t.jpg",
        "imdb_rating": 7.8,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "SonyLIV", "logo": "https://image.tmdb.org/t/p/original/7rw3L812b9p0M9Z6u9c7m42b827.jpg", "type": "Subscription", "url": "https://www.sonyliv.com/movies/everything-everywhere-all-at-once-1000216601"}
                ]
            }
        }
    },
    {
        "id": 579974,
        "title": "RRR",
        "original_title": "RRR",
        "tagline": "Rise. Roar. Revolt.",
        "overview": "A fictional history of two legendary revolutionaries' journey away from home before they began fighting for their country in the 1920s against British colonial rule.",
        "release_date": "2022-03-24",
        "release_year": 2022,
        "runtime": 187,
        "vote_average": 7.8,
        "vote_count": 1800,
        "popularity": 95.0,
        "genres": ["Action", "Drama", "History"],
        "director": "S.S. Rajamouli",
        "cast": ["N.T. Rama Rao Jr.", "Ram Charan", "Alia Bhatt", "Ajay Devgn", "Olivia Morris"],
        "keywords": ["freedom fighter", "british raj", "revolution", "bromance", "epic", "rebellion", "india"],
        "poster_path": "https://image.tmdb.org/t/p/w500/wE0noFUq1q16nmnV8I5U0Jd4b9x.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/2wP1m4pX6m6d8f8A5c7T18B9y8x.jpg",
        "imdb_rating": 7.8,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Netflix", "logo": "https://image.tmdb.org/t/p/original/9A1JSVmSxsya9Wi1egD6k6CGYg1.jpg", "type": "Subscription", "url": "https://www.netflix.com/title/81476453"},
                    {"name": "ZEE5", "logo": "https://image.tmdb.org/t/p/original/lpmZ08z2bB4m436M9c6qT18Z9x.jpg", "type": "Subscription", "url": "https://www.zee5.com/movies/details/rrr/0-0-1z5154316"}
                ]
            }
        }
    },
    {
        "id": 361743,
        "title": "Top Gun: Maverick",
        "original_title": "Top Gun: Maverick",
        "tagline": "Feel the need. The need for speed.",
        "overview": "After more than thirty years of service as one of the Navy's top aviators, and dodging the advancement in rank that would ground him, Pete “Maverick” Mitchell finds himself training a detachment of TOP GUN graduates for a specialized mission the likes of which no living pilot has ever seen.",
        "release_date": "2022-05-24",
        "release_year": 2022,
        "runtime": 130,
        "vote_average": 8.2,
        "vote_count": 8900,
        "popularity": 94.0,
        "genres": ["Action", "Drama"],
        "director": "Joseph Kosinski",
        "cast": ["Tom Cruise", "Miles Teller", "Jennifer Connelly", "Jon Hamm", "Glen Powell"],
        "keywords": ["fighter jet", "pilot", "navy", "training", "aerial combat", "dogfight", "mission"],
        "poster_path": "https://image.tmdb.org/t/p/w500/62HCnUTziyWcpDaBO2i1DX17ljH.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/AaV1YIdWKnjAiaOe8UUKKRm322h.jpg",
        "imdb_rating": 8.3,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=Top+Gun+Maverick"},
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=Top+Gun+Maverick"}
                ]
            }
        }
    },
    {
        "id": 129,
        "title": "Spirited Away",
        "original_title": "千と千尋の神隠し",
        "tagline": "The tunnel led Chihiro to a mysterious town.",
        "overview": "A young girl, Chihiro, becomes trapped in a strange new world of spirits. When her parents undergo a mysterious transformation, she must call upon the courage she never knew she had to free her family.",
        "release_date": "2001-07-20",
        "release_year": 2001,
        "runtime": 125,
        "vote_average": 8.5,
        "vote_count": 16400,
        "popularity": 86.0,
        "genres": ["Animation", "Family", "Fantasy"],
        "director": "Hayao Miyazaki",
        "cast": ["Rumi Hiiragi", "Miyu Irino", "Mari Natsuki", "Takashi Naito"],
        "keywords": ["studio ghibli", "spirit world", "bathhouse", "witch", "dragon", "curse", "folklore"],
        "poster_path": "https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/Ab8mkHmkYADjU7wQiOkia9BzGvS.jpg",
        "imdb_rating": 8.6,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Netflix", "logo": "https://image.tmdb.org/t/p/original/9A1JSVmSxsya9Wi1egD6k6CGYg1.jpg", "type": "Subscription", "url": "https://www.netflix.com/title/60023642"}
                ]
            }
        }
    },
    {
        "id": 372058,
        "title": "Your Name.",
        "original_title": "君の名は。",
        "tagline": "Treasure the experience. Dreams fade away after you wake up.",
        "overview": "High schoolers Mitsuha and Taki are complete strangers living separate lives in different parts of Japan. But one night, they suddenly switch places. Their bizarre occurrence continues to happen randomly, and the two must adjust their lives around each other.",
        "release_date": "2016-08-26",
        "release_year": 2016,
        "runtime": 106,
        "vote_average": 8.5,
        "vote_count": 11200,
        "popularity": 74.0,
        "genres": ["Animation", "Romance", "Drama"],
        "director": "Makoto Shinkai",
        "cast": ["Ryunosuke Kamiki", "Mone Kamishiraishi", "Ryo Narita", "Aoi Yuki"],
        "keywords": ["body swap", "comet", "fate", "tokyo", "rural japan", "time travel", "red string of fate"],
        "poster_path": "https://image.tmdb.org/t/p/w500/q719jXXEzOoYaps6qFsC8llRaQ.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/dIWwZW7dJJ1742Szsq97mg9WE4U.jpg",
        "imdb_rating": 8.4,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Netflix", "logo": "https://image.tmdb.org/t/p/original/9A1JSVmSxsya9Wi1egD6k6CGYg1.jpg", "type": "Subscription", "url": "https://www.netflix.com/title/80161371"}
                ]
            }
        }
    },
    {
        "id": 20453,
        "title": "3 Idiots",
        "original_title": "3 Idiots",
        "tagline": "Don't chase success, chase excellence.",
        "overview": "Two friends embark on a quest for a lost buddy. On this journey, they encounter a long forgotten bet, a wedding they must crash, and a funeral that goes impossibly out of control. As they make their way through the perilous landscape, another journey begins: their inner journey through memory, of their friend Rancho who influenced them to think differently.",
        "release_date": "2009-12-23",
        "release_year": 2009,
        "runtime": 170,
        "vote_average": 8.0,
        "vote_count": 2300,
        "popularity": 65.0,
        "genres": ["Drama", "Comedy"],
        "director": "Rajkumar Hirani",
        "cast": ["Aamir Khan", "R. Madhavan", "Sharman Joshi", "Kareena Kapoor", "Boman Irani"],
        "keywords": ["engineering college", "friendship", "education system", "inspiration", "inventor", "india"],
        "poster_path": "https://image.tmdb.org/t/p/w500/66A9MqXOyVFCssoloscw79z8OtQ.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/u7kuX66q16uN67k39bH99w2H1kC.jpg",
        "imdb_rating": 8.4,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/detail/3-Idiots/0PD334O9R4VMT9V6L42X5R8B"},
                    {"name": "YouTube", "logo": "https://image.tmdb.org/t/p/original/tbEdFQDwx5LEVr8Wp6z094VuOnz.jpg", "type": "Free", "url": "https://www.youtube.com/results?search_query=3+idiots+full+movie"}
                ]
            }
        }
    },
    {
        "id": 286217,
        "title": "The Martian",
        "original_title": "The Martian",
        "tagline": "Bring him home.",
        "overview": "During a mission to Mars, American astronaut Mark Watney is presumed dead after a fierce storm and left behind by his crew. But Watney has survived and finds himself stranded and alone on the hostile planet. With only meager supplies, he must draw upon his ingenuity, wit and spirit to subsist and find a way to signal to Earth that he is alive.",
        "release_date": "2015-09-30",
        "release_year": 2015,
        "runtime": 144,
        "vote_average": 7.7,
        "vote_count": 19200,
        "popularity": 78.0,
        "genres": ["Drama", "Adventure", "Science Fiction"],
        "director": "Ridley Scott",
        "cast": ["Matt Damon", "Jessica Chastain", "Kristen Wiig", "Jeff Daniels", "Michael Peña", "Kate Mara"],
        "keywords": ["mars", "astronaut", "botany", "survival", "nasa", "space mission", "ingenuity"],
        "poster_path": "https://image.tmdb.org/t/p/w500/5BHuvQ6p9kQT09NMnbErLhHbY4x.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/syTbptvslud9ao78v8L5k1U2t28.jpg",
        "imdb_rating": 8.0,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=The+Martian"}
                ]
            }
        }
    },
    {
        "id": 13,
        "title": "Forrest Gump",
        "original_title": "Forrest Gump",
        "tagline": "Life is like a box of chocolates...",
        "overview": "A man with a low IQ has accomplished great things in his life and been present during significant historic events—in each case, far exceeding what anyone imagined he could do. Yet, despite all the things he has attained, his only true love eludes him.",
        "release_date": "1994-06-23",
        "release_year": 1994,
        "runtime": 142,
        "vote_average": 8.5,
        "vote_count": 27200,
        "popularity": 92.0,
        "genres": ["Comedy", "Drama", "Romance"],
        "director": "Robert Zemeckis",
        "cast": ["Tom Hanks", "Robin Wright", "Gary Sinise", "Mykelti Williamson", "Sally Field"],
        "keywords": ["vietnam war", "running", "optimism", "historical events", "ping pong", "shrimp business"],
        "poster_path": "https://image.tmdb.org/t/p/w500/arw2VCBveWOVZr6pxd9XTd1TdQa.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/qdIMHd4sEfJSckfVJfKQvisL02a.jpg",
        "imdb_rating": 8.8,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Netflix", "logo": "https://image.tmdb.org/t/p/original/9A1JSVmSxsya9Wi1egD6k6CGYg1.jpg", "type": "Subscription", "url": "https://www.netflix.com/title/60000724"},
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=Forrest+Gump"}
                ]
            }
        }
    },
    {
        "id": 807,
        "title": "Se7en",
        "original_title": "Se7en",
        "tagline": "Seven deadly sins. Seven ways to die.",
        "overview": "Two homicide detectives are on a desperate hunt for a serial killer whose crimes are based on the \"seven deadly sins\": gluttony, greed, sloth, wrath, pride, lust and envy.",
        "release_date": "1995-09-22",
        "release_year": 1995,
        "runtime": 127,
        "vote_average": 8.4,
        "vote_count": 20500,
        "popularity": 81.0,
        "genres": ["Crime", "Mystery", "Thriller"],
        "director": "David Fincher",
        "cast": ["Brad Pitt", "Morgan Freeman", "Gwyneth Paltrow", "Kevin Spacey", "John C. McGinley"],
        "keywords": ["serial killer", "seven deadly sins", "detectives", "grim", "noir", "twist ending", "box"],
        "poster_path": "https://image.tmdb.org/t/p/w500/69Sns8WoET6C6T9CCx26WnstdaW.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/ba4CpFFxXwP7z5lT0c8u8yL28zM.jpg",
        "imdb_rating": 8.6,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Netflix", "logo": "https://image.tmdb.org/t/p/original/9A1JSVmSxsya9Wi1egD6k6CGYg1.jpg", "type": "Subscription", "url": "https://www.netflix.com/title/950149"}
                ]
            }
        }
    },
    {
        "id": 19404,
        "title": "Dilwale Dulhania Le Jayenge",
        "original_title": "दिलवाले दुल्हनिया ले जायेंगे",
        "tagline": "Come... Fall in Love.",
        "overview": "Raj and Simran meet on a train trip across Europe and fall in love. When Raj learns that Simran is already promised to another man back in India, he follows her to win over her traditional family before her wedding.",
        "release_date": "1995-10-20",
        "release_year": 1995,
        "runtime": 189,
        "vote_average": 8.5,
        "vote_count": 4400,
        "popularity": 60.0,
        "genres": ["Comedy", "Drama", "Romance"],
        "director": "Aditya Chopra",
        "cast": ["Shah Rukh Khan", "Kajol", "Amrish Puri", "Farida Jalal", "Anupam Kher"],
        "keywords": ["europe trip", "indian wedding", "love story", "tradition vs love", "punjab", "mustard fields"],
        "poster_path": "https://image.tmdb.org/t/p/w500/lf9RTEAddOH8oqgvWi93Oz7aR8z.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/90xD87Ue9C2bC3P6KqFq8zYyV0p.jpg",
        "imdb_rating": 8.0,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/detail/Dilwale-Dulhania-Le-Jayenge/0NDW4M2U30V83P868X9W2H"}
                ]
            }
        }
    },
    {
        "id": 38,
        "title": "Eternal Sunshine of the Spotless Mind",
        "original_title": "Eternal Sunshine of the Spotless Mind",
        "tagline": "You can erase someone from your mind. Getting them out of your heart is another story.",
        "overview": "Joel Barish, heartbroken that his girlfriend Clementine underwent a procedure to erase him from her memory, decides to do the same. However, as he watches his memories of her fade away, he realizes that he still loves her, and may be too late to correct his mistake.",
        "release_date": "2004-03-19",
        "release_year": 2004,
        "runtime": 108,
        "vote_average": 8.1,
        "vote_count": 14500,
        "popularity": 73.0,
        "genres": ["Science Fiction", "Drama", "Romance"],
        "director": "Michel Gondry",
        "cast": ["Jim Carrey", "Kate Winslet", "Kirsten Dunst", "Mark Ruffalo", "Elijah Wood"],
        "keywords": ["memory erasure", "heartbreak", "subconscious", "surrealism", "montauk", "lovers"],
        "poster_path": "https://image.tmdb.org/t/p/w500/5MwkWH9tYHv3mV9OdYTMR5q9IzL.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/x4UWWqptT8s1vJbXn5f3iZqQfA.jpg",
        "imdb_rating": 8.3,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=Eternal+Sunshine"}
                ]
            }
        }
    },
    {
        "id": 120,
        "title": "The Lord of the Rings: The Fellowship of the Ring",
        "original_title": "The Lord of the Rings: The Fellowship of the Ring",
        "tagline": "One ring to rule them all.",
        "overview": "Young hobbit Frodo Baggins, after inheriting a mysterious ring from his uncle Bilbo, must leave his home in order to keep it from falling into the hands of its evil creator. Along the way, a fellowship is formed to protect him and offer that one chance to destroy the Ring in Mount Doom.",
        "release_date": "2001-12-18",
        "release_year": 2001,
        "runtime": 178,
        "vote_average": 8.4,
        "vote_count": 24800,
        "popularity": 130.0,
        "genres": ["Adventure", "Fantasy", "Action"],
        "director": "Peter Jackson",
        "cast": ["Elijah Wood", "Ian McKellen", "Viggo Mortensen", "Sean Astin", "Orlando Bloom"],
        "keywords": ["one ring", "middle earth", "hobbit", "wizard", "fellowship", "sauron", "epic fantasy"],
        "poster_path": "https://image.tmdb.org/t/p/w500/6oom5QYQ2yQTMJIbnvbkBL9cDK6.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/vRQnzOnJeSu5OJ1XdTuVa546NKz.jpg",
        "imdb_rating": 8.9,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=Fellowship+of+the+Ring"},
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=Lord+of+the+Rings"}
                ]
            }
        }
    },
    {
        "id": 122,
        "title": "The Lord of the Rings: The Return of the King",
        "original_title": "The Lord of the Rings: The Return of the King",
        "tagline": "The eye of the enemy is moving.",
        "overview": "As armies mass for a final battle that will decide the fate of the world--and powerful, ancient forces of Light and Dark compete to determine the outcome--one member of the fellowship of the ring is revealed as the noble heir to the throne of the kings of men. Yet, the sole hope for triumph over evil lies with a brave hobbit, Frodo, who, accompanied by his loyal friend Sam and the hideous, wretched Gollum, ventures deep into the very dark heart of Mordor on his seemingly impossible quest to destroy the Ring of Power.",
        "release_date": "2003-12-17",
        "release_year": 2003,
        "runtime": 201,
        "vote_average": 8.6,
        "vote_count": 23600,
        "popularity": 125.0,
        "genres": ["Adventure", "Fantasy", "Action"],
        "director": "Peter Jackson",
        "cast": ["Elijah Wood", "Ian McKellen", "Viggo Mortensen", "Sean Astin", "Andy Serkis"],
        "keywords": ["battle of minas tirith", "mount doom", "king of gondor", "coronation", "epic climax"],
        "poster_path": "https://image.tmdb.org/t/p/w500/rCzpDGLbOoPwLjy3OAm5NUPOTrC.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/2u7zbn8EudG6kLlBzUYqP8RyFU4.jpg",
        "imdb_rating": 9.0,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=Return+of+the+King"}
                ]
            }
        }
    },
    {
        "id": 11,
        "title": "Star Wars",
        "original_title": "Star Wars",
        "tagline": "A long time ago in a galaxy far, far away...",
        "overview": "Princess Leia is captured and held hostage by the evil Imperial forces in their effort to take over the galactic Empire. Venturesome Luke Skywalker and dashing captain Han Solo team together with the loveable robot duo R2-D2 and C-3PO to rescue the beautiful princess and restore peace and justice in the Empire.",
        "release_date": "1977-05-25",
        "release_year": 1977,
        "runtime": 121,
        "vote_average": 8.2,
        "vote_count": 19800,
        "popularity": 85.0,
        "genres": ["Adventure", "Action", "Science Fiction"],
        "director": "George Lucas",
        "cast": ["Mark Hamill", "Harrison Ford", "Carrie Fisher", "Peter Cushing", "Alec Guinness"],
        "keywords": ["jedi", "the force", "death star", "lightsaber", "darth vader", "galactic empire", "space battle"],
        "poster_path": "https://image.tmdb.org/t/p/w500/6FfCtAuVAW8XJjZ7eWeLibRLWTw.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/4qCqAdHcNUmYK8nb8jhvQhS1j2i.jpg",
        "imdb_rating": 8.6,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/movies/star-wars-a-new-hope/1260018443"}
                ]
            }
        }
    },
    {
        "id": 77,
        "title": "Memento",
        "original_title": "Memento",
        "tagline": "Some memories are best forgotten.",
        "overview": "Leonard Shelby is tracking down the man who raped and murdered his wife. The difficulty of locating his wife's killer, however, is compounded by the fact that he suffers from a rare, untreatable form of short-term memory loss. Although he can recall details of life before his accident, Leonard cannot remember what happened fifteen minutes ago, where he's going, or why.",
        "release_date": "2000-10-11",
        "release_year": 2000,
        "runtime": 113,
        "vote_average": 8.2,
        "vote_count": 14200,
        "popularity": 62.0,
        "genres": ["Mystery", "Thriller"],
        "director": "Christopher Nolan",
        "cast": ["Guy Pearce", "Carrie-Anne Moss", "Joe Pantoliano", "Mark Boone Junior"],
        "keywords": ["short term memory", "reverse chronology", "polaroid", "tattoos", "revenge", "deception"],
        "poster_path": "https://image.tmdb.org/t/p/w500/yuNs09hvpHVU1cBTCAk9zxsL2oW.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/l91q7j0aR94P3u2k58a1V9c84r3.jpg",
        "imdb_rating": 8.4,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=Memento"}
                ]
            }
        }
    },
    {
        "id": 11324,
        "title": "Shutter Island",
        "original_title": "Shutter Island",
        "tagline": "Someone is missing.",
        "overview": "World War II soldier-turned-U.S. Marshal Teddy Daniels investigates the disappearance of a patient from Boston's Shutter Island Ashecliffe Hospital, an institution for the criminally insane. He's been pushing for an assignment on the island for personal reasons, but before long he wonders whether he hasn't been brought there as part of a twisted plot by hospital doctors whose radical treatments range from unethical to illegally mind-numbing.",
        "release_date": "2010-02-18",
        "release_year": 2010,
        "runtime": 138,
        "vote_average": 8.2,
        "vote_count": 23100,
        "popularity": 87.0,
        "genres": ["Drama", "Thriller", "Mystery"],
        "director": "Martin Scorsese",
        "cast": ["Leonardo DiCaprio", "Mark Ruffalo", "Ben Kingsley", "Max von Sydow", "Michelle Williams"],
        "keywords": ["psychiatric hospital", "lighthouse", "hallucinations", "conspiracy", "island", "twist"],
        "poster_path": "https://image.tmdb.org/t/p/w500/kve20tXwUZpu4GUX8l6X7Z4QI02.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/9BBTo63ANSmhC4e6r62OJFuK2GL.jpg",
        "imdb_rating": 8.2,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Netflix", "logo": "https://image.tmdb.org/t/p/original/9A1JSVmSxsya9Wi1egD6k6CGYg1.jpg", "type": "Subscription", "url": "https://www.netflix.com/title/70095139"},
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=Shutter+Island"}
                ]
            }
        }
    },
    {
        "id": 106646,
        "title": "The Wolf of Wall Street",
        "original_title": "The Wolf of Wall Street",
        "tagline": "Earn. Spend. Party.",
        "overview": "A New York stockbroker refuses to cooperate in a large securities fraud case involving corruption on Wall Street, corporate banking world and mob infiltration. Based on Jordan Belfort's autobiography.",
        "release_date": "2013-12-25",
        "release_year": 2013,
        "runtime": 180,
        "vote_average": 8.0,
        "vote_count": 23400,
        "popularity": 96.0,
        "genres": ["Crime", "Drama", "Comedy"],
        "director": "Martin Scorsese",
        "cast": ["Leonardo DiCaprio", "Jonah Hill", "Margot Robbie", "Kyle Chandler", "Rob Reiner"],
        "keywords": ["wall street", "stock broker", "fraud", "excess", "hedonism", "fbi", "greed"],
        "poster_path": "https://image.tmdb.org/t/p/w500/kW9LmvYfwKn9BqVExk17b5Z4eO9.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/7XoiwLzQWp8r2q8s2L5q7oR5m4y.jpg",
        "imdb_rating": 8.2,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=Wolf+of+Wall+Street"}
                ]
            }
        }
    },
    {
        "id": 1422,
        "title": "The Departed",
        "original_title": "The Departed",
        "tagline": "Lies. Betrayal. Sacrifice. How far will you go?",
        "overview": "To take down South Boston's Irish Mafia, the police send in one of their own to infiltrate the underworld, not realizing the syndicate has done likewise. While an undercover cop curries favor with the mob kingpin, a career criminal rises through the police ranks. But both sides soon discover there's a mole among them.",
        "release_date": "2006-10-05",
        "release_year": 2006,
        "runtime": 151,
        "vote_average": 8.2,
        "vote_count": 14300,
        "popularity": 71.0,
        "genres": ["Drama", "Thriller", "Crime"],
        "director": "Martin Scorsese",
        "cast": ["Leonardo DiCaprio", "Matt Damon", "Jack Nicholson", "Mark Wahlberg", "Martin Sheen"],
        "keywords": ["undercover cop", "mole", "irish mob", "boston", "cat and mouse", "betrayal"],
        "poster_path": "https://image.tmdb.org/t/p/w500/nT97ifVT2J1yMQmeq20Qblg61T.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/c4BCgI0rE2B5c4D2lZ7A9F5V1c.jpg",
        "imdb_rating": 8.5,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=The+Departed"}
                ]
            }
        }
    },
    {
        "id": 419430,
        "title": "Get Out",
        "original_title": "Get Out",
        "tagline": "Just because you're invited, doesn't mean you're welcome.",
        "overview": "Chris and his girlfriend Rose go upstate to visit her parents for the weekend. At first, Chris reads the family's overly accommodating behavior as nervous attempts to deal with their daughter's interracial relationship, but as the weekend progresses, a series of increasingly disturbing discoveries lead him to a truth that he never could have imagined.",
        "release_date": "2017-02-24",
        "release_year": 2017,
        "runtime": 104,
        "vote_average": 7.6,
        "vote_count": 16500,
        "popularity": 69.0,
        "genres": ["Mystery", "Thriller", "Horror"],
        "director": "Jordan Peele",
        "cast": ["Daniel Kaluuya", "Allison Williams", "Bradley Whitford", "Catherine Keener", "Caleb Landry Jones"],
        "keywords": ["hypnosis", "sunken place", "social horror", "racism", "mind control", "paranoia"],
        "poster_path": "https://image.tmdb.org/t/p/w500/tFXcEccSQMf3lfhfXKSU9iRBpa3.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/8u1YxL3l2b9fT0rB1y0d8F7g1Y.jpg",
        "imdb_rating": 7.8,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=Get+Out"}
                ]
            }
        }
    },
    {
        "id": 493922,
        "title": "Hereditary",
        "original_title": "Hereditary",
        "tagline": "Every family tree hides a secret.",
        "overview": "When Ellen, the matriarch of the Graham family, passes away, her daughter's family begins to unravel cryptic and increasingly terrifying secrets about their ancestry.",
        "release_date": "2018-06-07",
        "release_year": 2018,
        "runtime": 127,
        "vote_average": 7.3,
        "vote_count": 7400,
        "popularity": 63.0,
        "genres": ["Horror", "Mystery", "Drama"],
        "director": "Ari Aster",
        "cast": ["Toni Collette", "Alex Wolff", "Milly Shapiro", "Ann Dowd", "Gabriel Byrne"],
        "keywords": ["cult", "possession", "grief", "family trauma", "seance", "demon", "miniatures"],
        "poster_path": "https://image.tmdb.org/t/p/w500/p9fmuz2Oj3k19BGtU51vBshVNWZ.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/u20Z1k0L8Y9Vb6p4r8Z3F0r1d5K.jpg",
        "imdb_rating": 7.3,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=Hereditary"}
                ]
            }
        }
    },
    {
        "id": 354912,
        "title": "Coco",
        "original_title": "Coco",
        "tagline": "The celebration of a lifetime.",
        "overview": "Despite his family’s baffling generations-old ban on music, Miguel dreams of becoming an accomplished musician like his idol, Ernesto de la Cruz. Desperate to prove his talent, Miguel finds himself in the stunning and colorful Land of the Dead following a mysterious chain of events.",
        "release_date": "2017-10-27",
        "release_year": 2017,
        "runtime": 105,
        "vote_average": 8.2,
        "vote_count": 18900,
        "popularity": 90.0,
        "genres": ["Animation", "Family", "Music", "Adventure"],
        "director": "Lee Unkrich",
        "cast": ["Anthony Gonzalez", "Gael García Bernal", "Benjamin Bratt", "Alanna Ubach"],
        "keywords": ["day of the dead", "mexico", "guitar", "ancestors", "land of the dead", "family memory"],
        "poster_path": "https://image.tmdb.org/t/p/w500/gGEsBPAijhVUFoiNpgZXqRVWJt2.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/askg3SMvhqEl4OL52YuvdtQw40Y.jpg",
        "imdb_rating": 8.4,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/movies/coco/1260005574"}
                ]
            }
        }
    },
    {
        "id": 260513,
        "title": "Incredibles 2",
        "original_title": "Incredibles 2",
        "tagline": "Back to work.",
        "overview": "Elastigirl springs into action to save the day, while Mr. Incredible faces his greatest challenge yet -- taking care of the problems of his three children.",
        "release_date": "2018-06-14",
        "release_year": 2018,
        "runtime": 118,
        "vote_average": 7.5,
        "vote_count": 12800,
        "popularity": 72.0,
        "genres": ["Action", "Adventure", "Animation", "Family"],
        "director": "Brad Bird",
        "cast": ["Craig T. Nelson", "Holly Hunter", "Sarah Vowell", "Huck Milner", "Samuel L. Jackson"],
        "keywords": ["superhero family", "jack-jack", "screenslaver", "parenting", "retro futuristic"],
        "poster_path": "https://image.tmdb.org/t/p/w500/9lFKBtaVIhP7E2Pk0IY1CwTKTMZ.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/mabuNsGJgBWAAAjzgUVn97MRJaq.jpg",
        "imdb_rating": 7.6,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/movies/incredibles-2/1260005579"}
                ]
            }
        }
    },
    {
        "id": 10681,
        "title": "WALL·E",
        "original_title": "WALL·E",
        "tagline": "After 700 years of doing what he was built for - he'll discover what he was meant for.",
        "overview": "WALL·E is the last robot left on an Earth that has been overrun with garbage and all humans have evacuated to giant starships. One day, a sleek robot probe named EVE visits planet Earth and WALL·E falls deeply in love with her.",
        "release_date": "2008-06-22",
        "release_year": 2008,
        "runtime": 98,
        "vote_average": 8.1,
        "vote_count": 18200,
        "popularity": 79.0,
        "genres": ["Animation", "Family", "Science Fiction"],
        "director": "Andrew Stanton",
        "cast": ["Ben Burtt", "Elissa Knight", "Jeff Garlin", "Fred Willard"],
        "keywords": ["robot", "earth cleanup", "environmentalism", "space voyage", "plant life", "silent film homage"],
        "poster_path": "https://image.tmdb.org/t/p/w500/hbhFnRzzg6ZDmm8YAmxBnQpQIPh.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/f4pnf4wRkUqGk5cZ6uVf3uJ3z0Q.jpg",
        "imdb_rating": 8.4,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/movies/walle/1260005577"}
                ]
            }
        }
    },
    {
        "id": 264660,
        "title": "Ex Machina",
        "original_title": "Ex Machina",
        "tagline": "There is nothing more human than the will to survive.",
        "overview": "Caleb, a 26-year-old coder at the world's largest internet company, wins a competition to spend a week at a private mountain retreat belonging to Nathan, the reclusive CEO. But when Caleb arrives at the remote location, he finds that he will have to participate in a strange and fascinating experiment: interacting with the world's first true artificial intelligence, housed in the body of a beautiful robot woman.",
        "release_date": "2015-01-21",
        "release_year": 2015,
        "runtime": 108,
        "vote_average": 7.6,
        "vote_count": 13100,
        "popularity": 64.0,
        "genres": ["Drama", "Science Fiction"],
        "director": "Alex Garland",
        "cast": ["Domhnall Gleeson", "Alicia Vikander", "Oscar Isaac", "Sonoya Mizuno"],
        "keywords": ["artificial intelligence", "turing test", "android", "isolation", "manipulation", "consciousness"],
        "poster_path": "https://image.tmdb.org/t/p/w500/btbRB7BrD88799haR2YrSUvfR2m.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/z99U2qYtZ6qQe8W9u1Q3T9gM0n2.jpg",
        "imdb_rating": 7.7,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=Ex+Machina"}
                ]
            }
        }
    },
    {
        "id": 245891,
        "title": "John Wick",
        "original_title": "John Wick",
        "tagline": "Don't set him off.",
        "overview": "Ex-hitman John Wick comes out of retirement to track down the gangsters that took everything from him. With New York City as his bullet-riddled playground, Wick embarks on a merciless rampage.",
        "release_date": "2014-10-22",
        "release_year": 2014,
        "runtime": 101,
        "vote_average": 7.4,
        "vote_count": 18700,
        "popularity": 95.0,
        "genres": ["Action", "Thriller"],
        "director": "Chad Stahelski",
        "cast": ["Keanu Reeves", "Michael Nyqvist", "Alfie Allen", "Willem Dafoe", "Ian McShane"],
        "keywords": ["assassin", "revenge", "puppy", "underworld", "continental hotel", "gun fu", "bounty"],
        "poster_path": "https://image.tmdb.org/t/p/w500/fZPSd91yGE9fCcCe6OoQr6E3Bev.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/7XOi9WvR4oX7rWcQh5R0sT1oP7g.jpg",
        "imdb_rating": 7.4,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=John+Wick"},
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=John+Wick"}
                ]
            }
        }
    },
    {
        "id": 530915,
        "title": "1917",
        "original_title": "1917",
        "tagline": "Time is the enemy.",
        "overview": "At the height of the First World War, two young British soldiers must deliver a message deep in enemy territory that will stop 1,600 men, and one of the soldier's brothers, from walking straight into a deadly trap.",
        "release_date": "2019-12-25",
        "release_year": 2019,
        "runtime": 119,
        "vote_average": 7.9,
        "vote_count": 12100,
        "popularity": 76.0,
        "genres": ["War", "Action", "Drama"],
        "director": "Sam Mendes",
        "cast": ["George MacKay", "Dean-Charles Chapman", "Mark Strong", "Colin Firth", "Benedict Cumberbatch"],
        "keywords": ["world war i", "trench warfare", "one shot continuous", "mission against time", "no mans land"],
        "poster_path": "https://image.tmdb.org/t/p/w500/iZf0KyrE25z1sage4SYFLCCrMi9.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/cqa3hatHlhFikvl7ybT2m97UC08.jpg",
        "imdb_rating": 8.2,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "SonyLIV", "logo": "https://image.tmdb.org/t/p/original/7rw3L812b9p0M9Z6u9c7m42b827.jpg", "type": "Subscription", "url": "https://www.sonyliv.com/movies/1917-1000057288"}
                ]
            }
        }
    },
    {
        "id": 98,
        "title": "Gladiator",
        "original_title": "Gladiator",
        "tagline": "A hero will rise.",
        "overview": "In the year 180, the death of emperor Marcus Aurelius throws the Roman Empire into turmoil. Maximus, one of the Roman army's most capable and trusted generals and a key advisor to the emperor, is betrayed and condemned to death by Commodus, the emperor's corrupt son.",
        "release_date": "2000-05-01",
        "release_year": 2000,
        "runtime": 155,
        "vote_average": 8.2,
        "vote_count": 18400,
        "popularity": 88.0,
        "genres": ["Action", "Drama", "Adventure"],
        "director": "Ridley Scott",
        "cast": ["Russell Crowe", "Joaquin Phoenix", "Connie Nielsen", "Oliver Reed", "Richard Harris"],
        "keywords": ["roman empire", "colosseum", "gladiator", "revenge", "general", "emperor commodus"],
        "poster_path": "https://image.tmdb.org/t/p/w500/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/4HodYYKEIsGOdinkGi2Ucz6X9i0.jpg",
        "imdb_rating": 8.5,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Netflix", "logo": "https://image.tmdb.org/t/p/original/9A1JSVmSxsya9Wi1egD6k6CGYg1.jpg", "type": "Subscription", "url": "https://www.netflix.com/title/60000929"},
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=Gladiator"}
                ]
            }
        }
    },
    {
        "id": 49026,
        "title": "The Dark Knight Rises",
        "original_title": "The Dark Knight Rises",
        "tagline": "A fire will rise.",
        "overview": "Following the death of District Attorney Harvey Dent, Batman assumes responsibility for Dent's crimes to protect the late attorney's reputation and is subsequently hunted by the Gotham City Police Department. Eight years later, Batman encounters the mysterious Selina Kyle and the villainous Bane, a new terrorist leader who overwhelms Gotham's finest.",
        "release_date": "2012-07-16",
        "release_year": 2012,
        "runtime": 165,
        "vote_average": 7.8,
        "vote_count": 22100,
        "popularity": 85.0,
        "genres": ["Action", "Crime", "Drama", "Thriller"],
        "director": "Christopher Nolan",
        "cast": ["Christian Bale", "Tom Hardy", "Anne Hathaway", "Gary Oldman", "Joseph Gordon-Levitt"],
        "keywords": ["batman", "bane", "catwoman", "gotham siege", "revolution", "underground prison"],
        "poster_path": "https://image.tmdb.org/t/p/w500/hrJ0Q4T8j3QW7vjWvKq1bW5lY0x.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/3bgtU24g3nS5x6P0yQf7cZ9W5uA.jpg",
        "imdb_rating": 8.4,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=The+Dark+Knight+Rises"}
                ]
            }
        }
    },
    {
        "id": 539,
        "title": "Psycho",
        "original_title": "Psycho",
        "tagline": "The master of suspense invites you to a new shocker.",
        "overview": "When fugitive real estate clerk Marion Crane arrives at the remote Bates Motel after embezzling money, she encounters Norman Bates, a polite but anxious young proprietor under the domineering thumb of his mother.",
        "release_date": "1960-06-22",
        "release_year": 1960,
        "runtime": 109,
        "vote_average": 8.4,
        "vote_count": 10100,
        "popularity": 58.0,
        "genres": ["Horror", "Thriller", "Mystery"],
        "director": "Alfred Hitchcock",
        "cast": ["Anthony Perkins", "Janet Leigh", "Vera Miles", "John Gavin", "Martin Balsam"],
        "keywords": ["bates motel", "shower scene", "split personality", "embezzlement", "classic horror", "suspense"],
        "poster_path": "https://image.tmdb.org/t/p/w500/yz4555A22u7b85gQ0Jt6xH1Y3nK.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/suaEOtk1N1sgg2MTM7oZd2cfVp3.jpg",
        "imdb_rating": 8.5,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=Psycho"}
                ]
            }
        }
    },
    {
        "id": 429,
        "title": "The Good, the Bad and the Ugly",
        "original_title": "Il buono, il brutto, il cattivo",
        "tagline": "For three men the Civil War wasn't about love or hate. It was about gold.",
        "overview": "While the Civil War rages between the Union and a Confederate states, three men – a quiet loner, a ruthless hitman and a Mexican bandit – scour the American Southwest in search of a strongbox containing $200,000 in stolen Confederate gold.",
        "release_date": "1966-12-23",
        "release_year": 1966,
        "runtime": 161,
        "vote_average": 8.5,
        "vote_count": 8300,
        "popularity": 66.0,
        "genres": ["Western"],
        "director": "Sergio Leone",
        "cast": ["Clint Eastwood", "Eli Wallach", "Lee Van Cleef", "Aldo Giuffrè"],
        "keywords": ["spaghetti western", "civil war", "gold treasure", "mexican standoff", "cemetery shootout"],
        "poster_path": "https://image.tmdb.org/t/p/w500/bX2vxqn3Y0pGbsvCjW5z1gT9b4k.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/eoCSp75lxnDc6umq9Q5fsQI8BXb.jpg",
        "imdb_rating": 8.8,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=The+Good+the+Bad+and+the+Ugly"}
                ]
            }
        }
    },
    {
        "id": 19995,
        "title": "Avatar",
        "original_title": "Avatar",
        "tagline": "Enter the world of Pandora.",
        "overview": "In the 22nd century, a paraplegic Marine is dispatched to the moon Pandora on a unique mission, but becomes torn between following orders and protecting an alien civilization.",
        "release_date": "2009-12-15",
        "release_year": 2009,
        "runtime": 162,
        "vote_average": 7.6,
        "vote_count": 31400,
        "popularity": 138.0,
        "genres": ["Action", "Adventure", "Fantasy", "Science Fiction"],
        "director": "James Cameron",
        "cast": ["Sam Worthington", "Zoe Saldana", "Sigourney Weaver", "Stephen Lang", "Michelle Rodriguez"],
        "keywords": ["pandora", "navi", "avatar", "bioluminescence", "unobtainium", "eco defense"],
        "poster_path": "https://image.tmdb.org/t/p/w500/kyeqWdyUXW608qlYkRqosgbbJyK.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/vL5LR6WdxWPquCcAc446aeQqRp1.jpg",
        "imdb_rating": 7.9,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/movies/avatar/1260013917"}
                ]
            }
        }
    },
    {
        "id": 76600,
        "title": "Avatar: The Way of Water",
        "original_title": "Avatar: The Way of Water",
        "tagline": "Return to Pandora.",
        "overview": "Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
        "release_date": "2022-12-14",
        "release_year": 2022,
        "runtime": 192,
        "vote_average": 7.6,
        "vote_count": 11200,
        "popularity": 120.0,
        "genres": ["Science Fiction", "Adventure", "Action"],
        "director": "James Cameron",
        "cast": ["Sam Worthington", "Zoe Saldana", "Sigourney Weaver", "Stephen Lang", "Kate Winslet"],
        "keywords": ["ocean", "pandora", "reef clan", "family bond", "marine creatures", "whales"],
        "poster_path": "https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/ovM06PdF3M8wxmn0Keem6qR0p2k.jpg",
        "imdb_rating": 7.6,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/movies/avatar-the-way-of-water/1260143615"}
                ]
            }
        }
    },
    {
        "id": 597,
        "title": "Titanic",
        "original_title": "Titanic",
        "tagline": "Nothing on Earth could come between them.",
        "overview": "101-year-old Rose DeWitt Bukater tells the story of her life aboard the Titanic, 84 years later. A young Rose boards the ship with her mother and fiancé. Meanwhile, Jack Dawson and Fabrizio De Rossi win third-class tickets aboard the ship. The story tells of the mutual love they develop for each other and the tragic fate of the unsinkable ship.",
        "release_date": "1997-11-18",
        "release_year": 1997,
        "runtime": 194,
        "vote_average": 7.9,
        "vote_count": 24900,
        "popularity": 118.0,
        "genres": ["Drama", "Romance"],
        "director": "James Cameron",
        "cast": ["Leonardo DiCaprio", "Kate Winslet", "Billy Zane", "Kathy Bates", "Frances Fisher"],
        "keywords": ["shipwreck", "iceberg", "class divide", "romance", "tragic love", "heart of the ocean"],
        "poster_path": "https://image.tmdb.org/t/p/w500/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/yDHYTfA3R0jFYba16jBB1ef8oIt.jpg",
        "imdb_rating": 7.9,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/movies/titanic/1770001166"}
                ]
            }
        }
    },
    {
        "id": 508442,
        "title": "Soul",
        "original_title": "Soul",
        "tagline": "Is all this living really worth dying for?",
        "overview": "Joe Gardner is a middle school teacher with a love for jazz music. After a successful gig at the Half Note Club, he suddenly gets into an accident that separates his soul from his body and is transported to the You Seminar, where souls develop personal passions before being sent to newborn children.",
        "release_date": "2020-12-25",
        "release_year": 2020,
        "runtime": 100,
        "vote_average": 8.1,
        "vote_count": 10200,
        "popularity": 70.0,
        "genres": ["Animation", "Family", "Comedy", "Fantasy", "Music"],
        "director": "Pete Docter",
        "cast": ["Jamie Foxx", "Tina Fey", "Graham Norton", "Rachel House", "Alice Braga"],
        "keywords": ["jazz piano", "afterlife", "existential purpose", "passion vs spark", "new york city"],
        "poster_path": "https://image.tmdb.org/t/p/w500/hm58Jw4Lw8OIYECBhNTdwSV4Cje.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/kf456ZqeC45XTvo6W9pW5oE3498.jpg",
        "imdb_rating": 8.0,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/movies/soul/1260048386"}
                ]
            }
        }
    },
    {
        "id": 150540,
        "title": "Inside Out",
        "original_title": "Inside Out",
        "tagline": "Meet the little voices inside your head.",
        "overview": "Growing up can be a bumpy road, and it's no exception for Riley, who is uprooted from her Midwest life when her father starts a new job in San Francisco. Riley's guiding emotions— Joy, Fear, Anger, Disgust and Sadness—live in Headquarters, the control centre inside Riley's mind, where they help advise her through everyday life.",
        "release_date": "2015-06-09",
        "release_year": 2015,
        "runtime": 95,
        "vote_average": 7.9,
        "vote_count": 20100,
        "popularity": 80.0,
        "genres": ["Animation", "Family", "Adventure", "Drama", "Comedy"],
        "director": "Pete Docter",
        "cast": ["Amy Poehler", "Phyllis Smith", "Richard Kind", "Bill Hader", "Lewis Black", "Mindy Kaling"],
        "keywords": ["emotions", "memory islands", "growing up", "san francisco", "core memories", "sadness and joy"],
        "poster_path": "https://image.tmdb.org/t/p/w500/lRHE0vzf3oYJckQ5vsy5xe0788P.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/apR5WbE5o6u6GZf3sM3Gg3qA0pT.jpg",
        "imdb_rating": 8.1,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/movies/inside-out/1260005562"}
                ]
            }
        }
    },
    {
        "id": 1022789,
        "title": "Inside Out 2",
        "original_title": "Inside Out 2",
        "tagline": "Make room for new emotions.",
        "overview": "Teenager Riley's mind headquarters is undergoing a sudden demolition to make room for something entirely unexpected: new Emotions! Joy, Sadness, Anger, Fear and Disgust aren't sure how to feel when Anxiety shows up with Envy, Ennui, and Embarrassment.",
        "release_date": "2024-06-11",
        "release_year": 2024,
        "runtime": 96,
        "vote_average": 7.6,
        "vote_count": 5200,
        "popularity": 175.0,
        "genres": ["Animation", "Family", "Adventure", "Comedy"],
        "director": "Kelsey Mann",
        "cast": ["Amy Poehler", "Maya Hawke", "Kensington Tallman", "Liza Lapira", "Tony Hale"],
        "keywords": ["anxiety", "puberty", "hockey camp", "teenage emotions", "identity"],
        "poster_path": "https://image.tmdb.org/t/p/w500/vpnVM9B6NMmQpWeZvzLvDESb2QY.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/xg27NrXi7EgQxHQDCtl7cu00euv.jpg",
        "imdb_rating": 7.6,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/movies/inside-out-2/1271305417"}
                ]
            }
        }
    },
    {
        "id": 120467,
        "title": "The Grand Budapest Hotel",
        "original_title": "The Grand Budapest Hotel",
        "tagline": "A lavish tale of intrigue, theft and romance.",
        "overview": "The Grand Budapest Hotel tells of a legendary concierge at a famous European hotel between the wars and his friendship with a young employee who becomes his trusted protégé. The story involves the theft of a priceless Renaissance painting, the battle for an enormous family fortune and the slow and then sudden upheaval that changed Europe.",
        "release_date": "2014-02-26",
        "release_year": 2014,
        "runtime": 99,
        "vote_average": 8.0,
        "vote_count": 14100,
        "popularity": 68.0,
        "genres": ["Comedy", "Drama"],
        "director": "Wes Anderson",
        "cast": ["Ralph Fiennes", "Tony Revolori", "Adrien Brody", "Willem Dafoe", "Saoirse Ronan"],
        "keywords": ["concierge", "renaissance painting", "pastry", "pastel aesthetics", "symmetry", "hotel"],
        "poster_path": "https://image.tmdb.org/t/p/w500/eWdyYQreja6JGCzqHWX9ne3rNfg.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/vNswU1y6z581zUeP8P971kL3sZ9.jpg",
        "imdb_rating": 8.1,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=The+Grand+Budapest+Hotel"}
                ]
            }
        }
    },
    {
        "id": 210577,
        "title": "Gone Girl",
        "original_title": "Gone Girl",
        "tagline": "You don't know what you've got 'til it's...",
        "overview": "With his wife's disappearance having become the focus of an intense media circus, a man sees the spotlight turned on him when it's suspected that he may not be innocent.",
        "release_date": "2014-10-01",
        "release_year": 2014,
        "runtime": 149,
        "vote_average": 7.9,
        "vote_count": 18100,
        "popularity": 77.0,
        "genres": ["Mystery", "Thriller", "Drama"],
        "director": "David Fincher",
        "cast": ["Ben Affleck", "Rosamund Pike", "Neil Patrick Harris", "Tyler Perry", "Carrie Coon"],
        "keywords": ["missing wife", "cool girl monologue", "media manipulation", "diary", "sociopath", "marriage"],
        "poster_path": "https://image.tmdb.org/t/p/w500/qymaJhucquUwjpb8oiqynMeXnID.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/t5zCBSB5x2Gomulq8vFY57Z9B9Y.jpg",
        "imdb_rating": 8.1,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=Gone+Girl"}
                ]
            }
        }
    },
    {
        "id": 1949,
        "title": "Zodiac",
        "original_title": "Zodiac",
        "tagline": "There's more than one way to lose your life to a killer.",
        "overview": "A cartoonist, a beat reporter and a pair of cops become obsessed with identifying the elusive San Francisco-area Zodiac Killer in this true-crime thriller.",
        "release_date": "2007-03-02",
        "release_year": 2007,
        "runtime": 157,
        "vote_average": 7.5,
        "vote_count": 10200,
        "popularity": 64.0,
        "genres": ["Crime", "Drama", "Mystery", "Thriller"],
        "director": "David Fincher",
        "cast": ["Jake Gyllenhaal", "Mark Ruffalo", "Robert Downey Jr.", "Anthony Edwards", "Brian Cox"],
        "keywords": ["zodiac killer", "san francisco chronicle", "ciphers", "journalism", "unsolved mystery", "investigation"],
        "poster_path": "https://image.tmdb.org/t/p/w500/6YPuq5Hskn89qgR4bZk1qL77Gz1.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/71eXk81d7R2zU1X9C48wL3zV5bC.jpg",
        "imdb_rating": 7.7,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=Zodiac"}
                ]
            }
        }
    },
    {
        "id": 531428,
        "title": "Tumbbad",
        "original_title": "तुम्बाड",
        "tagline": "A greedy family unearths an ancient cursed treasure.",
        "overview": "In the rural village of Tumbbad in 1918 Maharashtra, Vinayak Rao seeks the hidden gold of Hastar, an ancient malevolent demon forbidden from being worshipped, plunging generations into endless greed and terrifying consequences.",
        "release_date": "2018-10-12",
        "release_year": 2018,
        "runtime": 104,
        "vote_average": 8.0,
        "vote_count": 780,
        "popularity": 61.0,
        "genres": ["Horror", "Fantasy", "Drama", "Mystery"],
        "director": "Rahi Anil Barve",
        "cast": ["Sohum Shah", "Jyoti Malshe", "Anita Date", "Ronjini Chakraborty", "Deepak Damle"],
        "keywords": ["folklore", "ancient curse", "greed", "womb of goddess", "hastar", "maharashtra", "treasure"],
        "poster_path": "https://image.tmdb.org/t/p/w500/q2ZgA8bF9k6gD0h5B3bT1yZ8r2Y.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/w4zZk0d9v8P2lC1u3X9yT5m8Q0a.jpg",
        "imdb_rating": 8.2,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/detail/Tumbbad/0HL5FOP7M11H4LMR73024S"}
                ]
            }
        }
    },
    {
        "id": 534780,
        "title": "Andhadhun",
        "original_title": "Andhadhun",
        "tagline": "He couldn't see what he was getting into.",
        "overview": "A series of mysterious events change the life of a blind pianist, who now must report a murder that he never officially saw.",
        "release_date": "2018-10-05",
        "release_year": 2018,
        "runtime": 139,
        "vote_average": 7.7,
        "vote_count": 890,
        "popularity": 55.0,
        "genres": ["Crime", "Thriller", "Comedy", "Mystery"],
        "director": "Sriram Raghavan",
        "cast": ["Ayushmann Khurrana", "Tabu", "Radhika Apte", "Anil Dhawan", "Manav Vij"],
        "keywords": ["blind pianist", "witness to murder", "black comedy", "organ trafficking", "pune", "twist"],
        "poster_path": "https://image.tmdb.org/t/p/w500/dy3CzRmwLHUPjR497V4HA28m4uP.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/6Z2lP9k7d8b5T2yA1w0C8eT4o9x.jpg",
        "imdb_rating": 8.2,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Netflix", "logo": "https://image.tmdb.org/t/p/original/9A1JSVmSxsya9Wi1egD6k6CGYg1.jpg", "type": "Subscription", "url": "https://www.netflix.com/title/81039381"},
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=Andhadhun"}
                ]
            }
        }
    },
    {
        "id": 8392,
        "title": "Gangs of Wasseypur",
        "original_title": "गैंग्स ऑफ़ वासेपुर",
        "tagline": "A clash of titans spanning three generations.",
        "overview": "A clash between Sultan and Shahid Khan leads to the expulsion of Khan from Wasseypur, and ignites a deadly blood feud spanning three generations involving coal mafia, politics, and ruthless revenge.",
        "release_date": "2012-06-22",
        "release_year": 2012,
        "runtime": 321,
        "vote_average": 8.1,
        "vote_count": 680,
        "popularity": 52.0,
        "genres": ["Action", "Crime", "Drama", "Thriller"],
        "director": "Anurag Kashyap",
        "cast": ["Manoj Bajpayee", "Nawazuddin Siddiqui", "Richa Chadha", "Huma Qureshi", "Tigmanshu Dhulia", "Pankaj Tripathi"],
        "keywords": ["coal mafia", "revenge feud", "bihar", "dhanbad", "raw violence", "three generations", "classic cult"],
        "poster_path": "https://image.tmdb.org/t/p/w500/fTq7X50F0hR5c7b3C2v8t6zY1Q9.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/mFq8x0Y6v5T8b9N1c2C3u8r6o9P.jpg",
        "imdb_rating": 8.2,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Netflix", "logo": "https://image.tmdb.org/t/p/original/9A1JSVmSxsya9Wi1egD6k6CGYg1.jpg", "type": "Subscription", "url": "https://www.netflix.com/title/70242554"}
                ]
            }
        }
    },
    {
        "id": 350,
        "title": "The Devil Wears Prada",
        "original_title": "The Devil Wears Prada",
        "tagline": "Meet Andy Sachs. A million girls would kill for her job. She's not one of them.",
        "overview": "Andy, a young graduate with big dreams, lands a job at Runway magazine as an assistant to the diabolical and demanding fashion magazine editor Miranda Priestly.",
        "release_date": "2006-06-30",
        "release_year": 2006,
        "runtime": 109,
        "vote_average": 7.4,
        "vote_count": 12100,
        "popularity": 71.0,
        "genres": ["Comedy", "Drama"],
        "director": "David Frankel",
        "cast": ["Meryl Streep", "Anne Hathaway", "Emily Blunt", "Stanley Tucci", "Simon Baker"],
        "keywords": ["fashion industry", "runway", "magazine editor", "ambition", "makeover", "new york"],
        "poster_path": "https://image.tmdb.org/t/p/w500/u6QBDGUCOEM5KG50iH4zQxQ2nO.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/tU4wWl0gQv8y6pT9r0m8b6c4Z1.jpg",
        "imdb_rating": 7.0,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=The+Devil+Wears+Prada"}
                ]
            }
        }
    },
    {
        "id": 269149,
        "title": "Zootopia",
        "original_title": "Zootopia",
        "tagline": "Welcome to the urban jungle.",
        "overview": "Determined to prove herself, Officer Judy Hopps, the first bunny on Zootopia's police force, jumps at the chance to crack her first case - even if that means partnering with scam-artist fox Nick Wilde to solve the mystery.",
        "release_date": "2016-02-11",
        "release_year": 2016,
        "runtime": 108,
        "vote_average": 7.7,
        "vote_count": 16100,
        "popularity": 80.0,
        "genres": ["Animation", "Adventure", "Family", "Comedy"],
        "director": "Byron Howard",
        "cast": ["Ginnifer Goodwin", "Jason Bateman", "Idris Elba", "Jenny Slate", "J.K. Simmons"],
        "keywords": ["mammal metropolis", "police investigation", "bunny and fox", "con artist", "prejudice allegory"],
        "poster_path": "https://image.tmdb.org/t/p/w500/hlK0e0wAQ3VFGACFiZozvQh89wa.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/mh0fF0H6u6g0n1s3d7k5b8C6p9y.jpg",
        "imdb_rating": 8.0,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/movies/zootopia/1260005578"}
                ]
            }
        }
    },
    {
        "id": 808,
        "title": "Shrek",
        "original_title": "Shrek",
        "tagline": "The greatest fairy tale never told.",
        "overview": "It ain't easy bein' green -- especially if you're a likable (sorta) ogre named Shrek. On a mission to retrieve a gorgeous princess from the clutches of a fire-breathing dragon, Shrek teams up with an unlikely partner: a wisecracking donkey.",
        "release_date": "2001-05-18",
        "release_year": 2001,
        "runtime": 90,
        "vote_average": 7.7,
        "vote_count": 16500,
        "popularity": 85.0,
        "genres": ["Animation", "Comedy", "Fantasy", "Adventure", "Family"],
        "director": "Andrew Adamson",
        "cast": ["Mike Myers", "Eddie Murphy", "Cameron Diaz", "John Lithgow", "Vincent Cassel"],
        "keywords": ["ogre", "donkey", "fairy tale satire", "dragon", "swamp", "princess fiona"],
        "poster_path": "https://image.tmdb.org/t/p/w500/iB64vpL3dIObOtMZgX3RqWCPCeg.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/m9mFq0P2b9c7V5a1X9d8k6b7R0a.jpg",
        "imdb_rating": 7.9,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Netflix", "logo": "https://image.tmdb.org/t/p/original/9A1JSVmSxsya9Wi1egD6k6CGYg1.jpg", "type": "Subscription", "url": "https://www.netflix.com/title/60010940"},
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/explore?search_query=Shrek"}
                ]
            }
        }
    },
    {
        "id": 140607,
        "title": "Star Wars: The Force Awakens",
        "original_title": "Star Wars: The Force Awakens",
        "tagline": "Every generation has a story.",
        "overview": "Thirty years after defeating the Galactic Empire, Han Solo and his allies face a new threat from the evil Kylo Ren and his army of Stormtroopers, while a young scavenger named Rey discovers her connection to the Force.",
        "release_date": "2015-12-15",
        "release_year": 2015,
        "runtime": 136,
        "vote_average": 7.3,
        "vote_count": 19400,
        "popularity": 78.0,
        "genres": ["Action", "Adventure", "Science Fiction", "Fantasy"],
        "director": "J.J. Abrams",
        "cast": ["Daisy Ridley", "John Boyega", "Adam Driver", "Harrison Ford", "Carrie Fisher", "Oscar Isaac"],
        "keywords": ["star wars", "kylo ren", "bb-8", "first order", "millennium falcon", "lightsaber"],
        "poster_path": "https://image.tmdb.org/t/p/w500/wqnLdw3cLLvo9ES7GdXRsvgoo2e.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/k68nPLbIST6NP96JmTxmZijEvCA.jpg",
        "imdb_rating": 7.8,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/movies/star-wars-the-force-awakens/1260018449"}
                ]
            }
        }
    },
    {
        "id": 8587,
        "title": "The Lion King",
        "original_title": "The Lion King",
        "tagline": "Life's greatest adventure is finding your place in the Circle of Life.",
        "overview": "A young lion prince is cast out of his pride by his cruel uncle, who claims he killed his father. While the uncle rules with an iron paw, the prince grows up beyond the Savannah, living by a philosophy: No worries for the rest of your days. But when his past comes to haunt him, the young prince must decide his fate: Will he remain an outcast, or face his demon and become what he needs to be?",
        "release_date": "1994-06-23",
        "release_year": 1994,
        "runtime": 89,
        "vote_average": 8.3,
        "vote_count": 18200,
        "popularity": 95.0,
        "genres": ["Animation", "Family", "Drama"],
        "director": "Roger Allers",
        "cast": ["Matthew Broderick", "Jeremy Irons", "James Earl Jones", "Nathan Lane", "Ernie Sabella"],
        "keywords": ["circle of life", "pride rock", "lion cub", "hakuna matata", "uncle scar", "savannah"],
        "poster_path": "https://image.tmdb.org/t/p/w500/sKCr78MXSLixwmZ8DyJLrpMsd15.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/w7Bsx6q5f0d9N3k1q6B4u2v8R0p.jpg",
        "imdb_rating": 8.5,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/movies/the-lion-king/1260005567"}
                ]
            }
        }
    },
    {
        "id": 772,
        "title": "Home Alone",
        "original_title": "Home Alone",
        "tagline": "A family comedy without the family.",
        "overview": "Eight-year-old Kevin McCallister makes the most of the situation after his family accidentally leaves him behind when they take a Christmas vacation to Paris. But when a pair of bumbling burglars target his home, Kevin must defend the house with an array of homemade booby traps.",
        "release_date": "1990-11-16",
        "release_year": 1990,
        "runtime": 103,
        "vote_average": 7.4,
        "vote_count": 11400,
        "popularity": 82.0,
        "genres": ["Comedy", "Family"],
        "director": "Chris Columbus",
        "cast": ["Macaulay Culkin", "Joe Pesci", "Daniel Stern", "John Heard", "Catherine O'Hara"],
        "keywords": ["christmas", "booby traps", "burglars", "left alone", "family holiday", "chicago suburbs"],
        "poster_path": "https://image.tmdb.org/t/p/w500/9wSbe4CwObACCQvaUVxnnzyxq9f.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/4HodYYKEIsGOdinkGi2Ucz6X9i0.jpg",
        "imdb_rating": 7.7,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/movies/home-alone/1260005560"}
                ]
            }
        }
    },
    {
        "id": 1891,
        "title": "The Empire Strikes Back",
        "original_title": "The Empire Strikes Back",
        "tagline": "The Adventure Continues...",
        "overview": "The epic saga continues as Luke Skywalker, in hopes of defeating the evil Galactic Empire, learns the ways of the Jedi from aging master Yoda. But Darth Vader is more determined than ever to capture Luke.",
        "release_date": "1980-05-20",
        "release_year": 1980,
        "runtime": 124,
        "vote_average": 8.4,
        "vote_count": 16900,
        "popularity": 76.0,
        "genres": ["Adventure", "Action", "Science Fiction"],
        "director": "Irvin Kershner",
        "cast": ["Mark Hamill", "Harrison Ford", "Carrie Fisher", "Billy Dee Williams", "Anthony Daniels"],
        "keywords": ["i am your father", "yoda", "cloud city", "hoth", "jedi training", "boba fett"],
        "poster_path": "https://image.tmdb.org/t/p/w500/nNAeTmF4CMbU0jwq8KnrZ9U0c45.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/4HodYYKEIsGOdinkGi2Ucz6X9i0.jpg",
        "imdb_rating": 8.7,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "JioHotstar", "logo": "https://image.tmdb.org/t/p/original/ebSnXb5T5KxGg02zYpT9jU3lZ9y.jpg", "type": "Subscription", "url": "https://www.hotstar.com/in/movies/star-wars-the-empire-strikes-back/1260018444"}
                ]
            }
        }
    },
    {
        "id": 500,
        "title": "Reservoir Dogs",
        "original_title": "Reservoir Dogs",
        "tagline": "Every dog has his day.",
        "overview": "A botched diamond heist leads to bloody chaos when surviving criminals suspect one of them is an undercover police informant.",
        "release_date": "1992-09-02",
        "release_year": 1992,
        "runtime": 99,
        "vote_average": 8.1,
        "vote_count": 14200,
        "popularity": 64.0,
        "genres": ["Crime", "Thriller"],
        "director": "Quentin Tarantino",
        "cast": ["Harvey Keitel", "Tim Roth", "Michael Madsen", "Chris Penn", "Steve Buscemi"],
        "keywords": ["diamond heist", "warehouse", "undercover cop", "mexican standoff", "ear torture"],
        "poster_path": "https://image.tmdb.org/t/p/w500/xi8Iu6qyTfyZVD377SVv02k98.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/7XOi9WvR4oX7rWcQh5R0sT1oP7g.jpg",
        "imdb_rating": 8.3,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=Reservoir+Dogs"}
                ]
            }
        }
    },
    {
        "id": 274,
        "title": "The Silence of the Lambs",
        "original_title": "The Silence of the Lambs",
        "tagline": "To enter the mind of a killer she must challenge the mind of a madman.",
        "overview": "Clarice Starling, a top FBI trainee, is assigned by her supervisor to interview Dr. Hannibal Lecter, an incarcerated psychiatrist turned cannibal serial killer, to gain insights into tracking another serial killer known as Buffalo Bill.",
        "release_date": "1991-02-14",
        "release_year": 1991,
        "runtime": 118,
        "vote_average": 8.3,
        "vote_count": 16400,
        "popularity": 79.0,
        "genres": ["Crime", "Drama", "Thriller"],
        "director": "Jonathan Demme",
        "cast": ["Jodie Foster", "Anthony Hopkins", "Scott Glenn", "Ted Levine", "Anthony Heald"],
        "keywords": ["hannibal lecter", "fbi agent", "serial killer", "cannibalism", "psychological mind game", "quid pro quo"],
        "poster_path": "https://image.tmdb.org/t/p/w500/uS9m8OBk1A8eM9I042v8vGgA3X5.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/suaEOtk1N1sgg2MTM7oZd2cfVp3.jpg",
        "imdb_rating": 8.6,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=The+Silence+of+the+Lambs"}
                ]
            }
        }
    },
    {
        "id": 1124,
        "title": "The Prestige",
        "original_title": "The Prestige",
        "tagline": "Are you watching closely?",
        "overview": "A mysterious story of two magicians whose intense rivalry leads them on a life-long battle for supremacy -- full of obsession, deceit and jealousy with dangerous and deadly consequences.",
        "release_date": "2006-10-19",
        "release_year": 2006,
        "runtime": 130,
        "vote_average": 8.2,
        "vote_count": 16100,
        "popularity": 79.0,
        "genres": ["Drama", "Mystery", "Science Fiction"],
        "director": "Christopher Nolan",
        "cast": ["Hugh Jackman", "Christian Bale", "Michael Caine", "Scarlett Johansson", "David Bowie"],
        "keywords": ["magicians", "rivalry", "teleportation", "nikola tesla", "stage illusion", "sacrifice"],
        "poster_path": "https://image.tmdb.org/t/p/w500/tRNlZbgNCNOpLpbPEz5L8G8A0JN.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/8ZTVqvKDQ8emSGUEMjsS4yHAwrp.jpg",
        "imdb_rating": 8.5,
        "watch_providers": {
            "IN": {
                "flatrate": [
                    {"name": "Amazon Prime Video", "logo": "https://image.tmdb.org/t/p/original/emthp39XA2zhRMT2XOpGACTn3m6.jpg", "type": "Subscription", "url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase=The+Prestige"}
                ]
            }
        }
    }
]

def main():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, "movies.json")
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(MOVIES, f, indent=2, ensure_ascii=False)
        
    print(f"Generated {len(MOVIES)} curated movies at: {output_path}")

if __name__ == "__main__":
    main()
