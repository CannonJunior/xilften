-- Add source column to soundtracks table

ALTER TABLE soundtracks
ADD COLUMN IF NOT EXISTS source VARCHAR DEFAULT 'unknown';

-- Update existing rows to have 'musicbrainz' as source where applicable
UPDATE soundtracks
SET source = 'musicbrainz'
WHERE source = 'unknown' AND musicbrainz_id IS NOT NULL;
