from collections import deque
# from sagemath.graphs.digraph import DiGraph
# import networkx as nx
import graph_tool.all as gt
import time
import pandas as pd
import numpy as np
import ast
import json
import matplotlib.pyplot as plt
from utils import load_sccs, load_file
import time
from tqdm import tqdm

def compute_lsc_component(sccs):
  '''
  This function takes the modified graph with SCCs replaced and identifies the Largest Strongly Connected (LSC) component, 
  which is the component with the largest number of original nodes. It returns the LSC component.

  If there are multiple components that are all the largest, it returns the first one it finds.
  ''' 
  return max(sccs, key=len)

def bfs(graph, start_vertices, forward=True): 
  '''
  This function performs a BFS starting from a given set of start vertices in the graph. 
  It returns the set of vertices reachable from the start vertices (excluding the start vertices themselves).
  '''
  # Initialize an empty set to store the visited vertices
  print(f"Starting BFS...: forward: {forward}")
  start = time.time()
  if forward:
     keyword = "addr_id1"
     other_keyword = "addr_id2"
  else:
     keyword = "addr_id2"
     other_keyword = "addr_id1"

  visited = set()
  
  # Initialize a queue for BFS traversal
  queue = deque()
  for start_vertex in start_vertices:
      # Enqueue the start vertices and mark them as visited
      queue.append(start_vertex)
      visited.add(start_vertex)

  # Initialize an empty set to store the reachable vertices
  out_component = set()
  
  # Perform BFS traversal
  while queue:
      vertex = queue.popleft()
      
      # Get the neighbors of the current vertex
      neighbors = graph.loc[graph[keyword] == vertex, other_keyword]
      # print("neighbors: ", neighbors)
      
      # Enqueue the unvisited neighbors
      for neighbor in neighbors:
          if neighbor not in visited:
              queue.append(neighbor)
              visited.add(neighbor)
              if neighbor not in start_vertices:
                out_component.add(neighbor)
  print(f"Forwad: {forward} BFS took {time.time() - start} seconds")
  return out_component

def categorize_vertices(graph, lsc_component, in_component, out_component): 
  '''
  This function takes the modified graph, LSC component, IN component, and OUT component as input. It categorizes the vertices into different categories (e.g., LEVELS, IN-TENDRILS, OUT-TENDRILS, BRIDGES, OTHER, DISCONNECTED) based on the described rules. It returns the categorized vertices.
  '''
  # Initialize empty sets for different categories
  print("Starting categorize_vertices...")
  start = time.time()
  levels = set()
  in_tendrils = set()
  out_tendrils = set()
  bridges = set()
  other = set()
  disconnected = set()
  unique_vertices = pd.unique(pd.concat([graph['addr_id1'], graph['addr_id2']]))

  # Categorize the vertices based on the described rules
  for vertex in tqdm(unique_vertices):
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
  

  print(f"Categorize_vertices took {time.time() - start} seconds")
  # Return the categorized vertices
  return {
      'LSC': levels,
      'IN': in_component,
      'OUT': out_component,
      'IN-TENDRILS': in_tendrils,
      'OUT-TENDRILS': out_tendrils,
      'BRIDGES': bridges,
      'OTHER': other,
      'DISCONNECTED': disconnected
  }

def create_macrostructure(df, sccs, filename="macrostructure"):
  '''
  This function serves as the main function that ties all the modular functions together. 
  It takes the original graph and the list of SCCs as input. 
  It performs the necessary steps to compute the macrostructure of the graph as described in the procedure. 
  It returns the resulting macrostructure graph.
  '''
  # Step 1: Replace SCCs with a single vertex and weighted arcs
  # modified_df = consolidate_sccs(df, scc_list)
  
  # Step 2: Identify the Largest Strongly Connected (LSC) component
  # print("df: ", df)
  # print(f"SCCS: {sccs}")
  start = time.time()
  print(f"About to compute LSC component\n")
  lsc_component = compute_lsc_component(sccs)
  print(f"Time to compute LSC component: {time.time() - start}\n")
  # print(f"LSC COMPONENT: {lsc_component}")
  
  # Step 3: Perform Breadth-First Search (BFS) from LSC component
  print(f"About to perform BFS\n")
  start = time.time()
  out_component = bfs(df, lsc_component)
  print(f"Time to perform BFS: {time.time() - start}\n")

  # print(f"OUT COMPONENT: {out_component}")
  
  # Step 4: Perform Reverse BFS from LSC component
  print(f"About to perform reverse BFS\n")
  start = time.time()
  in_component = bfs(df, lsc_component, forward=False)
  print(f"Time to perform reverse BFS: {time.time() - start}\n")
  
  # Step 5: Categorize vertices into different categories
  print(f"About to categorize vertices")
  start = time.time()
  categorized_vertices = categorize_vertices(df, lsc_component, in_component, out_component)
  print(f"Time to categorize vertices: {time.time() - start}\n")
  print(categorized_vertices)
  
  # Step 6: Create the macrostructure graph
  print(f"About to create macrostructure graph")
  start = time.time()
  macrostructure = gt.Graph(directed=False)
  
  # Add vertices and edges based on the categorized vertices
  # bottleneck
  # start = time.time()
  vertex_ids = pd.unique(pd.concat([df['addr_id1'], df['addr_id2']]))
  vertex_id = macrostructure.new_vertex_property("int")
  # v = macrostructure.add_vertex()

  # def remove_vertices_by_original_id(g, vertex_id_map, valid_ids):
  #   # First, we mark vertices for deletion
  #   delete_map = g.new_vertex_property("bool")  # property map for deletion
  #   print(f"G.VERTICES: {[v for v in g.vertices()]}")
  #   print(f"VALID IDS: {valid_ids}")
  #   for v in g.vertices():
  #       original_id = vertex_id_map[v]
  #       delete_map[v] = vertex_id_map[v] not in valid_ids

  #   print(f"DELETE MAP: {delete_map}")
  #   print("Vertices marked for deletion:")
  #   for v in g.vertices():
  #       if delete_map[v]:
  #           print(f"Vertex: {v}, original id: {vertex_id_map[v]}")
  #   # Then, we call purge_vertices() to delete all marked vertices
  #   g.purge_vertices(delete_map)
  #   print(g)
  #   print("Vertices remaining after deletion:")
  #   for v in g.vertices():
  #       print(f"Vertex: {v}, original id: {vertex_id_map[v]}")
  
  # print(f"Unique vertices: {vertex_ids}")
  all_vertices = set()
  vertex_id_map = macrostructure.new_vertex_property("int")
  # id_to_index = {id: index for index, id in enumerate(vertex_ids)}
  id_to_vertex = {}
  for category, vertices in tqdm(categorized_vertices.items()):
    all_vertices = all_vertices.union(set(vertices))
    for vertex in tqdm(vertices):
      # index = id_to_index[vertex]
      # macrostructure.add_vertex(int(index))
      # print(f"Adding vertex: {vertex}, category: {category}")
      v = macrostructure.add_vertex()
      id_to_vertex[vertex] = v
      vertex_id[v] = vertex
      vertex_id_map[v] = vertex
      # print(f"Adding edges: {[(vertex, edge) for edge in edges]}")
      if category == 'LEVELS':
        continue  # Skip adding edges within the LSC component
      if category in ('IN-TENDRILS', 'BRIDGES', 'OTHER'):
        edges = df.loc[df['addr_id1'] == vertex, 'addr_id2'].to_numpy()
        macrostructure.add_edge_list([(id_to_vertex[vertex], id_to_vertex[edge]) for edge in edges])
        print(f"Adding edges: {[(id_to_vertex[vertex], id_to_vertex[edge]) for edge in edges]}")
      if category in ('OUT-TENDRILS', 'BRIDGES', 'OTHER'):
        edges = df.loc[df['addr_id2'] == vertex, 'addr_id1'].to_numpy()
        macrostructure.add_edge_list([(id_to_vertex[edge], id_to_vertex[vertex]) for edge in edges])
  # start = time.time()
  print(f"Time to add nodes and edges: {time.time() - start}")
        # print(f"Adding edges: {[(vertex, edge) for edge in edges]}")
  # print(f"Time to add nodes and edges: {time.time() - start}")
  # print(f"Macrostructure: {macrostructure}")
  # remove_vertices_by_original_id(macrostructure, vertex_id, all_vertices)

  # remove extraneous vertices
  all_vertices = [macrostructure.vertex_index[v] for v in macrostructure.vertices()]
  all_edges = [(macrostructure.vertex_index[e.source()], macrostructure.vertex_index[e.target()]) for e in macrostructure.edges()]
  print(f"ALL VERTICES: {all_vertices}")
  print(f"ALL EDGES: {all_edges}")
  # delete_map = macrostructure.new_vertex_property("bool")  # property map for deletion
  # # vertex_ids = pd.unique(pd.concat([df['addr_id1'], df['addr_id2']]))
  # for v in macrostructure.vertices():
  #   if v not in all_vertices:
  #     delete_map[v] = vertex_id_map[v] not in all_vertices
  # macrostructure.purge_vertices(delete_map)
      # print(f"Removing vertex: {v}")
      # macrostructure.remove_vertex(v)
  # gt.graph_draw("macrostructure.png", vertex_text=macrostructure.vertex_index, vertex_font_size=12, output_size=(1000, 1000))
  # remove_extraneous_vertices_in_place(macrostructure)
  # assuming you have the `graph`, `all_vertices` and `all_edges` variables
  remove_extraneous_vertices_in_place(macrostructure, all_vertices, all_edges)
  # print(vertex_id_map)
  # for v in macrostructure.vertices():
  #   print(f"Vertex index: {int(v)}, original ID: {id_to_vertex[vertex_id_map[v]]}")
  gt.graph_draw(macrostructure, vertex_text=vertex_id_map, vertex_font_size=12, output_size=(1000, 1000), output=f"{filename}.png")
  # plt.show()
  
  return macrostructure

def remove_extraneous_vertices_in_place(graph, all_vertices, all_edges):
    """
    Function to remove vertices that have no edges connected to them.
    """
    # Create a set of vertices that are part of the edges
    vertices_with_edges = set()
    for edge in all_edges:
        vertices_with_edges.add(graph.vertex_index[edge[0]])
        vertices_with_edges.add(graph.vertex_index[edge[1]])
    # print("Here")

    # Iterate over all_vertices in reverse order
    for i in range(len(all_vertices) - 1, -1, -1):
        print(f"Vertex: {all_vertices[i]}")
        print(graph.vertex_index[all_vertices[i]] not in vertices_with_edges)
        if graph.vertex_index[all_vertices[i]] not in vertices_with_edges:
            # This vertex is extraneous, so remove it
            graph.remove_vertex(graph.vertex_index[all_vertices[i]])


if __name__ == '__main__':
  filename = "adj_list_dummy_3"
  df = load_file(f"{filename}.parquet")
  # print(df)
  sccs = load_sccs("sccs_dummy3.txt")
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

  macrostructure = create_macrostructure(df, sccs, filename=filename)
  print([macrostructure.vertex_index[v] for v in macrostructure.vertices()])
  print(macrostructure)