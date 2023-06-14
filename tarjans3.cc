#include <vector>
#include <stdio.h>
#include <iostream>
#include <stack>
using namespace std;

const int MAXN = 100;


vector<int> g[MAXN];
int d[MAXN], low[MAXN], scc[MAXN];
bool stacked[MAXN];
stack<int> s;
int ticks, current_scc;
void tarjan(int u){
  d[u] = low[u] = ticks++;
  s.push(u);
  stacked[u] = true;
  const vector<int> &out = g[u];
  for (int k=0, m=out.size(); k<m; ++k){
    const int &v = out[k];
    if (d[v] == -1){
      tarjan(v);
      low[u] = min(low[u], low[v]);
    }else if (stacked[v]){
      low[u] = min(low[u], low[v]);
    }
  }
  if (d[u] == low[u]){
    int v;
    do{
      v = s.top();
      s.pop();
      stacked[v] = false;
      scc[v] = current_scc;
    }while (u != v);
    current_scc++;
  }
}

int main() {
  // Construct the graph
  g[0].push_back(1);  // Add edge from node 0 to node 1
  g[1].push_back(0);  // Add edge from node 1 to node 0

  // Initialize variables
  ticks = 0;
  current_scc = 0;
  for (int i = 0; i < MAXN; ++i) {
    d[i] = -1;
    low[i] = -1;
    stacked[i] = false;
    scc[i] = -1;
  }

  // Run Tarjan's algorithm on each unvisited node
  for (int u = 0; u < 2; ++u) {  // Iterate over all nodes in the graph
    if (d[u] == -1) {
      tarjan(u);
    }
  }

  // Print the strongly connected components
  cout << "Strongly Connected Components:\n";
  for (int u = 0; u < 2; ++u) {
    cout << "Node " << u << " belongs to SCC " << scc[u] << "\n";
  }

  return 0;
}
