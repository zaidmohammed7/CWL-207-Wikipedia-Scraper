import time
import logging
from collections import deque
from src.wiki_api import get_category_members, canonicalize_titles
from src.scraper import WikiScraper
from src.graph_builder import BollywoodGraph

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DEPTH_LIMIT = 3
MAX_ENTITIES = None  # Set to a number for dry run

def run_mapper(seed_categories, max_entities=None):
    scraper = WikiScraper()
    graph = BollywoodGraph()
    
    # Phase 1: Seeding
    logger.info(f"Seeding from categories: {seed_categories}")
    raw_seeds = set()
    for cat in seed_categories:
        raw_seeds.update(get_category_members(cat, limit=100))
    
    logger.info(f"Canonicalizing {len(raw_seeds)} seeds...")
    seed_map = canonicalize_titles(list(raw_seeds))
    canonical_seeds = set(seed_map.values())
    
    # Phase 2: Recursive Extraction (BFS)
    # Queue stores (slug, depth)
    queue = deque([(slug, 0) for slug in canonical_seeds])
    visited = set(canonical_seeds)
    processed_count = 0
    
    logger.info("Starting BFS traversal...")
    
    while queue:
        if max_entities and processed_count >= max_entities:
            logger.info(f"Reached dry run limit of {max_entities} entities.")
            break
            
        current_slug, depth = queue.popleft()
        logger.info(f"[{processed_count+1}] Processing: {current_slug} (Depth: {depth})")
        
        # Add the current person as a node (if not already there with details)
        # We don't have the "Name" yet for some discovered links, 
        # but the scraper will find it or we use the slug as temporary name.
        graph.add_person(current_slug, current_slug.replace('_', ' '))
        
        # Extract family relationships
        relations = scraper.extract_family_data(current_slug)
        processed_count += 1
        
        # To avoid being a bad "web citizen"
        time.sleep(1)
        
        # We might want to canonicalize discovered links in batches, 
        # but for simplicity in BFS we can do it row-by-row or just track visited.
        # NOTE: Using the href slug directly is usually enough if we land on canonical pages.
        
        new_links = []
        for rel in relations:
            target = rel['target']
            name = rel['name']
            relation_type = rel['relation']
            is_terminal = rel['is_terminal']
            
            # Add node for target
            graph.add_person(target, name, is_terminal=is_terminal)
            
            # Add edge
            graph.add_marriage_or_blood_relation(current_slug, target, relation_type)
            
            # If not terminal and not visited, and within depth limit, add to queue
            if not is_terminal and target not in visited and depth < DEPTH_LIMIT:
                visited.add(target)
                queue.append((target, depth + 1))
                new_links.append(target)

    # Phase 3: Export
    logger.info("Exporting graph data...")
    graph.export_to_csv("bollywood_nodes.csv", "bollywood_edges.csv")
    logger.info("Mapping complete.")

if __name__ == "__main__":
    # Full Crawl Parameters
    SEED_CATS = [
        "Hindi_film_families", 
        "Hindi-language_film_directors",
        "Kapoor_family",
        "Bachchan_family",
        "Akhtar–Azmi_family",
        "Bhatt_family",
        "Pataudi_family"
    ]
    run_mapper(SEED_CATS, max_entities=None)
