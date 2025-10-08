print("Введите строку: ")
str1 = "fhb5kbfыshfm."
# str1 = input()
if not str1.endswith("."):
    print("Error: zero not found!")
else:
    str = str1.split(".")[0]

    count = {}
    for char in str:
        if "a" <= char <= "z":
            count[char] = count.get(char, 0) + 1

    for sps in sorted(count.keys()):
        print(sps, count[sps])

