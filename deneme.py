from math import sqrt

arr = []
for i in range(0, 10):
    row = []
    for k in range(1, 10):
        row.append(i * 9 + k)
    arr.append(row)

print(arr)
extended_air_x = 3
extended_air_y = 3
search = arr[
    extended_air_x - 3 : extended_air_x + 4,
    extended_air_y - 3 : extended_air_y + 4
]
print(search)
