with open('file1.txt', 'r') as file:
    xstr = file.readline().strip()

strdigits = []
for char in xstr:
    strdigits.append(int(char))

n = 1
while True:
    str1 = str(n)
    digits = []
    for char in str1:
        digits.append(int(char))
    i = 0
    j = 0
    while i < len(strdigits) and j < len(digits):
        if strdigits[i] == digits[j]:
            j += 1
        i += 1
    if j != len(digits):
        print(n)
        break
    n += 1
