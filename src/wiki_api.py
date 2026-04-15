import requests
import re
from typing import List, Dict, Set, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def get_links_from_page(page_title: str) -> Set[str]:
    """
    Extracts all internal Wikipedia links from a specific page.
    """
    params = {
        "action": "query",
        "titles": page_title,
        "prop": "links",
        "pllimit": "max",
        "plnamespace": 0,  # Only main namespace
        "redirects": 1,
        "format": "json"
    }
    
    links = set()
    headers = {"User-Agent": "BollywoodGenMapper/1.0 (https://github.com/example/repo)"}
    
    while True:
        response = requests.get(API_URL, params=params, headers=headers).json()
        if 'query' not in response or 'pages' not in response['query']:
            break
            
        pages = response['query']['pages']
        for page_id in pages:
            if 'links' in pages[page_id]:
                for link in pages[page_id]['links']:
                    links.add(link['title'])
                    
        if 'continue' in response:
            params.update(response['continue'])
        else:
            break
            
    return links

def filter_person_pages(titles: List[str]) -> List[str]:
    """
    Filters a list of titles to keep those likely pointing to a Person.
    Uses Template check (Infobox person, actor, etc.) and keyword exclusions.
    """
    if not titles:
        return []

    # Exclude years, awards, and general terms via regex
    exclude_patterns = [
        r'^\d{4}',            # Years (1990, 2024, etc)
        r'Award',             # Awards
        r'Cinema of',         # General terms
        r'Filmography',       # Filmographies
        r'List of',           # Other lists
        r'Bollywood',         # General Bollywood terms
        r'film industry',     # Industry terms
    ]
    
    filtered_titles = []
    for title in titles:
        if any(re.search(pattern, title, re.IGNORECASE) for pattern in exclude_patterns):
            continue
        filtered_titles.append(title)

    # Further narrow down by checking for Infoboxes (Batching 50 titles at a time)
    final_people = []
    chunk_size = 50
    headers = {"User-Agent": "BollywoodGenMapper/1.0 (https://github.com/example/repo)"}
    
    chunks = [filtered_titles[i:i + chunk_size] for i in range(0, len(filtered_titles), chunk_size)]
    
    def process_chunk(chunk):
        params = {
            "action": "query",
            "titles": "|".join(chunk),
            "prop": "templates",
            "tllimit": "max",
            "format": "json"
        }
        try:
            response = requests.get(API_URL, params=params, headers=headers).json()
            if 'query' not in response or 'pages' not in response['query']:
                return []
                
            chunk_results = []
            pages = response['query']['pages']
            for page_id in pages:
                page = pages[page_id]
                if 'templates' in page:
                    templates = [t['title'].lower() for t in page['templates']]
                    is_person = any(
                        "infobox person" in t or 
                        "infobox actor" in t or 
                        "infobox musical artist" in t or
                        "infobox filmmaker" in t
                        for t in templates
                    )
                    if is_person:
                        chunk_results.append(page['title'])
            return chunk_results
        except Exception as e:
            print(f"Error checking batch: {e}")
            return []

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_chunk, chunk) for chunk in chunks]
        for future in as_completed(futures):
            final_people.extend(future.result())
                    
    return final_people

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
    
    chunks = [titles[i:i + chunk_size] for i in range(0, len(titles), chunk_size)]
    
    def process_canon_chunk(chunk):
        params = {
            "action": "query",
            "titles": "|".join(chunk),
            "redirects": 1,
            "format": "json"
        }
        try:
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
                    
            chunk_mapping = {}
            for t in chunk:
                current = t
                current = norm_map.get(current, current)
                current = redirect_map.get(current, current)
                chunk_mapping[t] = current
            return chunk_mapping
        except Exception as e:
            print(f"Error canonicalizing chunk: {e}")
            return {t: t for t in chunk}

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_canon_chunk, chunk) for chunk in chunks]
        for future in as_completed(futures):
            mapping.update(future.result())
            
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
