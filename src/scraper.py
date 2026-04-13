import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Tuple, Optional

class WikiScraper:
    BASE_URL = "https://en.wikipedia.org/wiki/"
    
    # Common relationship keywords to look for in parentheses
    RELATION_KEYWORDS = {
        'spouse': 'SPOUSE',
        'husband': 'SPOUSE',
        'wife': 'SPOUSE',
        'father': 'PARENT',
        'mother': 'PARENT',
        'son': 'CHILD',
        'daughter': 'CHILD',
        'brother': 'SIBLING',
        'sister': 'SIBLING',
        'cousin': 'COUSIN',
        'uncle': 'UNCLE',
        'aunt': 'AUNT',
        'nephew': 'NEPHEW',
        'niece': 'NIECE',
        'relative': 'RELATIVE'
    }

    TARGET_FIELDS = ['spouse', 'children', 'parents', 'relatives', 'family', 'father', 'mother']

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "BollywoodGenMapper/1.0 (https://github.com/example/repo)"
        })

    def get_page_html(self, slug: str) -> Optional[str]:
        """Fetches the HTML content of a Wikipedia page."""
        url = f"{self.BASE_URL}{slug.replace(' ', '_')}"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None

    def parse_relationship_type(self, text: str, default: str) -> str:
        """Parses relationship type from text (usually in parentheses)."""
        match = re.search(r'\(([^)]+)\)', text)
        if match:
            content = match.group(1).lower()
            for keyword, relation in self.RELATION_KEYWORDS.items():
                if keyword in content:
                    return relation
        return default

    def extract_family_data(self, slug: str) -> List[Dict]:
        """
        Scrapes the infobox for family relationships.
        Returns a list of dicts: {target: slug/id, relation: type, is_terminal: bool, name: str}
        """
        html = self.get_page_html(slug)
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        infobox = soup.find('table', class_='infobox')
        if not infobox:
            return []

        relationships = []
        
        # Iterate through all rows in infobox
        rows = infobox.find_all('tr')
        for row in rows:
            label_cell = row.find('th', class_='infobox-label')
            data_cell = row.find('td', class_='infobox-data')
            
            if not label_cell or not data_cell:
                continue
                
            label_text = label_cell.get_text(strip=True).lower()
            
            # Check if this row is one of our target family fields
            target_field = None
            for field in self.TARGET_FIELDS:
                if field in label_text:
                    target_field = field
                    break
            
            if not target_field:
                continue

            # Identify the default relation based on the label
            default_relation = 'RELATIVE'
            if 'spouse' in label_text: default_relation = 'SPOUSE'
            elif 'children' in label_text: default_relation = 'CHILD'
            elif 'parents' in label_text or 'father' in label_text or 'mother' in label_text: default_relation = 'PARENT'

            # Extract names and links from the data cell
            # Wikipedia often uses bulleted lists (ul/li) or just line breaks (br)
            elements = data_cell.find_all(['a', 'li'])
            if not elements:
                # Might just be plain text in the cell
                self._process_text_node(data_cell, slug, default_relation, relationships)
            else:
                for elem in elements:
                    if elem.name == 'li':
                        # Look for link inside li
                        link = elem.find('a')
                        if link:
                            self._process_link_node(link, elem.get_text(), default_relation, relationships)
                        else:
                            # Plain text in li - Terminal Node
                            self._process_text_node(elem, slug, default_relation, relationships)
                    elif elem.name == 'a':
                        # Check if parent is li (to avoid double counting)
                        if not elem.find_parent('li'):
                            self._process_link_node(elem, elem.parent.get_text() if elem.parent else elem.get_text(), default_relation, relationships)

        # Cap at 50 to prevent infinite loops / extreme pages
        return relationships[:50]

    def _process_link_node(self, link, full_text, default_relation, results):
        href = link.get('href', '')
        if href.startswith('/wiki/') and not ':' in href:
            target_slug = href.replace('/wiki/', '')
            relation_type = self.parse_relationship_type(full_text, default_relation)
            results.append({
                'target': target_slug,
                'relation': relation_type,
                'is_terminal': False,
                'name': link.get_text(strip=True)
            })

    def _process_text_node(self, element, source_slug, default_relation, results):
        text = element.get_text(strip=True)
        # Clean up text (remove citations, etc)
        text = re.sub(r'\[\d+\]', '', text)
        if text and len(text) < 50: # Avoid capturing long descriptive sentences
            relation_type = self.parse_relationship_type(text, default_relation)
            # Generate a terminal ID
            clean_name = re.sub(r'\W+', '_', text).strip('_')
            terminal_id = f"terminal_{source_slug}_{clean_name}"
            results.append({
                'target': terminal_id,
                'relation': relation_type,
                'is_terminal': True,
                'name': text
            })

if __name__ == "__main__":
    scraper = WikiScraper()
    print("Testing extraction for Shah Rukh Khan...")
    data = scraper.extract_family_data("Shah_Rukh_Khan")
    for d in data:
        print(f"-> {d['relation']}: {d['name']} ({'Terminal' if d['is_terminal'] else 'Linked'})")
