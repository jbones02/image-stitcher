import numpy as np
import cv2
from .features import harrisFindCorners, findSift
from .matching import matchDescriptors
from .geometry import runRANSAC
from .blending import stitchAndBlendImagesRgb

def _downscale(img, maxSize):
  # Resize so longer size <= maxSize
  imgHeight, imgWidth = img.shape[:2]
  if max(imgHeight, imgWidth) <= maxSize:
    return img, 1.0
  scaleFactor = maxSize / float(max(imgHeight, imgWidth))
  return cv2.resize(img, None, fx=scaleFactor, fy=scaleFactor, interpolation=cv2.INTER_AREA)

def _prepImages(img1Bgr, img2Bgr, maxSize,):
  # Convert both to RGB and make grayscale copies
  img1Bgr = _downscale(img1Bgr, maxSize)
  img2Bgr = _downscale(img2Bgr, maxSize)

  img1Gray = cv2.cvtColor(img1Bgr, cv2.COLOR_BGR2GRAY)
  img2Gray = cv2.cvtColor(img2Bgr, cv2.COLOR_BGR2GRAY)
  img1Rgb = cv2.cvtColor(img1Bgr, cv2.COLOR_BGR2RGB)
  img2Rgb = cv2.cvtColor(img2Bgr, cv2.COLOR_BGR2RGB)

  return img1Rgb, img2Rgb, img1Gray, img2Gray

def _findHarrisCorners(img1Gray, img2Gray, sigma, harrisThresh, windowRadius):
  _, cornerRows1, cornerCols1 = harrisFindCorners(img1Gray, sigma, harrisThresh, windowRadius)
  _, cornerRows2, cornerCols2 = harrisFindCorners(img2Gray, sigma, harrisThresh, windowRadius)

  if len(cornerRows1) < 4 or len(cornerRows2) < 4:
    raise ValueError("Not enough Harris corners detected.")
  return cornerRows1, cornerCols1, cornerRows2, cornerCols2

def _siftAtCorners(img1Gray, img2Gray, cornerRows1, cornerCols1, cornerRows2, cornerCols2, siftEnlarge):
  keypointRadii1 = np.full(len(cornerRows1), 8)
  keypointRadii2 = np.full(len(cornerRows2), 8)

  keypoints1XYR = np.column_stack((cornerCols1, cornerRows1, keypointRadii1))
  keypoints2XYR = np.column_stack((cornerCols2, cornerRows2, keypointRadii2))

  siftDescriptors1 = findSift(img1Gray, keypoints1XYR, enlargeFactor=siftEnlarge)
  siftDescriptors2 = findSift(img2Gray, keypoints2XYR, enlargeFactor=siftEnlarge)

  keypoints1XY = np.column_stack((cornerCols1, cornerRows1))
  keypoints2XY = np.column_stack((cornerCols2, cornerRows2))

  return siftDescriptors1, siftDescriptors2, keypoints1XY, keypoints2XY

def _blendWarpedImages(img2Rgb, img1Rgb, homographyMatrix):
  blendedImageRgb = stitchAndBlendImagesRgb(img2Rgb, img1Rgb, homographyMatrix)
  outputImageBgr = cv2.cvtColor(blendedImageRgb, cv2.COLOR_RGB2BGR)
  return outputImageBgr

def stitchImages(
  img1Bgr,
  img2Bgr,
  *,
  sigma: float = 2.0,
  harrisThreshold: float = 3000.0,
  harrisWindowRadius: int = 3,
  siftEnlarge: float = 1.5,
  maxSize: int = 1600,
  maxDescriptorMatches=None,
  ransacIters=1000,
  ransacThreshold=1.0,
):
  img1Rgb, img2Rgb, img1Gray, img2Gray = _prepImages(img1Bgr, img2Bgr, maxSize)
  cornerRows1, cornerCols1, cornerRows2, cornerCols2 = _findHarrisCorners(
    img1Gray, img2Gray, sigma, harrisThreshold, harrisWindowRadius
  )
  sift1, sift2, keypoints1XY, keypoints2XY = _siftAtCorners(
    img1Gray, img2Gray, cornerRows1, cornerCols1, cornerRows2, cornerCols2, siftEnlarge
  )
  descriptorMatches = matchDescriptors(sift1, sift2, maxDescriptorMatches)

  homographyMatrix = runRANSAC(descriptorMatches, keypoints1XY, keypoints2XY, ransacIters, ransacThreshold)
  if homographyMatrix is None:
    raise ValueError("Homography estimation failed.")

  return _blendWarpedImages(img2Rgb, img1Rgb, homographyMatrix)
