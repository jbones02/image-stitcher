from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
import cv2
import numpy as np
from app.stitcher import stitchImages

app = FastAPI(title="image-stitcher", version="0.2.2")

def _readImg(upload):
  data = upload.file.read()
  if not data:
    raise ValueError("empty upload")
  arr = np.frombuffer(data, dtype=np.uint8)
  img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
  if img is None:
    raise ValueError("could not decode image")
  return img


@app.post("/stitch")
def stitch_endpoint(
  image1: UploadFile = File(...),
  image2: UploadFile = File(...),
  sigma: float = Form(2.0),
  harrisThreshold: float = Form(3000.0),
  harrisWindowRadius: int = Form(3),
  siftEnlarge: float = Form(1.5),
  maxSize: int = Form(1600),
  maxDescriptorMatches: int = Form(100),
  ransacIters: int = Form(1000),
  ransacThreshold: float = Form(1.0),
):
  try:
    img_left = _readImg(image1)
    img_right = _readImg(image2)
  except ValueError as e:
    raise HTTPException(status_code=422, detail=str(e))

  try:
    pano = stitchImages(
      img_left,
      img_right,
      sigma=sigma,
      harrisThreshold=harrisThreshold,
      harrisWindowRadius=harrisWindowRadius,
      siftEnlarge=siftEnlarge,
      maxSize=maxSize,
      maxDescriptorMatches=maxDescriptorMatches,
      ransacIters=ransacIters,
      ransacThreshold=ransacThreshold,
    )
  except Exception as e:
    raise HTTPException(status_code=500, detail="stitch failed") from e

  # Prefer jpeg, fallback to png
  media = "image/jpeg"
  ok, buf = cv2.imencode(".jpg", pano, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
  if not ok:
    ok, buf = cv2.imencode(".png", pano)
    if not ok:
      raise HTTPException(status_code=500, detail="encode failed")
    media = "image/png"

  return Response(content=buf.tobytes(), media_type=media, headers={"Cache-Control": "no-store"})
