import numpy as np
from scipy.signal import convolve2d
from scipy.ndimage import rank_filter
from scipy.stats import norm

def _normalizeGaussDerivative(gaussDerivative):
  return gaussDerivative * 2 / np.abs(gaussDerivative).sum()

def _buildGaussDerivativeKernels(sigma):
  GaussRadius = int(4 * np.floor(sigma))
  G = norm.pdf(np.arange(-GaussRadius, GaussRadius + 1), loc=0, scale=sigma).reshape(-1, 1)
  G = G.T * G

  # Calc derivatives
  Gx, Gy = np.gradient(G)
  Gx = _normalizeGaussDerivative(Gx)
  Gy = _normalizeGaussDerivative(Gy)
  return Gx, Gy

# SIFT helpers
def _prepSiftImg(img):
  return img.astype(np.float64)

def _calcGradients(img, sigmaEdge=1):
  Gx, Gy = _buildGaussDerivativeKernels(sigmaEdge)
  gradX = convolve2d(img, Gx, "same")
  gradY = convolve2d(img, Gy, "same")
  magnitude = np.sqrt(gradX ** 2 + gradY ** 2)
  theta = np.arctan2(gradY, gradX)
  return gradX, gradY, magnitude, theta

def _buildSiftAngleAndCellGrids(numAngles, numBins):
  angleStep = 2 * np.pi / numAngles
  angles = np.arange(0, 2 * np.pi, angleStep)

  start = -1 + 1 / numBins
  end = 1 + 1 / numBins
  step = 2 / numBins
  interval = np.arange(start, end, step)

  gridX, gridY = np.meshgrid(interval, interval)
  gridX = gridX.reshape((1, -1))
  gridY = gridY.reshape((1, -1))

  return angles, gridX, gridY

def _calcAngleVolume(theta, magnitude, angles, alpha, imgHeight, imgWidth):
  # Angle strength at each pixel
  numAngles = len(angles)
  angleVol = np.zeros((imgHeight, imgWidth, numAngles))
  for i in range(numAngles):
    cosAligned = np.cos(theta - angles[i]) ** alpha
    cosAligned = cosAligned * (cosAligned > 0)
    angleVol[:, :, i] = cosAligned * magnitude
  return angleVol

# Calc rectangle bounds and gridStep for a keypoint
def _calcKeypointBounds(centerX, centerY, keypointRadius, numBins, imgHeight, imgWidth):
  gridStep = 2.0 / numBins * keypointRadius
  xMin = np.floor(np.max([centerX - keypointRadius - gridStep / 2, 0])).astype(np.int32)
  xMax = np.ceil(np.min([centerX + keypointRadius + gridStep / 2, imgWidth])).astype(np.int32)
  yMin = np.floor(np.max([centerY - keypointRadius - gridStep / 2, 0])).astype(np.int32)
  yMax = np.ceil(np.min([centerY + keypointRadius + gridStep / 2, imgHeight])).astype(np.int32)
  return xMin, xMax, yMin, yMax, gridStep

# List all (x, y) pixels in rectangle
def _buildPixelGrid(xMin, xMax, yMin, yMax):
  pixelXGrid, pixelYGrid = np.meshgrid(np.arange(xMin, xMax, 1), np.arange(yMin, yMax, 1))
  pixelXGrid = pixelXGrid.reshape((-1, 1))
  pixelYGrid = pixelYGrid.reshape((-1, 1))
  return pixelXGrid, pixelYGrid

def _calcBilinearWeights(pixelXGrid, pixelYGrid, gridCenterX, gridCenterY, gridStep):
  distPX = np.abs(pixelXGrid - gridCenterX)
  distPY = np.abs(pixelYGrid - gridCenterY)
  weightX = np.divide(distPX, gridStep,
    out=np.zeros_like(distPX, dtype=float),
    where=gridStep != 0)
  weightX = (1 - weightX) * (weightX <= 1)
  weightY = np.divide(distPY, gridStep,
    out=np.zeros_like(distPY, dtype=float),
    where=gridStep != 0)
  weightY = (1 - weightY) * (weightY <= 1)
  return weightX * weightY

def _sumAngles(angleVol, xMin, xMax, yMin, yMax, cellWeights, numAngles, numBins):
  numSamples = numBins * numBins
  angleHistBlock = np.zeros((numAngles, numSamples))
  for j in range(numAngles):
    patchResponse = angleVol[yMin:yMax, xMin:xMax, j].reshape((-1, 1))
    angleHistBlock[j, :] = (patchResponse * cellWeights).sum(axis=0)
  return angleHistBlock.flatten()

def _calcKeypointSift(angleVol, centerX, centerY, keypointRadius, gridX, gridY, numBins, imgHeight, imgWidth, numAngles):
  gridCenterX = gridX * keypointRadius + centerX
  gridCenterY = gridY * keypointRadius + centerY
  xMin, xMax, yMin, yMax, gridStep = _calcKeypointBounds(centerX, centerY, keypointRadius, numBins, imgHeight, imgWidth)
  pixelXGrid, pixelYGrid = _buildPixelGrid(xMin, xMax, yMin, yMax)
  cellWeights = _calcBilinearWeights(pixelXGrid, pixelYGrid, gridCenterX, gridCenterY, gridStep)
  return _sumAngles(angleVol, xMin, xMax, yMin, yMax, cellWeights, numAngles, numBins)

def _normalizeDescriptors(siftDescriptors):
  normalizedDescriptors = np.sqrt(np.sum(siftDescriptors ** 2, axis=-1))
  if np.sum(normalizedDescriptors > 1) > 0:
    siftDescriptorsNorm = siftDescriptors[normalizedDescriptors > 1, :]
    siftDescriptorsNorm /= normalizedDescriptors[normalizedDescriptors > 1].reshape(-1, 1)
    siftDescriptorsNorm = np.clip(siftDescriptorsNorm, siftDescriptorsNorm.min(), 0.2)
    siftDescriptorsNorm /= np.sqrt(np.sum(siftDescriptorsNorm ** 2, axis=-1, keepdims=True))
    siftDescriptors[normalizedDescriptors > 1, :] = siftDescriptorsNorm
  return siftDescriptors

# Calc sift descriptors at circles
def findSift(img, keypointsXYR, enlargeFactor=1.5):
  img = _prepSiftImg(img)

  NUM_ANGLES = 8
  NUM_BINS = 4
  NUM_SAMPLES = NUM_BINS * NUM_BINS
  ALPHA = 9
  SIGMA_EDGE = 1

  angles, gridX, gridY = _buildSiftAngleAndCellGrids(NUM_ANGLES, NUM_BINS)
  imgHeight, imgWidth = img.shape[:2]
  numKeypoints = keypointsXYR.shape[0]

  # Gradients and angle tensor
  _, _, magnitude, theta = _calcGradients(img, sigmaEdge=SIGMA_EDGE)
  angleVol = _calcAngleVolume(theta, magnitude, angles, ALPHA, imgHeight, imgWidth)

  # Accumulate descriptors
  siftDescriptors = np.zeros((numKeypoints, NUM_SAMPLES * NUM_ANGLES))
  for i in range(numKeypoints):
    centerX, centerY = keypointsXYR[i, :2]
    sampleRadius = keypointsXYR[i, 2] * enlargeFactor
    siftDescriptors[i, :] = _calcKeypointSift(
      angleVol, centerX, centerY, sampleRadius, gridX, gridY,
      NUM_BINS, imgHeight, imgWidth, NUM_ANGLES
    )

  return _normalizeDescriptors(siftDescriptors)

# Harris helpers
def _buildHarrisGaussKernel(sigma):
  kernelRadius = int(np.round(3 * np.floor(sigma)))
  gaussKernel = norm.pdf(np.arange(-kernelRadius, kernelRadius + 1), loc=0, scale=sigma).reshape(-1, 1)
  gaussKernel = gaussKernel.T * gaussKernel
  return gaussKernel / gaussKernel.sum()

# Calc gradient derivatives
def _calcImgDerivatives(img):
  dx = np.tile([[-1, 0, 1]], [3, 1])
  dy = dx.T
  gradX = convolve2d(img, dx, "same")
  gradY = convolve2d(img, dy, "same")
  return gradX, gradY

def _calcHarrisResponse(gradX, gradY, gaussKernel):
  gradX2 = convolve2d(gradX ** 2, gaussKernel, "same")
  gradY2 = convolve2d(gradY ** 2, gaussKernel, "same")
  gradXY = convolve2d(gradX * gradY, gaussKernel, "same")
  den = gradX2 + gradY2
  num = (gradX2 * gradY2 - gradXY ** 2)
  return np.divide(num, den, out=np.zeros_like(den, dtype=float), where=den != 0)

def _suppressNonMaxAndThreshold(response, threshold, windowRadius):
  size = int(2 * windowRadius + 1)
  windowMax = rank_filter(response, -1, size=size)
  suppressionMask = (response == windowMax) & (response > threshold)
  cornerRows, cornerCols = suppressionMask.nonzero()
  return suppressionMask, cornerRows, cornerCols

# Img must be in grayscale
def harrisFindCorners(img, sigma, threshold=None, radius=None):
  gradX, gradY = _calcImgDerivatives(img)
  gaussKernel = _buildHarrisGaussKernel(sigma)
  response = _calcHarrisResponse(gradX, gradY, gaussKernel)

  if threshold is None or radius is None:
    return response
  else:
    return _suppressNonMaxAndThreshold(response, threshold, radius)
