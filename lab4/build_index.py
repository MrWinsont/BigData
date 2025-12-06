import sqlite3
import re
import json

DB = "search.db"
GRAPH_OUT = "graph.jsonl"


def tokenize(text):
    return re.findall(r"[a-zA-Zа-яА-Я0-9ёЁ]+", text.lower())


def build_index():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("DELETE FROM terms")
    c.execute("DELETE FROM postings")
    conn.commit()

    docs = c.execute("""
        SELECT id, url, content
        FROM documents
    """).fetchall()

    for doc_id, url, content in docs:
        if not content:
            content = ""

        tokens = tokenize(content)
        positions = {}

        for pos, t in enumerate(tokens):
            positions.setdefault(t, []).append(pos)

        for term, pos_list in positions.items():

            # term
            c.execute("INSERT OR IGNORE INTO terms(term) VALUES(?)", (term,))
            term_id = c.execute(
                "SELECT id FROM terms WHERE term=?", (term,)
            ).fetchone()[0]

            # posting
            c.execute("""
                INSERT INTO postings(term_id, doc_id, freq, positions)
                VALUES (?, ?, ?, ?)
            """, (term_id, doc_id, len(pos_list), json.dumps(pos_list)))

    conn.commit()

    print("Building PageRank graph...")

    with open(GRAPH_OUT, "w", encoding="utf-8") as f:
        for doc_id, url, content in docs:
            rows = c.execute(
                "SELECT to_doc FROM links WHERE from_doc=?",
                (doc_id,)
            ).fetchall()

            out_links = [r[0] for r in rows]

            node = {
                "rank": 1.0,
                "out": out_links,
                "title": url
            }

            f.write(f"{doc_id}\t{json.dumps(node, ensure_ascii=False)}\n")

    conn.close()
    print("Done! graph.jsonl created.")


if __name__ == "__main__":
    build_index()