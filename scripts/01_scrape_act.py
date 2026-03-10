import requests
from bs4 import BeautifulSoup
import re

URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202401689"

headers = {"User-Agent": "Mozilla/5.0 (academic research)"}
response = requests.get(URL, headers=headers)
soup = BeautifulSoup(response.content, "lxml")

# Remove boilerplate nav elements
for tag in soup(["script", "style", "nav", "footer", "header"]):
    tag.decompose()

# Extract article-level text with article numbers preserved
articles = []
for elem in soup.find_all(["p", "h1", "h2", "h3", "h4"]):
    text = elem.get_text(separator=" ", strip=True)
    if text:
        articles.append(text)

full_text = "\n\n".join(articles)

# Save plain text for GraphRAG input
with open("../data/input/eu_ai_act.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

print(f"Saved {len(full_text)} characters, {len(articles)} paragraphs")