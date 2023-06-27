from collections import deque
# from sagemath.graphs.digraph import DiGraph
import networkx as nx
import time
import pandas as pd
import numpy as np
import ast
import json
import matplotlib.pyplot as plt

# def consolidate_sccs(df, text_sccs):
#     """
#     Consolidate each strongly connected component into a single vertex.
#     Mutates the dataframe in place.

#     Parameters
#     ----------
#     df : pandas.DataFrame
#         Dataframe containing the graph edges. Columns: 'addr_id1', 'addr_id2'.
#     sccs : list of lists
#         List of strongly connected components. Each component is represented by a list of vertex IDs.

#     Returns
#     -------
#     pandas.DataFrame
#         Updated DataFrame where each SCC is consolidated into a single vertex.
#     """
#     df['weight'] = 1
#     for line in text_sccs:
#       line = "".join(line)
#       sccs = ast.literal_eval(line)
#       for scc in sccs:
#         # get the minimum id in the scc
#         min_id = min(scc)
#         # for every id that is not the minimum id, mark that row in the dataframe as NA
#         for id in scc:
#           weight = 1
#           if id != min_id:
#             idx = df.loc[(df['addr_id1'] == id) | (df['addr_id2'] == min_id)].index[0]
#             df.loc[idx, ['addr_id1', 'addr_id2']] = pd.NA
#             weight += 1
#             idx = df.loc[(df['addr_id1'] == min_id) | (df['addr_id2'] == id)].index[0]
#             df.loc[idx, ['weight']] = weight
#       # drop all the rows that are NA
#       mask = df['addr_id1'].notna() | df['addr_id2'].notna()
#       mask = ~(df['addr_id1'].notna() | df['addr_id2'].notna())
#       df.drop(df[mask].index, inplace=True)
#       mask = df['addr_id1'].isna()
#       df.loc[mask, 'addr_id1'] = df.loc[mask, 'addr_id2']

#     return None

def compute_lsc_component(sccs):
  '''
  This function takes the modified graph with SCCs replaced and identifies the Largest Strongly Connected (LSC) component, 
  which is the component with the largest number of original nodes. It returns the LSC component.
  ''' 
  print(sccs)
  print(f"type of sccs: {type(sccs)}")
  print(f"max(sccs, key=lambda x: len(x)): {max(sccs, key=len)}")
  return max(sccs, key=len)

def bfs(graph, start_vertices, forward=True): 
  '''
  This function performs a reverse BFS starting from a given start vertex in the graph. 
  It returns the set of vertices reached during the reverse BFS traversal.
  '''
  # Initialize an empty set to store the visited vertices
  if forward:
     keyword = "addr_id1"
     other_keyword = "addr_id2"
  else:
     keyword = "addr_id2"
     other_keyword = "addr_id1"

  visited = set()
  
  # Initialize a queue for reverse BFS traversal
  for vertex in start_vertices:
    queue = deque([vertex])
    print("queue: ", queue)
    
    # Perform reverse BFS traversal
    while queue:
        vertex = queue.popleft()
        visited.add(vertex)
        
        # Get the neighbors of the current vertex
        print("vertex: ", vertex)
        neighbors = graph.loc[graph[keyword] == vertex, other_keyword]
        print("neighbors: ", neighbors)
        
        # Enqueue the unvisited neighbors
        for neighbor in neighbors:
            if neighbor not in visited:
                queue.append(neighbor)
  
  return visited

def categorize_vertices(graph, lsc_component, in_component, out_component): 
  '''
  This function takes the modified graph, LSC component, IN component, and OUT component as input. It categorizes the vertices into different categories (e.g., LEVELS, IN-TENDRILS, OUT-TENDRILS, BRIDGES, OTHER, DISCONNECTED) based on the described rules. It returns the categorized vertices.
  '''
  # Initialize empty sets for different categories
  levels = set()
  in_tendrils = set()
  out_tendrils = set()
  bridges = set()
  other = set()
  disconnected = set()

  # Categorize the vertices based on the described rules
  for vertex in graph['addr_id1'].unique():
      if vertex in lsc_component:
          # Check if the vertex is in the LSC component
          levels.add(vertex)
      elif vertex in in_component:
          # Check if the vertex is in the IN component
          in_tendrils.add(vertex)
      elif vertex in out_component:
          # Check if the vertex is in the OUT component
          out_tendrils.add(vertex)
      else:
          # Check if the vertex has undirected paths to other components
          if graph.loc[(graph['addr_id1'] == vertex) & (graph['addr_id2'].isin(levels | in_tendrils | out_tendrils)), 'addr_id2'].any():
              bridges.add(vertex)
          else:
              other.add(vertex)
  
  # Find the disconnected vertices
  disconnected = set(graph['addr_id1'].unique()) - (levels | in_tendrils | out_tendrils | bridges | other)
  
  # Return the categorized vertices
  return {
      'LEVELS': levels,
      'IN-TENDRILS': in_tendrils,
      'OUT-TENDRILS': out_tendrils,
      'BRIDGES': bridges,
      'OTHER': other,
      'DISCONNECTED': disconnected
  }

def create_macrostructure(graph, sccs): 
  '''
  This function serves as the main function that ties all the modular functions together. 
  It takes the original graph and the list of SCCs as input. 
  It performs the necessary steps to compute the macrostructure of the graph as described in the procedure. 
  It returns the resulting macrostructure graph.
  '''
  # Step 1: Replace SCCs with a single vertex and weighted arcs
  # modified_df = consolidate_sccs(df, scc_list)
  
  # Step 2: Identify the Largest Strongly Connected (LSC) component
  lsc_component = compute_lsc_component(sccs)
  
  # Step 3: Perform Breadth-First Search (BFS) from LSC component
  out_component = bfs(df, lsc_component)
  
  # Step 4: Perform Reverse BFS from LSC component
  in_component = bfs(df, lsc_component, forward=False)
  
  # Step 5: Categorize vertices into different categories
  categorized_vertices = categorize_vertices(df, lsc_component, in_component, out_component)
  print(categorized_vertices)
  
  # Step 6: Create the macrostructure graph
  macrostructure = nx.DiGraph()
  
  # Add vertices and edges based on the categorized vertices
  for category, vertices in categorized_vertices.items():
      for vertex in vertices:
          macrostructure.add_node(vertex)
          if category == 'LEVELS':
              continue  # Skip adding edges within the LSC component
          if category in ('IN-TENDRILS', 'BRIDGES', 'OTHER'):
              edges = df.loc[df['addr_id1'] == vertex, 'addr_id2'].values
              macrostructure.add_edges_from([(vertex, edge) for edge in edges])
          if category in ('OUT-TENDRILS', 'BRIDGES', 'OTHER'):
              edges = df.loc[df['addr_id2'] == vertex, 'addr_id1'].values
              macrostructure.add_edges_from([(edge, vertex) for edge in edges])
  
  nx.draw(macrostructure, with_labels=True)
  plt.show()
  return macrostructure

def load_file(parquet_file):
  start = time.time()
  with open("log.txt", "w+") as log_f:
    log_f.write("Reading parquet...")
    log_f.flush()
  # os.chdir("/Users/dsert/Documents/Documents - Deniz's Macbook/MIT Semesters/Summer 2023/Inria/inria_twitter")
    df = pd.read_parquet(parquet_file, columns=["addr_id1", "addr_id2"] , engine='pyarrow')
    log_f.write("Finished reading!\n\n*********\n\n")
    log_f.flush()

    finish = time.time()
    log_f.write(f"Reading file took: {finish - start} seconds.\n")
  log_f.close()
  return df

def load_sccs(scc_file):
  sccs = []
  with open(scc_file, "r") as f, open("log.txt", "w+") as log_f:
    log_f.write("Reading sccs...")
    log_f.flush()
    sccs = json.loads(f.read())
    log_f.write("Finished reading!\n\n*********\n\n")
    log_f.flush()
  return sccs

if __name__ == '__main__':
  df = load_file("adj_list_dummy_3_1.parquet")
  # print(df)
  sccs = load_sccs("sccs.txt")
  # print(sccs)
  # consolidate_sccs(sccs)
  # print(f"End: {df}")

  # lsc_comp = compute_lsc_component(sccs)
  # print(lsc_comp)
  # # # print(df)
  # # # print(new_df)
  # in_comp = bfs(df, lsc_comp)
  # out_comp = bfs(df, lsc_comp, forward=False)
  
  # categories = categorize_vertices(df, lsc_comp, in_comp, out_comp)
  # print(f"Categories: {categories}")

  # print(reverse_bfs)
  # print(bfs_)

  macrostructure = create_macrostructure(df, sccs)
  print(macrostructure)
