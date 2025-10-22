import { useState, useRef } from "react";
import "./App.css";
import {
  Container, Row, Col,
  Alert, Card
} from "react-bootstrap";
import ImageUploadCard from "./components/ImageUploadCard";
import ResultCard from "./components/ResultCard";
import ControlPanel from "./components/ControlPanel";
import { PanoramaIcon, WarningIcon } from "@phosphor-icons/react";

const ACCEPTED = ["image/jpeg", "image/png", "image/jpg", "image/webp"];

const safeReadError = async (res) => {
  try {
    const data = await res.json();
    return data?.detail || "";
  } catch {
    try {
      return await res.text();
    } catch {
      return "";
    }
  }
};

const App = () => {
  // Files
  const [img1, setImg1] = useState(null);
  const [img2, setImg2] = useState(null);
  const [preview1, setPreview1] = useState(null);
  const [preview2, setPreview2] = useState(null);

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [resultUrl, setResultUrl] = useState(null);

  // Options
  const [sigma, setSigma] = useState(2.0);
  const [harrisThresh, setHarrisThresh] = useState(3000);
  const [harrisRadius, setHarrisRadius] = useState(3);
  const [siftEnlarge, setSiftEnlarge] = useState(1.5);
  const [maxSize, setMaxSize] = useState(1600);
  const [numMatches, setNumMatches] = useState(100);
  const [ransacIters, setRansacIters] = useState(1000);
  const [ransacThresh, setRansacThresh] = useState(1.0);

  const anchorRef = useRef(null);

  const handleUpload = (setter, setPreview) => (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!ACCEPTED.includes(file.type)) {
      setError("Please choose a JPG/PNG/WEBP image.");
      return;
    }
    setter(file);
    setPreview(URL.createObjectURL(file));
    setError("");
    if (resultUrl) {
      URL.revokeObjectURL(resultUrl);
      setResultUrl(null);
    }
  };

  const resetAll = () => {
    setImg1(null);
    setImg2(null);
    if (preview1) URL.revokeObjectURL(preview1);
    if (preview2) URL.revokeObjectURL(preview2);
    if (resultUrl) URL.revokeObjectURL(resultUrl);
    setPreview1(null);
    setPreview2(null);
    setResultUrl(null);
    setError("");
    setLoading(false);
  };

  const stitch = async () => {
    try {
      if (!img1 || !img2) {
        setError("Please select both images.");
        return;
      }
      setError("");
      setLoading(true);

      const formData = new FormData();
      formData.append("image1", img1);
      formData.append("image2", img2);
      formData.append("sigma", String(sigma));
      formData.append("harrisThresh", String(harrisThresh));
      formData.append("harrisRadius", String(harrisRadius));
      formData.append("siftEnlarge", String(siftEnlarge));
      formData.append("maxSize", String(maxSize));
      formData.append("numMatches", String(numMatches));
      formData.append("ransacIters", String(ransacIters));
      formData.append("ransacThresh", String(ransacThresh));

      const res = await fetch("/api/stitch", {
        method: "POST",
        body: formData
      });

      if (!res.ok) {
        const msg = await safeReadError(res);
        throw new Error(msg || `Server returned ${res.status}`);
      }

      const blob = await res.blob();

      if (resultUrl) URL.revokeObjectURL(resultUrl);
      const url = URL.createObjectURL(blob);
      setResultUrl(url);

      setTimeout(() => anchorRef.current?.focus(), 0);
    } catch (err) {
      setError(err?.message ?? "Something went wrong while stitching the images together.");
      if (resultUrl) {
        URL.revokeObjectURL(resultUrl);
        setResultUrl(null);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Container fluid="xxl" className="my-4 px-3 px-xl-5">
        <Row className="d-flex justify-content-center">
          <Col xs={12} sm={11} lg={10}>
            <Card className="rounded-4 shadow-lg pt-4 pb-4 pb-sm-5 px-4 px-sm-5 mt-4 mb-4 dirty-white-bg borderless">
              <h1 className="text-center d-flex justify-content-center align-items-center gap-3 mb-4  dark-olive-txt fw-bold">
                <PanoramaIcon size={55} weight="fill" className="d-none d-sm-block" />
                Panorama Maker
              </h1>

              <Row className="g-4 g-sm-5 g-md-4 g-lg-5 justify-content-center">
                <Col xs={12} md={6} className="d-flex justify-content-center">
                  <ImageUploadCard
                    title="Image 1"
                    controlId="image1"
                    onChange={handleUpload(setImg1, setPreview1)}
                    src={preview1}
                  />
                </Col>

                <Col xs={12} md={6} className="d-flex justify-content-center">
                  <ImageUploadCard
                    title="Image 2"
                    controlId="image2"
                    onChange={handleUpload(setImg2, setPreview2)}
                    src={preview2}
                  />
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>

        {error && (
          <Row className="mb-3 justify-content-center">
            <Col xs={12} sm={11} lg={10}>
              <Alert variant="danger" className="d-flex gap-2 align-items-center">
                <WarningIcon className="pt-1" size={30} />
                {error}
              </Alert>
            </Col>
          </Row>
        )}

        <Row className="d-flex justify-content-center mb-4">
          <Col xs={12} sm={11} lg={10}>
            <ControlPanel
              sigma={sigma} setSigma={setSigma}
              harrisThresh={harrisThresh} setHarrisThresh={setHarrisThresh}
              harrisRadius={harrisRadius} setHarrisRadius={setHarrisRadius}
              siftEnlarge={siftEnlarge} setSiftEnlarge={setSiftEnlarge}
              maxSize={maxSize} setMaxSize={setMaxSize}
              numMatches={numMatches} setNumMatches={setNumMatches}
              ransacIters={ransacIters} setRansacIters={setRansacIters}
              ransacThresh={ransacThresh} setRansacThresh={setRansacThresh}
              img1={img1}
              img2={img2}
              loading={loading}
              onStitch={stitch}
              onReset={resetAll}
            />
          </Col>
        </Row>

        {resultUrl && (
          <Row className="justify-content-center mb-5">
            <Col xs={12} sm={11} lg={10} className="d-flex justify-content-center">
              <ResultCard resultUrl={resultUrl} anchorRef={anchorRef} />
            </Col>
          </Row>
        )}
      </Container>
    </>
  );
};

export default App;
