import pandas as pd
from collections import defaultdict
# from tarjan import tarjan
import time
import os
import numba as nb

# @nb.njit
def tarjan(graph):
    S = []
    S_set = set()
    index = {}
    lowlink = {}
    ret = []

    for v in graph:
        if v not in index:
            visit(v, index, lowlink, S, S_set, ret, graph)
    return ret

# @nb.njit
def visit(v, index, lowlink, S, S_set, ret, graph):
    index[v] = len(index)
    lowlink[v] = index[v]
    S.append(v)
    S_set.add(v)
    for w in graph.get(v, ()):
        if w not in index:
            visit(w, index, lowlink, S, S_set, ret, graph)
            lowlink[v] = min(lowlink[w], lowlink[v])
        elif w in S_set:
            lowlink[v] = min(lowlink[v], index[w])
    if lowlink[v] == index[v]:
        scc = []
        w = None
        while v != w:
            w = S.pop()
            scc.append(w)
            S_set.remove(w)
        ret.append(scc)

def construct_graph(df):
    graph = defaultdict(set)
    unique_nodes = set()
    counter = 0
    NA_counter = 0
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
    return graph, unique_nodes, NA_counter



def write_to_file(output_path, unique_nodes, sccs):
    io_start = time.time()
    with open(output_path, "w") as output_file:
        output_file.write("Summary Statistics:\n")
        output_file.write(f"Total Nodes: {len(unique_nodes)}\n")
        
        print("Writing SCCs to file...")
        # Output the SCCs with more than 1 member
        counter = 0
        
        for scc in sccs:
            if counter % 1_000_000 == 0:
                print("counter: ", counter)
            output_file.write(f"Members of SCC {counter}: {scc}\n")
            counter += 1
        io_end = time.time()
        print(f"Took {io_end - io_start} seconds to write SCCs to file.")
        print("Finished writing SCCs to file.")
        

        print(f"Finished writing to {output_file.name}")
        output_file.write("**** END ****\n\n")
        output_file.close()



if __name__ == '__main__':

    # *** Loading input file ***
    start = time.time()
    print("Starting...")
    print("Loading input file...")
    df = pd.read_parquet("adj_list_dummy_3.parquet", columns=["addr_id1", "addr_id2"] , engine='pyarrow', dtype_backend='pyarrow')
    print("Finished loading input file.")

    output_file = "output.txt"
    output_path = os.path.join(os.getcwd(), output_file)
    # **************************


    # *** Constructing graph ***
    print("Constructing graph...")
    graph, unique_nodes, NA_counter = construct_graph(df)
    print("Finished constructing graph.")

    # **************************


    # *** Running Tarjan's Algorithm ***
    print("Running Tarjan's Algorithm...")
    tarjans_start = time.time()
    sccs = tarjan(graph)
    tarjans_end = time.time()
    print(f"Took {tarjans_end - tarjans_start} seconds to run Tarjan's Algorithm.")
    # print(sccs)
    print("Finished running Tarjan's Algorithm.")
    # **********************************

    # *** Writing output to file ***
    print(f"Output file: {output_path}")
    io_start = time.time()
    write_to_file(output_path, unique_nodes, sccs)
    end = time.time()
    # ***************************** 
    print(f"Took {end - start} seconds to run whole program.")
    print("**** END ****\n\n")

        




