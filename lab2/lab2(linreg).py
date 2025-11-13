from collections import defaultdict
from typing import Iterator, Tuple, Dict, List


def do_map(data: List[Tuple[float, float]]) -> Iterator[Tuple[str, float]]:
    for x, y in data:
        yield ("sum_x", x)
        yield ("sum_y", y)
        yield ("sum_xy", x * y)
        yield ("sum_x2", x * x)
        yield ("n", 1)


grouped = defaultdict(list)
def do_shuffle(mapped_data: Iterator[Tuple[str, float]]):
    for key, value in mapped_data:
        grouped[key].append(value)


def do_reduce(grouped_data: Dict[str, List[float]]):
    reduced = {}
    for key, values in grouped_data.items():
        reduced[key] = sum(values)

    sum_x = reduced["sum_x"]
    sum_y = reduced["sum_y"]
    sum_xy = reduced["sum_xy"]
    sum_x2 = reduced["sum_x2"]
    n = reduced["n"]

    a = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
    b = (sum_y - a * sum_x) / n
    return a, b


if __name__ == "__main__":
    data = [
        (1.02, 2.7),
        (2.6, 1),
        (5, 4.5),
        (7.36, 2),
        (5.55, 9),
        (7.25, 6),
        (6.75, 3.44)
    ]

    do_shuffle(do_map(data))
    a, b = do_reduce(grouped)

    print(f"a = {a:.4f}")
    print(f"b = {b:.4f}")

    x_test = 7
    y_pred = a * x_test + b
    print(f"x={x_test}: {y_pred:.2f}")