import numpy as np

def _calcHomography(matchedPoints1, matchedPoints2):
  numPoints = matchedPoints1.shape[0]
  A = np.zeros((2 * numPoints, 9))
  for i in range(numPoints):
    x1, y1 = matchedPoints1[i]
    x2, y2 = matchedPoints2[i]
    A[2 * i] = [-x1, -y1, -1, 0, 0, 0, x1 * x2, y1 * x2, x2]
    A[2 * i + 1] = [0, 0, 0, -x1, -y1, -1, x1 * y2, y1 * y2, y2]

  # Solve Ah = 0
  _, _, V = np.linalg.svd(A)
  H = V[-1].reshape(3, 3)
  return H / H[2, 2]

def _asArrayOrRaise(descriptorMatches):
  arr = np.array(descriptorMatches)
  if len(arr) < 4:
    raise ValueError("Not enough matches")
  return arr

def _sampleFourIndices(numMatches):
  return np.random.choice(numMatches, size=4, replace=False)

def _homographyFromSample(descriptorMatches, keypoints1, keypoints2, sampleIndices):
  selectedMatches = descriptorMatches[sampleIndices]
  matchedPoints1 = keypoints1[selectedMatches[:, 0]]
  matchedPoints2 = keypoints2[selectedMatches[:, 1]]
  return _calcHomography(matchedPoints1, matchedPoints2)

def _projectPoints(homographyMatrix, keypoints1):
  homogenousKeypoints1 = np.column_stack((keypoints1[:, :2], np.ones(len(keypoints1))))
  transformedPoints = (homographyMatrix @ homogenousKeypoints1.T)
  transformedPoints /= (transformedPoints[2] + 1e-10)
  return transformedPoints

def _calcMatchErrors(transformedPoints, descriptorMatches, keypoints2):
  predictedPoints = transformedPoints[:2].T[descriptorMatches[:, 0]]
  targetPoints = keypoints2[descriptorMatches[:, 1]]
  return np.sum((predictedPoints - targetPoints) ** 2, axis=1)

def _filterInlierMatches(descriptorMatches, errors, inlierThresh):
  return descriptorMatches[errors < inlierThresh**2]

def _refitIfNeeded(bestInliers, keypoints1, keypoints2, bestHomographyMatrix):
  if len(bestInliers) > 4:
    sourceInlierPoints = keypoints1[bestInliers[:, 0]]
    destinationInlierPoints = keypoints2[bestInliers[:, 1]]
    return _calcHomography(sourceInlierPoints, destinationInlierPoints)
  return bestHomographyMatrix

def runRANSAC(descriptorMatches, keypoints1, keypoints2, iters=2000, inlierThresh=0.1):
  # Convert to arr and validate
  descriptorMatches = _asArrayOrRaise(descriptorMatches)

  bestInliers = np.array([], dtype=int)
  bestHomographyMatrix = None

  for _ in range(iters):
    sampleIndices = _sampleFourIndices(len(descriptorMatches))

    curHomographyMatrix = _homographyFromSample(
      descriptorMatches, keypoints1, keypoints2, sampleIndices
    )
    transformedPoints = _projectPoints(curHomographyMatrix, keypoints1)
    errors = _calcMatchErrors(transformedPoints, descriptorMatches, keypoints2)
    inliers = _filterInlierMatches(descriptorMatches, errors, inlierThresh)

    # If more inliers save cur H
    if len(inliers) > len(bestInliers):
      bestInliers = inliers
      bestHomographyMatrix = curHomographyMatrix

  bestHomographyMatrix = _refitIfNeeded(bestInliers, keypoints1, keypoints2, bestHomographyMatrix)

  return bestHomographyMatrix
