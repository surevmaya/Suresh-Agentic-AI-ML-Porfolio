def get_movie_info(movie_title: str) -> str:
    """Get movie info and ratings from OMDB/IMDB"""
    api_key = os.environ.get("OMDB_API_KEY")
    
    url = "http://www.omdbapi.com/"
    params = {
        "t": "Citadel"        # movie title
        "apikey": ???    # your key
    }
