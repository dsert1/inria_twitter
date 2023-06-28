#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <iostream>
#include <stack>
#include <fstream>
#include <sstream>
#include <map>
#include <set>
using namespace std;

// Function to split a string into a vector of tokens
std::vector<std::string> split(const std::string& line, char delimiter) {
    std::vector<std::string> tokens;
    std::stringstream ss(line);
    std::string token;
    
    while (std::getline(ss, token, delimiter)) {
        tokens.push_back(token);
    }
    
    return tokens;
}

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
        }
        else if (stacked[v]) {
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

    std::string filename = "adj_list_dummy_3.csv";
    std::ifstream inputFile(filename);
    ofstream outputFile("tarjans.txt");

    if (!inputFile) {
        std::cout << "Error opening file: " << filename << std::endl;
        return 0;
    }

    std::string line;
    // Skip the header line
    std::getline(inputFile, line);
    while (std::getline(inputFile, line)) {
      std::vector<std::string> tokens = split(line, ',');

      // Assuming the file is space-separated and the data provided is tabular representation
      // Both addr_id1 and addr_id2 are provided
      int u, v;
      if (tokens[0] == "") {
        u = stoi(tokens[1]);
        v = stoi(tokens[1]);
      } else {
        u = stoi(tokens[0]);
        v = stoi(tokens[1]);
      }
      edges.push_back(make_pair(u, v));
    }

    inputFile.close();


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
  // cout << "Strongly Connected Components:\n";
  std::map<int, std::vector<int> > sccGroups;
  for (const auto& node : scc) {
      sccGroups[node.second].push_back(node.first);
  }

  // std::ofstream outputFile("output.txt");
  for (const auto& group : sccGroups) {
      outputFile << "SCC " << group.first << " contains nodes: ";
      for (const auto& node : group.second) {
          outputFile << node << " ";
      }
      outputFile << "\n";
  }
  outputFile.close();
  return 0;
}