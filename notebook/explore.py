# FIND ALL POSSIBLE SCORE COMBINATIONS
import matplotlib.pyplot as plt

# start with all possible numbers you can score:
numbers = list(range(1, 51))
for x in [23, 29, 31, 35, 37, 41, 43, 44, 46, 47, 49]:
  numbers.remove(x)
# there are 39 possible scores between 1-50  (we'll add zero manually to deal with edge cases)

# count number of combinations to reach 50
oneDartCombos = 0
twoDartCombos = 0
threeDartCombos = 0
listOfCombos = []
instances = {n: 0 for n in numbers}
instances[0] = 0

# winning with 1 dart
listOfCombos.append([50])
oneDartCombos += 1
# zero edge cases
listOfCombos.extend([[0, 50], [0, 0, 50]])
twoDartCombos += 1
threeDartCombos += 1
instances[50] += 3

# winning with 2 scoring darts
for i in numbers:
  if (50 - i) in numbers:
    listOfCombos.extend([[i, 50-i], [0, i, 50-i], [i, 0, 50-i]])
    twoDartCombos += 1
    threeDartCombos += 2
    instances[i] += 3
    instances[50-i] += 3
    instances[0] += 2
  # hitting bullseye second
  if (i < 50):
    listOfCombos.extend([[i, 50], [0, i, 50], [i, 0, 50]])
    twoDartCombos += 1
    threeDartCombos += 2
    instances[i] += 1
    instances[50] += 1

  # winning with 3 scoring darts
  for j in numbers:
    if (50 - i - j) in numbers:
      listOfCombos.append([i, j, 50-i-j])
      threeDartCombos += 1
      instances[i] += 1
      instances[j] += 1
      instances[50-i-j] += 1
    # hitting bullseye third
    if (i + j < 50):
      listOfCombos.append([i, j, 50])
      threeDartCombos += 1
      instances[i] += 1
      instances[j] += 1
      instances[50] += 1

print(f"Ways to win with one dart: {oneDartCombos}, two darts: {twoDartCombos}, three darts: {threeDartCombos}, \ntotal combos: {oneDartCombos + twoDartCombos + threeDartCombos}")
print(f"list of combos length: {len(listOfCombos)}")
# test that the instances dict and combo counts add up:
dartsThrown = 0
for l in listOfCombos:
  dartsThrown += len(l)
print(f"Total darts thrown:\n1 * oneDartCombos = {oneDartCombos}\n2 * twoDartCombos = {twoDartCombos * 2}\n3 * threeDartCombos = {threeDartCombos*3}\n total instances: {oneDartCombos + (2*twoDartCombos) + (3*threeDartCombos)}\nDarts thrown in 'instances' dict: {dartsThrown}")

# find most popular numbers found in combination (besides 50)
inst_copy = instances
inst_copy[50] = 0
plt.bar(inst_copy.keys(), inst_copy.values())
plt.xlabel("Score")
plt.ylabel("Occurences")
plt.title("Individual dart score occurences in all possible winning games\n(excluding 50)")
plt.show()