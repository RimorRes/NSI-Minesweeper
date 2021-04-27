import random

def mines():
  minelist = []
  counter = 0 

  while len(minelist) < 10:
    x = random.randint(0,7)
    y = random.randint(0,12)
    pos = [x,y]
    minelist.append(pos)
    counter += 1 
    print(minelist)

    for i in range(len(minelist)-1):
      if pos == minelist[i]:
        minelist.remove[i]
