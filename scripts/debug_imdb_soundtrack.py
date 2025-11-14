"""
Debug script to fetch and analyze IMDB soundtrack page structure.

This script helps identify the correct CSS selectors for extracting soundtrack data.
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def debug_imdb_soundtrack_page(imdb_id: str, movie_title: str):
    """
    Fetch and analyze IMDB soundtrack page HTML structure.

    Args:
        imdb_id: IMDB ID (e.g., "tt10676052")
        movie_title: Movie title for logging
    """
    url = f"https://www.imdb.com/title/{imdb_id}/soundtrack"

    print("=" * 80)
    print(f"🔍 DEBUGGING IMDB SOUNDTRACK PAGE: {movie_title}")
    print("=" * 80)
    print(f"URL: {url}")
    print()

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            print(f"Status Code: {response.status_code}")
            print()

            if response.status_code != 200:
                print(f"❌ Failed to fetch page: HTTP {response.status_code}")
                return

            soup = BeautifulSoup(response.text, 'lxml')

            # Try current selectors
            print("=" * 80)
            print("TESTING CURRENT SELECTORS")
            print("=" * 80)
            print()

            # Current primary selector
            items_new = soup.select('.ipc-metadata-list__item')
            print(f"✅ Found {len(items_new)} items with '.ipc-metadata-list__item'")

            # Current fallback selector
            items_old = soup.select('.soundTrack')
            print(f"✅ Found {len(items_old)} items with '.soundTrack'")

            print()
            print("=" * 80)
            print("EXPLORING ALTERNATIVE SELECTORS")
            print("=" * 80)
            print()

            # Try alternative selectors
            alternatives = [
                'li[class*="ipc-metadata-list"]',
                '[data-testid*="soundtrack"]',
                '[data-testid*="track"]',
                'section[data-testid*="Soundtracks"] li',
                'div[class*="soundtrack"]',
                'li.ipc-metadata-list-summary-item',
            ]

            for selector in alternatives:
                items = soup.select(selector)
                if items:
                    print(f"✅ Found {len(items)} items with '{selector}'")

                    # Show first item structure
                    if items:
                        print(f"   First item HTML snippet:")
                        print(f"   {str(items[0])[:500]}...")
                        print()

            print()
            print("=" * 80)
            print("ANALYZING PAGE STRUCTURE")
            print("=" * 80)
            print()

            # Look for sections
            sections = soup.find_all('section')
            print(f"Found {len(sections)} <section> elements")
            for section in sections:
                testid = section.get('data-testid', '')
                class_name = section.get('class', [])
                if testid or class_name:
                    print(f"  - Section: data-testid='{testid}', class={class_name}")

            print()

            # Look for ul/li structures
            lists = soup.find_all('ul')
            print(f"Found {len(lists)} <ul> elements")

            # Find lists with multiple items
            for ul in lists:
                items = ul.find_all('li')
                if len(items) > 3:  # Likely a soundtrack list
                    print(f"  - UL with {len(items)} items:")
                    print(f"    Parent classes: {ul.get('class', [])}")
                    if items:
                        print(f"    First LI classes: {items[0].get('class', [])}")
                        print(f"    First LI HTML: {str(items[0])[:300]}...")

            print()
            print("=" * 80)
            print("SAMPLE TRACK EXTRACTION")
            print("=" * 80)
            print()

            # Try to extract from the most promising selector
            if items_new:
                print("Extracting from '.ipc-metadata-list__item' selector:")
                for i, item in enumerate(items_new[:3], 1):
                    print(f"\nTrack {i}:")

                    # Try different title selectors
                    title_selectors = [
                        '.ipc-metadata-list-summary-item__t',
                        'a',
                        'div',
                        'span'
                    ]

                    for selector in title_selectors:
                        elem = item.select_one(selector)
                        if elem:
                            text = elem.get_text(strip=True)
                            if text:
                                print(f"  {selector}: {text[:100]}")

                    # Full text content
                    print(f"  Full text: {item.get_text(strip=True)[:200]}")

            # Save full HTML for inspection
            output_file = f"/home/junior/src/xilften/imdb_debug_{imdb_id}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(response.text)

            print()
            print("=" * 80)
            print(f"✅ Full HTML saved to: {output_file}")
            print("=" * 80)

    except Exception as e:
        logger.error(f"Error debugging IMDB page: {e}", exc_info=True)


async def main():
    """Run debug analysis for Fantastic 4 and other failing movies."""

    test_cases = [
        ("tt10676052", "The Fantastic 4: First Steps"),
        ("tt6263850", "Deadpool & Wolverine"),
        ("tt0076759", "Star Wars"),
    ]

    for imdb_id, title in test_cases:
        await debug_imdb_soundtrack_page(imdb_id, title)
        print("\n\n")


if __name__ == "__main__":
    asyncio.run(main())
