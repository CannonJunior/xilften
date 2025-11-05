"""
TMDB API Client Service.

Wrapper around The Movie Database (TMDB) API for fetching media metadata.
"""

import httpx
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


class TMDBClient:
    """
    TMDB API client with rate limiting and caching.
    """

    def __init__(self):
        """Initialize TMDB client."""
        self.base_url = settings.tmdb_base_url
        self.image_base_url = settings.tmdb_image_base_url
        self.api_key = settings.tmdb_api_key
        self.rate_limit = settings.tmdb_rate_limit
        self.request_count = 0
        self.rate_limit_reset = datetime.now()

        # Simple in-memory cache
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self._cache_ttl = timedelta(hours=1)

    async def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to TMDB API with rate limiting.

        Args:
            endpoint (str): API endpoint
            params (dict): Query parameters

        Returns:
            dict: JSON response

        Raises:
            HTTPException: If request fails
        """
        # Check cache first
        cache_key = f"{endpoint}:{str(params)}"
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if datetime.now() - cached_time < self._cache_ttl:
                logger.debug(f"Cache hit for {endpoint}")
                return cached_data

        # Check rate limit
        await self._check_rate_limit()

        # Prepare request
        if params is None:
            params = {}

        # Add API key to params
        params["api_key"] = self.api_key

        url = f"{self.base_url}{endpoint}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()

                # Cache response
                self._cache[cache_key] = (data, datetime.now())

                # Increment request count
                self.request_count += 1

                return data

        except httpx.HTTPStatusError as e:
            logger.error(f"TMDB API error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"TMDB request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    async def _check_rate_limit(self):
        """
        Check and enforce rate limiting (40 requests per 10 seconds).
        """
        now = datetime.now()

        # Reset counter if 10 seconds have passed
        if now - self.rate_limit_reset > timedelta(seconds=10):
            self.request_count = 0
            self.rate_limit_reset = now

        # If we've hit the limit, wait
        if self.request_count >= self.rate_limit:
            wait_time = 10 - (now - self.rate_limit_reset).total_seconds()
            if wait_time > 0:
                logger.warning(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
                self.request_count = 0
                self.rate_limit_reset = datetime.now()

    async def get_movie(self, movie_id: int) -> Dict[str, Any]:
        """
        Get movie details by TMDB ID.

        Args:
            movie_id (int): TMDB movie ID

        Returns:
            dict: Movie details
        """
        endpoint = f"/movie/{movie_id}"
        params = {"append_to_response": "credits,videos,release_dates"}
        return await self._make_request(endpoint, params)

    async def get_tv_show(self, tv_id: int) -> Dict[str, Any]:
        """
        Get TV show details by TMDB ID.

        Args:
            tv_id (int): TMDB TV show ID

        Returns:
            dict: TV show details
        """
        endpoint = f"/tv/{tv_id}"
        params = {"append_to_response": "credits,videos,content_ratings"}
        return await self._make_request(endpoint, params)

    async def search_movie(self, query: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for movies.

        Args:
            query (str): Search query
            year (int): Optional release year filter

        Returns:
            list: List of movie results
        """
        endpoint = "/search/movie"
        params = {"query": query}

        if year:
            params["year"] = year

        response = await self._make_request(endpoint, params)
        return response.get("results", [])

    async def search_tv(self, query: str, first_air_date_year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for TV shows.

        Args:
            query (str): Search query
            first_air_date_year (int): Optional first air date year

        Returns:
            list: List of TV show results
        """
        endpoint = "/search/tv"
        params = {"query": query}

        if first_air_date_year:
            params["first_air_date_year"] = first_air_date_year

        response = await self._make_request(endpoint, params)
        return response.get("results", [])

    async def get_genres(self, media_type: str = "movie") -> List[Dict[str, Any]]:
        """
        Get list of official TMDB genres.

        Args:
            media_type (str): 'movie' or 'tv'

        Returns:
            list: List of genres
        """
        endpoint = f"/genre/{media_type}/list"
        response = await self._make_request(endpoint)
        return response.get("genres", [])

    async def get_person(self, person_id: int) -> Dict[str, Any]:
        """
        Get person details by TMDB ID.

        Args:
            person_id (int): TMDB person ID

        Returns:
            dict: Person details
        """
        endpoint = f"/person/{person_id}"
        params = {"append_to_response": "combined_credits"}
        return await self._make_request(endpoint, params)

    async def discover_movies(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Discover movies with filters.

        Args:
            filters (dict): Filter parameters (genre, year, rating, etc.)

        Returns:
            list: List of movies
        """
        endpoint = "/discover/movie"
        params = filters or {}
        params.setdefault("sort_by", "popularity.desc")

        response = await self._make_request(endpoint, params)
        return response.get("results", [])

    async def discover_tv(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Discover TV shows with filters.

        Args:
            filters (dict): Filter parameters

        Returns:
            list: List of TV shows
        """
        endpoint = "/discover/tv"
        params = filters or {}
        params.setdefault("sort_by", "popularity.desc")

        response = await self._make_request(endpoint, params)
        return response.get("results", [])

    def get_image_url(self, path: str, size: str = "w500") -> str:
        """
        Get full TMDB image URL.

        Args:
            path (str): Image path from TMDB
            size (str): Image size (w92, w154, w185, w342, w500, w780, original)

        Returns:
            str: Full image URL
        """
        if not path:
            return ""
        return f"{self.image_base_url}/{size}{path}"

    def transform_movie_to_media(self, tmdb_movie: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform TMDB movie data to our media format.

        Args:
            tmdb_movie (dict): TMDB movie data

        Returns:
            dict: Media data in our format
        """
        # Extract release date
        release_date = None
        if tmdb_movie.get("release_date"):
            try:
                release_date = datetime.strptime(
                    tmdb_movie["release_date"], "%Y-%m-%d"
                ).date()
            except ValueError:
                pass

        # Extract maturity rating
        maturity_rating = None
        if "release_dates" in tmdb_movie:
            results = tmdb_movie["release_dates"].get("results", [])
            for result in results:
                if result.get("iso_3166_1") == "US":
                    release_dates = result.get("release_dates", [])
                    if release_dates:
                        maturity_rating = release_dates[0].get("certification")
                    break

        # Extract genres
        genres = []
        if tmdb_movie.get("genres"):
            genres = [genre["name"].lower().replace(" ", "-") for genre in tmdb_movie["genres"]]

        return {
            "tmdb_id": tmdb_movie.get("id"),
            "imdb_id": tmdb_movie.get("imdb_id"),
            "title": tmdb_movie.get("title"),
            "original_title": tmdb_movie.get("original_title"),
            "media_type": "movie",
            "release_date": release_date,
            "runtime": tmdb_movie.get("runtime"),
            "overview": tmdb_movie.get("overview"),
            "tagline": tmdb_movie.get("tagline"),
            "tmdb_rating": tmdb_movie.get("vote_average"),
            "tmdb_vote_count": tmdb_movie.get("vote_count"),
            "popularity_score": tmdb_movie.get("popularity"),
            "maturity_rating": maturity_rating,
            "original_language": tmdb_movie.get("original_language"),
            "production_countries": [c["iso_3166_1"] for c in tmdb_movie.get("production_countries", [])],
            "spoken_languages": [l["iso_639_1"] for l in tmdb_movie.get("spoken_languages", [])],
            "poster_path": tmdb_movie.get("poster_path"),
            "backdrop_path": tmdb_movie.get("backdrop_path"),
            "status": tmdb_movie.get("status"),
            "genres": genres,
        }

    def transform_tv_to_media(self, tmdb_tv: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform TMDB TV show data to our media format.

        Args:
            tmdb_tv (dict): TMDB TV show data

        Returns:
            dict: Media data in our format
        """
        # Extract first air date
        first_air_date = None
        if tmdb_tv.get("first_air_date"):
            try:
                first_air_date = datetime.strptime(
                    tmdb_tv["first_air_date"], "%Y-%m-%d"
                ).date()
            except ValueError:
                pass

        # Extract maturity rating
        maturity_rating = None
        if "content_ratings" in tmdb_tv:
            results = tmdb_tv["content_ratings"].get("results", [])
            for result in results:
                if result.get("iso_3166_1") == "US":
                    maturity_rating = result.get("rating")
                    break

        # Calculate average episode runtime
        runtime = None
        if tmdb_tv.get("episode_run_time"):
            runtime = int(sum(tmdb_tv["episode_run_time"]) / len(tmdb_tv["episode_run_time"]))

        # Extract genres
        genres = []
        if tmdb_tv.get("genres"):
            genres = [genre["name"].lower().replace(" ", "-") for genre in tmdb_tv["genres"]]

        return {
            "tmdb_id": tmdb_tv.get("id"),
            "title": tmdb_tv.get("name"),
            "original_title": tmdb_tv.get("original_name"),
            "media_type": "tv",
            "release_date": first_air_date,
            "runtime": runtime,
            "overview": tmdb_tv.get("overview"),
            "tagline": tmdb_tv.get("tagline"),
            "tmdb_rating": tmdb_tv.get("vote_average"),
            "tmdb_vote_count": tmdb_tv.get("vote_count"),
            "popularity_score": tmdb_tv.get("popularity"),
            "maturity_rating": maturity_rating,
            "original_language": tmdb_tv.get("original_language"),
            "production_countries": [c["iso_3166_1"] for c in tmdb_tv.get("production_countries", [])],
            "spoken_languages": [l["iso_639_1"] for l in tmdb_tv.get("spoken_languages", [])],
            "poster_path": tmdb_tv.get("poster_path"),
            "backdrop_path": tmdb_tv.get("backdrop_path"),
            "status": tmdb_tv.get("status"),
            "genres": genres,
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        Check TMDB API health and configuration.

        Returns:
            dict: Health check status with details
        """
        if not self.api_key or self.api_key == "your_tmdb_api_key_here":
            return {
                "status": "not_configured",
                "message": "TMDB API key not configured. Please set TMDB_API_KEY in .env file.",
                "healthy": False,
            }

        try:
            # Try to fetch a simple configuration endpoint
            endpoint = "/configuration"
            await self._make_request(endpoint)

            return {
                "status": "healthy",
                "message": "TMDB API is accessible and configured correctly",
                "healthy": True,
                "api_version": "3",
                "base_url": self.base_url,
            }

        except Exception as e:
            logger.error(f"TMDB health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"TMDB API is not accessible: {str(e)}",
                "healthy": False,
            }


# Global TMDB client instance
tmdb_client = TMDBClient()
