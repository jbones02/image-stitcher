import numpy as np

def _calcSquaredDistance(queryDescriptors, candidateDescriptors):
  assert queryDescriptors.shape[1] == candidateDescriptors.shape[1], "Descriptor dimensions must match"
  queryDescriptors = np.expand_dims(queryDescriptors, axis=0)
  candidateDescriptors = np.expand_dims(candidateDescriptors, axis=1)
  return np.sum((queryDescriptors - candidateDescriptors) ** 2, axis=-1)

# Flatten distance matrix into (i, j, squaredDist)
def _buildPairs(distances: np.ndarray) -> list[tuple[int, int, float]]:
  numQuery, numCandidate = distances.shape
  return [(i, j, float(distances[i, j])) for i in range(numQuery) for j in range(numCandidate)]

# Ascending order
def _sortPairsByDist(pairs: list[tuple[int, int, float]]) -> list[tuple[int, int, float]]:
  return sorted(pairs, key=lambda pair: pair[2])

def _greedyNonconflictingSelection(sortedPairs: list[tuple[int, int, float]], maxMatches: int) -> list[tuple[int, int]]:
  usedQuery, usedCandidate = set(), set()
  matches: list[tuple[int, int]] = []
  for i, j, _ in sortedPairs:
    if len(matches) >= maxMatches:
      break
    if i not in usedQuery and j not in usedCandidate:
      matches.append((i, j))
      usedQuery.add(i)
      usedCandidate.add(j)
  return matches

def findDescriptorMatches(descriptorsSet1, descriptorsSet2, numMatchesToFind):
  distances = _calcSquaredDistance(descriptorsSet1, descriptorsSet2)
  pairs = _buildPairs(distances)
  sortedPairs = _sortPairsByDist(pairs)
  return _greedyNonconflictingSelection(sortedPairs, numMatchesToFind)
