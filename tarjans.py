from collections import defaultdict, deque

g = defaultdict(set)
d = {}
low = {}
scc = {}
stacked = {}
s = deque()
ticks = 0
current_scc = 0

def tarjan(u):
    global ticks, current_scc
    d[u] = low[u] = ticks
    ticks += 1
    s.append(u)
    stacked[u] = True

    out = g[u]

    for v in out:
        if d.get(v, 0) == 0:
            tarjan(v)
            low[u] = min(low[u], low[v])
        elif stacked.get(v, False):
            low[u] = min(low[u], low[v])

    if d[u] == low[u]:
        v = 0
        while u != v:
            v = s.pop()
            stacked[v] = False
            scc[v] = current_scc

        current_scc += 1

def main():
    edges = []

    # Read the text file
    filename = "adjacency_list.txt"
    with open(filename, "r") as inputFile:
        lines = inputFile.readlines()

    unique_nodes = set()
    na_counter = 0
    line_counter = 0
    for line in lines:
        parts = line.split()
        u_str, v_str, weight_str, height_str = parts[:4]

        if u_str == "<NA>" and v_str != "<NA>":
            na_counter += 1
            v = int(v_str)
            edges.append((v, v))
            unique_nodes.add(v)
        elif u_str != "<NA>" and v_str == "<NA>":
            na_counter += 1
            u = int(u_str)
            edges.append((u, u))
            unique_nodes.add(u)
        else:
            u = int(u_str)
            v = int(v_str)
            edges.append((u, v))
            unique_nodes.add(u)
            unique_nodes.add(v)

        line_counter += 1

    print("Number of NAs found:", na_counter)
    print("Line counter:", line_counter)
    print("Number of unique nodes:", len(unique_nodes))

    # Construct the graph
    for u, v in edges:
        g[u].add(v)

    # Add isolated nodes to the processing maps
    for node in unique_nodes:
        if node not in d:
            tarjan(node)
    

    # Write the strongly connected components to a file
    output_file = "scc_py.txt"
    with open(output_file, "w") as outputFile:
        outputNodes = 0
        for node, component in scc.items():
            outputNodes += 1
            outputFile.write(f"Node {node} belongs to SCC {component}\n")

    print("Number of connected nodes:", outputNodes)

if __name__ == "__main__":
    main()
