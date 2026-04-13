import csv
import json
import os

def generate_visualization(nodes_file, edges_file, output_html):
    nodes = []
    edges = []
    degrees = {}
    
    # Process Edges first to calculate degrees
    if not os.path.exists(edges_file):
        print(f"Error: {edges_file} not found.")
        return

    temp_edges = []
    with open(edges_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            src, tgt = row['Source'], row['Target']
            temp_edges.append(row)
            degrees[src] = degrees.get(src, 0) + 1
            degrees[tgt] = degrees.get(tgt, 0) + 1

    # Read Nodes
    if not os.path.exists(nodes_file):
        print(f"Error: {nodes_file} not found.")
        return

    with open(nodes_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            is_terminal = row['IsTerminal'].lower() == 'true'
            color = '#ff9999' if is_terminal else '#97c2fc'
            
            # Hub highlighting: larger size if degree > 5
            degree = degrees.get(row['ID'], 0)
            size = 20
            if is_terminal: size = 10
            if degree > 5: size = 40
            
            node_entry = {
                'id': row['ID'],
                'color': color,
                'title': f"Name: {row['Label']}<br>Connections: {degree}<br>Type: {'Terminal' if is_terminal else 'Linked'}",
                'shape': 'dot',
                'size': size
            }
            
            # ONLY show label if NOT terminal
            if not is_terminal:
                node_entry['label'] = row['Label']
            
            nodes.append(node_entry)
            
    for row in temp_edges:
        edges.append({
            'from': row['Source'],
            'to': row['Target'],
            'label': row['Relation'],
            'arrows': 'to',
            'font': {'align': 'middle', 'size': 10}
        })
            
    # HTML Template with Vis.js
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Bollywood Genealogical Map (Cleaned)</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        #mynetwork {{
            width: 100%;
            height: 90vh;
            border: 1px solid #ddd;
            background-color: #ffffff;
        }}
        .legend {{
            padding: 15px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            border-bottom: 2px solid #eee;
        }}
        .legend-item {{
            margin-right: 20px;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="legend">
        <h2 style="margin:0 0 10px 0;">Bollywood Dynasty Mapper: Cleaned & Filtered</h2>
        <span class="legend-item"><span style="color:#97c2fc">&#9679;</span> Blue: Linked Entity (Labeled)</span>
        <span class="legend-item"><span style="color:#ff9999">&#9679;</span> Red: Terminal Node (Hover to see name)</span>
        <span class="legend-item"><span style="font-size: 1.2em;">&#9673;</span> Large Hub: >5 Connections</span>
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
                font: {{ size: 12, color: '#333' }},
                borderWidth: 1,
                borderWidthSelected: 4
            }},
            edges: {{
                width: 1.5,
                color: {{ color: '#848484', opacity: 0.6 }},
                smooth: {{ type: 'cubicBezier', forceDirection: 'none', roundness: 0.5 }}
            }},
            physics: {{
                solver: 'forceAtlas2Based',
                forceAtlas2Based: {{
                    gravitationalConstant: -150,
                    centralGravity: 0.005,
                    springLength: 100,
                    springConstant: 0.18,
                    avoidOverlap: 1.0
                }},
                maxVelocity: 50,
                minVelocity: 0.1,
                stabilization: {{ iterations: 150 }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200,
                hideEdgesOnDrag: true,
                navigationButtons: true
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
