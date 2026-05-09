import os
import requests
from datetime import datetime, timedelta


def search_news(query: str, days_back: int = 7) -> str:
    """Search recent news for supply chain disruptions"""
    api_key = os.getenv("NEWS_API_KEY")
    from_date = (datetime.now() - timedelta(days=days_back))
    from_str = from_date.strftime("%Y-%m-%d")

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": from_str,
        "sortBy": "relevancy",
        "language": "en",
        "pageSize": 10,
        "apiKey": api_key
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data.get("status") != "ok":
            return f"News API error: {data.get('message')}"

        articles = data.get("articles", [])
        if not articles:
            return "No recent news found for this query"

        results = []
        for article in articles[:5]:
            results.append(f"""
Title: {article['title']}
Source: {article['source']['name']}
Date: {article['publishedAt'][:10]}
Summary: {article['description']}
URL: {article['url']}
""")
        return "\n---\n".join(results)

    except Exception as e:
        return f"Error searching news: {e}"

def search_geopolitical_risks(region: str) -> str:
    """Search for geopolitical risks affecting supply chains"""
    api_key = os.getenv("NEWS_API_KEY")
    query = f"{region} tariffs sanctions trade war oil price disruption geopolitical"

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"),
        "sortBy": "relevancy",
        "language": "en",
        "pageSize": 5,
        "apiKey": api_key
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        articles = data.get("articles", [])

        if not articles:
            return f"No geo risk found for {region}"

        results = []
        for article in articles[:3]:
            results.append(f"""
Title: {article['title']}
Date: {article['publishedAt'][:10]}
Summary: {article['description']}
""")
        return "\n---\n".join(results)

    except Exception as e:
        return f"Error searching geopolitical risks: {e}"



def search_weather_disruptions(region: str) -> str:
    """Search for weather events affecting supply chains"""
    api_key = os.getenv("NEWS_API_KEY")
    query = f"{region} extreme weather flood disruption logistics"

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"),
        "sortBy": "relevancy",
        "language": "en",
        "pageSize": 5,
        "apiKey": api_key
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        articles = data.get("articles", [])

        if not articles:
            return f"No weather disruption news found for {region}"

        results = []
        for article in articles[:3]:
            results.append(f"""
Title: {article['title']}
Date: {article['publishedAt'][:10]}
Summary: {article['description']}
""")
        return "\n---\n".join(results)

    except Exception as e:
        return f"Error searching weather news: {e}"


def search_port_disruptions(region: str) -> str:
    """Search for port and logistics disruptions"""
    api_key = os.getenv("NEWS_API_KEY")
    query = f"{region} port delay shipping disruption congestion"

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"),
        "sortBy": "relevancy",
        "language": "en",
        "pageSize": 5,
        "apiKey": api_key
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        articles = data.get("articles", [])

        if not articles:
            return f"No port disruption news found for {region}"

        results = []
        for article in articles[:3]:
            results.append(f"""
Title: {article['title']}
Date: {article['publishedAt'][:10]}
Summary: {article['description']}
""")
        return "\n---\n".join(results)

    except Exception as e:
        return f"Error searching port news: {e}"


def search_commodity_price(commodity: str) -> str:
    """Get commodity price context via news search"""
    api_key = os.getenv("NEWS_API_KEY")
    query = f"{commodity} price supply shortage spike"

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 5,
        "apiKey": api_key
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        articles = data.get("articles", [])

        if not articles:
            return f"No recent price news found for {commodity}"

        results = []
        for article in articles[:3]:
            results.append(f"""
Title: {article['title']}
Date: {article['publishedAt'][:10]}
Summary: {article['description']}
""")
        return "\n---\n".join(results)

    except Exception as e:
        return f"Error fetching commodity data: {e}"
