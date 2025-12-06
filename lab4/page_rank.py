import json
from collections import defaultdict

DAMPING = 0.85


def parse_jsonl_line(line: str):
    doc_id, payload = line.split("\t", 1)
    return doc_id, json.loads(payload)


def map_phase(nodes):
    emitted = defaultdict(list)

    for doc_id, data in nodes.items():
        rank = data.get("rank", 1.0)
        outs = data.get("out", [])

        emitted[doc_id].append(("NODE", data))

        if outs:
            share = rank / len(outs)
            for dest in outs:
                emitted[dest].append(("PR", share))
        else:
            pass

    return emitted


def reduce_phase(emitted):
    new_nodes = {}

    for key, values in emitted.items():
        node = None
        sum_pr = 0.0

        for typ, val in values:
            if typ == "NODE":
                node = val
            else:  # PR contribution
                sum_pr += val

        if node is None:
            node = {"rank": 0.0, "out": []}

        new_rank = (1 - DAMPING) + DAMPING * sum_pr
        node["rank"] = new_rank
        new_nodes[key] = node

    return new_nodes


def load_jsonl(path):
    nodes = {}
    with open(path, "r", encoding="utf8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            doc_id, data = parse_jsonl_line(line)
            nodes[doc_id] = data
    return nodes


def write_jsonl(path, nodes):
    with open(path, "w", encoding="utf8") as f:
        for doc_id, data in nodes.items():
            f.write(f"{doc_id}\t{json.dumps(data, ensure_ascii=False)}\n")


def run_pagerank(input_file, iterations=10):
    nodes = load_jsonl(input_file)

    for i in range(iterations):
        print(f"Iteration {i+1}/{iterations}...")

        emitted = map_phase(nodes)
        nodes = reduce_phase(emitted)

        out_file = f"pagerank_{i+1}.jsonl"
        write_jsonl(out_file, nodes)

    print("Done.")
    return nodes


if __name__ == "__main__":
    run_pagerank("graph.jsonl", iterations=10)

