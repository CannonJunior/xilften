### MCP Genre Classifier

This MCP (Model Context Protocol) server provides genre classification tools for movies.

- **Port**: This tool runs locally and doesn't require a port (connects directly to database at 7575)
- **Purpose**: Classifies movies into TMDB-standard genres based on title, overview, and existing metadata
- **Usage**: Can be run standalone or integrated as an MCP tool
- **Database**: Connects to DuckDB at `./database/xilften.duckdb`

### TMDB Official 19 Genres

The classifier uses TMDB's official 19 genre taxonomy:
1. Action
2. Adventure
3. Animation
4. Comedy
5. Crime
6. Documentary
7. Drama
8. Family
9. Fantasy
10. History
11. Horror
12. Music
13. Mystery
14. Romance
15. Science Fiction
16. Thriller
17. TV Movie
18. War
19. Western

### Running the Tool

```bash
# Classify all movies
PYTHONPATH=/home/junior/src/xilften uv run python mcp_servers/genre_classifier/server.py

# Classify first N movies
PYTHONPATH=/home/junior/src/xilften uv run python mcp_servers/genre_classifier/server.py 10
```
