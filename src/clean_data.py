import csv
import re
import os

def clean_label(label):
    """Cleans names and labels."""
    if not label: return ""
    # Remove citations like [1], [22]
    label = re.sub(r'\[\d+\]', '', label)
    # Strip whitespace
    label = label.strip()
    # Remove trailing 's' if preceded by a letter (e.g. Zoya Akhtars -> Zoya Akhtar)
    # but avoid breaking names like 'Vikas' or 'Manish'
    if label.endswith('s') and len(label) > 1 and label[-2].isalpha():
        # Check if it looks like a possessive s
        # For simplicity, we'll only strip if it's trailing whitespace/extra 's' 
        # that often appears in infoboxes. 
        # A more aggressive way: label = label[:-1] if label.endswith('s')
        # But let's stick to the prompt's example: "Zoya Akhtars" -> "Zoya Akhtar"
        label = label[:-1]
    return label.strip()

def is_junk(id_str, label, is_terminal):
    """Checks if a node is junk."""
    label_clean = label.lower()
    # Numeric or too short
    if label.isdigit() or len(label) < 3:
        return True
    
    # Junk keywords
    junk_keywords = ["filmography", "discography", "list of", "awards", "nomination", "category:"]
    for kw in junk_keywords:
        if kw in label_clean or kw in id_str.lower():
            return True
            
    return False

def clean_data(nodes_file, edges_file, output_nodes, output_edges):
    if not os.path.exists(nodes_file) or not os.path.exists(edges_file):
        print("Input files not found.")
        return

    nodes = {} # slug -> {attrs}
    
    # 1. Load and Initial Clean
    with open(nodes_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            slug = row['ID']
            label = clean_label(row['Label'])
            is_terminal = row['IsTerminal'].lower() == 'true'
            
            if is_junk(slug, label, is_terminal):
                continue
                
            nodes[slug] = {
                'ID': slug,
                'Label': label,
                'IsTerminal': is_terminal,
                'URL': row['URL']
            }

    # 2. Deduplication: Terminal vs Linked
    # Create a map of CleanedName -> LinkedSlug
    name_to_linked_slug = {}
    for slug, attr in nodes.items():
        if not attr['IsTerminal']:
            name_to_linked_slug[attr['Label'].lower()] = slug

    id_map = {} # old_slug -> new_slug
    to_delete = set()

    for slug, attr in nodes.items():
        if attr['IsTerminal']:
            # If a terminal node has the same name as a linked entity, merge
            name_key = attr['Label'].lower()
            if name_key in name_to_linked_slug:
                id_map[slug] = name_to_linked_slug[name_key]
                to_delete.add(slug)
            else:
                id_map[slug] = slug
        else:
            id_map[slug] = slug

    # Remove merged terminal nodes
    for slug in to_delete:
        del nodes[slug]

    # 3. Load and Filter Edges
    new_edges = []
    with open(edges_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            src = row['Source']
            tgt = row['Target']
            
            # Map IDs if they were merged
            new_src = id_map.get(src)
            new_tgt = id_map.get(tgt)
            
            # Only keep if both exist in our cleaned nodes
            if new_src in nodes and new_tgt in nodes:
                # Avoid self-loops after merge
                if new_src != new_tgt:
                    new_edges.append({
                        'Source': new_src,
                        'Target': new_tgt,
                        'Type': row['Type'],
                        'Relation': row['Relation']
                    })

    # Deduplicate edges (e.g. if merge created duplicate relations)
    unique_edges = {}
    for edge in new_edges:
        key = (edge['Source'], edge['Target'], edge['Relation'])
        unique_edges[key] = edge

    # 4. Save
    with open(output_nodes, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['ID', 'Label', 'IsTerminal', 'URL'])
        writer.writeheader()
        for attr in nodes.values():
            writer.writerow(attr)

    with open(output_edges, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Source', 'Target', 'Type', 'Relation'])
        writer.writeheader()
        for edge in unique_edges.values():
            writer.writerow(edge)

    print(f"Cleanup complete: {len(nodes)} nodes left, {len(unique_edges)} edges left.")

if __name__ == "__main__":
    clean_data('bollywood_nodes.csv', 'bollywood_edges.csv', 'bollywood_nodes_cleaned.csv', 'bollywood_edges_cleaned.csv')
    # Overwrite original for visualization
    # os.replace('bollywood_nodes_cleaned.csv', 'bollywood_nodes.csv')
    # os.replace('bollywood_edges_cleaned.csv', 'bollywood_edges.csv')
