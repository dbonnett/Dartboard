# FIND ALL POSSIBLE SCORE COMBINATIONS
import matplotlib.pyplot as plt

# start with all possible numbers you can score:
numbers = list(range(0, 51))
for x in [23, 29, 31, 35, 37, 41, 43, 44, 46, 47, 49]:
  numbers.remove(x)
# there are 39 possible scores between 1-50  (we'll add zero manually to deal with edge cases)

# list for permutations of winning results
listOfCombos = []

# winning with 1 dart
listOfCombos.append([50])

# winning with 2 darts
for i in numbers:
  if (50 - i) in numbers:
    listOfCombos.append([i, 50-i])
  # hitting bullseye second
  if (0 < i < 50):
    listOfCombos.append([i, 50])

  # winning with 3 darts
  for j in numbers:
    if (50 - i - j) in numbers:
      listOfCombos.append([i, j, 50-i-j])
    # hitting bullseye third
    if (0 < i + j < 50):
      listOfCombos.append([i, j, 50])

#remove combos with trailing zeros
listOfCombosCopy = []
for l in listOfCombos:
  if l[-1] != 0:
    listOfCombosCopy.append(l)
# list of permutations complete ✅

# find most popular numbers found in combination (besides 50)
num_dict = {n: 0 for n in numbers}
for l in listOfCombosCopy:
  for i in l:
    num_dict[i] += 1
del num_dict[50]

# plot
bars = plt.bar(num_dict.keys(), num_dict.values())
for bar in bars:
  height = bar.get_height()
  plt.text(
    bar.get_x() + bar.get_width() / 2,
    height,
    str(height),
    ha='center',
    va='bottom',
    fontsize=6
  )
plt.xlabel("Score")
plt.ylabel("Occurences")
plt.title("Individual dart score occurences in all possible winning games\n(excluding 50)")
plt.show()