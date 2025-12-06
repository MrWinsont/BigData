import sqlite3
import json
import math

DB = "search.db"

def get_postings_for_term(term):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    row = c.execute("SELECT id FROM terms WHERE term=?", (term,)).fetchone()
    if not row:
        return []
    term_id = row[0]
    rows = c.execute("SELECT doc_id, freq FROM postings WHERE term_id=?", (term_id,)).fetchall()
    conn.close()
    return [(doc_id, freq) for doc_id, freq in rows]

def compute_tf_idf_scores(query_terms):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    N = c.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    scores = {}
    for term in query_terms:
        row = c.execute("SELECT id FROM terms WHERE term=?", (term,)).fetchone()
        if not row: continue
        tid = row[0]
        df = c.execute("SELECT COUNT(DISTINCT doc_id) FROM postings WHERE term_id=?", (tid,)).fetchone()[0]
        idf = math.log((N+1) / (df+1)) + 1
        for doc_id, freq, in c.execute("SELECT doc_id, freq FROM postings WHERE term_id=?", (tid,)):
            tf = 1 + math.log(freq)
            scores.setdefault(doc_id, 0.0)
            scores[doc_id] += tf * idf
    conn.close()
    # normalize by doc length (optional)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def search_taat(query):
    terms = [t for t in query.lower().split() if t]
    return compute_tf_idf_scores(terms)

def search_daat_and(query):
    terms = [t for t in query.lower().split() if t]
    lists = []
    for t in terms:
        lists.append(sorted(get_postings_for_term(t), key=lambda x: x[0]))
    if not lists: return []
    idxs = [0]*len(lists)
    result = []
    while True:
        try:
            cur_ids = [lists[i][idxs[i]][0] for i in range(len(lists))]
        except IndexError:
            break
        if all(x == cur_ids[0] for x in cur_ids):
            doc_id = cur_ids[0]
            freq_sum = sum(lists[i][idxs[i]][1] for i in range(len(lists)))
            result.append((doc_id, freq_sum))
            for i in range(len(idxs)): idxs[i] += 1
        else:
            min_val = min(cur_ids)
            for i in range(len(idxs)):
                if lists[i][idxs[i]][0] == min_val:
                    idxs[i] += 1
    result.sort(key=lambda x: x[1], reverse=True)
    return result


if __name__ == "__main__":
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    query = input("Введите запрос: ").strip()

    print("\nTAAT")
    results = search_taat(query)
    for doc_id, score in results[:]:
        url = c.execute("SELECT url FROM documents WHERE id=?", (doc_id,)).fetchone()[0]
        print(f"{url} — score={score:.4f}")

    print("\nDAAT")
    results = search_daat_and(query)
    for doc_id, score in results[:]:
        url = c.execute("SELECT url FROM documents WHERE id=?", (doc_id,)).fetchone()[0]
        print(f"{url} — freq_sum={score}")

    conn.close()