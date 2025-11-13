import os
import json
from collections import defaultdict
from typing import Iterator, Tuple, Dict, List


def do_map(data) -> Iterator[Tuple[Tuple[str, str], int]]:
    product_type = str(data.get("data").get("productTypeId"))
    color = str(data.get("data").get("baseColour"))
    if product_type and color:
        print(product_type, color)
        yield ((product_type, color), 1)


grouped = defaultdict(list)
def do_shuffle(mapped_data: Iterator[Tuple[Tuple[str, str], int]]):
    for key, value in mapped_data:
        grouped[key].append(value)


def do_reduce(grouped_data: Dict[Tuple[str, str], List[int]]) -> Iterator[Tuple[str, str, int]]:
    for (product_type, color), values in grouped_data.items():
        yield (product_type, color, sum(values))


if __name__ == "__main__":
    directory = "styles"
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
            do_shuffle(do_map(data))

    reduced = do_reduce(grouped)

    for product_type, color, count in reduced:
        print(f"{product_type:15}  {color:15}  {count}")

