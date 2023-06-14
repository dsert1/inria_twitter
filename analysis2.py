from collections import defaultdict

# Read the SCC file
filename = "scc_1.txt"

# Dictionary to store the SCC information
scc_counts = defaultdict(int)
total_nodes = set()

# Read the SCC file and count the SCC members
with open(filename, "r") as file:
    for line in file:
        parts = line.split()
        if len(parts) >= 6 and parts[0] == "Node" and parts[2] == "belongs" and parts[3] == "to" and parts[4] == "SCC":
            node = parts[1]
            scc = parts[5]
            scc_counts[scc] += 1
            total_nodes.add(node)

# Sort the SCCs by count in descending order
sorted_sccs = sorted(scc_counts.items(), key=lambda x: x[1], reverse=True)

# Write the summary statistics to a file
output_filename = "summary2.txt"
with open(output_filename, "w") as output_file:
    output_file.write("Summary Statistics:\n")
    output_file.write(f"Total Nodes: {len(total_nodes)}\n")
    
    # Output the SCCs with more than 1 member
    for scc, count in sorted_sccs:
        if count > 1:
            output_file.write(f"SCC {scc} has {count} members\n")

    # Count the number of SCCs with 1 member
    one_member_scc_count = sum(1 for count in scc_counts.values() if count == 1)
    if one_member_scc_count > 0:
        output_file.write(f"{one_member_scc_count} SCCs with 1 member\n")

print(f"Summary statistics written to {output_filename}")
