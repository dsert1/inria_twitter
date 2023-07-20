import numpy as np
import pandas as pd
import numba as nb
import time
import ast
import json
from collections import deque
from tqdm import tqdm

def main(adjacency):
  with open("log.txt", "w+") as log_f:
    start = time.time()
    log_f.write("Start reading adjacency list\n")
    log_f.flush()

    # Compute the number of vertices in the graph
    log_f.write("computing number of vertices...")
    vertex = pd.concat([adjacency["addr_id1"], adjacency["addr_id2"]]).dropna().unique()
    adjacency_nb_vertices = len(vertex)

    # if vertex.min() != 0:
    #     raise ValueError(
    #         f"vertices must start at 0, they actually start at {vertex.min()}"
    #     )

    # if vertex.max() != adjacency_nb_vertices - 1:
    #     raise ValueError(
    #         f"vertices must end at {adjacency_nb_vertices - 1=}, they actually end at {vertex.max()}"
    #     )

    log_f.write(f"number of vertices: {adjacency_nb_vertices}")

    # free the memory for the temporary variable vertex
    del vertex

    log_f.write("computing combine_first...")
    start = time.time()
    adjacency["addr_id1"] = adjacency["addr_id1"].combine_first(adjacency["addr_id2"])
    log_f.write(f" Done combine_first in {time.time() - start}.\n")
    # log.info(f" Done ({t.duration():{FP}}).")

    log_f.write("sorting values...")
    adjacency = adjacency.sort_values(by=["addr_id1"])
    log_f.write(f" Done sorting values in {time.time() - start}.\n")
    # log.info(f" Done ({t.duration():{FP}}).")

    log_f.write("convert to numpy...")
    start = time.time()
    adjacency = adjacency.to_numpy(dtype=np.uint32)
    # print(adjacency)
    log_f.write(f" Done converting to numpy {time.time() - start}.\n")

    return adjacency

def sccs_from_file(filepath):
    out = []
    max_len = 0
    max_len_scc = []
    with open(filepath, 'r+') as f:
       counter = 0
       lines = f.readlines()[0]
       for line in lines:
          line_eval = ast.literal_eval(line.strip())
          print(len(line_eval))
          if len(line_eval) > max_len:
            max_len = len(line_eval)
            max_len_scc = line_eval
          out.append(line_eval)
          counter += 1
    print(f"counter: {counter}")
    return out, max_len_scc
      # return [ast.literal_eval(line.strip()) for line in f.readlines()]

def sccs_from_file2(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
        max_len_scc = max(data, key=len)
        max_len = len(max_len_scc)
        counter = len(data)
        print(f"counter: {counter}")
    return data, max_len_scc

@nb.njit
def bfs(adjacency, start_vertices, forward=True):
    '''
    Runs Breadth First Search from every vertex in start_vertices.
    Returns a list of nodes that are reachable from start_vertices.
    '''
    num_vertices = adjacency.shape[0]
    visited = np.zeros(num_vertices, dtype=np.bool_)
    bfs_queue = np.empty(num_vertices, dtype=np.int32)
    queue_end = 0

    # if exclude_vertices is not None:
        # visited[exclude_vertices] = True

    for start_vertex in start_vertices:
        bfs_queue[queue_end] = start_vertex
        queue_end += 1
        # visited[start_vertex] = True

    counter = 0
    while queue_end > 0:
        print(f"queue_end: {queue_end}")
        if counter % 10000 == 0:
           print('.')
        if counter % 30000 == 0:
           print(f"counter: {counter}, queue_end: {queue_end}")
        current_vertex = bfs_queue[queue_end - 1]
        print(f"current_vertex: {current_vertex}")
        queue_end -= 1

        idx = np.where(adjacency[:, 0] == current_vertex)[0] if forward else np.where(adjacency[:, 1] == current_vertex)[0]
        print(f"idx: {idx}")
        for neighbor_index in idx:
            print(f"neighbor_index: {neighbor_index}")
            neighbor = adjacency[neighbor_index, 1] if forward else adjacency[neighbor_index, 0]
            print(f"neighbor: {neighbor}")
            if not visited[neighbor] and neighbor not in start_vertices:
                print()
                bfs_queue[queue_end] = neighbor
                queue_end += 1
                visited[neighbor] = True
        counter += 1

    return np.nonzero(visited)[0]  # Return the indices of visited nodes

# Example usage:
# visited = bfs(adjacency, start_vertices)


def get_out_comp(df, max_sccs):
   return bfs(df, max_sccs, forward=True)

def get_in_comp(df, max_sccs):
    return bfs(df, max_sccs, forward=False)

def write_comp_to_file(comp, filepath):
    with open(filepath, 'w+') as f:
        for c in comp:
            f.write(str(c) + "\n")


def get_tendrils(adj, out_comp_file, max_sccs, out=True):
  with open(out_comp_file, 'r+') as f:
    out_comp = f.readlines()
    out_comp = [int(x.strip()) for x in out_comp]
    max_sccs = np.array(max_sccs, dtype=np.int32)
    out_tendrils = bfs(adj, out_comp, forward=True)
    out_tendrils = np.setdiff1d(out_tendrils, out_comp)
    return out_tendrils


  
if __name__ == '__main__':
  df = pd.read_parquet("adj_list_dummy_3.parquet", columns=["addr_id1", "addr_id2"] , engine='pyarrow')
  adj = main(df)
  # del df
  sccs, max_len_scc = sccs_from_file2("sccs_dummy3.txt")
  max_len_scc = np.array(max_len_scc, dtype=np.int32)
  print(f"sccs: {sccs}")
  print(f"max_len_scc: {max_len_scc}")
  print(f"adj: {adj}")

  OUT = bfs(adj, max_len_scc, forward=True)
  print(f"OUT: {OUT}")
  IN = bfs(adj, max_len_scc, forward=False)
  print(f"IN: {IN}")
  # write_comp_to_file(OUT, "out_comp.txt")
  # OUT = np.setdiff1d(OUT, max_len_scc)
  # write_comp_to_file(OUT, "out_diff_lsc.txt")

  # out_tendrils = get_tendrils(adj, "out_diff_lsc.txt", max_len_scc, out=True)
  # write_comp_to_file(out_tendrils, "out_tendrils.txt")
  # print(f"out_tendrils[:25]: {out_tendrils[:25]}")
  # print(f"max len scc[:25]: {max_len_scc[:25]}")
  # out_tendrils = np.setdiff1d(adj, out_tendrils, max_len_scc)
  # write_comp_to_file(out_tendrils, "out_tendrils_diff_lsc.txt")
  # print(f"out_tendrils: {len(out_tendrils)}")
  # in_tendrils = get_tendrils("out_.txt", out=False)
  # write_comp_to_file(in_tendrils, "in_tendrils.txt")
  
    
    
