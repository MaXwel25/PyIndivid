print("Введите строку: ")
str1 = "fhb5kbfыshfm."
# str1 = input()
if not str1.endswith("."):
    print("Error: zero not found!")
    exit()
else:
    str = str1.split(".")[0]

alfavit = "abcdefghijklmnopqrstuvwxyz"
let = ""
for char in str1:
    if char in alfavit:
        let += char

sort_let = "".join(sorted(let))
if sort_let:
    cur_let = sort_let[0]
    count = 1

    for i in range(1, len(sort_let)):
        if sort_let[i] == cur_let:
            count += 1
        else:
            print(f"{cur_let}{count}")
            cur_let = sort_let[i]
            count = 1
    print(f"{cur_let}{count}")
