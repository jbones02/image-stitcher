import { Form, Button, Spinner,
  Accordion, Row, Col,
  OverlayTrigger, Tooltip, FormGroup
} from "react-bootstrap";

const ControlPanel = (props) => {
  const {
    sigma, setSigma,
    harrisThresh, setHarrisThresh,
    harrisRadius, setHarrisRadius,
    siftEnlarge, setSiftEnlarge,
    maxSize, setMaxSize,
    numMatches, setNumMatches,
    ransacIters, setRansacIters,
    ransacThresh, setRansacThresh,
    img1, img2, loading, onStitch, onReset,
  } = props;

  const bothImagesUploaded = img1 || img2;
  const stitchReady = !loading && bothImagesUploaded;

  const stitchTooltip = (
    <Tooltip id="stitchHint">
      You must upload 2 images first
    </Tooltip>
  );

  return (
    <div className="d-flex flex-column flex-md-row align-items-stretch gap-2">
      <div className="flex-grow-1">
        <Accordion className="shadow rounded-3 dirty-white-bg h-100">
          <Accordion.Item eventKey="0">
            <Accordion.Header>Advanced options</Accordion.Header>
            <Accordion.Body>
              <Row className="gy-3">
                <Col sm={6} lg={4}>
                  <FormGroup controlId="sigma">
                    <Form.Label>Sigma</Form.Label>
                    <Form.Control
                      type="number"
                      step="0.1"
                      value={sigma}
                      onChange={(e) => setSigma(Number(e.target.value))}
                    />
                  </FormGroup>
                </Col>
                <Col sm={6} lg={4}>
                  <FormGroup controlId="harrisThresh">
                    <Form.Label>Harris Threshold</Form.Label>
                    <Form.Control
                      type="number"
                      step="1"
                      value={harrisThresh}
                      onChange={(e) => setHarrisThresh(Number(e.target.value))}
                    />
                  </FormGroup>
                </Col>
                <Col sm={6} lg={4}>
                  <FormGroup controlId="harrisRadius">
                    <Form.Label>Harris Radius</Form.Label>
                    <Form.Control
                      type="number"
                      step="1"
                      value={harrisRadius}
                      onChange={(e) => setHarrisRadius(Number(e.target.value))}
                    />
                  </FormGroup>
                </Col>
                <Col sm={6} lg={4}>
                  <FormGroup controlId="siftEnlarge">
                    <Form.Label>SIFT Enlarge</Form.Label>
                    <Form.Control
                      type="number"
                      step="0.1"
                      value={siftEnlarge}
                      onChange={(e) => setSiftEnlarge(Number(e.target.value))}
                    />
                  </FormGroup>
                </Col>
                <Col sm={6} lg={4}>
                  <FormGroup controlId="maxSize">
                    <Form.Label>Max Size (px)</Form.Label>
                    <Form.Control
                      type="number"
                      step="1"
                      value={maxSize}
                      onChange={(e) => setMaxSize(Number(e.target.value))}
                    />
                  </FormGroup>
                </Col>
                <Col sm={6} lg={4}>
                  <FormGroup controlId="numMatches">
                    <Form.Label>Num Matches</Form.Label>
                    <Form.Control
                      type="number"
                      step="1"
                      value={numMatches}
                      onChange={(e) => setNumMatches(Number(e.target.value))}
                    />
                  </FormGroup>
                </Col>
                <Col sm={6} lg={4}>
                  <FormGroup controlId="ransacIters">
                    <Form.Label>RANSAC Iters</Form.Label>
                    <Form.Control
                      type="number"
                      step="50"
                      value={ransacIters}
                      onChange={(e) => setRansacIters(Number(e.target.value))}
                    />
                  </FormGroup>
                </Col>
                <Col sm={6} lg={4}>
                  <FormGroup controlId="ransacThres">
                    <Form.Label>RANSAC Threshold</Form.Label>
                    <Form.Control
                      type="number"
                      step="0.1"
                      value={ransacThresh}
                      onChange={(e) => setRansacThresh(Number(e.target.value))}
                    />
                  </FormGroup>
                </Col>
              </Row>
            </Accordion.Body>
          </Accordion.Item>
        </Accordion>
      </div>

      <div
        className="d-flex flex-row align-items-stretch gap-2 mt-2 mt-md-0 ms-md-2 flex-shrink-0 justify-content-end justify-content-md-start"
        style={{ minWidth: "fit-content" }}
      >
        <OverlayTrigger
          placement="top"
          overlay={!bothImagesUploaded ? stitchTooltip : <></>}
          delay={{ show: 200, hide: 0 }}
        >
          <span
            className={!bothImagesUploaded ? "cursor-not-allowed" : ""}
            style={{ display: "inline-block" }}
          >
            <Button
              variant="primary"
              disabled={!stitchReady}
              onClick={onStitch}
              className={`shadow ${!stitchReady ? "btn-soft-disabled" : ""}`}
              style={{ minWidth: 96, height: 45, pointerEvents: stitchReady ? "auto" : "none" }}
              size="lg"
              aria-disabled={!stitchReady}
              aria-describedby={!bothImagesUploaded ? "stitchHint" : undefined}
            >
              {loading ? <Spinner animation="border" size="sm" role="status" /> : "Stitch"}
            </Button>
          </span>
        </OverlayTrigger>

        <Button
          variant="secondary"
          onClick={onReset}
          disabled={loading}
          className="shadow"
          style={{ minWidth: 96, height: 45 }}
          size="lg"
        >
          Reset
        </Button>
      </div>
    </div>
  );
};

export default ControlPanel;
