import os
import requests
from urllib.parse import quote
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def fetch_youtube_videos(query, max_results=5):
    """
    Fetch relevant videos from YouTube API
    
    Args:
        query (str): The search query
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of video data
    """
    try:
        # Initialize the YouTube API client
        youtube = build(
            'youtube', 
            'v3', 
            developerKey=os.getenv('YOUTUBE_API_KEY')
        )
        
        # Execute the search
        search_response = youtube.search().list(
            q=query,
            part='snippet',
            maxResults=max_results,
            type='video',
            relevanceLanguage='en',
            safeSearch='moderate'
        ).execute()
        
        # Process the results
        videos = []
        for item in search_response.get('items', []):
            video_id = item['id']['videoId']
            videos.append({
                'id': video_id,
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                'publishedAt': item['snippet']['publishedAt'],
                'channelTitle': item['snippet']['channelTitle'],
                'url': f"https://www.youtube.com/watch?v={video_id}"
            })
        
        return videos
    
    except HttpError as e:
        print(f"YouTube API error: {e}")
        return []
    except Exception as e:
        print(f"Error fetching YouTube videos: {e}")
        return []

def fetch_google_scholar_papers(query, max_results=5):
    """
    Fetch academic papers from Google Scholar via RapidAPI
    
    Args:
        query (str): The search query
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of paper data
    """
    import os
    import requests
    
    print("Query- ", query)
    
    try:
        # RapidAPI endpoint for Google Scholar
        url = "https://google-scholar1.p.rapidapi.com/search_pubs"
        
        # Set up the request parameters
        querystring = {
            "query": query,
            "max_results": str(max_results),
            "patents": "true",
            "citations": "true",
            "sort_by": "relevance",
            "include_last_year": "abstracts",
            "start_index": "0"
        }
        
        headers = {
            "x-rapidapi-key": os.getenv('GOOGLE_SCHOLOR_API_KEY'),
            "x-rapidapi-host": "google-scholar1.p.rapidapi.com"
        }
        
        # Make the API request
        response = requests.get(url, headers=headers, params=querystring)
        
        if response.status_code != 200:
            print(f"Google Scholar API error: {response.status_code} - {response.text}")
            return []
        
        # Process the results
        data = response.json()
        papers = []
        
        # Handle the actual response format returned by the API
        if 'result' in data and isinstance(data['result'], list):
            for item in data['result'][:max_results]:
                # Extract author names from the bib.author list
                authors = []
                if 'bib' in item and 'author' in item['bib'] and isinstance(item['bib']['author'], list):
                    authors = item['bib']['author']
                
                # Create paper object with available fields
                paper = {
                    'title': item.get('bib', {}).get('title', 'Untitled'),
                    'authors': authors,
                    'abstract': item.get('bib', {}).get('abstract', 'No abstract available'),
                    'year': item.get('bib', {}).get('pub_year', 'Unknown year'),
                    'citations': item.get('num_citations', 0),
                    'url': item.get('pub_url', '')
                }
                papers.append(paper)
                print(f"Added paper: {paper['title']}")
        
        print(f"Found {len(papers)} papers")
        return papers
    
    except Exception as e:
        import traceback
        print(f"Error fetching Google Scholar papers: {e}")
        print(traceback.format_exc())
        return []
    
def fetch_google_search_results(query, max_results=5):
    """
    Fetch general web resources from Google Custom Search API
    
    Args:
        query (str): The search query
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of web resource data
    """
    try:
        # Google Custom Search API endpoint
        url = "https://www.googleapis.com/customsearch/v1"
        
        # Parameters for the API request
        params = {
            'key': os.getenv('GOOGLE_CUSTOM_SEARCH_API_KEY'),
            'cx': '017576662512468239146:omuauf_lfve',  # This is a placeholder, you need to create a CSE and get your own cx value
            'q': query,
            'num': max_results
        }
        
        # Make the API request
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"Google Search API error: {response.status_code} - {response.text}")
            return []
        
        # Process the results
        data = response.json()
        results = []
        
        for item in data.get('items', []):
            results.append({
                'title': item.get('title', 'Untitled'),
                'link': item.get('link'),
                'snippet': item.get('snippet', 'No description available'),
                'displayLink': item.get('displayLink'),
                'formattedUrl': item.get('formattedUrl')
            })
        
        return results
    
    except Exception as e:
        print(f"Error fetching Google search results: {e}")
        return []

def fetch_github_repositories(query, max_results=5):
    """
    Fetch relevant GitHub repositories
    
    Args:
        query (str): The search query
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of repository data
    """
    try:
        # GitHub Search API endpoint
        url = f"https://api.github.com/search/repositories?q={quote(query)}&sort=stars&order=desc&per_page={max_results}"
        
        # Make the API request
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"GitHub API error: {response.status_code} - {response.text}")
            return []
        
        # Process the results
        data = response.json()
        repos = []
        
        for item in data.get('items', []):
            repos.append({
                'name': item.get('name'),
                'full_name': item.get('full_name'),
                'description': item.get('description', 'No description available'),
                'url': item.get('html_url'),
                'stars': item.get('stargazers_count', 0),
                'forks': item.get('forks_count', 0),
                'language': item.get('language'),
                'updated_at': item.get('updated_at')
            })
        
        return repos
    
    except Exception as e:
        print(f"Error fetching GitHub repositories: {e}")
        return []