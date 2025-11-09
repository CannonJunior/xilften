/**
 * Placeholder Poster Images
 *
 * Provides media-type-specific placeholder images as data URIs
 * for content without TMDB poster data.
 */

/**
 * Generate SVG placeholder for different media types
 * @param {string} mediaType - Type of media (movie, tv, anime, documentary, etc.)
 * @param {string} title - Media title to display
 * @returns {string} Data URI for SVG image
 */
export function getPlaceholderPoster(mediaType, title = '') {
    const config = PLACEHOLDER_CONFIGS[mediaType] || PLACEHOLDER_CONFIGS.default;

    // Truncate title if too long
    const displayTitle = title.length > 30 ? title.substring(0, 27) + '...' : title;

    const svg = `
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="450" viewBox="0 0 300 450">
  <defs>
    <linearGradient id="grad-${mediaType}" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:${config.gradientStart};stop-opacity:1" />
      <stop offset="100%" style="stop-color:${config.gradientEnd};stop-opacity:1" />
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="300" height="450" fill="url(#grad-${mediaType})"/>

  <!-- Icon -->
  <g transform="translate(150, 180)">
    ${config.icon}
  </g>

  <!-- Media Type Label -->
  <text x="150" y="280" text-anchor="middle" fill="#ffffff" font-size="16" font-family="Arial, sans-serif" font-weight="bold" opacity="0.9">
    ${config.label}
  </text>

  <!-- Title -->
  <text x="150" y="310" text-anchor="middle" fill="#ffffff" font-size="14" font-family="Arial, sans-serif" opacity="0.7">
    ${displayTitle}
  </text>

  <!-- No Poster Available -->
  <text x="150" y="400" text-anchor="middle" fill="#ffffff" font-size="12" font-family="Arial, sans-serif" opacity="0.5">
    No Poster Available
  </text>
</svg>`.trim();

    // Convert to data URI
    return 'data:image/svg+xml;base64,' + btoa(svg);
}

/**
 * Placeholder configurations for different media types
 */
const PLACEHOLDER_CONFIGS = {
    movie: {
        label: 'MOVIE',
        gradientStart: '#1a1a2e',
        gradientEnd: '#16213e',
        icon: `<path d="M-30,-30 L30,-30 L30,30 L-30,30 Z" fill="none" stroke="#6366f1" stroke-width="3"/>
               <circle cx="-15" cy="-15" r="8" fill="#6366f1"/>
               <circle cx="15" cy="-15" r="8" fill="#6366f1"/>
               <circle cx="-15" cy="15" r="8" fill="#6366f1"/>
               <circle cx="15" cy="15" r="8" fill="#6366f1"/>
               <path d="M30,0 L50,0" stroke="#6366f1" stroke-width="3"/>
               <path d="M50,-10 L70,0 L50,10 Z" fill="#6366f1"/>`
    },
    tv: {
        label: 'TV SERIES',
        gradientStart: '#0f172a',
        gradientEnd: '#1e293b',
        icon: `<rect x="-35" y="-25" width="70" height="50" rx="2" fill="none" stroke="#10b981" stroke-width="3"/>
               <rect x="-30" y="-20" width="60" height="40" fill="#10b981" opacity="0.2"/>
               <circle cx="-25" cy="35" r="5" fill="#10b981"/>
               <circle cx="25" cy="35" r="5" fill="#10b981"/>
               <line x1="-25" y1="25" x2="-25" y2="30" stroke="#10b981" stroke-width="2"/>
               <line x1="25" y1="25" x2="25" y2="30" stroke="#10b981" stroke-width="2"/>`
    },
    anime: {
        label: 'ANIME',
        gradientStart: '#4c1d95',
        gradientEnd: '#5b21b6',
        icon: `<circle cx="0" cy="-10" r="20" fill="none" stroke="#a78bfa" stroke-width="3"/>
               <circle cx="-8" cy="-12" r="4" fill="#a78bfa"/>
               <circle cx="8" cy="-12" r="4" fill="#a78bfa"/>
               <path d="M-10,0 Q0,8 10,0" stroke="#a78bfa" stroke-width="3" fill="none"/>
               <path d="M-25,-15 L-35,-25" stroke="#a78bfa" stroke-width="3"/>
               <path d="M25,-15 L35,-25" stroke="#a78bfa" stroke-width="3"/>
               <path d="M-20,10 Q0,30 20,10" stroke="#a78bfa" stroke-width="2" fill="none"/>`
    },
    documentary: {
        label: 'DOCUMENTARY',
        gradientStart: '#14532d',
        gradientEnd: '#166534',
        icon: `<circle cx="0" cy="0" r="30" fill="none" stroke="#22c55e" stroke-width="3"/>
               <circle cx="0" cy="0" r="20" fill="none" stroke="#22c55e" stroke-width="2"/>
               <circle cx="0" cy="0" r="5" fill="#22c55e"/>
               <path d="M0,-30 L0,-35 M0,30 L0,35 M-30,0 L-35,0 M30,0 L35,0" stroke="#22c55e" stroke-width="2"/>`
    },
    default: {
        label: 'MEDIA',
        gradientStart: '#1e293b',
        gradientEnd: '#334155',
        icon: `<rect x="-30" y="-30" width="60" height="60" rx="5" fill="none" stroke="#64748b" stroke-width="3"/>
               <path d="M-15,-10 L-15,15 L15,15" stroke="#64748b" stroke-width="2" fill="none"/>
               <circle cx="15" cy="15" r="3" fill="#64748b"/>
               <path d="M-10,-20 L10,-20 L10,0" stroke="#64748b" stroke-width="2" fill="none"/>`
    }
};
