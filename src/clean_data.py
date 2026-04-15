import csv
import re
import os
from collections import defaultdict

def clean_label(label):
    """Cleans names and labels."""
    if not label: return ""
    label = re.sub(r'\[\d+\]', '', label)
    label = label.strip()
    return label

def is_junk(id_str, label):
    """Checks if a node is junk."""
    if not label or not id_str:
        return True
    
    label_clean = label.strip()
    if not label_clean or label_clean.isdigit() or len(label_clean) < 2:
        return True
    
    # Check for symbols only
    if re.match(r'^[\W_]+$', label_clean):
        return True
        
    return False

def smart_merge(nodes_file, edges_file, output_nodes, output_edges):
    if not os.path.exists(nodes_file) or not os.path.exists(edges_file):
        print("Input files not found.")
        return

    # 1. Load Nodes
    nodes = {} # id -> attrs
    with open(nodes_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            node_id = row['ID']
            label = clean_label(row['Label'])
            if is_junk(node_id, label):
                continue
            nodes[node_id] = {
                'id': node_id,
                'label': label,
                'is_terminal': row['IsTerminal'].lower() == 'true',
                'url': row['URL']
            }

    # 2. Load Edges and build adjacency for neighbor check
    edges = []
    adj = defaultdict(set)
    with open(edges_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            src, tgt = row['Source'], row['Target']
            if src in nodes and tgt in nodes:
                edges.append(row)
                adj[src].add(tgt)
                adj[tgt].add(src)

    # 3. Identity Check & Merging
    # We'll use a Union-Find or a mapping to track winners
    parent = {node_id: node_id for node_id in nodes}

    def find(i):
        if parent[i] == i:
            return i
        parent[i] = find(parent[i])
        return parent[i]

    def union(i, j):
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            # Decide the winner
            node_i = nodes[root_i]
            node_j = nodes[root_j]
            
            # Winner selection rules
            # Rule 1: Blue (Linked) wins over Red (Terminal)
            if node_i['is_terminal'] and not node_j['is_terminal']:
                winner, loser = root_j, root_i
            elif not node_i['is_terminal'] and node_j['is_terminal']:
                winner, loser = root_i, root_j
            # Rule 2: Most connections wins
            else:
                conn_i = len(adj[root_i])
                conn_j = len(adj[root_j])
                if conn_i >= conn_j:
                    winner, loser = root_i, root_j
                else:
                    winner, loser = root_j, root_i
            
            parent[loser] = winner
            return True
        return False

    # Perform Merges
    node_list = list(nodes.keys())
    
    # Criteria 1: Exact URL Match
    url_to_id = {}
    for node_id in node_list:
        url = nodes[node_id]['url']
        if url and url.strip():
            if url in url_to_id:
                union(node_id, url_to_id[url])
            else:
                url_to_id[url] = node_id
    
    # Criteria 2: Name + Neighbor Match
    name_to_ids = defaultdict(list)
    for node_id in node_list:
        name_to_ids[nodes[node_id]['label'].lower()].append(node_id)
        
    for name, ids in name_to_ids.items():
        if len(ids) > 1:
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    id_a = ids[i]
                    id_b = ids[j]
                    # Check shared neighbors
                    if adj[id_a].intersection(adj[id_b]):
                        union(id_a, id_b)
                    # Criteria 3: Terminal vs Linked (same name)
                    # Rule: If names match and one is linked, one is terminal -> merge
                    elif nodes[id_a]['is_terminal'] != nodes[id_b]['is_terminal']:
                        union(id_a, id_b)

    # 4. Consolidate Nodes and Edges
    final_nodes = {}
    for node_id in nodes:
        root = find(node_id)
        if root not in final_nodes:
            final_nodes[root] = nodes[root]
            
    final_edges = []
    seen_edges = set()
    for edge in edges:
        src = find(edge['Source'])
        tgt = find(edge['Target'])
        
        # Remove self-loops and duplicates
        if src != tgt:
            edge_key = tuple(sorted((src, tgt))) + (edge['Relation'],)
            if edge_key not in seen_edges:
                final_edges.append({
                    'Source': src,
                    'Target': tgt,
                    'Type': edge['Type'],
                    'Relation': edge['Relation']
                })
                seen_edges.add(edge_key)

    # 5. Export
    with open(output_nodes, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['ID', 'Label', 'IsTerminal', 'URL'])
        writer.writeheader()
        for node in final_nodes.values():
            writer.writerow({
                'ID': node['id'],
                'Label': node['label'],
                'IsTerminal': node['is_terminal'],
                'URL': node['url']
            })

    with open(output_edges, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Source', 'Target', 'Type', 'Relation'])
        writer.writeheader()
        for edge in final_edges:
            writer.writerow(edge)

    print(f"Smart Merge complete: {len(final_nodes)} nodes, {len(final_edges)} edges.")

if __name__ == "__main__":
    smart_merge('bollywood_nodes.csv', 'bollywood_edges.csv', 'bollywood_nodes_cleaned.csv', 'bollywood_edges_cleaned.csv')
    # Overwrite originals
    os.replace('bollywood_nodes_cleaned.csv', 'bollywood_nodes.csv')
    os.replace('bollywood_edges_cleaned.csv', 'bollywood_edges.csv')
    print("Files updated with Smart Merge logic.")
