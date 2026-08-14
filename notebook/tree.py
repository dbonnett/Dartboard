from explore import listOfCombosFinal as combos

tree = {}

for path in combos:
    node = tree
    for step in path:
        node = node.setdefault(step, {})

def print_tree(node, indent=0):
    for key, child in node.items():
        print("  " * indent + str(key))
        if child:
            print_tree(child, indent + 1)

print_tree(tree)