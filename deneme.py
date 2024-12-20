class Deneme:
    def __init__(self, k):
        self.a = k
        
        
x = Deneme(2)
y = Deneme(3)
k = Deneme(6)
z = Deneme(4)


arr = [x, y]
arr2 = []
for i in arr:
    arr2.append(i)
arr.clear()
print(arr2)

for a in arr2:
  print(a.a)
  if a.a == 2:
    arr2.remove(a)
    
for a in arr2:
    print(a.a)
