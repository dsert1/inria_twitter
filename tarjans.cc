#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <iostream>
#include <stack>
#include <fstream>
#include <sstream>
#include <set>
using namespace std;

unordered_map < int, unordered_set < int > > g;
unordered_map < int, int > d, low, scc;
unordered_map < int, bool > stacked;
stack < int > s;
int ticks, current_scc;

void tarjan(int u) {
  d[u] = low[u] = ticks++;
  s.push(u);
  stacked[u] = true;

  const unordered_set < int > & out = g[u];

  for (const int & v: out) {
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
    vector<pair<int, int> > edges;

    // Open the text file for reading
    ifstream inputFile("adjacency_list.txt");

    // output file for writing
    ofstream outputFile("scc3.txt");

    // Check if the file opened successfully
    if (!inputFile) {
        cout << "Error opening the file." << endl;
        return 1;
    }

    int u, v, weight, height;
    string u_str, v_str, weight_str, height_str;
    set<int> unique_nodes;
    int na_counter = 0;
    int line_counter = 0;
    while (inputFile >> u_str >> v_str >> weight_str >> height_str) {
        if (u_str == "<NA>" && v_str != "<NA>") {
          na_counter++;
          stringstream(v_str) >> v;
          edges.push_back(make_pair(v, v));
          unique_nodes.insert(v);
        } else if (u_str != "<NA>" && v_str == "<NA>") {
          na_counter++;
          stringstream(u_str) >> u;
          unique_nodes.insert(u);
          edges.push_back(make_pair(u, u));
        } else {
          stringstream(u_str) >> u;
          stringstream(v_str) >> v;
          edges.push_back(make_pair(u, v));
          unique_nodes.insert(u);
          unique_nodes.insert(v);
        }
        line_counter++;
    }
    cout << "Number of NAs found: " << na_counter << endl;
    cout << "Line counter: " << line_counter << endl;
    cout << "Number of unique nodes: " << unique_nodes.size() << endl;

    // Close the file
    inputFile.close();

    // Print the edges
    // for (const auto& edge : edges) {
    //     cout << "Node " << edge.first << " -> " << "Node " << edge.second << endl;
    // }

    // Construct the graph
  for (const auto& edge : edges) {
    int u = edge.first;
    int v = edge.second;
    g[u].insert(v);
  }

  // Add isolated nodes to the processing maps
  for (const int& node : unique_nodes) {
    if (d[node] == 0) {
        tarjan(node);
    }
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
  // cout << "Strongly Connected Components:\n";
  int outputNodes = 0;
  for (const auto& node : scc) {
    outputNodes++;
    int u = node.first;
    int component = node.second;
    // cout << "Node " << u << " belongs to SCC " << component << "\n";
    outputFile << "Node " << u << " belongs to SCC " << component << "\n";
  }
  cout << "Number of connected nodes: " << outputNodes << endl;

  return 0;
}