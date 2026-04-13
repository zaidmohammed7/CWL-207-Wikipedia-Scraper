# Bollywood Genealogical Mapper

An advanced Wikipedia scraper and graph generator designed to map familial connections (blood and marriage) within the Indian film industry. This project uses the MediaWiki API for seeding and BeautifulSoup for targeted Infobox scraping, ensuring entity uniqueness via canonical Wikipedia slugs.

## 🚀 Features
- **Deterministic Disambiguation**: Identifies people by unique Wikipedia PageIDs/slugs, not ambiguous name strings.
- **Familial Edge Scope**: Maps Parent, Child, Spouse, Sibling, and Relative connections exclusively.
- **Recursive BFS Traversal**: Scrapes up to a depth of 3 from initial seed categories.
- **Terminal Node Detection**: Identifies relatives mentioned in plain text (without Wiki links) as Terminal Nodes for a complete graph.
- **Interactive Visualization**: Generates a zoomable, color-coded HTML network map using Vis.js.

## 📁 Repository Structure
- `src/wiki_api.py`: Handles category crawling and URL canonicalization via MediaWiki API.
- `src/scraper.py`: Extracts relationship data from Wikipedia Infoboxes using BeautifulSoup.
- `src/graph_builder.py`: Manages a native Graph structure (nodes/edges) and exports to CSV.
- `src/main.py`: The orchestrator that runs the BFS recursive crawl.
- `src/visualize.py`: Generates the interactive HTML visualization from the exported data.

## 🛠️ Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/zaidmohammed7/CWL-207-Wikipedia-Scraper.git
   ```
2. Install dependencies:
   ```bash
   pip install requests beautifulsoup4
   ```

## 📊 How to Use
1. **Run the Full Crawl**:
   Execute the orchestrator to scrape Wikipedia and generate the CSV datasets (`bollywood_nodes.csv` and `bollywood_edges.csv`).
   ```bash
   python src/main.py
   ```
2. **Generate Visualization**:
   Run the visualization script to create the interactive HTML map.
   ```bash
   python src/visualize.py
   ```
3. **View the Map**:
   Open `bollywood_dynasties.html` in your web browser.

## 🎨 Visualization Key
- 🔵 **Blue Nodes**: Linked Wikipedia Entities (have their own pages).
- 🔴 **Red Nodes**: Terminal Nodes (mentioned in relatives list but no individual Wiki page).
- ➡️ **Edges**: Directed arrows indicating relationship hierarchy (e.g., Parent → Child).

## 📄 License
Created for CWL 207.
