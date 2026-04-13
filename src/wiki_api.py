import requests
from typing import List, Dict, Set

API_URL = "https://en.wikipedia.org/w/api.php"

def get_category_members(category_name: str, limit: int = 500) -> Set[str]:
    """
    Fetches page titles from a specific Wikipedia category.
    """
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category_name}",
        "cmlimit": "max",
        "format": "json"
    }
    
    titles = set()
    headers = {"User-Agent": "BollywoodGenMapper/1.0 (https://github.com/example/repo)"}
    while len(titles) < limit:
        response = requests.get(API_URL, params=params, headers=headers).json()
        if 'query' not in response:
            break
            
        for member in response['query']['categorymembers']:
            if member['ns'] == 0:  # Only main namespace pages
                titles.add(member['title'])
                
        if 'continue' in response and len(titles) < limit:
            params.update(response['continue'])
        else:
            break
            
    return set(list(titles)[:limit])

def canonicalize_titles(titles: List[str]) -> Dict[str, str]:
    """
    Resolves redirects and normalizes Wikipedia titles.
    Returns a mapping of original_title -> canonical_title.
    """
    if not titles:
        return {}
        
    # Wikipedia API allows up to 50 titles per request
    chunk_size = 50
    mapping = {}
    
    headers = {"User-Agent": "BollywoodGenMapper/1.0 (https://github.com/example/repo)"}
    
    for i in range(0, len(titles), chunk_size):
        chunk = titles[i:i + chunk_size]
        params = {
            "action": "query",
            "titles": "|".join(chunk),
            "redirects": 1,
            "format": "json"
        }
        
        response = requests.get(API_URL, params=params, headers=headers).json()
        
        # Track redirects
        redirect_map = {}
        if 'query' in response and 'redirects' in response['query']:
            for redir in response['query']['redirects']:
                redirect_map[redir['from']] = redir['to']
        
        # Track normalized names
        norm_map = {}
        if 'query' in response and 'normalized' in response['query']:
            for norm in response['query']['normalized']:
                norm_map[norm['from']] = norm['to']
                
        for t in chunk:
            current = t
            # First apply normalization
            current = norm_map.get(current, current)
            # Then apply redirect
            current = redirect_map.get(current, current)
            mapping[t] = current
            
    return mapping

if __name__ == "__main__":
    # Test seeding
    print("Testing category fetch...")
    seeds = get_category_members("Indian_film_families", limit=10)
    print(f"Found {len(seeds)} seeds: {list(seeds)[:5]}")
    
    print("\nTesting canonicalization...")
    test_titles = ["Shahrukh Khan", "Amitabh Bachan"]
    canon = canonicalize_titles(test_titles)
    print(f"Canonical titles: {canon}")
