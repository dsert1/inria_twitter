import pandas as pd
import numpy as np
import argparse
from tqdm import tqdm
from collections import defaultdict

def construct_graph(df):
    edges = []
    unique_nodes = set()
    line_counter = 0
    NA_counter = 0
    for _, row in tqdm(df.iterrows()):
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
    return edges, unique_nodes, line_counter, NA_counter

def tarjan(graph):
    index_counter = [0]
    stack = []
    lowlinks = {}
    index = {}
    result = []

    def strongconnect(node):
        index[node] = index_counter[0]
        lowlinks[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)

        for neighbor in graph[node]:
            if neighbor not in index:
                strongconnect(neighbor)
                lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
            elif neighbor in stack:
                lowlinks[node] = min(lowlinks[node], index[neighbor])

        if lowlinks[node] == index[node]:
            connected_component = []
            while True:
                successor = stack.pop()
                connected_component.append(successor)
                if successor == node:
                    break
            result.append(connected_component)

    nodes = list(graph.keys())
    for node in nodes:
        if node not in index:
            strongconnect(node)

    return result



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tarjan\'s Algorithm')
    parser.add_argument('-i', '--input', type=str, required=True)
    args = parser.parse_args()
    input_file_path = args.input
    # input_file_path = "adj_list_dummy_3.parquet"

    # Read input file as parquet
    df = pd.read_parquet(input_file_path)
    edges, unique_nodes, line_counter, NA_counter = construct_graph(df)

    g = defaultdict(list)
    for u, v in tqdm(edges):
        u, v = int(u), int(v)
        if u not in g:
            g[u] = []
        g[u].append(v)
    print("Edges: ", edges)
    print("g: ", g)

    sccs = tarjan(g)
    sccs.sort(key=lambda x: len(x), reverse=True)

    output_file = open(f"{input_file_path}_summary_stats.txt", "w")

    output_file.write("Summary Statistics:\n")
    output_file.write(f"Total Nodes: {len(unique_nodes)}\n")
    
    # Output the SCCs with more than 1 member
    one_member_sccs = 0
    for scc in sccs:
        if len(scc) > 1:
            output_file.write(f"SCC ({scc[0]}) has {len(scc)} members\n")
        else:
            one_member_sccs += 1

    # Count the number of SCCs with 1 member
    if one_member_sccs > 0:
        output_file.write(f"{one_member_sccs} SCCs with 1 member\n")
    
    print(f"Finished writing to {output_file.name}")

        




