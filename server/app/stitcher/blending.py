import numpy as np
import cv2
from scipy.ndimage import distance_transform_edt

# Helpers
def _computeBoundsAndTransform(img1, img2, homographyMatrix):
  img1Height, img1Width = img1.shape
  img2Height, img2Width = img2.shape

  topLeftH = np.array([0, 0, 1])
  topRightH = np.array([img2Width, 0, 1])
  bottomRightH = np.array([img2Width, img2Height, 1])
  bottomLeftH = np.array([0, img2Height, 1])
  corners = np.vstack([topLeftH, topRightH, bottomRightH, bottomLeftH])

  warpedCorners = (homographyMatrix @ corners.T).T
  warpedCorners /= warpedCorners[:, 2:3]

  img1Corners = np.array([
    [0, 0],
    [img1Width, 0],
    [img1Width, img1Height],
    [0, img1Height],
  ])
  warpedXY = warpedCorners[:, :2]
  allCorners = np.vstack([img1Corners, warpedXY])

  xMin, yMin = np.int32(allCorners.min(axis=0).ravel() - 0.5)
  xMax, yMax = np.int32(allCorners.max(axis=0).ravel() + 0.5)

  offset = [-xMin, -yMin]
  offsetTransform = np.array([[1,0,offset[0]],[0,1,offset[1]],[0,0,1]], dtype=np.float32)
  panoramaHeight, panoramaWidth = (yMax - yMin), (xMax - xMin)
  return offset, offsetTransform, panoramaHeight, panoramaWidth


def _warpImage2(img2, offsetTransform, homographyMatrix, panoramaWidth, panoramaHeight):
  return cv2.warpPerspective(img2, offsetTransform @ homographyMatrix, (panoramaWidth, panoramaHeight))


def _placeImage1OnCanvas(img1, offset, canvasTemplate):
  canvas = np.zeros_like(canvasTemplate, dtype=np.uint8)
  offsetY, offsetX = offset[1], offset[0]
  img1Height, img1Width = img1.shape
  canvas[offsetY:offsetY+img1Height, offsetX:offsetX+img1Width] = img1
  return canvas


def _calcMasks(canvas1, warped2):
  mask1 = canvas1 > 0
  mask2 = warped2 > 0
  overlap = mask1 & mask2
  onlyMask1 = mask1 & (~mask2)
  onlyMask2 = mask2 & (~mask1)
  return mask1, mask2, overlap, onlyMask1, onlyMask2


def _distanceWeights(mask1, mask2, eps):
  distance1 = distance_transform_edt(mask1)
  distance2 = distance_transform_edt(mask2)

  weight1 = distance1.astype(np.float32) * mask1.astype(np.float32)
  weight2 = distance2.astype(np.float32) * mask2.astype(np.float32)
  weightSum = weight1 + weight2 + eps
  weight1Normalized = weight1 / weightSum
  weight2Normalized = weight2 / weightSum
  return weight1Normalized, weight2Normalized


def _blend(canvas1, warped2, overlap, only1, only2, weight1Norm, weight2Norm):
  out = np.zeros_like(canvas1, dtype=np.float32)
  out[overlap] = (
    weight1Norm[overlap] * canvas1[overlap].astype(np.float32) +
    weight2Norm[overlap] * warped2[overlap].astype(np.float32)
  )
  out[only1] = canvas1[only1].astype(np.float32)
  out[only2] = warped2[only2].astype(np.float32)
  return np.clip(out, 0, 255).astype(np.uint8)


def stitchAndBlendImagesGray(img1, img2, homographyMatrix, eps: float = 1e-6):
  # Use dist transform feathering
  offset, offsetTransform, panoramaHeight, panoramaWidth = _computeBoundsAndTransform(img1, img2, homographyMatrix)
  warped2 = _warpImage2(img2, offsetTransform, homographyMatrix, panoramaWidth, panoramaHeight)
  canvas1 = _placeImage1OnCanvas(img1, offset, warped2)

  mask1, mask2, overlap, onlyMask1, onlyMask2 = _calcMasks(canvas1, warped2)

  if not overlap.any():
    out = canvas1.copy()
    out[onlyMask2] = warped2[onlyMask2]
    return out

  weight1Normalized, weight2Normalized = _distanceWeights(mask1, mask2, eps)
  return _blend(canvas1, warped2, overlap, onlyMask1, onlyMask2, weight1Normalized, weight2Normalized)


def stitchAndBlendImagesRgb(image1, image2, homographyMatrix):
  red1, green1, blue1 = cv2.split(image1)
  red2, green2, blue2 = cv2.split(image2)

  stitchedRed = stitchAndBlendImagesGray(red1, red2, homographyMatrix)
  stitchedGreen = stitchAndBlendImagesGray(green1, green2, homographyMatrix)
  stitchedBlue = stitchAndBlendImagesGray(blue1, blue2, homographyMatrix)

  panorama = cv2.merge((stitchedRed, stitchedGreen, stitchedBlue))
  return panorama
