import ast

# Analyzes the result.txt file and write to analysis_result.txt
def run():
    one_connection_comps = 0
    with open('result.txt', 'r') as f:
        lines = f.readlines()
        seen = set()
        print("len of all comps: ", len(lines))
        for line in lines:
            try:
                evald = ast.literal_eval(line)
                # print(evald)
                if len(evald) > 1:
                    # print(tuple(evald))
                    seen.add(tuple(evald))
                else:
                    one_connection_comps += 1
            except SyntaxError:
                print("SyntaxError")
                continue
        f.close()
    print("len of mult connection comps: ", len(seen))

    # Sort the components by size in descending order
    sorted_comps = sorted(seen, key=len, reverse=True)
    max_comp = len(sorted_comps[0]) if sorted_comps else 0
    lengths = []

    with open("analysis_result2.txt", 'w+') as f:
        for comp in sorted_comps:
            lengths.append(len(comp))
            f.write(str(comp))
            f.write("\n")
        
        f.write("\n")
        f.write("len of mult connection comps: " + str(len(seen)))
        f.write(f"\nlen of the largest connected comp: {max_comp}")
        f.write("\n")
        f.write("\n")
        counter = 1
        for ix, length in enumerate(lengths):
            if ix != len(lengths) - 1 and lengths[ix] == lengths[ix+1]:
                counter += 1
            else:
                f.write(f"count: {counter}, magnitude: {length}")
                f.write("\n")
                counter = 1
        f.write(f"count: {one_connection_comps}, magnitude: 1")
        f.close()

if __name__ == '__main__':
    run()