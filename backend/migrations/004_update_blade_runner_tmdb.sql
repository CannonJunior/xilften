-- Migration 004: Update Blade Runner with TMDB data
-- Adds TMDB ID, poster, and additional metadata

UPDATE media
SET
    tmdb_id = 78,
    imdb_id = 'tt0083658',
    poster_path = '/63N9uy8nd9j7Eog2axPQ8lbr3Wj.jpg',
    backdrop_path = '/wfQTVBIQj1wJUe0jV3OZ4zOivIO.jpg',
    custom_fields = json_set(
        COALESCE(custom_fields, '{}'),
        '$.tmdb_data', json('{
            "director": "Ridley Scott",
            "screenplay": "Hampton Fancher, David Webb Peoples",
            "starring": "Harrison Ford, Rutger Hauer, Sean Young",
            "cinematography": "Jordan Cronenweth",
            "music": "Vangelis",
            "editing": "Marsha Nakashima",
            "production_companies": "The Ladd Company, Shaw Brothers, Warner Bros.",
            "budget": 28000000,
            "box_office": 41722424,
            "languages": "English, German, Cantonese, Japanese, Hungarian"
        }')
    )
WHERE id = 'c84acdb8-71ca-4ab8-a297-1f4866e19d49';
