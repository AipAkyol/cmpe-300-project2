class Deneme:
    def __init__(self, k):
        self.a = k
        
        
x = Deneme(2)
y = Deneme(3)


arr = [x, y]
arr2 = []
for i in arr:
    arr2.append(i)
arr.clear()
print(arr2)

for a in arr2:
  if a.a == 2:
    arr2.remove(a)
    
print(arr2)
