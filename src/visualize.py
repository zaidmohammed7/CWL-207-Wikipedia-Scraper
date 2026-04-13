import csv
import json
import os

def generate_visualization(nodes_file, edges_file, output_html):
    nodes = []
    edges = []
    
    # Read Nodes
    if not os.path.exists(nodes_file):
        print(f"Error: {nodes_file} not found.")
        return

    with open(nodes_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Color coding: Linked = Blue/Green, Terminal = Red/Orange
            is_terminal = row['IsTerminal'].lower() == 'true'
            color = '#ff9999' if is_terminal else '#97c2fc'
            
            nodes.append({
                'id': row['ID'],
                'label': row['Label'],
                'color': color,
                'title': f"Relationship: {'Terminal' if is_terminal else 'Linked'}<br>URL: {row['URL']}",
                'shape': 'dot',
                'size': 15 if is_terminal else 25
            })
            
    # Read Edges
    if not os.path.exists(edges_file):
        print(f"Error: {edges_file} not found.")
        return

    with open(edges_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            edges.append({
                'from': row['Source'],
                'to': row['Target'],
                'label': row['Relation'],
                'arrows': 'to',
                'font': {'align': 'middle'}
            })
            
    # HTML Template with Vis.js
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Bollywood Genealogical Map</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        #mynetwork {{
            width: 100%;
            height: 90vh;
            border: 1px solid lightgray;
            background-color: #f5f5f5;
        }}
        .legend {{
            padding: 10px;
            font-family: sans-serif;
        }}
        .legend-item {{
            margin-right: 20px;
        }}
    </style>
</head>
<body>
    <div class="legend">
        <h2>Bollywood Dynasty Mapper</h2>
        <span class="legend-item"><span style="color:#97c2fc">&#9679;</span> Linked Entity (Wikipedia Page)</span>
        <span class="legend-item"><span style="color:#ff9999">&#9679;</span> Terminal Node (No Wiki Link)</span>
        <p><i>Depth: 3 | Seeded from 7 Categories</i></p>
    </div>
    <div id="mynetwork"></div>
    <script type="text/javascript">
        var nodes = new vis.DataSet({json.dumps(nodes)});
        var edges = new vis.DataSet({json.dumps(edges)});

        var container = document.getElementById('mynetwork');
        var data = {{
            nodes: nodes,
            edges: edges
        }};
        var options = {{
            nodes: {{
                font: {{ size: 14, color: '#333' }},
                borderWidth: 2
            }},
            edges: {{
                width: 2,
                color: {{ inherit: 'from' }},
                smooth: {{ type: 'continuous' }}
            }},
            physics: {{
                stabilization: false,
                barnesHut: {{
                    gravitationalConstant: -2000,
                    springLength: 150
                }}
            }},
            interaction: {{
                hover: true,
                navigationButtons: true,
                keyboard: true
            }}
        }};
        var network = new vis.Network(container, data, options);
    </script>
</body>
</html>
"""
    
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"Visualization created: {output_html}")

if __name__ == "__main__":
    generate_visualization('bollywood_nodes.csv', 'bollywood_edges.csv', 'bollywood_dynasties.html')
