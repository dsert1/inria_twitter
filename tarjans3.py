import pandas as pd
# from tarjan import tarjan
import time
import os
from numba import njit
from numba.core import types
from numba.typed import Dict, List
from numba.types import int64
import numpy as np

SENTINEL = -1.0
SMALL_VALUE = 0.01

@njit
def tarjan(graph):
    S = List([SENTINEL])
    S_set = set([SENTINEL])
    index = {SENTINEL:SENTINEL}
    lowlink = {SENTINEL:SENTINEL}
    temp0 = List([SENTINEL])
    ret = List([temp0])

    for v in graph:
        if v not in index:
            visit(v, index, lowlink, S, S_set, ret, graph)
    return ret

@njit
def visit(v, index, lowlink, S, S_set, ret, graph):
    index[v] = len(index)
    lowlink[v] = index[v]
    S.append(v)
    S_set.add(v)
    if v in graph:
        for w in graph[v]:
            if w not in index:
                visit(w, index, lowlink, S, S_set, ret, graph)
                lowlink[v] = min(lowlink[w], lowlink[v])
            elif w in S_set:
                lowlink[v] = min(lowlink[v], index[w])
    if lowlink[v] == index[v]:
        scc = List([SENTINEL])
        w = None
        while v != w:
            w = S.pop()
            scc.append(w)
            S_set.remove(w)
        ret.append(scc)

def construct_graph(df):
    # graph = defaultdict(set)
    graph = Dict.empty(
        key_type=types.float64,
        value_type=types.float64[:]
    )
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
            # graph[v].add(v)
            if v not in graph:
                graph[v] = np.array([], dtype='f8')
            graph[v] = np.concatenate((graph[v], np.array([v])))
        # u is a miner address
        elif not pd.isna(u) and pd.isna(v):
            u = int(u)
            unique_nodes.add(u)
            NA_counter += 1
            # graph[u].add(u)
            if u not in graph:
                graph[u] = np.array([], dtype='f8')
            graph[u] = np.concatenate((graph[u], np.array([u])))
        # both addresses are valid
        else:
            u = int(u)
            v = int(v)
            unique_nodes.add(u)
            unique_nodes.add(v)
            # graph[u].add(v)
            if u not in graph:
                graph[u] = np.array([], dtype='f8')
            graph[u] = np.concatenate((graph[u], np.array([v])))
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
        batch_size = 1_000_000
        buffer = []
        for scc in sccs:
            # ******** LOGGING *********
            if counter % 10_000_000 == 0:
                print(f"counter: {counter} out of {len(scc)}. {counter / len(scc)}% complete.")
            # **************************
            if len(scc) == 1 and abs(scc[0] - SENTINEL) < SMALL_VALUE: # if scc is [-1.0]
                continue
            buffer.append(f"Members of SCC {counter}: {scc}\n")
            if counter % batch_size == 0:
                output_file.write(f"Members of SCC {counter}: {scc}\n")
                buffer = []
            counter += 1
        if buffer:
            output_file.writelines(buffer)
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
    df = pd.read_parquet("adj_list_dummy_2.parquet", columns=["addr_id1", "addr_id2"] , engine='pyarrow', dtype_backend='pyarrow')
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
    io_start = time.time()
    write_to_file(output_path, unique_nodes, sccs)
    end = time.time()
    # ***************************** 
    print(f"Took {end - start} seconds to run whole program.")
    print("**** END ****\n\n")

        




