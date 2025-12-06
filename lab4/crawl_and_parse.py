import requests
from bs4 import BeautifulSoup
import sqlite3
from urllib.parse import urljoin, urlparse
import re
import time

DB = "search.db"

WIKI_DOMAIN = "en.wikipedia.org"

def normalize_text(s):
    s = s.lower()
    s = re.sub(r'[^a-zа-я0-9ё\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.executescript("""
    DROP TABLE IF EXISTS documents;
    DROP TABLE IF EXISTS links;

    CREATE TABLE documents (
        id INTEGER PRIMARY KEY,
        url TEXT UNIQUE,
        title TEXT,
        content TEXT
    );

    CREATE TABLE links (
        from_doc INTEGER,
        to_doc INTEGER,
        FOREIGN KEY(from_doc) REFERENCES documents(id),
        FOREIGN KEY(to_doc) REFERENCES documents(id)
    );
    """)
    conn.commit()
    conn.close()


def save_document(url, title, content):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO documents(url,title,content) VALUES(?,?,?)",
              (url, title, content))
    conn.commit()

    row = c.execute("SELECT id FROM documents WHERE url=?", (url,)).fetchone()
    conn.close()
    return row[0] if row else None


def save_link(from_id, to_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO links(from_doc,to_doc) VALUES(?,?)", (from_id, to_id))
    conn.commit()
    conn.close()


def parse_page(url):
    try:
        headers = {"User-Agent": "MiniSearchBot/1.0 (student project)"}
        r = requests.get(url, timeout=10, headers=headers)

        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.title.string.replace(" - Wikipedia", "") if soup.title else url

        for s in soup(["script", "style", "noscript", "table"]):
            s.extract()

        text = soup.get_text(separator=" ")
        text = normalize_text(text)

        outlinks = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("/wiki/") and ":" not in href:
                full = urljoin("https://en.wikipedia.org", href)
                outlinks.append(full)

        outlinks = list(set(outlinks))

        return title, text, outlinks

    except Exception as e:
        print("ERROR fetching", url, "->", e)
        return None, None, []


def crawl(seed_urls, max_pages=50):
    init_db()
    visited = set()
    queue = list(seed_urls)

    while queue and len(visited) < max_pages:
        url = queue.pop(0)

        if urlparse(url).netloc != WIKI_DOMAIN:
            continue
        if url in visited:
            continue

        print(f"[{len(visited)+1}/{max_pages}] Fetch:", url)
        title, text, links = parse_page(url)
        if not text or len(text) < 50:
            visited.add(url)
            continue

        from_id = save_document(url, title, text)
        visited.add(url)

        for l in links:
            if urlparse(l).netloc == WIKI_DOMAIN:
                to_id = save_document(l, None, "")
                save_link(from_id, to_id)
                if l not in visited and l not in queue:
                    queue.append(l)

        time.sleep(0.7)

    print("Crawling finished.")


if __name__ == "__main__":
    seeds = [
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://en.wikipedia.org/wiki/Neural_network",
        "https://en.wikipedia.org/wiki/Deep_learning"
    ]

    crawl(seeds, max_pages=30)