from tqdm import tqdm as progressbar
import numpy as np
import pandas as pd
from collections import defaultdict

df_adjacency_list = pd.read_parquet('early_adj.parquet')

def tarjans_algorithm(graph):
    with open('result_python.txt', 'w+') as f:
        index_counter = [0]
        stack = []
        lowlink = {}
        indices = {}
        visited = set()
        result = []

        
        def strongconnect(node):
            indices[node] = index_counter[0]
            lowlink[node] = index_counter[0]
            index_counter[0] += 1
            stack.append(node)
            visited.add(node)

            successors = list(graph.loc[graph['addr_id1'] == node]['addr_id2'])
            for successor in successors:
                if successor not in visited:
                    strongconnect(successor)
                    lowlink[node] = min(lowlink[node], lowlink[successor])
                elif successor in stack:
                    lowlink[node] = min(lowlink[node], indices[successor])

            if lowlink[node] == indices[node]:
                scc = []
                while True:
                    successor = stack.pop()
                    scc.append(successor)
                    if pd.isnull(successor) or successor == node:
                        break
                result.append(scc)
                f.write(str(scc) + '\n')

        for node in progressbar(graph['addr_id1'].unique()):
            if node not in visited:
                strongconnect(node)
        f.close()
    return result
        

if __name__ == "__main__":
    strongly_connected_components = np.array(tarjans_algorithm(df_adjacency_list))
    # print all the elements in the array whose length is greater than 1
    print(strongly_connected_components)
    print([x for x in strongly_connected_components if len(x) > 1])
