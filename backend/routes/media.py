"""
Media API Routes.

CRUD operations and search for media content.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID
import logging

from backend.models.media import (
    MediaCreate,
    MediaUpdate,
    MediaResponse,
    MediaListResponse,
    MediaFilters,
    TMDBFetchRequest,
)
from backend.services.tmdb_client import tmdb_client
from backend.services.media_service import media_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=dict)
async def get_media_list(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    media_type: Optional[str] = Query(None, description="Filter by media type"),
    genre: Optional[str] = Query(None, description="Filter by genre slug"),
    min_rating: Optional[float] = Query(None, ge=0.0, le=10.0),
    max_rating: Optional[float] = Query(None, ge=0.0, le=10.0),
    year_from: Optional[int] = Query(None, ge=1900, le=2100),
    year_to: Optional[int] = Query(None, ge=1900, le=2100),
    maturity_rating: Optional[str] = Query(None),
    sort_by: str = Query("title", description="Sort field"),
    sort_order: str = Query("asc", description="Sort order: asc or desc"),
    search: Optional[str] = Query(None, description="Search query"),
):
    """
    Get paginated list of media with optional filtering.

    Args:
        page: Page number
        page_size: Items per page
        media_type: Filter by type
        genre: Filter by genre
        min_rating: Minimum rating
        max_rating: Maximum rating
        year_from: From year
        year_to: To year
        maturity_rating: Maturity rating filter
        sort_by: Sort field
        sort_order: Sort order
        search: Search query

    Returns:
        dict: Paginated media list with success status
    """
    try:
        logger.info(f"Fetching media list - page: {page}, filters applied")

        # Build filters
        filters = MediaFilters(
            media_type=media_type,
            genre=genre,
            min_rating=min_rating,
            max_rating=max_rating,
            year_from=year_from,
            year_to=year_to,
            maturity_rating=maturity_rating,
            sort_by=sort_by,
            sort_order=sort_order
        )

        # Get media from database
        result = media_service.get_all_media(page=page, page_size=page_size, filters=filters)

        return {
            "success": True,
            "data": result,
        }

    except Exception as e:
        logger.error(f"Error fetching media list: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=dict)
async def search_media(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    Search media by title and overview.

    Args:
        q: Search query
        page: Page number
        page_size: Items per page

    Returns:
        dict: Search results with success status
    """
    try:
        logger.info(f"Searching media: {q}")

        result = media_service.search_media(query=q, page=page, page_size=page_size)

        return {
            "success": True,
            "data": result,
        }

    except Exception as e:
        logger.error(f"Error searching media: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{media_id}", response_model=dict)
async def get_media_by_id(media_id: UUID):
    """
    Get media details by ID.

    Args:
        media_id: Media UUID

    Returns:
        dict: Media details with success status

    Raises:
        HTTPException: If media not found
    """
    try:
        logger.info(f"Fetching media by ID: {media_id}")

        media = media_service.get_media_by_id(media_id)

        if not media:
            raise HTTPException(status_code=404, detail="Media not found")

        return {
            "success": True,
            "data": media,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching media: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=dict, status_code=201)
async def create_media(media_data: MediaCreate):
    """
    Create new media entry.

    Args:
        media_data: Media creation data

    Returns:
        dict: Created media with success status
    """
    try:
        logger.info(f"Creating new media: {media_data.title}")

        media = media_service.create_media(media_data)

        return {
            "success": True,
            "data": media,
            "message": "Media created successfully",
        }

    except Exception as e:
        logger.error(f"Error creating media: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{media_id}", response_model=dict)
async def update_media(media_id: UUID, updates: MediaUpdate):
    """
    Update existing media.

    Args:
        media_id: Media UUID
        updates: Fields to update

    Returns:
        dict: Updated media with success status

    Raises:
        HTTPException: If media not found
    """
    try:
        logger.info(f"Updating media: {media_id}")

        media = media_service.update_media(media_id, updates)

        if not media:
            raise HTTPException(status_code=404, detail="Media not found")

        return {
            "success": True,
            "data": media,
            "message": "Media updated successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating media: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{media_id}", response_model=dict)
async def delete_media(media_id: UUID):
    """
    Delete media entry.

    Args:
        media_id: Media UUID

    Returns:
        dict: Deletion confirmation with success status

    Raises:
        HTTPException: If media not found
    """
    try:
        logger.info(f"Deleting media: {media_id}")

        deleted = media_service.delete_media(media_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Media not found")

        return {
            "success": True,
            "message": "Media deleted successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting media: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch-tmdb", response_model=dict)
async def fetch_from_tmdb(request: TMDBFetchRequest):
    """
    Fetch media metadata from TMDB and create/update local entry.

    Args:
        request: TMDB fetch request with ID and type

    Returns:
        dict: Fetched/updated media with success status

    Raises:
        HTTPException: If TMDB fetch fails
    """
    try:
        logger.info(f"Fetching from TMDB: {request.media_type} ID {request.tmdb_id}")

        # Fetch from TMDB
        if request.media_type == "movie":
            tmdb_data = await tmdb_client.get_movie(request.tmdb_id)
            media_data_dict = tmdb_client.transform_movie_to_media(tmdb_data)
        elif request.media_type == "tv":
            tmdb_data = await tmdb_client.get_tv_show(request.tmdb_id)
            media_data_dict = tmdb_client.transform_tv_to_media(tmdb_data)
        else:
            raise HTTPException(status_code=400, detail="Invalid media_type")

        logger.info(f"Successfully fetched: {media_data_dict['title']}")

        # Extract genres for later association
        genres_list = media_data_dict.pop("genres", [])

        # Check if media already exists with this TMDB ID
        conn = media_service.db.get_duckdb_connection()
        existing = conn.execute(
            "SELECT id FROM media WHERE tmdb_id = ?",
            [media_data_dict["tmdb_id"]]
        ).fetchone()

        if existing:
            # Update existing media
            media_id = UUID(str(existing[0]))
            media_data = MediaUpdate(**media_data_dict)
            updated_media = media_service.update_media(media_id, media_data)

            logger.info(f"Updated existing media: {media_id}")
            message = f"Media '{updated_media['title']}' updated from TMDB"
            result_media = updated_media
        else:
            # Create new media entry
            media_data = MediaCreate(**media_data_dict)
            created_media = media_service.create_media(media_data)

            logger.info(f"Created new media: {created_media['id']}")
            message = f"Media '{created_media['title']}' created from TMDB"
            result_media = created_media

        # TODO: Map TMDB genres to our genre taxonomy and create associations
        # This will be implemented when we add genre mapping functionality

        return {
            "success": True,
            "data": result_media,
            "message": message,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching from TMDB: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch from TMDB: {str(e)}")


@router.post("/seed-sample", response_model=dict)
async def seed_sample_media():
    """
    Seed sample media data for testing the frontend.

    Returns:
        dict: Statistics about seeded data

    Note:
        This is a development/testing endpoint and should be removed in production.
    """
    try:
        import uuid
        from datetime import date
        from config.database import db_manager

        conn = db_manager.get_duckdb_connection()

        # Check if we already have media
        count = conn.execute("SELECT COUNT(*) FROM media").fetchone()[0]
        if count > 0:
            logger.info(f"📊 Media already seeded ({count} items found)")
            return {
                "success": True,
                "data": {"count": count, "newly_seeded": 0},
                "message": f"Media already exists ({count} items)",
            }

        logger.info("🎬 Seeding sample media data...")

        # Sample media data with diverse genres and types
        sample_media = [
            {"tmdb_id": 603, "imdb_id": "tt0133093", "title": "The Matrix", "original_title": "The Matrix", "media_type": "movie", "release_date": date(1999, 3, 31), "runtime": 136, "overview": "Set in the 22nd century, The Matrix tells the story of a computer hacker who joins a group of underground insurgents fighting the vast and powerful computers who now rule the earth.", "tagline": "Welcome to the Real World", "tmdb_rating": 8.2, "tmdb_vote_count": 24000, "popularity_score": 145.5, "maturity_rating": "R", "original_language": "en", "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg", "backdrop_path": "/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg", "status": "Released"},
            {"tmdb_id": 155, "imdb_id": "tt0816692", "title": "The Dark Knight", "original_title": "The Dark Knight", "media_type": "movie", "release_date": date(2008, 7, 18), "runtime": 152, "overview": "Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations.", "tagline": "Why So Serious?", "tmdb_rating": 8.5, "tmdb_vote_count": 32000, "popularity_score": 189.3, "maturity_rating": "PG-13", "original_language": "en", "poster_path": "/qJ2tW6WMUDux911r6m7haRef0WH.jpg", "backdrop_path": "/nMKdUUepR0i5zn0y1T4CsSB5chy.jpg", "status": "Released"},
            {"tmdb_id": 78, "imdb_id": "tt0083658", "title": "Blade Runner", "original_title": "Blade Runner", "media_type": "movie", "release_date": date(1982, 6, 25), "runtime": 117, "overview": "In the smog-choked dystopian Los Angeles of 2019, blade runner Rick Deckard is called out of retirement to terminate a quartet of replicants.", "tagline": "Man has made his match... now it's his problem", "tmdb_rating": 7.9, "tmdb_vote_count": 13000, "popularity_score": 98.7, "maturity_rating": "R", "original_language": "en", "poster_path": "/63N9uy8nd9j7Eog2axPQ8lbr3Wj.jpg", "backdrop_path": "/6aIb2GH98x17PqiJ5qqBwwFrDTR.jpg", "status": "Released"},
            {"tmdb_id": 13, "imdb_id": "tt0109830", "title": "Forrest Gump", "original_title": "Forrest Gump", "media_type": "movie", "release_date": date(1994, 7, 6), "runtime": 142, "overview": "A man with a low IQ has accomplished great things in his life and been present during significant historic events.", "tagline": "The world will never be the same once you've seen it through the eyes of Forrest Gump.", "tmdb_rating": 8.5, "tmdb_vote_count": 26000, "popularity_score": 156.2, "maturity_rating": "PG-13", "original_language": "en", "poster_path": "/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg", "backdrop_path": "/7c9UVPPiTPltouxRVY6N9uugaVA.jpg", "status": "Released"},
            {"tmdb_id": 550, "imdb_id": "tt0137523", "title": "Fight Club", "original_title": "Fight Club", "media_type": "movie", "release_date": date(1999, 10, 15), "runtime": 139, "overview": "A ticking-time-bomb insomniac and a slippery soap salesman channel primal male aggression into a shocking new form of therapy.", "tagline": "Mischief. Mayhem. Soap.", "tmdb_rating": 8.4, "tmdb_vote_count": 28000, "popularity_score": 167.8, "maturity_rating": "R", "original_language": "en", "poster_path": "/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg", "backdrop_path": "/hZkgoQYus5vegHoetLkCJzb17zJ.jpg", "status": "Released"},
            {"tmdb_id": 680, "imdb_id": "tt0110413", "title": "Pulp Fiction", "original_title": "Pulp Fiction", "media_type": "movie", "release_date": date(1994, 10, 14), "runtime": 154, "overview": "A burger-loving hit man, his philosophical partner, a drug-addled gangster's moll and a washed-up boxer converge in this sprawling crime caper.", "tagline": "You won't know the facts until you've seen the fiction.", "tmdb_rating": 8.5, "tmdb_vote_count": 27000, "popularity_score": 178.9, "maturity_rating": "R", "original_language": "en", "poster_path": "/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg", "backdrop_path": "/suaEOtk1N1sgg2MTM7oZd2cfVp3.jpg", "status": "Released"},
            {"tmdb_id": 27205, "imdb_id": "tt1375666", "title": "Inception", "original_title": "Inception", "media_type": "movie", "release_date": date(2010, 7, 16), "runtime": 148, "overview": "Cobb, a skilled thief who commits corporate espionage by infiltrating the subconscious of his targets is offered a chance to regain his old life.", "tagline": "Your mind is the scene of the crime", "tmdb_rating": 8.4, "tmdb_vote_count": 34000, "popularity_score": 194.5, "maturity_rating": "PG-13", "original_language": "en", "poster_path": "/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg", "backdrop_path": "/s3TBrRGB1iav7gFOCNx3H31MoES.jpg", "status": "Released"},
            {"tmdb_id": 157336, "imdb_id": "tt2380307", "title": "Interstellar", "original_title": "Interstellar", "media_type": "movie", "release_date": date(2014, 11, 7), "runtime": 169, "overview": "The adventures of a group of explorers who make use of a newly discovered wormhole to surpass the limitations on human space travel.", "tagline": "Mankind was born on Earth. It was never meant to die here.", "tmdb_rating": 8.4, "tmdb_vote_count": 33000, "popularity_score": 188.2, "maturity_rating": "PG-13", "original_language": "en", "poster_path": "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg", "backdrop_path": "/xu9zaAevzQ5nnrsXN6JcahLnG4i.jpg", "status": "Released"},
            {"tmdb_id": 122, "imdb_id": "tt0120737", "title": "The Lord of the Rings: The Fellowship of the Ring", "original_title": "The Lord of the Rings: The Fellowship of the Ring", "media_type": "movie", "release_date": date(2001, 12, 19), "runtime": 178, "overview": "Young hobbit Frodo Baggins, after inheriting a mysterious ring from his uncle Bilbo, must leave his home in order to keep it from falling into the hands of its evil creator.", "tagline": "One ring to rule them all", "tmdb_rating": 8.4, "tmdb_vote_count": 24000, "popularity_score": 210.5, "maturity_rating": "PG-13", "original_language": "en", "poster_path": "/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg", "backdrop_path": "/x2RS3uTcsJJ9IfjNPcgDmukoEcQ.jpg", "status": "Released"},
            {"tmdb_id": 278, "imdb_id": "tt0111161", "title": "The Shawshank Redemption", "original_title": "The Shawshank Redemption", "media_type": "movie", "release_date": date(1994, 9, 23), "runtime": 142, "overview": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.", "tagline": "Fear can hold you prisoner. Hope can set you free.", "tmdb_rating": 8.7, "tmdb_vote_count": 26000, "popularity_score": 125.8, "maturity_rating": "R", "original_language": "en", "poster_path": "/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg", "backdrop_path": "/kXfqcdQKsToO0OUXHcrrNCHDBzO.jpg", "status": "Released"},
            {"tmdb_id": 19404, "imdb_id": "tt1345836", "title": "The Dark Knight Rises", "original_title": "The Dark Knight Rises", "media_type": "movie", "release_date": date(2012, 7, 20), "runtime": 165, "overview": "Following the death of District Attorney Harvey Dent, Batman assumes responsibility for Dent's crimes to protect the late attorney's reputation.", "tagline": "The Legend Ends", "tmdb_rating": 8.1, "tmdb_vote_count": 20000, "popularity_score": 165.3, "maturity_rating": "PG-13", "original_language": "en", "poster_path": "/hr0L2aueqlP2BYUblTTjmtn0hw4.jpg", "backdrop_path": "/f6ljQGv7WnJuwBPty017oPWfqjx.jpg", "status": "Released"},
            {"tmdb_id": 872585, "imdb_id": "tt6710474", "title": "Everything Everywhere All at Once", "original_title": "Everything Everywhere All at Once", "media_type": "movie", "release_date": date(2022, 3, 25), "runtime": 139, "overview": "An aging Chinese immigrant is swept up in an insane adventure, where she alone can save what's important to her by connecting with the lives she could have led.", "tagline": "The universe is so much bigger than you realize.", "tmdb_rating": 7.8, "tmdb_vote_count": 8500, "popularity_score": 220.4, "maturity_rating": "R", "original_language": "en", "poster_path": "/w3LxiVYdWWRvEVdn5RYq6jIqkb1.jpg", "backdrop_path": "/yTjKkc4phIGUJ0h26RxQvO0kVG3.jpg", "status": "Released"},
        ]

        # Insert sample media
        seeded_count = 0
        for media_data in sample_media:
            try:
                media_id = str(uuid.uuid4())
                conn.execute("""
                    INSERT INTO media (
                        id, tmdb_id, imdb_id, title, original_title, media_type,
                        release_date, runtime, overview, tagline, tmdb_rating,
                        tmdb_vote_count, popularity_score, maturity_rating,
                        original_language, poster_path, backdrop_path, status
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?,
                        ?, ?, ?,
                        ?, ?, ?, ?
                    )
                """, [
                    media_id, media_data["tmdb_id"], media_data["imdb_id"],
                    media_data["title"], media_data["original_title"], media_data["media_type"],
                    media_data["release_date"], media_data["runtime"], media_data["overview"],
                    media_data["tagline"], media_data["tmdb_rating"], media_data["tmdb_vote_count"],
                    media_data["popularity_score"], media_data["maturity_rating"],
                    media_data["original_language"], media_data["poster_path"],
                    media_data["backdrop_path"], media_data["status"],
                ])
                seeded_count += 1
                logger.info(f"✅ Seeded: {media_data['title']}")
            except Exception as e:
                logger.error(f"❌ Failed to seed {media_data['title']}: {e}")

        logger.info(f"✨ Seeded {seeded_count} media items")

        return {
            "success": True,
            "data": {"count": seeded_count, "newly_seeded": seeded_count},
            "message": f"Successfully seeded {seeded_count} sample media items",
        }

    except Exception as e:
        logger.error(f"Error seeding sample media: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to seed sample media: {str(e)}")
