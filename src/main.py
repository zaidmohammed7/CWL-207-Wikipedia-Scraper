import time
import logging
import os
import pandas as pd
from src.wiki_api import get_category_members, canonicalize_titles, get_links_from_page, filter_person_pages
from src.scraper import WikiScraper
from src.graph_builder import BollywoodGraph
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DEPTH_LIMIT = 2  # Reduced slightly because seed list is massive
MAX_ENTITIES = None

def run_mapper(seed_lists, max_entities=None):
    scraper = WikiScraper()
    graph = BollywoodGraph()
    
    nodes_file = "bollywood_nodes.csv"
    edges_file = "bollywood_edges.csv"
    graph.load_from_csv(nodes_file, edges_file)
    existing_nodes = set(graph.nodes.keys())
    logger.info(f"Loaded {len(existing_nodes)} existing nodes.")

    # Phase 1: Aggressive Discovery from Lists
    logger.info(f"Seeding from major lists: {seed_lists}")
    raw_seeds = set()
    for page in seed_lists:
        logger.info(f"Extracting links from: {page}")
        links = get_links_from_page(page)
        logger.info(f"Found {len(links)} links on {page}")
        raw_seeds.update(links)
    
    logger.info(f"Filtering {len(raw_seeds)} discovered links for 'Person' pages...")
    potential_people = filter_person_pages(list(raw_seeds))
    logger.info(f"After filtration, {len(potential_people)} potential people remain.")

    logger.info(f"Canonicalizing {len(potential_people)} seeds...")
    seed_map = canonicalize_titles(potential_people)
    canonical_seeds = set(seed_map.values())
    
    # Exclude already processed nodes
    initial_queue = [slug for slug in canonical_seeds if slug not in existing_nodes]
    logger.info(f"{len(initial_queue)} new seeds to process after checking existing data.")

    # Phase 2: Recursive Extraction (BFS)
    from collections import deque
    queue = deque([(slug, 0) for slug in initial_queue])
    visited = existing_nodes.union(set(initial_queue))
    processed_count = 0
    
    logger.info("Starting BFS traversal...")
    
    while queue:
        if max_entities and processed_count >= max_entities:
            logger.info(f"Reached dry run limit of {max_entities} entities.")
            break
            
        current_slug, depth = queue.popleft()
        
        # Double check if already in existing_nodes (case-sensitivity/canonicalization safety)
        if current_slug in existing_nodes and depth == 0:
             continue

        logger.info(f"[{processed_count+1}/~{len(initial_queue)+processed_count}] Processing: {current_slug} (Depth: {depth})")
        
        try:
            # Add the current person as a node
            graph.add_person(current_slug, current_slug.replace('_', ' '))
            
            # Extract family relationships
            relations = scraper.extract_family_data(current_slug)
            processed_count += 1
            
            # To avoid being a bad "web citizen"
            time.sleep(1)
            
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
        
        except Exception as e:
            logger.error(f"Error processing {current_slug}: {e}")
            continue # Robustness: keep going if one page fails

    # Phase 3: Export (Append mode handled by graph_builder or just overwrite if it consolidates)
    # The current graph_builder export_to_csv seems to overwrite. 
    # To truly 'append', we should load the graph with existing data first or merge.
    # Looking at the existing graph_builder... I'll check it.
    logger.info("Exporting graph data...")
    graph.export_to_csv("bollywood_nodes.csv", "bollywood_edges.csv")
    logger.info("Mapping complete.")

    # Post-processing
    logger.info("Running post-processing scripts...")
    try:
        subprocess.run(["python", "src/clean_data.py"], check=True)
        subprocess.run(["python", "src/visualize.py"], check=True)
    except Exception as e:
        logger.error(f"Post-processing failed: {e}")

if __name__ == "__main__":
    SEED_LISTS = [
        'List of Hindi film actors',
        'List of Hindi film actresses',
        'List of Hindi film directors',
        'List of Hindi film families',
        'List of Bollywood actors',
        'List of Bollywood actresses',
        'List of Indian film families'
    ]
    run_mapper(SEED_LISTS, max_entities=None)
