# FIND ALL POSSIBLE SCORE COMBINATIONS

# start with all possible numbers you can score:
numbers = list(range(1, 51))
for x in [23, 29, 31, 35, 37, 41, 43, 44, 46, 47, 49]:
  numbers.remove(x)
print(numbers)
# there are 39 possible scores between 1-50 

# count number of combinations to reach 50
singleDartCombos = 1
doubleDartCombos = 0
tripleDartCombos = 0

for i in numbers:
  if (50 - i) in numbers:
    doubleDartCombos += 1

for i in numbers:
  for j in numbers:
    if (50 - i - j) in numbers:
      tripleDartCombos += 1

print(f"Ways to win with one dart: {singleDartCombos}, two darts: {doubleDartCombos}, three darts: {tripleDartCombos}, \ntotal combos: {singleDartCombos + doubleDartCombos + tripleDartCombos}")