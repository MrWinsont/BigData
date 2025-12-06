import networkx as nx
import json

DAMPING = 0.85
ITERATIONS = 50
GRAPH_FILE = "graph.jsonl"


def load_graph(file_path):
    G = nx.DiGraph()
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            doc_id, data = line.split("\t", 1)
            data = json.loads(data)
            G.add_node(doc_id, rank=data.get("rank", 1.0), title=data.get("title", ""))
            for out in data.get("out", []):
                G.add_edge(doc_id, str(out))
    return G


def pregel_pagerank(G, iterations=ITERATIONS, damping=DAMPING):
    n = G.number_of_nodes()

    pr = {v: 1.0 / n for v in G.nodes()}

    for it in range(iterations):
        messages = {v: 0.0 for v in G.nodes()}
        dangling_sum = 0.0

        for v in G.nodes():
            out_nodes = list(G.successors(v))
            deg = len(out_nodes)
            if deg == 0:
                dangling_sum += pr[v]
            else:
                share = pr[v] / deg
                for w in out_nodes:
                    messages[w] += share

        for v in G.nodes():
            pr[v] = (1 - damping) / n + damping * (messages[v] + dangling_sum / n)

    for v in G.nodes():
        G.nodes[v]["rank"] = pr[v]

    return G


if __name__ == "__main__":
    G = load_graph(GRAPH_FILE)
    print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    G = pregel_pagerank(G, iterations=ITERATIONS, damping=DAMPING)

    top = sorted(G.nodes(data=True), key=lambda x: x[1]["rank"], reverse=True)[:]
    for doc_id, data in top:
        print(f"{data['title']} — PageRank={data['rank']:.4f}")