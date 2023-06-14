#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <iostream>
#include <stack>
using namespace std;

unordered_map<int, unordered_set<int> > g;
unordered_map<int, int> d, low, scc;
unordered_map<int, bool> stacked;
stack<int> s;
int ticks, current_scc;

void tarjan(int u) {
  d[u] = low[u] = ticks++;
  s.push(u);
  stacked[u] = true;
  
  const unordered_set<int>& out = g[u];
  
  for (const int& v : out) {
    if (d[v] == 0) {
      tarjan(v);
      low[u] = min(low[u], low[v]);
    } else if (stacked[v]) {
      low[u] = min(low[u], low[v]);
    }
  }
  
  if (d[u] == low[u]) {
    int v;
    do {
      v = s.top();
      s.pop();
      stacked[v] = false;
      scc[v] = current_scc;
    } while (u != v);
    
    current_scc++;
  }
}

int main() {
  // Sample data
  pair<int, int> edges[] = {
    make_pair(1, 2),
    make_pair(2, 1),
    };


  // Construct the graph
  for (const auto& edge : edges) {
    int u = edge.first;
    int v = edge.second;
    g[u].insert(v);
  }

  // Initialize variables
  ticks = 1;
  current_scc = 1;

  // Run Tarjan's algorithm on each unvisited node
  for (const auto& node : g) {
    int u = node.first;
    if (d[u] == 0) {
      tarjan(u);
    }
  }

  // Print the strongly connected components
  cout << "Strongly Connected Components:\n";
  for (const auto& node : scc) {
    int u = node.first;
    int component = node.second;
    cout << "Node " << u << " belongs to SCC " << component << "\n";
  }

  return 0;
}
