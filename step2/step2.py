from collections import deque
# from sagemath.graphs.digraph import DiGraph
import networkx as nx

def replace_scc_with_vertex(graph, scc): 
  '''
  This function takes the original graph and an SCC as input. It replaces the SCC with a single vertex in the graph. 
  The multiple arcs between any two vertices within the SCC 
  are replaced with a weighted arc whose weight is equal to the number of arcs it replaces.
  '''
  # Create a new vertex to replace the SCC
  new_vertex = tuple(scc)  # Convert the SCC list to a tuple for hashability
  
  # Remove edges within the SCC from the DataFrame
  df = df[~((df['addr_id1'].isin(scc)) & (df['addr_id2'].isin(scc)))]
  
  # Remove edges incident to SCC vertices from the DataFrame
  df = df[~((df['addr_id1'].isin(scc)) | (df['addr_id2'].isin(scc)))]
  
  # Add a new row for the new vertex with weighted arcs
  num_arcs = len(scc) * (len(scc) - 1)
  new_row = {'addr_id1': new_vertex, 'addr_id2': new_vertex, 'weight': num_arcs}
  df = df.append(new_row, ignore_index=True)
  
  return df

def compute_lsc_component(graph):
  '''
  This function takes the modified graph with SCCs replaced and identifies the Largest Strongly Connected (LSC) component, 
  which is the component with the largest number of original nodes. It returns the LSC component.
  ''' 
  # Count the number of original nodes for each SCC
  scc_counts = graph.groupby('addr_id1').size().to_dict()
  
  # Find the SCC with the largest count
  lsc_component = max(scc_counts, key=scc_counts.get)
  
  return lsc_component


def bfs(graph, start_vertex): 
  '''
  This function performs a Breadth-First Search (BFS) starting from a given start vertex in the graph. 
  It returns the set of vertices reached during the BFS traversal.
  '''
  # Initialize an empty set to store the visited vertices
  visited = set()
  
  # Initialize a queue for BFS traversal
  queue = deque([start_vertex])
  
  # Perform BFS traversal
  while queue:
      vertex = queue.popleft()
      visited.add(vertex)
      
      # Get the neighbors of the current vertex
      neighbors = graph.loc[graph['addr_id1'] == vertex, 'addr_id2']
      
      # Enqueue the unvisited neighbors
      for neighbor in neighbors:
          if neighbor not in visited:
              queue.append(neighbor)
  
  return visited

def reverse_bfs(graph, start_vertex): 
  '''
  This function performs a reverse BFS starting from a given start vertex in the graph. 
  It returns the set of vertices reached during the reverse BFS traversal.
  '''
  # Initialize an empty set to store the visited vertices
  visited = set()
  
  # Initialize a queue for reverse BFS traversal
  queue = deque([start_vertex])
  
  # Perform reverse BFS traversal
  while queue:
      vertex = queue.popleft()
      visited.add(vertex)
      
      # Get the neighbors of the current vertex
      neighbors = graph.loc[graph['addr_id2'] == vertex, 'addr_id1']
      
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

def create_macrostructure(graph, scc_list): 
  '''
  This function serves as the main function that ties all the modular functions together. 
  It takes the original graph and the list of SCCs as input. 
  It performs the necessary steps to compute the macrostructure of the graph as described in the procedure. 
  It returns the resulting macrostructure graph.
  '''
  # Step 1: Replace SCCs with a single vertex and weighted arcs
  modified_df = replace_scc_with_vertex(df, scc_list)
  
  # Step 2: Identify the Largest Strongly Connected (LSC) component
  lsc_component = compute_lsc_component(modified_df)
  
  # Step 3: Perform Breadth-First Search (BFS) from LSC component
  out_component = bfs(modified_df, lsc_component)
  
  # Step 4: Perform Reverse BFS from LSC component
  in_component = reverse_bfs(modified_df, lsc_component)
  
  # Step 5: Categorize vertices into different categories
  categorized_vertices = categorize_vertices(modified_df, lsc_component, in_component, out_component)
  
  # Step 6: Create the macrostructure graph
  macrostructure = nx.DiGraph()
  
  # Add vertices and edges based on the categorized vertices
  for category, vertices in categorized_vertices.items():
      for vertex in vertices:
          macrostructure.add_node(vertex)
          if category == 'LEVELS':
              continue  # Skip adding edges within the LSC component
          if category in ('IN-TENDRILS', 'BRIDGES', 'OTHER'):
              edges = modified_df.loc[modified_df['addr_id1'] == vertex, 'addr_id2'].values
              macrostructure.add_edges_from([(vertex, edge) for edge in edges])
          if category in ('OUT-TENDRILS', 'BRIDGES', 'OTHER'):
              edges = modified_df.loc[modified_df['addr_id2'] == vertex, 'addr_id1'].values
              macrostructure.add_edges_from([(edge, vertex) for edge in edges])
  
  return macrostructure