import csv

class BollywoodGraph:
    def __init__(self):
        # Nodes: { slug: { name: str, is_terminal: bool, canonical_url: str } }
        self.nodes = {}
        # Edges: [ (source, target, relation) ]
        self.edges = []

    def add_person(self, slug: str, name: str, is_terminal: bool = False, canonical_url: str = ""):
        """Adds or updates a person node in the graph."""
        if slug not in self.nodes:
            self.nodes[slug] = {
                'name': name,
                'is_terminal': is_terminal,
                'canonical_url': canonical_url
            }
        else:
            # Update attributes if they were missing
            if name and not self.nodes[slug].get('name'):
                self.nodes[slug]['name'] = name
            if is_terminal:
                self.nodes[slug]['is_terminal'] = is_terminal

    def add_marriage_or_blood_relation(self, source_slug: str, target_slug: str, relation_type: str):
        """Adds a directed edge representing a familial connection."""
        self.edges.append((source_slug, target_slug, relation_type))

    def export_to_csv(self, nodes_filename: str, edges_filename: str):
        """Exports the graph to CSV format suitable for Gephi or D3.js."""
        # Export Nodes
        with open(nodes_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['ID', 'Label', 'IsTerminal', 'URL'])
            writer.writeheader()
            for slug, attrs in self.nodes.items():
                writer.writerow({
                    'ID': slug,
                    'Label': attrs.get('name', slug),
                    'IsTerminal': attrs.get('is_terminal', False),
                    'URL': attrs.get('canonical_url', "")
                })
        
        # Export Edges
        with open(edges_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Source', 'Target', 'Type', 'Relation'])
            writer.writeheader()
            for source, target, relation in self.edges:
                writer.writerow({
                    'Source': source,
                    'Target': target,
                    'Type': 'Directed',
                    'Relation': relation
                })
            
        print(f"Graph exported: {len(self.nodes)} nodes, {len(self.edges)} edges.")

if __name__ == "__main__":
    # Quick test
    bg = BollywoodGraph()
    bg.add_person("Shah_Rukh_Khan", "Shah Rukh Khan")
    bg.add_person("Gauri_Khan", "Gauri Khan")
    bg.add_marriage_or_blood_relation("Shah_Rukh_Khan", "Gauri_Khan", "SPOUSE")
    bg.export_to_csv("test_nodes.csv", "test_edges.csv")
