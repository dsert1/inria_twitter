import pandas as pd
import numpy as np
import argparse
from collections import defaultdict
import sys
from tarjan import tarjan


if __name__ == '__main__':
    print("Starting...")
    parser = argparse.ArgumentParser(description='Tarjan\'s Algorithm')
    parser.add_argument('-i', '--input', type=str, required=True)
    args = parser.parse_args()
    input_file_path = args.input
    # input_file_path = "adj_list_dummy_3.parquet"


    # Read input file as parquet
    print("Reading input file...")
    df = pd.read_parquet(input_file_path, columns=["addr_id1", "addr_id2"] , engine='pyarrow', dtype_backend='pyarrow')
    print("Finished reading input file.")
    print("Constructing graph...")
    print("Finished constructing graph.")


    print("Reading edges...")
    graph = defaultdict(set)
    counter = 0
    unique_nodes = set()
    NA_counter = 0
    for u, v in df.itertuples(index=False):
        counter += 1
        if counter % 1_000_000 == 0:
            print("counter: ", counter)
        # v is a miner address
        if pd.isna(u) and not pd.isna(v):
            v = int(v)
            unique_nodes.add(v)
            NA_counter += 1
            graph[v].add(v)
        # u is a miner address
        elif not pd.isna(u) and pd.isna(v):
            u = int(u)
            unique_nodes.add(u)
            NA_counter += 1
            graph[u].add(u)
        # both addresses are valid
        else:
            u = int(u)
            v = int(v)
            unique_nodes.add(u)
            unique_nodes.add(v)
            graph[u].add(v)

        
    print("Finished reading edges.")

    print("Running Tarjan's Algorithm...")
    sccs = tarjan(graph)
    print(sccs)
    print("Finished running Tarjan's Algorithm.")
    # sccs.sort(key=lambda x: len(x), reverse=True)

    output_file = open(f"{input_file_path}_summary_stats.txt", "w")

    output_file.write("Summary Statistics:\n")
    output_file.write(f"Total Nodes: {len(unique_nodes)}\n")
    
    print("Writing SCCs to file...")
    # Output the SCCs with more than 1 member
    one_member_sccs = 0
    counter = 0
    for scc in sccs:
        counter += 1
        if counter % 1_000_000 == 0:
            print("counter: ", counter)
        if len(scc) > 1:
            output_file.write(f"SCC ({scc[0]}) has {len(scc)} members\n")
        else:
            one_member_sccs += 1
    print("Finished writing SCCs to file.")

    # Count the number of SCCs with 1 member
    if one_member_sccs > 0:
        output_file.write(f"{one_member_sccs} SCCs with 1 member\n")
    
    print(f"Finished writing to {output_file.name}")

        




