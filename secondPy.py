n = int(input().strip())

tree = {}
people = set()

for _ in range(n):
    child, parent = input().split()
    if parent not in tree:
        tree[parent] = []
    tree[parent].append(child)
    people.add(child)
    people.add(parent)
for person in people:
    if person not in tree:
        tree[person] = []
result = {}

fl = True
while fl:
    fl = False
    for person in people:
        if person not in result:
            all_children_known = True
            total = 0

            for child in tree[person]:
                if child in result:
                    total += 1 + result[child]
                else:
                    all_children_known = False
                    break
            if all_children_known:
                result[person] = total
                fl = True

for person in sorted(people):
    print(f"{person} {result[person]}")
