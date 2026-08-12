# FIND ALL POSSIBLE SCORE COMBINATIONS
import matplotlib.pyplot as plt

# start with all possible numbers you can score:
numbers = list(range(1, 51))
for x in [23, 29, 31, 35, 37, 41, 43, 44, 46, 47, 49]:
  numbers.remove(x)
# there are 39 possible scores between 1-50 

# count number of combinations to reach 50
oneDartCombos = 1
twoDartCombos = 0
threeDartCombos = 0
listOfCombos = []
d = {n: 0 for n in numbers}

for i in numbers:
  if (50 - i) in numbers:
    twoDartCombos += 1
    listOfCombos.append([i, 50-i])
    d[i] += 1
    d[50-i] += 1
  for j in numbers:
    if (50 - i - j) in numbers:
      threeDartCombos += 1
      listOfCombos.append([i, j, 50-i-j])
      d[i] += 1
      d[j] += 1
      d[50-i-j] += 1
listOfCombos.append([50])
d[50] = 1

print(f"Ways to win with one dart: {oneDartCombos}, two darts: {twoDartCombos}, three darts: {threeDartCombos}, \ntotal combos: {oneDartCombos + twoDartCombos + threeDartCombos}")
print(len(listOfCombos))

# find most popular numbers found in combination
plt.bar(d.keys(), d.values())
plt.xlabel("Score")
plt.ylabel("Occurences")
plt.title("Dart score occurences in all possible winning games")
plt.show()