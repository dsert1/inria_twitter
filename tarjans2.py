import pandas as pd
import numpy as np
import argparse
import numba
from tqdm import tqdm


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tarjan\'s Algorithm')
    parser.add_argument('-i', '--input', type=str, required=True)
    args = parser.parse_args()
    input_file_path = args.input

    # Read input file as parquet
    df = pd.read_parquet(input_file_path)

    g = numba.typed.Dict.empty(
      key_type=numba.types.int64,
      value_type=numba.types.ListType(numba.types.int64)
    )
    d = numba.typed.Dict.empty(
        key_type=numba.types.int64,
        value_type=numba.types.int64
    )
    low = numba.typed.Dict.empty(
        key_type=numba.types.int64,
        value_type=numba.types.int64
    )
    scc = numba.typed.Dict.empty(
        key_type=numba.types.int64,
        value_type=numba.types.int64
    )
    stacked = numba.typed.Dict.empty(
        key_type=numba.types.int64,
        value_type=numba.types.boolean
    )

    stack = numba.typed.List.empty_list(numba.types.int64)
    ticks = numba.types.int64(0)
    current_scc = numba.types.int64(0)

    @numba.njit
    def tarjan(u, d, low, stack, scc, ticks, current_scc, g):
        u = int(u)
        d[int(u)] = ticks
        low[int(u)] = ticks
        ticks += 1
        stack.append(int(u))

        out = g.get(u, numba.typed.List.empty_list(numba.types.int64))

        for v in out:
            v = int(v)
            if d.get(v, 0) == 0:
                tarjan(v, d, low, stack, scc, ticks, current_scc, g)
                low[u] = min(low[u], low[v])
            elif v in stack:
                low[u] = min(low[u], low[v])

        print(d[u], low[u])
        print(d[u] == low[u])
        u = int(u)
        if d[u] == low[u]:
            v = 0
            while u != v:
                v = stack.pop()
                v = int(v)
                scc[v] = current_scc

            current_scc += 1

    edges = numba.typed.List.empty_list(numba.types.Tuple((numba.types.int64, numba.types.int64)))
    unique_nodes = set()

    line_counter = 0
    NA_counter = 0

    for index, row in tqdm(df.iterrows()):
        # address 1 is a miner address
        if pd.isna(row["addr_id1"]) and not pd.isna(row["addr_id2"]):
            v = int(row["addr_id2"])
            edges.append((v, v))
            unique_nodes.add(v)
            NA_counter += 1
        # address 2 is a miner address
        elif not pd.isna(row["addr_id1"]) and pd.isna(row["addr_id2"]):
            u = int(row["addr_id1"])
            edges.append((u, u))
            unique_nodes.add(u)
            NA_counter += 1
        # both addresses are valid
        else:
            u = int(row["addr_id1"])
            v = int(row["addr_id2"])
            edges.append((u, v))
            unique_nodes.add(u)
            unique_nodes.add(v)
        line_counter += 1

    print("Number of lines: ", line_counter)
    print("Number of NAs: ", NA_counter)
    print("Number of unique nodes:", len(unique_nodes))

    # construct graph
    for u, v in tqdm(edges):
        u, v = int(u), int(v)
        if u not in g:
            g[u] = numba.typed.List.empty_list(numba.types.int64)
        g[u].append(v)

    # add isolated nodes to the processing maps
    for node in tqdm(unique_nodes):
        print("Node:", node)
        print("d:", d)
        # print("d[node]: ", d[node])
        node = int(node)
        if int(node) not in d:
            tarjan(node, d, low, stack, scc, ticks, current_scc, g)

    ticks = 1
    current_scc = 1

    # run Tarjan's algorithm on each unvisited node
    for node in tqdm(g):
        node = int(node)
        if d[node] == 0:
            tarjan(node, d, low, stack, scc, ticks, current_scc, g)

    output_nodes = numba.types.int64(0)

    with open("output.txt", "w") as f:
        for node in tqdm(scc):
            output_nodes += 1
            f.write(f"Node {node} belongs to SCC {scc[node]}\n")

    print("Number of nodes in output:", output_nodes)
