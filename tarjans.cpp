#include <iostream>
#include <vector>
#include <algorithm>
#include <fstream>
#include <string>
#include <unordered_map>
#include <unordered_set>

using namespace std;

struct Tarjan {
    unordered_map<int, vector<int> > graph;
    vector<int> represent, low, st;
    vector<bool> instack;
    unordered_map<int, int> idx;  // Map node identifier to index
    int numSCC;
    int n, cur;

    Tarjan(int N) : n(N), numSCC(0), cur(0) {
        represent = vector<int>(n);
        low = vector<int>(n);
        instack = vector<bool>(n);
    }

    void dfs(int v) {
        low[v] = idx[v] = ++cur;
        st.push_back(v);
        instack[v] = true;
        for (int out : graph[v]) {
            if (idx[out] == -1) {  // Check if the node has been visited
                dfs(out);
            }
            if (instack[out]) {
                low[v] = min(low[v], low[out]);
            }
        }
        if (low[v] == idx[v]) {
            numSCC++;
            int top;
            do {
                top = st.back();
                st.pop_back();
                instack[top] = false;
                represent[top] = numSCC;  // Assign representative node
            } while (top != v);
        }
    }

    int start() {
        cout << "Starting Tarjan's algorithm.." << endl;
        st.clear();
        represent = low = vector<int>(n);
        instack = vector<bool>(n);
        numSCC = 0, cur = 0;
        vector<bool> visited(n, false);  // Track visited nodes

        for (const auto& kvp : graph) {
            int i = kvp.first;
            if (!visited[i]) {  // Check if the node has been visited
                dfs(i);
                for (int j : st) {
                    visited[j] = true;
                }
                st.clear();
            }
        }
        cout << "Finished Tarjan's algorithm.." << endl;

        return numSCC;
    }

    void addEdge(int a, int b) {
        graph[a].push_back(b);
    }

    void readGraphFromFile(const string& filename) {
        ifstream file(filename);
        if (!file) {
            cerr << "Error opening file: " << filename << endl;
            return;
        }

        unordered_set<int> uniqueNodes;

        int a, b, value, height;
        while (file >> a >> b >> value >> height) {
            uniqueNodes.insert(a);
            uniqueNodes.insert(b);
            addEdge(a, b);
        }

        n = uniqueNodes.size();
        represent = vector<int>(n);  // Initialize represent vector with size n

        // Assign indices to node identifiers
        int index = 0;
        for (const auto& node : uniqueNodes) {
            idx[node] = index++;
        }
    }
};

int main() {
    cout << "Starting.." << endl;

    Tarjan tarjan(0);
    cout << "Reading graph from file.." << endl;
    tarjan.readGraphFromFile("adj_list_dummy_2.txt");
    cout << "Finished reading graph from file." << endl;

    cout << "Starting Tarjan's algorithm.." << endl;
    int numSCC = tarjan.start();
    cout << "Number of SCC: " << numSCC << endl;
    for (int i = 0; i < tarjan.n; i++) {
        cout << "Node " << i << ", representative node " << tarjan.represent[i] << endl;
    }

    return 0;
}
