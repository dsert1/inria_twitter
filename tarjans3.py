import pandas as pd
import argparse
from collections import defaultdict
from tarjan import tarjan
import time

if __name__ == '__main__':
    start = time.time()
    print("Starting...")
    parser = argparse.ArgumentParser(description='Tarjan\'s Algorithm')
    parser.add_argument('-i', '--input', type=str, required=True)
    args = parser.parse_args()
    input_file_path = args.input
    # input_file_path = "adj_list_dummy_3.parquet"


    # Read input file as parquet
    print("Loading input file...")
    df = pd.read_parquet(input_file_path, columns=["addr_id1", "addr_id2"] , engine='pyarrow', dtype_backend='pyarrow')
    print("Finished loading input file.")

    graph = defaultdict(set)
    unique_nodes = set()
    counter = 0
    NA_counter = 0
    print("Constructing graph...")
    graph_construction_start = time.time()
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

    graph_construction_end = time.time()
    print(f"Took {graph_construction_end - graph_construction_start} seconds to construct graph.")
    
    print("Finished constructing graph.")

    print("Running Tarjan's Algorithm...")
    tarjans_start = time.time()
    sccs = tarjan(graph)
    tarjans_end = time.time()
    print(f"Took {tarjans_end - tarjans_start} seconds to run Tarjan's Algorithm.")
    # print(sccs)
    print("Finished running Tarjan's Algorithm.")
    output_file = open(f"{input_file_path}_summary_stats.txt", "w")

    output_file.write("Summary Statistics:\n")
    output_file.write(f"Total Nodes: {len(unique_nodes)}\n")
    
    print("Writing SCCs to file...")
    # Output the SCCs with more than 1 member
    one_member_sccs = 0
    counter = 0
    io_start = time.time()
    for scc in sccs:
        if counter % 1000000 == 0:
            print("counter: ", counter)
        output_file.write(f"Members of SCC {counter}: {scc}\n")
        counter += 1
    io_end = time.time()
    print(f"Took {io_end - io_start} seconds to write SCCs to file.")
    print("Finished writing SCCs to file.")
    

    print(f"Finished writing to {output_file.name}")
    output_file.close()
    end = time.time()
    print(f"Took {end - start} seconds to run Tarjan's Algorithm.")

        




