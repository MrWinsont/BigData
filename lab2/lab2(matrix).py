from collections import defaultdict
from typing import Iterator, Tuple, Dict, List

A = [[1, 2],
     [3, 4]]

B = [[5, 6],
     [7, 8]]

C = defaultdict(int)
n, p = len(A), len(B[0])
C = [[0] * p for i in range(n)]

def do_map(A, B) -> Iterator[Tuple[Tuple[str, str], Tuple[str, int, int]]]:
    n, m = len(A), len(A[0])
    m2, p = len(B), len(B[0])

    for i in range(n):
        for k in range(m):
            for j in range(p):
                yield ((i, j), ('A', k, A[i][k]))

    for k in range(m):
        for j in range(p):
            for i in range(n):
                yield ((i, j), ('B', k, B[k][j]))


grouped = defaultdict(list)
def do_shuffle(mapped):
    for key, value in mapped:
        grouped[key].append(value)


def do_reduce(grouped):
    for (i, j), values in grouped.items():
        a_values = {}
        b_values = {}

        for tag, k, v in values:
            if tag == 'A':
                a_values[k] = v
            elif tag == 'B':
                b_values[k] = v

        total = 0
        for k in a_values:
            if k in b_values:
                total += a_values[k] * b_values[k]
        C[i][j] = total


if __name__ == "__main__":
    do_shuffle(do_map(A, B))
    do_reduce(grouped)

    for row in C:
        print(row)