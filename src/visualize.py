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
            if degree > 10: size = 50 # Bigger hubs for "Big Data"
            
            node_entry = {
                'id': row['ID'],
                'color': color,
                'title': f"Name: {row['Label']}<br>Connections: {degree}<br>Type: {'Terminal' if is_terminal else 'Linked'}",
                'shape': 'dot',
                'size': size
            }
            
            if not is_terminal:
                node_entry['label'] = row['Label']
            
            nodes.append(node_entry)
            
    for row in temp_edges:
        edges.append({
            'from': row['Source'],
            'to': row['Target'],
            'label': row['Relation'],
            'arrows': 'to',
            'font': {'align': 'middle', 'size': 10},
            'smooth': False # Optimization 1: Straight lines
        })
            
    # HTML Template with Vis.js Big Data Settings
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Bollywood Genealogical Map (Optimized)</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        body {{ margin: 0; overflow: hidden; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f6; }}
        #mynetwork {{
            width: 100vw;
            height: 100vh;
        }}
        .overlay {{
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 10;
            background: rgba(255, 255, 255, 0.9);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            backdrop-filter: blur(5px);
            max-width: 320px;
        }}
        #loading-overlay {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(255,255,255,0.8);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 100;
        }}
        .spinner {{
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #97c2fc;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        
        .search-container {{ margin-top: 15px; display: flex; gap: 8px; }}
        #search-input {{ flex-grow: 1; padding: 8px 12px; border: 1px solid #ccc; border-radius: 6px; }}
        #search-btn {{ padding: 8px 16px; background: #97c2fc; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }}
    </style>
</head>
<body>
    <div id="loading-overlay">
        <div class="spinner"></div>
        <h2 style="margin-top:20px;">Calculating Family Trees...</h2>
        <p>Optimizing layout for {len(nodes)} members</p>
    </div>

    <div class="overlay">
        <h2 style="margin:0 0 5px 0; font-size: 1.2em;">Bollywood Dynasty Map</h2>
        <div class="legend-content">
            <span style="font-size: 0.9em;"><span style="color:#97c2fc">&#9679;</span> Linked Entity</span>
            <span style="font-size: 0.9em; margin-left: 10px;"><span style="color:#ff9999">&#9679;</span> Terminal Node</span>
        </div>
        
        <div class="search-container">
            <input type="text" id="search-input" list="names-list" placeholder="Search a family member...">
            <datalist id="names-list">
                {"".join([f'<option value="{n["label"]}">' for n in nodes if 'label' in n])}
            </datalist>
            <button id="search-btn">Go</button>
        </div>
    </div>

    <div id="mynetwork"></div>

    <script type="text/javascript">
        var nodes = new vis.DataSet({json.dumps(nodes)});
        var edges = new vis.DataSet({json.dumps(edges)});

        var container = document.getElementById('mynetwork');
        var data = {{ nodes: nodes, edges: edges }};
        var options = {{
            nodes: {{
                font: {{ size: 14, color: '#333' }},
                borderWidth: 1.5,
                borderWidthSelected: 5
            }},
            edges: {{
                width: 1.2,
                color: {{ color: '#aaa', opacity: 0.4 }},
                smooth: false // Performance optimization: Straight lines
            }},
            physics: {{
                solver: 'forceAtlas2Based',
                forceAtlas2Based: {{
                    gravitationalConstant: -150,
                    centralGravity: 0.01,
                    springLength: 100,
                    avoidOverlap: 1.0
                }},
                stabilization: {{ 
                    enabled: true,
                    iterations: 1500, // Pre-calculate deeply
                    updateInterval: 50
                }}
            }},
            interaction: {{
                hover: true,
                hideEdgesOnDrag: true, // Performance optimization
                tooltipDelay: 100,
                navigationButtons: true
            }}
        }};
        
        var network = new vis.Network(container, data, options);

        // Optimization: Freeze physics after stabilization to stop the "jumping"
        network.on("stabilizationIterationsDone", function () {{
            network.setOptions({{ physics: false }});
            document.getElementById('loading-overlay').style.display = 'none';
            console.log("Physics frozen. Stability reached.");
        }});

        function doSearch() {{
            var name = document.getElementById('search-input').value;
            var foundNode = nodes.get().find(n => n.label === name || n.id === name);
            if (foundNode) {{
                network.focus(foundNode.id, {{
                    scale: 1.0,
                    animation: {{ duration: 1000, easingFunction: 'easeInOutQuad' }}
                }});
                network.selectNodes([foundNode.id]);
            }}
        }}

        document.getElementById('search-btn').onclick = doSearch;
        document.getElementById('search-input').onkeypress = function(e) {{ if (e.which == 13) {{ doSearch(); }} }};
    </script>
</body>
</html>
"""
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"Optimized Visualization created: {output_html}")

if __name__ == "__main__":
    generate_visualization('bollywood_nodes.csv', 'bollywood_edges.csv', 'bollywood_dynasties.html')
