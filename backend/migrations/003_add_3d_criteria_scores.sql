-- Migration 003: Add 3D Criteria Scores to Media
-- Adds storytelling, characters, and cohesive_vision scores for 3D visualization

-- Update existing media with 3D criteria scores
-- Blade Runner (c84acdb8-71ca-4ab8-a297-1f4866e19d49)
UPDATE media
SET custom_fields = json_set(
    COALESCE(custom_fields, '{}'),
    '$.storytelling', 9.5,
    '$.characters', 8.5,
    '$.cohesive_vision', 9.8
)
WHERE id = 'c84acdb8-71ca-4ab8-a297-1f4866e19d49';

-- Cowboy Bebop (a485a00c-6ddb-4504-8ccd-06bd3e6c4392)
UPDATE media
SET custom_fields = json_set(
    COALESCE(custom_fields, '{}'),
    '$.storytelling', 9.0,
    '$.characters', 9.5,
    '$.cohesive_vision', 9.2
)
WHERE id = 'a485a00c-6ddb-4504-8ccd-06bd3e6c4392';

-- The Matrix (df85d13c-3b91-4d12-8ad0-4ad13c8f2e39)
UPDATE media
SET custom_fields = json_set(
    COALESCE(custom_fields, '{}'),
    '$.storytelling', 8.8,
    '$.characters', 7.5,
    '$.cohesive_vision', 9.3
)
WHERE id = 'df85d13c-3b91-4d12-8ad0-4ad13c8f2e39';
