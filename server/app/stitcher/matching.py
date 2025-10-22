import numpy as np

def _calcSquaredDistance(descriptors1, descriptors2):
  descriptors1 = np.expand_dims(descriptors1, axis=0)
  descriptors2 = np.expand_dims(descriptors2, axis=1)
  return np.sum((descriptors1 - descriptors2) ** 2, axis=-1)

# Flatten distance matrix into (i, j, squaredDist)
def _buildPairs(distances: np.ndarray) -> list[tuple[int, int, float]]:
  num1, num2 = distances.shape
  return [(i, j, float(distances[i, j])) for i in range(num1) for j in range(num2)]

# Ascending order
def _sortPairsByDist(pairs: list[tuple[int, int, float]]) -> list[tuple[int, int, float]]:
  return sorted(pairs, key=lambda pair: pair[2])

def _greedyNonconflictingSelection(sortedPairs: list[tuple[int, int, float]], maxMatches: int) -> list[tuple[int, int]]:
  used1, used2 = set(), set()
  matches: list[tuple[int, int]] = []
  for i, j, _ in sortedPairs:
    if len(matches) >= maxMatches:
      break
    if i not in used1 and j not in used2:
      matches.append((i, j))
      used1.add(i)
      used2.add(j)
  return matches

def matchDescriptors(descriptors1, descriptors2, numMatchesToFind):
  distances = _calcSquaredDistance(descriptors1, descriptors2)
  pairs = _buildPairs(distances)
  sortedPairs = _sortPairsByDist(pairs)
  return _greedyNonconflictingSelection(sortedPairs, numMatchesToFind)
