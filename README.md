# Bollywood Genealogical Mapper

An advanced Wikipedia scraper and graph generator designed to map familial connections (blood and marriage) within the Indian film industry. This project uses the MediaWiki API for seeding and BeautifulSoup for targeted Infobox scraping, ensuring entity uniqueness via canonical Wikipedia slugs.

## 🚀 Features
- **Deterministic Disambiguation**: Identifies people by unique Wikipedia PageIDs/slugs, not ambiguous name strings.
- **Familial Edge Scope**: Maps Parent, Child, Spouse, Sibling, and Relative connections exclusively.
- **Recursive BFS Traversal**: Scrapes major Indian film lists and families (depth-limited).
- **Smart Merge Deduplication**: Automatically resolves duplicate entries using URL matching and neighbor overlap algorithms.
- **Terminal Node Detection**: Identifies relatives mentioned in plain text (without Wiki links) as Terminal Nodes for a complete graph.
- **Optimized Visualization**: High-performance "Big Data" settings for Vis.js with physics-freezing and straight-edge rendering.

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
   Execute the orchestrator to scrape Wikipedia and generate the CSV datasets.
   > [!NOTE]
   > The discovery phase uses aggressive list-based seeding. The full crawl can take several minutes to an hour depending on network conditions due to the mandatory 1-second delay between requests.
   ```bash
   python -m src.main
   ```
2. **Generate Visualization**:
   Run the visualization script to create the interactive HTML map.
   ```bash
   python src/visualize.py
   ```
3. **View the Map**:
   Open `bollywood_dynasties.html`. 
   > [!WARNING]
   > With 1,000+ members, the page will show a "**Calculating Family Trees...**" overlay while it computes the optimized layout. This can take 10-30 seconds. The map will "freeze" once stable for maximum responsiveness.

## 🎨 Visualization Key
- 🔵 **Blue Nodes**: Linked Wikipedia Entities (have their own pages).
- 🔴 **Red Nodes**: Terminal Nodes (mentioned in relatives list but no individual Wiki page).
- ➡️ **Edges**: Directed arrows indicating relationship hierarchy (e.g., Parent → Child).

## 📄 License
Created for CWL 207.
